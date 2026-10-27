"""Actual nxdk COFF probe under modeled MMIO/control-register reads.
No hardware, kernel scheduling or physical cache proof. CLI/POPFD execute.
"""
import datetime,hashlib,json,struct,sys,os
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn721/build001')
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import *
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'model001.json';assert not out.exists()
b=(P/'probe.obj').read_bytes();r={'passed':False,'object_sha256':sha(P/'probe.obj'),'scope':__doc__,'cases':[]}
try:
 machine,nsec,_,symptr,nsyms,optsz,_=struct.unpack_from('<HHLLLHH',b);assert machine==0x14c and not optsz
 strings=b[symptr+18*nsyms:];sections=[];symbols={};indices={};i=0
 for j in range(nsec):
  h=struct.unpack_from('<8sLLLLLLHHL',b,20+40*j)
  sections.append({'base':0x100000+j*0x10000,'size':h[3],'raw':h[4],'reloc':h[5],'count':h[7]})
 while i<nsyms:
  name,value,sec,typ,storage,aux=struct.unpack_from('<8sLhHBB',b,symptr+18*i)
  name=(strings[struct.unpack('<L',name[4:])[0]:] if name[:4]==b'\0'*4 else name).split(b'\0')[0].decode()
  if sec>0:indices[i]=sections[sec-1]['base']+value;symbols[name]=indices[i]
  elif name=='_memcpy':indices[i]=0x300000
  elif name=='_memset':indices[i]=0x300100
  i+=aux+1
 u=Uc(UC_ARCH_X86,UC_MODE_32)
 u.mem_map(0x300000,4096)
 # Harness cdecl memcpy, preserves ESI/EDI. This is not the nxdk libc implementation.
 u.mem_write(0x300000,bytes.fromhex('57568b7c240c8b7424108b4c241489f8fcf3a45e5fc3'))
 u.mem_write(0x300100,bytes.fromhex('578b7c24088b44240c8b4c241089fafcf3aa89d05fc3'))
 for s in sections:
  u.mem_map(s['base'],0x10000)
  if s['size']:u.mem_write(s['base'],b[s['raw']:s['raw']+s['size']])
 for s in sections:
  for j in range(s['count']):
   off,idx,typ=struct.unpack_from('<LLH',b,s['reloc']+j*10);assert idx in indices
   addr=s['base']+off;old=struct.unpack('<L',u.mem_read(addr,4))[0]
   assert typ in (6,20)
   value=old+indices[idx]-(addr+4 if typ==20 else 0)
   u.mem_write(addr,struct.pack('<L',value&0xffffffff))
 u.mem_map(0x200000,0x40000)

 for base in (0xfd601000,0xfd0c0000):u.mem_map(base,4096)
 regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_EBX,x.UC_X86_REG_ESP,x.UC_X86_REG_EBP,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI]
 state={}
 def code(uc,pc,n,_):
  state['steps']+=1
  raw=bytes(uc.mem_read(pc,n))
  if raw[:2]==b'\x0f\x20':
   mod=raw[2];assert mod>>6==3
   cr=(mod>>3)&7;assert cr in (0,3,4)
   uc.reg_write(regs[mod&7],state['cpu'][cr]);uc.reg_write(x.UC_X86_REG_EIP,pc+n)
  if uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200==0:state['critical_steps']+=1
 def read_hook(uc,access,addr,size,value,_):
  if addr<0xfd000000:return
  assert size==1 and not(uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200)
  if addr==0xfd6013d4:value=state['ci']
  elif addr==0xfd0c03c4:value=state['si']
  elif addr==0xfd6013d5:
   i=state['ci'];assert i in (0x1b,0x11,0x1f)
   value=state['cr'].get(i,0)
   if i==0x1b and state['data_writes'] and state['behavior']=='reselect_only' and state['post_selects']>0:value=5
   if i==0x11 and state['gate']==4 and state['fault']=='final_cr11':value=0x0a
  elif addr==0xfd0c03c5:
   assert state['si']==1;value=state['seq']
   if state['gate']==5 and state['fault']=='blank':value=1
   if state['gate']==4 and state['fault']=='final_seq':value=0x21
  else:raise AssertionError(('unknown read',hex(addr)))
  if state['fault']=='restore_selector' and state['gate']==4 and addr==0xfd6013d4 and state['ci']==0x44:value=0x22
  uc.mem_write(addr,bytes([value]));state['reads'].append((addr,value))
 def write_hook(uc,access,addr,size,value,_):
  if addr<0xfd000000:
   assert 0x200000<=addr and addr+size<=0x209000,('unexpected RAM write',hex(addr),size)
   return
  assert size==1 and not(uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200)
  state['writes'].append((addr,value))
  if addr==0xfd6013d4:
   assert value in (0x1b,0x11,0x1f,0x44);state['ci']=value
   if value==0x1b and state['data_writes']:state['post_selects']+=1
  elif addr==0xfd0c03c4:assert value in (1,4);state['si']=value
  elif addr==0xfd0c03c5:
   assert state['si']==1 and value in (1,0x21);state['seq']=value;state['seq_writes'].append(value)
  elif addr==0xfd6013d5:
   if state['ci']==0x1f:
    assert value==0x57 and not state['unlocked'];state['unlocked']=True
    if state['fault']=='prewrite':state['cr'][0x1b]=5
    if state['fault']=='unlock_cr11':state['cr'][0x11]=0x0a
   else:
    assert state['ci']==0x1b and value==0x85 and state['data_writes']==0
    state['data_writes']+=1
    if state['behavior']=='clear7':state['cr'][0x1b]=5
    elif state['behavior']=='arbitrary':state['cr'][0x1b]=state['readback']
    elif state['behavior'] in ('faithful','ignored','reselect_only'):state['cr'][0x1b]=0x85
    else:raise AssertionError('unknown model')
  else:raise AssertionError(('unknown write',hex(addr)))
 def output(uc,port,size,value,_):
  assert port==0x80d3 and size==1 and not(uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200)
  assert value==([5,4][len(state['outs'])]);state['outs'].append(value);state['gate']=value
 u.hook_add(UC_HOOK_CODE,code)
 u.hook_add(UC_HOOK_MEM_READ,read_hook)
 u.hook_add(UC_HOOK_MEM_WRITE,write_hook)
 u.hook_add(UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
 def run(label,want,writes=1,behavior='faithful',fault='',baseline=0x85,seq=1,cr11=9,cpu0=0x8001003b,cpu4=0x610,flags=0x202,readback=0):
  state.clear();state.update(steps=0,critical_steps=0,cpu={0:cpu0,3:0xf000,4:cpu4},ci=0x44,si=4,cr={0x1b:baseline,0x11:cr11,0x1f:3},seq=seq,gate=0,reads=[],writes=[],outs=[],seq_writes=[],unlocked=False,data_writes=0,post_selects=0,behavior=behavior,fault=fault,readback=readback)
  u.mem_write(0x200000,b'\xa5'*0x9000)
  u.mem_write(0x208000,struct.pack('<LL',0x20ff00,0x201000))
  u.reg_write(x.UC_X86_REG_ESP,0x208000);u.reg_write(x.UC_X86_REG_EFLAGS,flags)
  u.emu_start(symbols['_probe721'],0x20ff00,count=10000)
  assert u.reg_read(x.UC_X86_REG_EIP)==0x20ff00
  v=struct.unpack('<24L',u.mem_read(0x201000,96))
  assert v[0]==want,(label,hex(v[0]),hex(want))
  assert state['data_writes']==writes and v[1]==writes,(label,state['data_writes'],v[1])
  assert v[12]==v[14] and (v[13]&0x200)==0,(label,'flags not restored')
  assert u.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
  assert state['outs'] in ([],[5,4]) and state['seq_writes'] in ([],[0x21,1])
  if state['outs']:assert state['seq']==1
  assert bytes(u.mem_read(0x200ff0,16))==b'\xa5'*16 and bytes(u.mem_read(0x201060,16))==b'\xa5'*16
  if writes:
   assert v[2]==v[5]==v[6]==0x85
   direct=5 if behavior=='clear7' else readback if behavior=='arbitrary' else 0x85
   selected=5 if behavior=='reselect_only' else direct
   assert v[7]==direct and v[8]==selected and v[9]==selected,(label,v[7:10])
  r['cases'].append({'name':label,'code':hex(v[0]),'data_writes':writes,'steps':state['steps'],'critical_steps':state['critical_steps'],'raw':list(v)})
 for flags in (0x202,0x246,0x2):
  for behavior in ('faithful','ignored','clear7','reselect_only'):
   run(behavior+'-'+hex(flags),0x721 if behavior in ('faithful','ignored') else 0x7218,behavior=behavior,flags=flags)
 for v in range(256):
  run('arbitrary-readback-'+str(v),0x721 if v==0x85 else 0x7218,behavior='arbitrary',readback=v)
  if v!=0x85:run('baseline-refuse-'+str(v),0x7212,writes=0,baseline=v)
  if v!=1:run('seq-refuse-'+str(v),0x7212,writes=0,seq=v)
 for bit in range(128,256):run('locked-cr11-'+str(bit),0x7212,writes=0,cr11=bit)
 for fault,want,writes in [('blank',0x7213,0),('prewrite',0x7214,0),('unlock_cr11',0x7215,0),('final_cr11',0x7215,1),('final_seq',0x7215,1),('restore_selector',0x7216,1)]:run(fault,want,writes,fault=fault)
 for cr0 in (0,1,0x80000000):run('cpu-refuse-'+str(cr0),0x7211,writes=0,cpu0=cr0)
 run('PAE-refuse',0x7211,writes=0,cpu4=0x630)
 r['passed']=True;r['case_count']=len(r['cases']);r['max_critical_instructions']=max(v['critical_steps'] for v in r['cases'])
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'cases':r.get('case_count'),'max_critical_instructions':r.get('max_critical_instructions')}))

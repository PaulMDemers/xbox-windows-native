"""Execute actual723 setup-prefix COFF with independent modeled MMIO, not hardware proof."""
import datetime,hashlib,json,struct,sys,os
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn723/build001')
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

 for base in (0xfd601000,0xfd0c0000,0xfd680000):u.mem_map(base,4096)
 setup=[(0x680884,0),(0x680888,0),(0x68088c,0x10001000),(0x680890,0x10000000),(0x680894,0x10000000),(0x680898,0x10000000),(0x68089c,0x10000000),(0x680880,0x21101100),(0x680630,2),(0x68084c,0x00801080),(0x6808c4,0x40801080)]
 cs=[(0x14,0),(0x17,0xe3),(0x19,0x10),(0x1b,5)]
 initial_mm={a:(3 if a==0x680630 else v) for a,v in setup}
 initial_cr={0x14:0,0x17:0xe3,0x19:0x51,0x1b:0x85,0x1f:3,0x11:9,0x22:0xfe}
 regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_EBX,x.UC_X86_REG_ESP,x.UC_X86_REG_EBP,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI]
 state={}
 def code(uc,pc,n,_):
  state['steps']+=1;raw=bytes(uc.mem_read(pc,n));assert raw[:2]!=b'\x0f\x22'
  if raw[:2]==b'\x0f\x20':
   mod=raw[2];assert mod>>6==3;cr=(mod>>3)&7;assert cr in (0,3,4)
   uc.reg_write(regs[mod&7],state['cpu'][cr]);uc.reg_write(x.UC_X86_REG_EIP,pc+n)
  if not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200:state['critical']+=1
 def read_hook(uc,access,addr,size,value,_):
  if addr<0xfd000000:return
  assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  if addr==0xfd6013d4:
   assert size==1;value=state['ci']
   if state['gate']==4 and state['fault']=='selector' and state['ci']==0x44:value=0
  elif addr==0xfd0c03c4:assert size==1;value=state['si']
  elif addr==0xfd0c03c5:
   assert size==1 and state['si']==1;value=state['seq']
   if state['gate']==5 and state['fault']=='blank':value=1
   if state['gate']==4 and state['fault']=='restore_seq':value=0x21
  elif addr==0xfd6013d5:
   assert size==1 and state['ci'] in initial_cr;value=state['cr'][state['ci']]
   if state['gate']==4 and state['fault']=='restore_cr22' and state['ci']==0x22:value=0xff
   if state['fault']=='unlock_cr11' and state['unlocked'] and state['ci']==0x11:value=0x89
  else:
   assert size==4 and addr-0xfd000000 in initial_mm;value=state['mm'][addr-0xfd000000]
  if state['pending']==addr:
   value^=1;state['pending']=None
  uc.mem_write(addr,value.to_bytes(size,'little'))
 def write_hook(uc,access,addr,size,value,_):
  if addr<0xfd000000:
   assert (0x201000<=addr and addr+size<=0x201108) or (0x207000<=addr and addr+size<=0x208008)
   return
  assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  if addr==0xfd6013d4:assert size==1 and value in list(initial_cr)+[0x44];state['ci']=value
  elif addr==0xfd0c03c4:assert size==1 and value in (1,4);state['si']=value
  elif addr==0xfd0c03c5:
   assert size==1 and state['si']==1 and value in (1,0x21);state['seq']=value;state['sw'].append(value)
  elif addr==0xfd6013d5:
   assert size==1;index=state['ci'];assert index in (0x1f,0x14,0x17,0x19,0x1b)
   state['cw'].append((index,value))
   if index==0x1f:assert value==0x57;state['unlocked']=True
   elif index==0x19 and value==0x51:
    assert state['ncr']>=3
    if state['fault']!='restore_cr19':state['cr'][index]=value
   else:
    assert state['nmm']==11 and (index,value)==cs[state['ncr']]
    state['ncr']+=1
    if state['fault']!='drop_cr'+str(index):state['cr'][index]=value
    if state['read_fault']==100+state['ncr']:state['pending']=addr
   if index==0x1f and state['fault']=='unlock_cr22':state['cr'][0x22]=0xff
  else:
   assert size==4 and addr-0xfd000000 in initial_mm;offset=addr-0xfd000000
   state['mw'].append((offset,value))
   if offset==0x680630 and value==3:
    assert state['nmm']>=9
    if state['fault']!='restore_630':state['mm'][offset]=value
   else:
    assert (offset,value)==setup[state['nmm']];state['nmm']+=1
    if state['fault']!='drop_mm'+str(state['nmm']):state['mm'][offset]=value
    if state['read_fault']==state['nmm']:state['pending']=addr
 def output(uc,port,size,value,_):
  assert port==0x80d3 and size==1 and not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  assert value==[5,4][len(state['outs'])];state['outs'].append(value);state['gate']=value
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read_hook);u.hook_add(UC_HOOK_MEM_WRITE,write_hook)
 u.hook_add(UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
 def run(label,want=0x723,nmm=11,ncr=4,first=0xffffffff,flags=0x202,read_fault=0,fault='',mm_change=None,cr_change=None,seq=1,cpu0=0x80010031,cpu4=0x610):
  state.clear();state.update(steps=0,critical=0,cpu={0:cpu0,3:0xf000,4:cpu4},ci=0x44,si=4,seq=seq,gate=0,mm=initial_mm.copy(),cr=initial_cr.copy(),nmm=0,ncr=0,mw=[],cw=[],sw=[],outs=[],unlocked=False,pending=None,read_fault=read_fault,fault=fault)
  if mm_change:state['mm'][mm_change[0]]=mm_change[1]
  if cr_change:state['cr'][cr_change[0]]=cr_change[1]
  u.mem_write(0x200000,b'\xa5'*0x9000);u.mem_write(0x208000,struct.pack('<LL',0x20ff00,0x201000))
  u.reg_write(x.UC_X86_REG_ESP,0x208000);u.reg_write(x.UC_X86_REG_EFLAGS,flags)
  u.emu_start(symbols['_probe723'],0x20ff00,count=15000)
  assert u.reg_read(x.UC_X86_REG_EIP)==0x20ff00
  v=list(struct.unpack('<66L',u.mem_read(0x201000,264)))
  assert v[:4]==[want,nmm,ncr,first],(label,v[:4],[want,nmm,ncr,first])
  assert v[4]==v[6] and not v[5]&0x200 and v[4]&0x200==flags&0x200
  assert state['nmm']==nmm and state['ncr']==ncr
  assert state['mw']==setup[:nmm]+([(0x680630,3)] if nmm>=9 else [])
  assert state['cw']==([(0x1f,0x57)] if state['unlocked'] else [])+cs[:ncr]+([(0x19,0x51)] if ncr>=3 else [])
  assert state['sw'] in ([],[0x21,1]) and state['outs'] in ([],[5,4])
  assert state['ci']==0x44 and state['si']==4
  assert bytes(u.mem_read(0x200ff0,16))==b'\xa5'*16 and bytes(u.mem_read(0x201108,16))==b'\xa5'*16
  if want==0x723:
   assert v[19:21]==[1,1] and v[32:43]==[v for _,v in setup] and v[58:62]==[v for _,v in cs]
   assert v[43:54]==list(initial_mm.values()) and v[62:66]==[0,0xe3,0x51,5]
   assert v[16]==v[17]==0xfe and state['cr'][0x1b]==5
  r['cases'].append({'name':label,'code':hex(v[0]),'attempted_mmio':v[1],'attempted_crtc':v[2],'first_mismatch':v[3],'cleanup_ok':v[20],'critical_instructions':state['critical'],'steps':state['steps']})
 for f in (0x202,0x246,0x2):run('prefix-success-'+hex(f),flags=f)
 for i in range(1,12):run('read-mismatch-mm-'+str(i),0x7238,i,0,i,read_fault=i)
 for i in range(1,5):run('read-mismatch-cr-'+str(i),0x7238,11,i,100+i,read_fault=100+i)
 for a,v in initial_mm.items():run('pre-mm-'+hex(a),0x7232,0,0,mm_change=(a,v^1))
 for a in (0x14,0x17,0x19,0x1b,0x22):run('pre-cr-'+hex(a),0x7232,0,0,cr_change=(a,initial_cr[a]^1))
 for value in range(256):
  if value!=1:run('seq-refusal-'+str(value),0x7232,0,0,seq=value)
 run('locked-cr11',0x7232,0,0,cr_change=(0x11,0x89))
 for fault,want,mm,cr in [('blank',0x7233,0,0),('unlock_cr11',0x7235,0,0),('unlock_cr22',0x7235,0,0),('restore_630',0x7235,11,4),('restore_cr19',0x7235,11,4),('restore_cr22',0x7235,11,4),('restore_seq',0x7235,11,4),('selector',0x7236,11,4)]:run(fault,want,mm,cr,fault=fault)
 run('drop630',0x7238,9,0,9,fault='drop_mm9')
 run('dropCR19',0x7238,11,3,103,fault='drop_cr25')
 run('dropCR1b',0x7235,11,4,104,fault='drop_cr27')
 for value in (0,1,0x80000000):run('badCPU'+str(value),0x7231,0,0,cpu0=value)
 run('PAE',0x7231,0,0,cpu4=0x630)
 r.update(passed=True,case_count=len(r['cases']),max_critical_instructions=max(c['critical_instructions'] for c in r['cases']))
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ('passed','case_count','max_critical_instructions') if k in r}))


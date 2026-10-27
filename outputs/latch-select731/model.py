"""Actual731 COFF with independent GR04/CR22 hypotheses and fault injection.
Only access/restore/reporting is validated; no NV2A latch semantics are inferred.
"""
import datetime,hashlib,json,struct,sys,os,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn731/build001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'model001.json';assert not out.exists()
b=(P/'probe.obj').read_bytes()
R={'passed':False,'scope':__doc__,'object_sha256':sha(P/'probe.obj'),'harness_sha256':sha(Path(__file__)),'cases':[]}
GPU=0xfd000000;deadline=time.monotonic()+90

def run(name,want=0x731,flags=0x246,cpu0=0x80010031,cpu3=0xf000,cpu4=0x610,initial=0,latches=(0xfe,)*4,fault=''):
 assert time.monotonic()<deadline
 machine,nsec,_,symptr,nsyms,optsz,_=struct.unpack_from('<HHLLLHH',b);assert machine==0x14c and not optsz
 strings=b[symptr+18*nsyms:];sections=[];symbols={};indices={};i=0
 for j in range(nsec):
  h=struct.unpack_from('<8sLLLLLLHHL',b,20+40*j)
  sections.append({'base':0x100000+j*0x10000,'size':h[3],'raw':h[4],'reloc':h[5],'count':h[7]})
 while i<nsyms:
  symbol_name,value,sec,typ,storage,aux=struct.unpack_from('<8sLhHBB',b,symptr+18*i)
  symbol_name=(strings[struct.unpack('<L',symbol_name[4:])[0]:] if symbol_name[:4]==b'\0'*4 else symbol_name).split(b'\0')[0].decode()
  if sec>0:indices[i]=sections[sec-1]['base']+value;symbols[symbol_name]=indices[i]
  elif symbol_name=='_memcpy':indices[i]=0x300000
  elif symbol_name=='_memset':indices[i]=0x300100
  i+=aux+1
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32)
 c.mem_map(0x300000,4096)
 # Harness cdecl memcpy, preserves ESI/EDI. This is not the nxdk libc implementation.
 c.mem_write(0x300000,bytes.fromhex('57568b7c240c8b7424108b4c241489f8fcf3a45e5fc3'))
 c.mem_write(0x300100,bytes.fromhex('578b7c24088b44240c8b4c241089fafcf3aa89d05fc3'))
 for s in sections:
  c.mem_map(s['base'],0x10000)
  if s['size']:c.mem_write(s['base'],b[s['raw']:s['raw']+s['size']])
 for s in sections:
  for j in range(s['count']):
   off,idx,typ=struct.unpack_from('<LLH',b,s['reloc']+j*10);assert idx in indices
   addr=s['base']+off;old=struct.unpack('<L',c.mem_read(addr,4))[0]
   assert typ in (6,20)
   value=old+indices[idx]-(addr+4 if typ==20 else 0)
   c.mem_write(addr,struct.pack('<L',value&0xffffffff))
 c.mem_map(0x200000,0x40000)

 c.mem_write(0x200000,b'G'*0x40000);c.mem_map(GPU,0x1000000)
 c.mem_write(0x208000,struct.pack('<II',0x20ff00,0x201000))
 c.reg_write(x.UC_X86_REG_ESP,0x208000);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 sels={0x6013d4:0x67,0xc03ce:0x91};original=sels.copy();state={'gr':initial,'restoring':False,'read22':0}
 writes=[];io=[];steps=[0,0]
 word=lambda n:struct.unpack('<I',c.mem_read(0x201000+n*4,4))[0]
 def access(uc,kind,addr,width,value,_):
  off=addr-GPU;assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  io.append([kind,off,width,value if kind==u.UC_MEM_WRITE else None])
  if off in sels:
   assert width==1
   if kind==u.UC_MEM_WRITE:sels[off]=value;return
   val=sels[off]
   if fault=='selector' and state['restoring'] and val==original[off]:val^=1
  elif off==0xc03cf:
   assert width==1 and sels[0xc03ce]==4
   if kind==u.UC_MEM_WRITE:
    assert value in range(4)
    restore=word(22)==4 or word(0)==0x7313
    state['restoring']=restore;writes.append(value)
    if not (fault=='drop-plane1' and len(writes)==2 or fault=='restore-gr' and restore):state['gr']=value
    return
   val=state['gr']
  elif off==0x6013d5:
   assert kind==u.UC_MEM_READ and width==1
   index=sels[0x6013d4];assert index in [0x22,0x33,0x1b]
   if index==0x22:
    val=latches[state['gr']&3];n=state['read22'];state['read22']+=1
    if fault=='direct-difference' and 1<=n<=12 and (n-1)%3==1:val^=1
    if fault=='changed-latch-after' and state['restoring']:val^=1
   else:
    val=0x11 if index==0x33 else 0x85
    if fault=='changed-cr33' and index==0x33 and state['restoring']:val^=1
  else:
   assert off==0x680630 and width==4 and kind==u.UC_MEM_READ
   val=2 if fault=='changed630' and state['restoring'] else 3
  uc.mem_write(addr,val.to_bytes(width,'little'))
 regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_EBX,x.UC_X86_REG_ESP,x.UC_X86_REG_EBP,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI]
 def code(uc,pc,n,_):
  steps[0]+=1;raw=bytes(uc.mem_read(pc,n));assert raw[:2]!=b'\x0f\x22'
  if raw[:2]==b'\x0f\x20':
   mod=raw[2];assert mod>>6==3;reg=(mod>>3)&7;assert reg in (0,3,4)
   uc.reg_write(regs[mod&7],{0:cpu0,3:cpu3,4:cpu4}[reg]);uc.reg_write(x.UC_X86_REG_EIP,pc+n)
  if not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200:steps[1]+=1
 def ramwrite(uc,kind,addr,size,val,_):
  if GPU<=addr<GPU+0x1000000:return
  assert 0x201000<=addr and addr+size<=0x2010ac or 0x207000<=addr and addr+size<=0x208008,(hex(addr),size)
 def port(*args):raise AssertionError('Port IO forbidden')
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,GPU,GPU+0xffffff)
 c.hook_add(u.UC_HOOK_MEM_WRITE,ramwrite);c.hook_add(u.UC_HOOK_CODE,code)
 c.hook_add(u.UC_HOOK_INSN,port,None,1,0,x.UC_X86_INS_OUT)
 c.hook_add(u.UC_HOOK_INSN,port,None,1,0,x.UC_X86_INS_IN)
 c.emu_start(symbols['_probe731'],0x20ff00,timeout=2000000,count=15000)
 assert c.reg_read(x.UC_X86_REG_EIP)==0x20ff00 and c.reg_read(x.UC_X86_REG_ESP)==0x208004
 v=list(struct.unpack('<43I',c.mem_read(0x201000,172)))
 assert v[0]==want,(name,hex(v[0]),hex(want),v)
 assert v[1]==v[3] and not v[2]&0x200 and v[1]&0x200==flags&0x200
 assert v[4:7]==[cpu0,cpu3,cpu4] and c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
 assert bytes(c.mem_read(0x200000,4096))==b'G'*4096
 assert bytes(c.mem_read(0x2010ac,0x5f54))==b'G'*0x5f54
 assert bytes(c.mem_read(0x208008,0xff8))==b'G'*0xff8
 assert sels==original
 if want==0x7311:assert not io and not writes and v[23:]==[0xffffffff]*20
 elif want==0x7312:assert not writes and v[9]==initial and v[19]==1 and v[23:]==[0xffffffff]*20
 else:
  assert writes==([0,1,initial] if fault=='drop-plane1' else [0,1,2,3,initial])
  assert v[21]==len(writes) and v[22]==(1 if fault=='drop-plane1' else 4)
  if fault!='drop-plane1':
   assert v[23:27]==list(range(4)) and v[27:31]==list(range(4))
   assert v[31:35]==list(latches) and v[39:43]==list(latches)
   assert v[35:39]==[a^(1 if fault=='direct-difference' else 0) for a in latches]
  else:
   assert v[23:27]==[0,1,0xffffffff,0xffffffff] and v[27:31]==[0,0,0xffffffff,0xffffffff]
   assert v[31:35]==[latches[0],0xffffffff,0xffffffff,0xffffffff]
  if want==0x731:assert v[19:21]==[1,1] and v[10]==initial
  if want==0x7313:assert v[19:21]==[1,1]
  if want==0x7315:assert v[20]==0
  if want==0x7316:assert v[19]==0
 R['cases'].append({'name':name,'code':v[0],'raw_result':v,'GR04_data_writes':writes,'CRTC_data_writes':0,'MMIO_data_writes_except_GR04':0,'instructions':steps[0],'critical_instructions':steps[1],'IO_sha256':hashlib.sha256(json.dumps(io).encode()).hexdigest()})
try:
 for initial in range(4):run('distinct-planes-initial'+str(initial),initial=initial,latches=(0x12,0x34,0x56,0x78))
 for value in [0,0x85,0xfe,0xff]:run('constant-readout-'+hex(value),latches=(value,)*4)
 for flags in [2,0x202,0x246]:run('flags-'+hex(flags),flags=flags)
 run('direct-read-difference-recorded',fault='direct-difference',latches=(1,2,3,4))
 for initial in [4,0x80,255]:run('high-GR04-refused-'+hex(initial),initial=initial,want=0x7312)
 for fault,want in [('drop-plane1',0x7313),('restore-gr',0x7315),('changed-latch-after',0x7315),('changed-cr33',0x7315),('changed630',0x7315),('selector',0x7316)]:run(fault,fault=fault,want=want)
 for value in [0,1,0x40000001,0x80000000]:run('cpu0-'+hex(value),cpu0=value,want=0x7311)
 run('PAE-refused',cpu4=0x630,want=0x7311)
 run('alternate-CR3',cpu3=0x23000)
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:R['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,indent=2)+'\n')
print('PASS actual731 COFF',len(R['cases']),'cases; no hardware semantics claim')

"""Actual775 COFF: read-only MMIO bounds/order, captures, refusals and sentinels.
Host access-contract tests; not proof of physical register meaning or atomicity.
"""
import datetime,hashlib,json,struct,sys,os
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn775/build001')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'model001.json';assert not out.exists()
b=(P/'probe.obj').read_bytes();GPU=0xfd000000
R={'passed':False,'physical_access':False,'object_sha256':sha(P/'probe.obj'),'harness_sha256':sha(Path(__file__)),'cases':[]}
OFFSETS=[0x680800,0x680804,0x680808,0x68080c,0x680810,0x680814,0x680818]
BASE=[719,749,719,724,729,0,719]
def run(name,cpu0=0x80010031,cpu3=0xf000,cpu4=0x610,flags=0x246,phase=-1,field=-1,value=0,base=None):
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
 reads=[];ram=[];regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_EBX,x.UC_X86_REG_ESP,x.UC_X86_REG_EBP,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI]
 expected=[(base or BASE).copy() for _ in range(3)]
 if phase>=0:expected[phase][field]=value
 order=list(range(7))+list(range(6,-1,-1))+list(range(7))
 def access(uc,kind,addr,width,val,_):
  assert kind==u.UC_MEM_READ and width==4 and len(reads)<21,'MMIO writes or unbounded reads forbidden'
  i=len(reads);j=order[i];assert addr==GPU+OFFSETS[j]
  sample=expected[i//7][j];uc.mem_write(addr,struct.pack('<I',sample));reads.append([addr-GPU,sample])
 def code(uc,pc,n,_):
  raw=bytes(uc.mem_read(pc,n));assert raw[:2] not in [b'\x0f\x22',b'\x0f\x30'] and raw[0] not in [0xfa,0xfb],'No control/interrupt-state writes'
  assert uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
  if raw[:2]==b'\x0f\x20':
   mod=raw[2];assert mod>>6==3;reg=(mod>>3)&7;assert reg in [0,3,4]
   uc.reg_write(regs[mod&7],{0:cpu0,3:cpu3,4:cpu4}[reg]);uc.reg_write(x.UC_X86_REG_EIP,pc+n)
 def write(uc,kind,addr,size,val,_):
  assert 0x201000<=addr and addr+size<=0x201078 or 0x207000<=addr and addr+size<=0x208008,(hex(addr),size)
  ram.append([addr,size])
 def forbidden(*args):raise AssertionError('Port I/O forbidden')
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,GPU,GPU+0xffffff)
 c.hook_add(u.UC_HOOK_MEM_WRITE,write);c.hook_add(u.UC_HOOK_CODE,code)
 c.hook_add(u.UC_HOOK_INSN,forbidden,None,1,0,x.UC_X86_INS_IN)
 c.hook_add(u.UC_HOOK_INSN,forbidden,None,1,0,x.UC_X86_INS_OUT)
 c.emu_start(symbols['_probe775'],0x20ff00,count=10000,timeout=1000000)
 assert c.reg_read(x.UC_X86_REG_EIP)==0x20ff00 and c.reg_read(x.UC_X86_REG_ESP)==0x208004
 v=list(struct.unpack('<30I',c.mem_read(0x201000,120)))
 assert v[4]&0x200==v[5]&0x200==flags&0x200 and v[6:9]==[cpu0,cpu3,cpu4]
 bad=(cpu0&0x80000001)!=0x80000001 or bool(cpu4&0x20)
 if bad:assert v[:4]==[0x7751,0,0,0] and v[9:]==[0]*21 and not reads
 else:
  assert v[9:]==sum(expected,[]) and len(reads)==v[1]==21
  unstable=sum(1<<i for i in range(7) if len({row[i] for row in expected})!=1)
  invalid=sum(1<<i for i in range(7) if any(row[i]&0xffff0000 for row in expected))
  assert v[2:4]==[unstable,invalid] and v[0]==(0x7753 if invalid else 0x7752 if unstable else 0x775)
 assert bytes(c.mem_read(0x200000,4096))==b'G'*4096
 assert bytes(c.mem_read(0x201078,0x5f88))==b'G'*0x5f88
 assert bytes(c.mem_read(0x208008,0xff8))==b'G'*0xff8
 R['cases'].append({'name':name,'raw_result':v,'reads':reads,'no_MMIO_port_or_CPU_state_writes':True,'result_and_stack_guards_exact':True})
try:
 run('baseline');run('interrupts-already-disabled',flags=0x46)
 run('zero-values',base=[0]*7);run('max16-values',base=[65535]*7)
 for n,c0,c4 in [('no-PG',0x10031,0x610),('no-PE',0x80010030,0x610),('PAE',0x80010031,0x630)]:run(n,cpu0=c0,cpu4=c4)
 for phase in range(3):
  for i in range(7):
   run('change-%d-%d'%(phase,i),phase=phase,field=i,value=BASE[i]^1)
   run('invalid-%d-%d'%(phase,i),phase=phase,field=i,value=0xffffffff)
 R['passed']=True
except BaseException as e:R['failure']=repr(e);raise
finally:R['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,indent=2)+'\n')
print('PASS775 actual COFF read-only cases',len(R['cases']))

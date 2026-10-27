"""Execute actual722 capture COFF with independent modeled MMIO, not hardware proof."""
import datetime,hashlib,json,struct,sys,os
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn722/build001')
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import *
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'model001.json';assert not out.exists()
b=(P/'capture.obj').read_bytes();r={'passed':False,'object_sha256':sha(P/'capture.obj'),'scope':__doc__,'cases':[]}
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

 for base in (0xfd601000,0xfd0c0000,0xfd600000,0xfd100000,0xfd680000):u.mem_map(base,4096)
 mmio=[0x600800,0x600804,0x100200,0x680508,0x68050c,0x680884,0x680888,0x68088c,0x680890,0x680894,0x680898,0x68089c,0x680880,0x680630,0x68084c,0x6808c4,0x680800,0x680804,0x680808,0x68080c,0x680810,0x680814,0x680818,0x680820,0x680824,0x680828,0x68082c,0x680830,0x680834,0x680838]
 crtc=[0,1,2,3,4,5,6,7,9,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x1a,0x1b,0x1f,0x21,0x22,0x25,0x28,0x2d,0x33,0x39,0x44,0x20]
 ports=[0xfd6013d4,0xfd0c03c4,0xfd0c03ce]
 regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_EBX,x.UC_X86_REG_ESP,x.UC_X86_REG_EBP,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI]
 state={}
 def code(uc,pc,n,_):
  state['steps']+=1;raw=bytes(uc.mem_read(pc,n))
  assert raw[:2]!=b'\x0f\x22','control register write'
  if raw[:2]==b'\x0f\x20':
   mod=raw[2];assert mod>>6==3;cr=(mod>>3)&7;assert cr in (0,3,4)
   uc.reg_write(regs[mod&7],state['cpu'][cr]);uc.reg_write(x.UC_X86_REG_EIP,pc+n)
  if not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200:state['critical']+=1
 def read_hook(uc,access,addr,size,value,_):
  if addr<0xfd000000:return
  assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  if addr in ports:
   assert size==1;idx=ports.index(addr);value=state['selectors'][idx]
   if state['fault']==idx and len(state['writes'])==48:value^=1
  elif addr-1 in ports:
   assert size==1;idx=ports.index(addr-1);index=state['selectors'][idx]
   assert index in (crtc if idx==0 else range(5 if idx==1 else 9))
   value=(state['seed']+index*17+idx*43)&255
  else:
   assert size==4 and addr-0xfd000000 in mmio
   value=((addr-0xfd000000)*0x112233+state['seed'])&0xffffffff
  uc.mem_write(addr,value.to_bytes(size,'little'));state['reads'].append((addr,size,value))
 def write_hook(uc,access,addr,size,value,_):
  if addr<0xfd000000:
   assert (0x201000<=addr and addr+size<=0x201160) or (0x207000<=addr and addr+size<=0x208008),('RAM outside result/stack',hex(addr),size)
   return
  assert size==1 and addr in ports and not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  state['selectors'][ports.index(addr)]=value;state['writes'].append((addr,value))
 def forbidden(*args):raise AssertionError('unexpected port I/O')
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read_hook);u.hook_add(UC_HOOK_MEM_WRITE,write_hook)
 u.hook_add(UC_HOOK_INSN,forbidden,None,1,0,x.UC_X86_INS_OUT)
 u.hook_add(UC_HOOK_INSN,forbidden,None,1,0,x.UC_X86_INS_IN)
 def run(seed,flags,fault=-1):
  selectors=[seed&255,(seed*3+19)&255,(seed*7+9)&255]
  state.clear();state.update(seed=seed,selectors=selectors.copy(),writes=[],reads=[],steps=0,critical=0,fault=fault,cpu={0:0x80010031,3:0xf000,4:0x610})
  u.mem_write(0x200000,b'\xa5'*0x9000);u.mem_write(0x208000,struct.pack('<LL',0x20ff00,0x201000))
  u.reg_write(x.UC_X86_REG_ESP,0x208000);u.reg_write(x.UC_X86_REG_EFLAGS,flags)
  u.emu_start(symbols['_capture722'],0x20ff00,count=10000)
  assert u.reg_read(x.UC_X86_REG_EIP)==0x20ff00
  v=list(struct.unpack('<88L',u.mem_read(0x201000,352)))
  assert v[0]==v[2] and not v[1]&0x200 and v[0]&0x200==flags&0x200
  assert v[3:6]==[0x80010031,0xf000,0x610] and v[6:9]==selectors
  after=selectors.copy()
  if fault>=0:after[fault]^=1
  assert v[9:12]==after and v[12]==int(fault<0)
  assert v[13:43]==[(offset*0x112233+seed)&0xffffffff for offset in mmio]
  assert v[43:74]==[(seed+index*17)&255 for index in crtc]
  assert v[74:79]==[(seed+index*17+43)&255 for index in range(5)]
  assert v[79:88]==[(seed+index*17+86)&255 for index in range(9)]
  expected=[(ports[0],i) for i in crtc]+[(ports[1],i) for i in range(5)]+[(ports[2],i) for i in range(9)]+list(zip(ports,selectors))
  assert state['writes']==expected and state['selectors']==selectors
  assert len(state['reads'])==81
  assert bytes(u.mem_read(0x200ff0,16))==b'\xa5'*16 and bytes(u.mem_read(0x201160,16))==b'\xa5'*16
  r['cases'].append({'seed':seed,'input_flags':flags,'fault_selector':fault,'steps':state['steps'],'critical_instructions':state['critical'],'selectors_restored':v[12]})
 for seed in range(256):
  for flags in (0x202,0x246,0x2):run(seed,flags)
 for fault in range(3):run(71,0x202,fault)
 r.update(passed=True,case_count=len(r['cases']),max_critical_instructions=max(c['critical_instructions'] for c in r['cases']))
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ('passed','case_count','max_critical_instructions') if k in r}))


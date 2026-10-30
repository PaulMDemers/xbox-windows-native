"""Execute compiled context823 admission with independently specified PCI/MMIO values.
Kernel service calls and indexed-register responses are harness stubs. This checks
the frontend predicate, selector restoration and refusal, not physical services.
"""
from pathlib import Path
import datetime,hashlib,json,os,struct,sys
K=Path(__file__).resolve().parent;P=Path('C:/xwn823/build003')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
out=K/'frontend-model002.json';assert not out.exists()
b=(P/'main.obj').read_bytes();sha=lambda v:hashlib.sha256(v).hexdigest()
r=dict(passed=False,object_sha256=sha(b),harness_sha256=sha(Path(__file__).read_bytes()),scope=__doc__,cases=[])
PCI={(1,0,0):0x02a010de,(1,0,4):0x02b00007,(1,0,16):0xfd000000,
 (0,33,0):0x01b410de,(0,33,4):0x00b00001,(0,33,20):0xc001,
 (0,1,0):0x01b210de,(0,1,4):0x00b0000f,(0,1,16):0,(0,1,132):0x8001}
CR={0:200,1:159,2:159,3:140,4:167,5:49,6:236,7:240,9:96,16:212,17:9,18:207,19:128,
 20:0,21:207,22:237,23:227,24:255,25:81,26:56,27:133,31:3,33:255,34:254,37:16,40:131,45:224,51:17,57:255,68:0}
MM={0x680508:0x3c20d,0x68050c:0x100a0400,0x680880:0x21101100,0x100200:0x3070003,0x600804:3}
GPU=0xfd000000
def run(name,kind=None,key=None,val=None,saved=0):
 pci=PCI.copy();cr=CR.copy();mm=MM.copy()
 if kind=='pci':pci[key]=val
 if kind=='cr':cr[key]=val
 if kind=='mm':mm[key]=val
 machine,nsec,_,sp,ns,ops,_=struct.unpack_from('<HHLLLHH',b);assert machine==0x14c and ops==0
 st=b[sp+18*ns:];secs=[];syms={};ids={};extern={};i=0
 for j in range(nsec):
  h=struct.unpack_from('<8sLLLLLLHHL',b,20+40*j)
  assert h[3]<0x20000
  secs.append(dict(base=0x1000000+j*0x20000,size=h[3],raw=h[4],rel=h[5],count=h[7]))
 while i<ns:
  nam,v,sec,typ,sc,aux=struct.unpack_from('<8sLhHBB',b,sp+18*i)
  nam=(st[struct.unpack('<L',nam[4:])[0]:] if nam[:4]==b'\0'*4 else nam).split(b'\0')[0].decode()
  if sec>0:ids[i]=secs[sec-1]['base']+v;syms[nam]=ids[i]
  elif sec==0:
   addr=0x3000000+16*len(extern);extern[nam]=addr;ids[i]=addr
  i+=aux+1
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x3000000,0x10000)
 for nam,addr in extern.items():c.mem_write(addr,struct.pack('<I',addr+8));c.mem_write(addr+8,b'\xc3')
 for s in secs:
  c.mem_map(s['base'],0x20000)
  if s['size'] and s['raw']:c.mem_write(s['base'],b[s['raw']:s['raw']+s['size']])
 for s in secs:
  for j in range(s['count']):
   off,idx,typ=struct.unpack_from('<LLH',b,s['rel']+10*j);assert idx in ids and typ in [6,20]
   addr=s['base']+off;old=struct.unpack('<I',c.mem_read(addr,4))[0]
   c.mem_write(addr,struct.pack('<I',(old+ids[idx]-(addr+4 if typ==20 else 0))&0xffffffff))
 c.mem_map(0x200000,0x20000);c.mem_write(0x200000,b'G'*0x20000);c.mem_map(GPU,0x1000000)
 c.mem_write(0x210000,struct.pack('<I',0x21ff00));c.reg_write(x.UC_X86_REG_ESP,0x210000)
 c.reg_write(x.UC_X86_REG_CR0,0x11);c.reg_write(x.UC_X86_REG_CR3,0xf000);c.reg_write(x.UC_X86_REG_CR4,0x610)
 sels={0x6013d4:0x67,0xc03c4:0x72};orig=sels.copy();calls=[];writes=[];checkpoints=[]
 def word(a):return struct.unpack('<I',c.mem_read(a,4))[0]
 def ret(result=0,cleanup=0):
  esp=c.reg_read(x.UC_X86_REG_ESP);pc=word(esp);c.reg_write(x.UC_X86_REG_EAX,result);c.reg_write(x.UC_X86_REG_ESP,esp+4+cleanup);c.reg_write(x.UC_X86_REG_EIP,pc)
 def string(a):
  v=bytearray()
  while len(v)<512:
   q=bytes(c.mem_read(a+len(v),1))
   if q==b'\0':return v.decode()
   v+=q
  raise AssertionError('unterminated string')
 def code(uc,pc,size,_):
  esp=uc.reg_read(x.UC_X86_REG_ESP)
  if pc==syms['_append']:ret();return
  if pc==syms['_checkpoint']:
   checkpoints.append((string(word(esp+4)),word(esp+8)));ret(saved);return
  if pc==extern['__imp__HalReadWritePCISpace@24']+8:
   a=[word(esp+4+4*i) for i in range(6)];assert a[4:]==[4,0]
   cfg=tuple(a[:3]);assert cfg in pci;calls.append(cfg);uc.mem_write(a[3],struct.pack('<I',pci[cfg]));ret(cleanup=24);return
  if pc==extern.get('_memset'):
   dest,v,n=[word(esp+4+4*i) for i in range(3)];assert 0x200000<=dest and dest+n<=0x210000 and n==256
   uc.mem_write(dest,bytes([v&255])*n);ret(dest);return
  assert not 0x3000000<=pc<0x3010000,hex(pc)
 def access(uc,typ,addr,size,value,_):
  off=addr-GPU
  if typ==u.UC_MEM_WRITE:
   assert off in sels and size==1;(writes.append([off,value]));sels[off]=value;return
  if off in sels:assert size==1;v=sels[off]
  elif off==0x6013d5:assert size==1;v=cr[sels[0x6013d4]]
  elif off==0xc03c5:assert size==1;v=[3,1,15,0,6][sels[0xc03c4]]
  else:assert size==4 and off in mm;v=mm[off]
  uc.mem_write(addr,v.to_bytes(size,'little'))
 c.hook_add(u.UC_HOOK_CODE,code);c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,begin=GPU,end=GPU+0xffffff)
 c.emu_start(syms['_context823'],0x21ff00,count=30000,timeout=1000000)
 assert c.reg_read(x.UC_X86_REG_EIP)==0x21ff00 and c.reg_read(x.UC_X86_REG_ESP)==0x210004
 actual=c.reg_read(x.UC_X86_REG_EAX);expected=int(kind is not None or bool(saved))
 assert actual==expected,(name,actual,expected)
 assert sels==orig and calls==list(PCI) and checkpoints==[('kernel_context_captured',0)]
 r['cases'].append(dict(name=name,refused=bool(actual),PCI_calls=len(calls),selector_writes=len(writes),selectors_restored=True,checkpoint_saved=saved))
try:
 run('exact-recorded-baseline-8001')
 for key in PCI:
  bit=2 if key==(1,0,4) else 1
  run('PCI-'+str(key),'pci',key,PCI[key]^bit)
 run('previous-bug-literal-8021','pci',(0,1,132),0x8021)
 for key,val in [(17,0x89),(33,0),(68,1),(9,0xe0),(57,0)]:run('CR-'+str(key),'cr',key,val)
 for key in MM:run('MMIO-'+hex(key),'mm',key,MM[key]^1)
 for saved in [1,3,5,6]:run('checkpoint-failure-'+str(saved),saved=saved)
 r.update(passed=True,case_count=len(r['cases']),hardware_PCI_literal=0x8001)
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with out.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print('PASS823 actual frontend admission',len(r['cases']),'cases')

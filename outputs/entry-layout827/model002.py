"""Fresh827 compiled read-only sampler test. Stubbed kernel PCI and MMIO;
checks exact capture, selector restoration, and no display writes. Not hardware proof."""
from pathlib import Path
import datetime,hashlib,json,os,struct,sys
K=Path(__file__).resolve().parent;P=Path('C:/xwn827/build002')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
out=K/'model002.json';assert not out.exists()
b=(P/'main.obj').read_bytes();sha=lambda v:hashlib.sha256(v).hexdigest()
r=dict(passed=False,object_sha256=sha(b),harness_sha256=sha(Path(__file__).read_bytes()),scope=__doc__,cases=[])
GPU=0xfd000000
OFF=[0x600800,0x680800,0x680804,0x68080c,0x680810,0x680818,0x680820,0x680824,0x68082c,0x680830,0x680838,0x680630,0x68084c,0x680880,0x6808c4,0x600804,0x680508,0x68050c,0x100200]
def run(name):
 pci=[0x02a010de,7,0xfd000008]
 if name=='bad-id':pci[0]^=1
 if name=='memory-disabled':pci[1]&=~2
 if name=='wrong-bar':pci[2]=0xfe000000
 mm={a:0x90000000+i for i,a in enumerate(OFF)}
 mm[0x680838]=1279 if name=='720p' else 639
 mm[0x680818]=719 if name=='720p' else 479
 cr={0x13:128 if name=='720p' else 64,0x19:0x51 if name=='720p' else 0x20,0x25:0x10,0x28:0x83}
 if name=='unknown-layout':mm={a:0xffffffff for a in OFF};cr={a:255 for a in cr}
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

 c.mem_map(GPU,0x1000000)
 c.mem_map(0x200000,0x20000);ptr=0x200000;sp=0x210000;end=0x21ff00
 c.mem_write(sp,struct.pack('<II',end,ptr));c.reg_write(x.UC_X86_REG_ESP,sp)
 calls=[];writes=[];reads=[];selector=[0x67]
 def word(a):return struct.unpack('<I',c.mem_read(a,4))[0]
 def code(uc,pc,size,_):
  if pc==extern['__imp__HalReadWritePCISpace@24']+8:
   esp=uc.reg_read(x.UC_X86_REG_ESP);a=[word(esp+4+4*i) for i in range(6)]
   assert a[0:2]==[1,0] and a[4:]==[4,0] and a[2] in [0,4,16]
   calls.append(a[2]);uc.mem_write(a[3],struct.pack('<I',pci[[0,4,16].index(a[2])]))
   uc.reg_write(x.UC_X86_REG_ESP,esp+28);uc.reg_write(x.UC_X86_REG_EIP,word(esp));return
  assert not 0x3000000<=pc<0x3010000,hex(pc)
 def access(uc,typ,a,size,v,_):
  off=a-GPU
  if typ==u.UC_MEM_WRITE:
   assert off==0x6013d4 and size==1;writes.append(v);selector[0]=v;return
  reads.append(off)
  if off==0x6013d4:
   v=0x66 if name=='selector-mismatch' and len(writes)==5 else selector[0];assert size==1
  elif off==0x6013d5:v=cr[selector[0]];assert size==1
  else:assert size==4 and off in mm;v=mm[off]
  uc.mem_write(a,v.to_bytes(size,'little'))
 c.hook_add(u.UC_HOOK_CODE,code);c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,begin=GPU,end=GPU+0xffffff)
 c.emu_start(syms['_sample827'],end,count=20000,timeout=1000000)
 assert c.reg_read(x.UC_X86_REG_EIP)==end and calls==[0,4,16]
 words=list(struct.unpack('<29I',c.mem_read(ptr,116)));assert words[:3]==pci
 bad=name in ['bad-id','memory-disabled','wrong-bar']
 if bad:assert not reads and not writes and words[3:]==[0]*26
 else:
  assert words[3:22]==[mm[a] for a in OFF] and words[22:26]==list(cr.values())
  assert writes==[0x13,0x19,0x25,0x28,0x67]
  assert words[26:]==[0x67,0x66 if name=='selector-mismatch' else 0x67,int(name!='selector-mismatch')]
 r['cases'].append(dict(name=name,PCI_calls=calls,display_data_writes=0,selector_writes=writes,accepted=bool(words[-1])))
try:
 for name in ['720p','640x480','unknown-layout','bad-id','memory-disabled','wrong-bar','selector-mismatch']:run(name)
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with out.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print('PASS827 compiled sampler',len(r['cases']),'cases')

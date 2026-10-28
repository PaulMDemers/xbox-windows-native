"""Execute actual756 layout COFF with independent modeled MMIO, not hardware proof."""
import datetime,hashlib,json,struct,sys,os
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn756/build001')
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import *
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'layout-model001.json';assert not out.exists()
b=(P/'layout.obj').read_bytes();r={'passed':False,'object_sha256':sha(P/'layout.obj'),'scope':__doc__,'cases':[]}
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

 count=0
 def call(name,args):
  global count
  u.mem_write(0x208000,struct.pack('<'+'L'*(len(args)+1),0x20ff00,*args));u.reg_write(x.UC_X86_REG_ESP,0x208000)
  u.emu_start(symbols[name],0x20ff00,count=1000);assert u.reg_read(x.UC_X86_REG_EIP)==0x20ff00
  count+=1;return u.reg_read(x.UC_X86_REG_EAX)
 def write(uc,access,address,size,value,_):assert 0x207000<=address and address+size<=0x208000
 u.hook_add(UC_HOOK_MEM_WRITE,write)
 good=[0x3000000,3686400,3686400,5120,1280,720,32,0x3000000]
 def admission(v):
  u.mem_write(0x201000,struct.pack('<8L',*v));return call('_framebuffer_admit701',[0x201000])
 assert admission(good)==1 and call('_framebuffer_admit701',[0])==0
 for i,values in {0:[0x3000001,0x4000000,0xffffffff],1:[0,3686399,0xffffffff],2:[0,3686399],3:[0,5119,5121],4:[0,1279],5:[0,719],6:[0,16],7:[0,0x3000001]}.items():
  for v in values:
   a=good.copy();a[i]=v;assert admission(a)==0
 for y in sorted(set([0,7,8,79,80,399,400,718,719,720,0xffffffff]+list(range(0,720,17)))):
  for x0 in sorted(set([0,7,8,639,640,1271,1272,1279,1280,0xffffffff]+list(range(0,1280,37)))):
   if x0>=1280 or y>=720:want=0
   elif x0<8 or x0>=1272 or y<8 or y>=719:want=0xffffff
   elif y<80:want=0x2080ff
   else:want=[[0xff0000,0x00ff00],[0x0000ff,0xffffff]][y>=400][x0>=640]
   assert call('_checkpoint_pixel701',[x0,y])==want
 r.update(passed=True,case_count=count,cases=['all admission fields/invalid pointer','pixel region and dimension boundaries','no framebuffer writes by pure helpers'])
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'cases':r.get('case_count')}))


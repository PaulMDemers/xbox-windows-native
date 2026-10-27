"""Execute actual722 layout and pixel COFF with independent modeled MMIO, not hardware proof."""
import datetime,hashlib,json,struct,sys,os
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn722/build001')
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
  u.mem_write(0x208000,struct.pack('<'+'L'*(len(args)+1),0x20ff00,*args))
  u.reg_write(x.UC_X86_REG_ESP,0x208000)
  u.emu_start(symbols[name],0x20ff00,count=1000)
  assert u.reg_read(x.UC_X86_REG_EIP)==0x20ff00
  count+=1;return u.reg_read(x.UC_X86_REG_EAX)
 def ram_write(uc,access,addr,size,value,_):assert 0x207000<=addr and addr+size<=0x208000
 u.hook_add(UC_HOOK_MEM_WRITE,ram_write)
 for w,h in [(1280,720),(720,480)]:
  size=w*h*4;a=0x3000000
  good=[a,size,a,w,h,w*4]
  assert call('_layout722',good)==1
  assert call('_layout722',[0,0x4000000,0,w,h,w*4])==1
  for i,values in {0:[a+1,0x4000000,0xffffffff],1:[0,size-1,0xffffffff],2:[a+4,0xffffffff],3:[0,640,0xffffffff],4:[0,481,0xffffffff],5:[0,w*4-4,w*4+4,0xffffffff]}.items():
   for value in values:
    args=good.copy();args[i]=value;assert call('_layout722',args)==0,(i,args)
  # Independent region classifier, including both sides of every edge.
  xs=sorted(set([0,7,8,w//4-1,w//4,w//2-1,w//2,3*w//4-1,3*w//4,w-9,w-8,w-1,w,0xffffffff]+list(range(0,w,29))))
  ys=sorted(set([0,7,8,63,64,h//2-1,h//2,h-81,h-80,h-17,h-16,h-9,h-8,h-1,h,0xffffffff]+list(range(0,h,31))))
  for y in ys:
   for x0 in xs:
    color=0x2080ff
    if x0>=w or y>=h:want=0
    elif not(8<=x0<w-8 and 8<=y<h-8):want=0xffffff
    elif y<=63:want=color
    elif h-80<=y<h-16 and w//4<=x0<3*w//4:want=0xffffff if (x0//8)%2!=(y//8)%2 else 0
    else:want=[[0xff0000,0x00ff00],[0x0000ff,0xffffff]][int(y>=h//2)][int(x0>=w//2)]
    assert call('_pixel722',[x0,y,w,h,color])==want,(w,h,x0,y)
 for w,h in [(640,480),(720,720),(0,0),(0xffffffff,0xffffffff)]:assert call('_pixel722',[0,0,w,h,0xabcdef])==0
 r.update(passed=True,case_count=count,cases=['allocation extent/alignment/scanout/stride refusals','pixel regions and out-of-bounds; both supported sizes','writes restricted to stack; no framebuffer mapped'])
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'cases':r.get('case_count')}))


"""Actual nxdk COFF arithmetic under Unicorn; no kernel/API/physical execution."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn690/build001')
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP
out=K/'object-review001.json';assert not out.exists()
b=(P/'layout.obj').read_bytes();r={'passed':False,'object_sha256':hashlib.sha256(b).hexdigest(),'scope':__doc__,'cases':[]}
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
  i+=aux+1
 u=Uc(UC_ARCH_X86,UC_MODE_32)
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
 u.mem_map(0x200000,0x10000)
 def call(name,args,want,label):
  u.reg_write(UC_X86_REG_ESP,0x208000)
  u.mem_write(0x208000,struct.pack('<'+'L'*(len(args)+1),0x20ff00,*args))
  u.emu_start(symbols[name],0x20ff00,count=500)
  assert u.reg_read(UC_X86_REG_EIP)==0x20ff00
  actual=u.reg_read(UC_X86_REG_EAX);assert actual==want&0xffffffff,(label,actual,want)
  r['cases'].append({'case':label,'actual':actual})
 f=[0x03000000,3686400,3686400,5120,1280,720,32,0x03000000]
 call('_framebuffer_admit690',[0],0,'null')
 for idx in range(-1,8):
  g=f.copy()
  if idx>=0:g[idx]+=1 if idx!=2 else -1
  u.mem_write(0x201000,struct.pack('<8L',*g))
  call('_framebuffer_admit690',[0x201000],int(idx<0),'layout '+str(idx))
 for a,n,want in [(0,0,-1),(0xfffff000,4096,-1),(0x03ffffff,1,0),(0x03ffffff,2,-1)]+[(a,n,w) for lo,hi in [(0xa0000,0xa1000),(0xb0000,0xb5000),(0x2600000,0x2800000)] for a,n,w in [(lo-1,1,0),(lo-1,2,1),(hi-1,1,1),(hi,1,0)]]:
  call('_handoff_overlap690',[a,n],want,'overlap '+hex(a)+' '+str(n))
 for x,y,want in [(0,0,0xffffff),(8,8,0x2080ff),(8,80,0xff0000),(640,80,0xff00),(8,400,0xff),(640,400,0xffffff),(1272,400,0xffffff),(1271,711,0xffffff),(100,712,0xffffff),(1280,0,0),(0,720,0),(0xffffffff,0,0)]:
  call('_checkpoint_pixel690',[x,y],want,'pixel '+str((x,y)))
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS nxdk object cases:',len(r['cases']))

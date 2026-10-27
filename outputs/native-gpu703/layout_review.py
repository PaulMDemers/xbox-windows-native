"""Actual nxdk COFF arithmetic under Unicorn; harness memcpy helper; no kernel/API/physical execution."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn703/build001')
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP
out=K/'layout-review001.json';assert not out.exists()
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
  elif name=='_memcpy':indices[i]=0x300000
  i+=aux+1
 u=Uc(UC_ARCH_X86,UC_MODE_32)
 u.mem_map(0x300000,4096)
 # Harness cdecl memcpy, preserves ESI/EDI. This is not the nxdk libc implementation.
 u.mem_write(0x300000,bytes.fromhex('57568b7c240c8b7424108b4c241489f8fcf3a45e5fc3'))
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
 steps=[0]
 def step(uc,pc,n,user):steps[0]+=1
 u.hook_add(UC_HOOK_CODE,step)
 def call(name,args,want,label):
  u.reg_write(UC_X86_REG_ESP,0x208000)
  u.mem_write(0x208000,struct.pack('<'+'L'*(len(args)+1),0x20ff00,*args))
  steps[0]=0
  u.emu_start(symbols[name],0x20ff00,count=2000)
  r['latest']={'case':label,'instructions':steps[0],'stopped_eip':u.reg_read(UC_X86_REG_EIP)}
  assert u.reg_read(UC_X86_REG_EIP)==0x20ff00
  actual=u.reg_read(UC_X86_REG_EAX);assert actual==want&0xffffffff,(label,actual,want)
  r['cases'].append({'case':label,'actual':actual,'instructions':steps[0]})
 f=[0x3c5c000,1228800,1228800,2560,640,480,32,0x3c5c000]
 call('_framebuffer_admit703',[0],0,'null framebuffer')
 for label,changes,want in [('valid',{},1),('wrong width',{4:1280},0),('wrong height',{5:720},0),('wrong pitch',{3:5120},0),('depth',{6:16},0),('short allocation',{2:1228799},0),('short coverage',{1:1228799},0),('unaligned',{0:0x3c5c001},0),('overflow',{0:0x3fff000},0),('wrong start',{7:0x3c5d000},0)]:
  q=f.copy()
  for i,v in changes.items():q[i]=v
  u.mem_write(0x201000,struct.pack('<8I',*q));call('_framebuffer_admit703',[0x201000],want,label)
 for xx,yy,want in [(0,0,0xffffff),(639,479,0xffffff),(320,472,0xffffff),(8,8,0x2080ff),(8,80,0xff0000),(319,279,0xff0000),(320,279,0xff00),(319,280,0xff),(320,280,0xffffff),(640,0,0),(0,480,0)]:
  call('_checkpoint_pixel703',[xx,yy],want,f'pixel {xx},{yy}')
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS nxdk480p framebuffer layout/pixel object cases:',len(r['cases']))

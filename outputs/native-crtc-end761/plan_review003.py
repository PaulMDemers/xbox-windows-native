"""Actual nxdk COFF arithmetic under Unicorn; harness memcpy helper; no kernel/API/physical execution."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn761/build002')
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP
out=K/'plan-review001.json';assert not out.exists()
b=(P/'plan.obj').read_bytes();r={'passed':False,'object_sha256':hashlib.sha256(b).hexdigest(),'scope':__doc__,'cases':[]}
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
  u.emu_start(symbols[name],0x20ff00,count=20000)
  r['latest']={'case':label,'instructions':steps[0],'stopped_eip':u.reg_read(UC_X86_REG_EIP)}
  assert u.reg_read(UC_X86_REG_EIP)==0x20ff00
  actual=u.reg_read(UC_X86_REG_EAX);assert actual==want&0xffffffff,(label,actual,want)
  r['cases'].append({'case':label,'actual':actual,'instructions':steps[0]})
 def good():return [0x1c00000,0x100000,0x100000,1,0x1ef0000,32768,32768,1,0,0x1ef0000,0x1ef0000,65536]+[0x2200000+i*8192 for i in range(8)]+[0x2200000+i*8192+4095 for i in range(8)]+[0x3000000,3686400,3686400]
 def oracle(v):
  e=0
  fits=lambda a,n,l,h:n>0 and a>=l and a+n<=h
  if not (v[1]==1048576 and v[2]>=v[1] and v[3]==1 and not v[0]%4096 and fits(v[0],v[2],0x200000,0x2000000)):e|=1
  if not (v[5]==32768 and v[6]>=v[5] and v[7]==1 and not v[4]%4096 and fits(v[4],v[6],0x1000000,0x2000000)):e|=2
  if not (v[8]<0x80000000 and v[9]==v[4] and all(not v[i]%4096 for i in (9,10,11)) and 32768<=v[11]<=131072 and 0<=v[10]<=v[9] and v[9]+32768<=v[10]+v[11]<=0x80000000):e|=4
  for i in range(8):
   if not (v[12+i]%4096==0 and fits(v[12+i],4096,0,0x4000000) and v[20+i]==v[12+i]+4095):e|=4
  if not (v[29]==3686400 and v[30]>=v[29] and v[28]%4096==0 and fits(v[28],v[30],0x2000000,0x4000000)):e|=16
  if not e:
   intervals=[(v[0],v[0]+v[2]),(v[4],v[4]+v[6]),(v[28],v[28]+v[30])]
   ov=lambda a,b:max(a[0],b[0])<min(a[1],b[1])
   if ov(intervals[0],intervals[1]) or ov(intervals[2],(0x2600000,0x2800000)):e|=8
   for i in range(8):
    a=(v[12+i],v[12+i]+4096)
    if ov(a,intervals[0]) or ov(a,intervals[2]) or (ov(a,intervals[1]) and v[12+i]!=v[4]+i*4096) or v[12+i] in v[12:12+i]:e|=8
  return e
 call('_admit705',[0],31,'null plan')
 def check(v,label):
  u.mem_write(0x201000,struct.pack('<31L',*v));call('_admit705',[0x201000],oracle(v),label)
 check(good(),'valid-scattered')
 for i in range(31):
  for value in (0,1,4095,4096,0x7fffffff,0x80000000,0xffffffff):
   v=good();v[i]=value;check(v,str(i)+'-'+hex(value))
 for i in range(8):
  for a in (0,0x1c00000,0x1ef0000,0x1ef7000,0x2200000,0x2202000,0x3000000,0x3fff000,0x4000000):
   v=good();v[12+i]=a;v[20+i]=a+4095;check(v,'alias-'+str(i)+'-'+hex(a))
 v=good()
 for i in range(8):v[12+i]=v[4]+4096*i;v[20+i]=v[12+i]+4095
 check(v,'identity')
 for size in (32768,36864,65536,98304,131072):
  for off in range(0,65536,4096):
   v=good();v[10]=v[9]-off;v[11]=size;check(v,'reservation-'+str(size)+'-'+str(off))
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS nxdk707 ownership cases:',len(r['cases']))

"""Execute newly linked702 code against explicit indexed-CRTC/MMIO models.
No display, clock, encoder, allocation service or physical-console qualification.
"""
from pathlib import Path
import sys,os,json,hashlib,struct,random,datetime,time
K=Path(__file__).resolve().parent;P=Path('C:/xwn702/build001')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
out=K/'cpu003.json';assert not out.exists()
b=json.loads((K/'build001.json').read_text());assert b['passed']
sha=lambda data:hashlib.sha256(data).hexdigest()
for n,h in b['files'].items():assert sha((P/n).read_bytes())==h
for n,h in b['sources'].items():assert sha((K/n).read_bytes())==h
blob=(P/'native.bin').read_bytes()
syms={a[2]:int(a[0],16) for line in (P/'symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
BASE=0xfd000000;RP=0x201000;OP=0x202000;SP=0x208000;END=0x10ff00
DEFAULT=[0x4000000,0x3c5c000,3686400,3686400,1,1,1280,720,5120,32,1]
# Literal review oracle from the720x480 source recipe, not read from the binary.
TIMING={0x680800:479,0x680804:524,0x680808:479,0x68080c:489,0x680810:492,
 0x680814:0,0x680818:479,0x680820:719,0x680824:779,0x680828:719,
 0x68082c:738,0x680830:770,0x680834:0,0x680838:719}
MASKS={0x00:(255,0x5c),0x01:(255,0x59),0x02:(255,0x59),0x03:(31,0),
 0x04:(255,0x5d),0x05:(0x9f,0x9e),0x06:(255,0x0c),0x07:(255,0x3e),
 0x09:(0x60,0x40),0x10:(255,0xe9),0x12:(255,0xdf),0x13:(255,0x68),
 0x15:(255,0xdf),0x16:(0x7f,0x0c),0x17:(0x80,0x80),0x18:(255,255),
 0x19:(0xe0,0x20),0x1a:(255,4),0x25:(255,0x10),0x28:(255,0x83),
 0x2d:(31,0),0x39:(255,255)}
CONTEXT={0x680508:0x3c20d,0x68050c:0x100a0400,0x680880:0x21101100,
 0x100200:0x3070003,0x600804:3}
PROTECTED=[0x100,0x140,0x600100,0x600140,0x608000,0x8000,
 0x680500,0x680504,0x680514,0x680630,0x68084c,0x6808c4]
r={'passed':False,'scope':__doc__,'physical_access':False,'image_sha256':sha(blob),
   'sources':b['sources'],'harness_sha256':sha(Path(__file__).read_bytes()),'cases':[]}
def machine():
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000)
 c.mem_write(0x100000,blob);c.mem_map(0x200000,0x10000);return c
def run(label,seed=0,request=None,expect=1,early=False,pre=None,fault=None,drop=None,
        locked=False,flags=2,null=None):
 c=machine();c.mem_map(BASE,0x800000)
 req=list(DEFAULT if request is None else request);c.mem_write(RP,pack(*req))
 c.mem_write(OP-16,b'G'*16);c.mem_write(OP,b'\xaa'*32);c.mem_write(OP+32,b'Z'*16)
 c.mem_write(SP,pack(END,0 if null=='request' else RP,0 if null=='gpu' else BASE,0 if null=='result' else OP))
 c.reg_write(x.UC_X86_REG_ESP,SP);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 rng=random.Random(seed);regs=bytearray(rng.randrange(256) for _ in range(256))
 regs[0x13]=0x80;regs[0x19]=(regs[0x19]&31)|0x40;regs[0x25]&=0xdf
 regs[0x28]=0x83;regs[0x39]=255
 mm={off:0xa5a50000+seed for off in PROTECTED};mm.update(CONTEXT)
 mm.update({off:0xdead0000+off for off in TIMING})
 mm.update({0x600800:req[1],0x680838:1279,0x680818:719})
 if pre:
  kind,key,value=pre
  (regs if kind=='cr' else mm)[key]=value
 original=bytes(regs);saved=rng.randrange(256);sel=[saved];writes=[];reads=[]
 def phase():return struct.unpack('<I',c.mem_read(OP,4))[0]
 def access(c,kind,addr,size,value,_):
  off=addr-BASE
  if kind==u.UC_MEM_WRITE:
   writes.append((off,size,value))
   if off==0x6013d4:assert size==1;sel[0]=value
   elif off==0x6013d5:
    assert size==1 and sel[0] in MASKS
    if not (locked and sel[0]<8) and drop!=('cr',sel[0]):regs[sel[0]]=value
   else:
    assert size==4 and off in (set(TIMING)|{0x600800})
    if drop!=('mm',off):mm[off]=value
  else:
   reads.append((off,size))
   if off==0x6013d4:assert size==1;c.mem_write(addr,bytes([sel[0]]));return
   if off==0x6013d5:assert size==1;v=regs[sel[0]];key=('cr',sel[0])
   else:assert size==4 and off in mm;v=mm[off];key=('mm',off)
   if fault and key==fault[:2] and phase()==3:v^=fault[2]
   c.mem_write(addr,bytes([v]) if size==1 else pack(v))
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,BASE,BASE+0x7fffff)
 c.emu_start(syms['geometry702'],END,timeout=1000000,count=30000)
 assert c.reg_read(x.UC_X86_REG_EIP)==END,label
 result=c.reg_read(x.UC_X86_REG_EAX);assert result==expect,(label,result,expect)
 assert c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200,label
 assert c.mem_read(RP,44)==pack(*req) and c.mem_read(0x100000,len(blob))==blob
 assert c.mem_read(OP-16,16)==b'G'*16 and c.mem_read(OP+32,16)==b'Z'*16
 assert sel[0]==saved,label
 assert all(mm[off]==CONTEXT[off] for off in CONTEXT if not pre or pre[:2]!=('mm',off))
 assert all(mm[off]==0xa5a50000+seed for off in PROTECTED)
 if early:assert not writes and not reads,label
 if expect==5:assert not any(off!=0x6013d4 for off,_,_ in writes),label
 if expect==1:
  assert all(mm[off]==n for off,n in TIMING.items())
  assert mm[0x600800]==req[1]
  assert (regs[0x13]|((regs[0x19]&0xe0)<<3)|((regs[0x25]&0x20)<<6))*8==2880
  for i in range(256):
   mask,v=MASKS.get(i,(0,0));assert regs[i]&mask==v and regs[i]&(~mask&255)==original[i]&(~mask&255),(label,i)
  assert struct.unpack('<8I',c.mem_read(OP,32))==(4,1,720,480,2880,0x83,req[1],255)
 r['cases'].append({'name':label,'return':result,'phase':phase(),'reads':len(reads),
  'writes':len(writes),'write_trace_sha256':sha(json.dumps(writes).encode()),'selector_restored':True})
try:
 for seed in range(256):run('mixed-crtc-'+str(seed),seed=seed)
 for off in TIMING:run('timing-readback-'+hex(off),fault=('mm',off,1),expect=6)
 for i,(mask,_) in MASKS.items():run('crtc-readback-'+hex(i),fault=('cr',i,mask&-mask),expect=6)
 for off in CONTEXT:run('context-drift-'+hex(off),fault=('mm',off,1),expect=6)
 run('start-readback',fault=('mm',0x600800,4096),expect=6)
 for off in CONTEXT:run('baseline-'+hex(off),pre=('mm',off,CONTEXT[off]^1),expect=5)
 for off,val in [(0x600800,0x3c5d000),(0x680838,639),(0x680818,479)]:run('baseline-'+hex(off),pre=('mm',off,val),expect=5)
 for i,val in [(0x13,0),(0x19,0),(0x25,0x20),(0x28,0x81),(0x39,0)]:run('baseline-cr-'+hex(i),pre=('cr',i,val),expect=5)
 for i in [0,1,2,3,4,5,6,7,0x13,0x19,0x25,0x28]:run('dropped-cr-'+str(i),drop=('cr',i),expect=1 if i==0x28 else 6)
 for off in TIMING:run('dropped-mm-'+hex(off),drop=('mm',off),expect=6)
 run('unchanged-start-write-dropped',drop=('mm',0x600800))
 run('protected-low-crtc',locked=True,expect=6)
 for i in range(11):
  req=list(DEFAULT);req[i]=0;run('invalid-field-'+str(i),request=req,expect=3,early=True)
 for n in ('request','gpu','result'):run('null-'+n,null=n,expect=2,early=True)
 run('interrupts-enabled',flags=0x202,expect=4,early=True)
 # Execute the actual bounds function for every page in and just outside64MiB.
 c=machine();boundary_count=0;deadline=time.monotonic()+120
 for base in range(0,0x4001000,4096):
  for allocation in (3686400,0xffffffff):
   req=list(DEFAULT);req[1]=base;req[2]=allocation
   c.mem_write(RP,pack(*req));c.mem_write(SP,pack(END,RP));c.reg_write(x.UC_X86_REG_ESP,SP)
   assert time.monotonic()<deadline,'boundary suite wall-clock limit'
   c.emu_start(syms['bounds702'],END,count=1000)
   # Unbounded Python arithmetic independently checks overflow and overlap.
   yes=base>=0x2000000 and base+allocation<=0x4000000 and not (base<0x2800000 and base+allocation>0x2600000)
   assert c.reg_read(x.UC_X86_REG_EIP)==END and c.reg_read(x.UC_X86_REG_EAX)==int(yes),(base,allocation)
   boundary_count+=1
 r['bounds_cases']=boundary_count;r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 out.write_text(json.dumps(r,indent=2)+'\n')
print(f"PASS {len(r['cases'])} linked geometry cases and {r['bounds_cases']} boundary cases")

"""Actual linked703 PCI/MMIO/CRTC reads and exact pixels, using modeled registers.
No physical GPU/register behavior or full CPU transition is represented here.
"""
import datetime,hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn703/build001')
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import *
from unicorn.x86_const import *
from oracle import expected_framebuffer
out=K/'io-review001.json';assert not out.exists()
x=json.loads((K/'extract001.json').read_text());blob=(P/'stub.bin').read_bytes();o=x['offsets']
assert x['passed'] and hashlib.sha256(blob).hexdigest()==x['template_sha256']
cases=[]
def case(name,**kw):
 d=dict(name=name,pci_id=0x02a010de,command=7,bar=0xfd000008,base=0x1eff000,selector=0x17,seed=0x12345678);d.update(kw);cases.append(d)
case('normal');case('nonprefetch',bar=0xfd000000);case('relocated',base=0x1edc000)
for seed in [0,0xffffffff,0x55555555,0xaaaaaaaa]:case('registers_'+str(seed),seed=seed)
case('wrong_gpu',pci_id=0x01b410de);case('absent',pci_id=0xffffffff,command=0xffffffff,bar=0xffffffff)
case('memory_disabled',command=5)
for bar in [0xfc000008,0xfd000009,0xfd00000c,0]:case('bar_'+str(bar),bar=bar)
for selector in [0,255,0x39,0x13]:case('index_'+str(selector),selector=selector)
r={'passed':False,'scope':__doc__,'template_sha256':x['template_sha256'],'cases':[]}
try:
 for c in cases:
  base=c['base'];fb=0x3000000;u=Uc(UC_ARCH_X86,UC_MODE_32)
  u.mem_map(base-4096,12288);u.mem_write(base-4096,b'\x5a'*12288);u.mem_write(base,blob);u.mem_write(base+0x508,struct.pack('<I',fb));u.mem_write(base+0x540,struct.pack('<I',3))
  u.mem_map(fb-4096,1228800+8192);u.mem_write(fb-4096,b'\xa5'*4096);u.mem_write(fb+1228800,b'\xa5'*4096)
  initial=bytearray(b'\x20'*1228800)
  for y in range(8,80):initial[(y*640+8)*4:(y*640+632)*4]=struct.pack('<I',0xff00)*624
  u.mem_write(fb,bytes(initial));u.mem_map(0xfd000000,0x800000)
  mmoffs=[0x680508,0x68050c,0x680880,0x600800,0x100200]
  vals={off:(c['seed']^(i*0x01010101))&0xffffffff for i,off in enumerate(mmoffs)}
  crtc={i:((c['seed']>>(j*8))&255) for j,i in enumerate([0x13,0x19,0x28,0x39])}
  crtc[0x25]=(c['seed']>>8)&255
  selector=[c['selector']];pci=[0x80005010];events=[];gpu=[];done=[False];minsp=[base+4096]
  u.reg_write(UC_X86_REG_EBP,base);u.reg_write(UC_X86_REG_ESP,base+4096);u.reg_write(UC_X86_REG_EFLAGS,2)
  result=2 if c['pci_id']!=0x02a010de else 3 if not c['command']&2 else 4 if c['bar'] not in (0xfd000000,0xfd000008) else 1
  def inp(uc,port,size,_):
   assert size==4 and port in (0xcf8,0xcfc)
   v=pci[0] if port==0xcf8 else {0x80010000:c['pci_id'],0x80010004:c['command'],0x80010010:c['bar']}[pci[0]]
   events.append(['in',port,v]);return v
  def output(uc,port,size,value,_):assert port==0xcf8 and size==4;pci[0]=value;events.append(['out',port,value])
  def read(uc,kind,address,size,value,_):
   assert result==1,'no GPU reads after rejected PCI';off=address-0xfd000000
   if off in vals:assert size==4;v=vals[off];uc.mem_write(address,struct.pack('<I',v))
   elif off==0x6013d4:assert size==1;v=selector[0];uc.mem_write(address,bytes([v]))
   else:assert off==0x6013d5 and size==1;v=crtc[selector[0]];uc.mem_write(address,bytes([v]))
   gpu.append(['read',off,size,v])
  def write(uc,kind,address,size,value,_):
   if address==0xfd6013d4:
    assert size==1 and result==1;selector[0]=value;gpu.append(['write',0x6013d4,size,value]);return
   assert (fb<=address and address+size<=fb+1228800) or (base+0x5a0<=address and address+size<=base+0x5d0) or (base+0xe00<=address and address+size<=base+4096) or (address==base+0x540 and size==4),hex(address)
  def step(uc,pc,size,_):
   minsp[0]=min(minsp[0],uc.reg_read(UC_X86_REG_ESP))
   if pc==base+o['hold']:done[0]=True;uc.emu_stop()
  u.hook_add(UC_HOOK_INSN,inp,None,1,0,UC_X86_INS_IN);u.hook_add(UC_HOOK_INSN,output,None,1,0,UC_X86_INS_OUT)
  u.hook_add(UC_HOOK_MEM_READ,read,None,0xfd000000,0xfd7fffff);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_CODE,step)
  u.emu_start(base+o['probe'],base+o['code_end'],count=2000000)
  assert done[0] and pci[0]==0x80005010 and selector[0]==c['selector'] and minsp[0]>=base+0xe00
  expected_events=[['in',0xcf8,0x80005010]]
  for reg,v in [(0x80010000,c['pci_id']),(0x80010004,c['command']),(0x80010010,c['bar'])]:expected_events.extend([['out',0xcf8,reg],['in',0xcfc,v]])
  expected_events.append(['out',0xcf8,0x80005010]);assert events==expected_events
  expected_gpu=[]
  if result==1:
   expected_gpu=[['read',off,4,vals[off]] for off in mmoffs[:3]]+[['read',0x6013d4,1,c['selector']]]
   for i in [0x25,0x13,0x19,0x28,0x39]:expected_gpu.extend([['write',0x6013d4,1,i],['read',0x6013d5,1,crtc[i]]])
   expected_gpu.append(['write',0x6013d4,1,c['selector']]);expected_gpu.extend([['read',off,4,vals[off]] for off in mmoffs[3:]])
  assert gpu==expected_gpu
  wanted=[c['pci_id'],c['command'],c['bar']]+([crtc[0x25]]+[vals[i] for i in mmoffs[:3]]+[c['seed'],vals[0x600800],vals[0x100200]] if result==1 else [0xffffffff]*7)
  raw=list(struct.unpack('<10I',u.mem_read(base+0x5a4,40)));assert raw==wanted
  assert struct.unpack('<I',u.mem_read(base+0x5cc,4))[0]==result
  assert u.mem_read(fb,1228800)==expected_framebuffer(raw,result)
  assert u.mem_read(base-4096,4096)==u.mem_read(base+4096,4096)==b'\x5a'*4096
  assert u.mem_read(fb-4096,4096)==u.mem_read(fb+1228800,4096)==b'\xa5'*4096
  assert not u.reg_read(UC_X86_REG_EFLAGS)&0x200
  r['cases'].append({'name':c['name'],'inputs':c,'raw':raw,'result':result,'gpu_trace':gpu,'exact_pixels':True,'selectors_restored':True,'memory_guards':True,'passed':True})
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['cases']),'linked read-only GPU/pixel cases')

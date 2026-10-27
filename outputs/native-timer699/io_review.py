"""Execute linked699 timer/render bytes with explicit port and RDTSC models.
Does not model the physical timer rate, native handoff or cache timing.
"""
import datetime,hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn699/build002')
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE,UC_HOOK_INSN,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
from oracle import expected_framebuffer
out=K/'io-review001.json';assert not out.exists()
x=json.loads((K/'extract001.json').read_text());blob=(P/'stub.bin').read_bytes();o=x['offsets']
assert x['passed'] and hashlib.sha256(blob).hexdigest()==x['template_sha256']
cases=[]
def case(name,**kw):
 d=dict(name=name,pci_id=0x01b410de,command=0x00b00001,bar=0xc001,
        start=0x1000000,step=1,delay=0,mask=0xffffffff,base=0x1eff000,
        tsc_start=0xfffffff0,tsc_delta=366666);d.update(kw);cases.append(d)
for step in [1,2,3,100,1687,1688,1689,33750,33751,0,-1]:case('step_'+str(step),step=step)
case('wrap32',start=0xfffffff0,step=17)
case('wrap24_rejected',start=0xfffff0,step=17,mask=0xffffff)
case('last_read_success',step=1688,delay=99999)
case('one_too_late',step=1688,delay=100000)
case('relocated',base=0x1edc000)
case('tsc64_wrap',tsc_start=0xfffffffffffffff0,tsc_delta=0x100000002)
case('wrong_device',pci_id=0x70108086)
case('absent_device',pci_id=0xffffffff,command=0xffffffff,bar=0xffffffff)
case('io_disabled',command=0x00b00000)
case('wrong_bar',bar=0xd001)
case('bar_not_io',bar=0xc000)

def reference(c):
 result=2 if c['pci_id']!=0x01b410de else 3 if not c['command']&1 else 4 if c['bar']!=0xc001 else 0
 first=last=elapsed=0xffffffff;reads=0;delta=0xffffffffffffffff
 if not result:
  first=last=c['start'];elapsed=0;reads=1
  for n in range(1,100001):
   now=(c['start']+c['step']*max(0,n-c['delay']))&c['mask']
   difference=(now-last)&0xffffffff;elapsed=(now-first)&0xffffffff;last=now;reads+=1
   if difference>33750 or elapsed>33750:result=6;break
   if elapsed>=1688:result=1;break
  else:result=5
  delta=c['tsc_delta']
 return [c['pci_id'],c['command'],c['bar'],first,last,elapsed,reads,result,delta&0xffffffff,delta>>32]

r={'passed':False,'scope':__doc__,'template_sha256':x['template_sha256'],'cases':[]}
try:
 for c in cases:
  base=c['base'];fb=0x3000000;u=Uc(UC_ARCH_X86,UC_MODE_32)
  u.mem_map(base-4096,12288);u.mem_write(base-4096,b'\x5a'*12288);u.mem_write(base,blob)
  u.mem_write(base+0x508,struct.pack('<L',fb));u.mem_write(base+0x540,struct.pack('<L',3))
  u.mem_map(fb-4096,3686400+8192);u.mem_write(fb-4096,b'\xa5'*4096);u.mem_write(fb+3686400,b'\xa5'*4096)
  initial=bytearray(b'\x20'*3686400)
  for y in range(8,80):initial[(y*1280+8)*4:(y*1280+1272)*4]=struct.pack('<L',0x00ff00)*1264
  u.mem_write(fb,bytes(initial));u.reg_write(UC_X86_REG_EBP,base);u.reg_write(UC_X86_REG_ESP,base+4096);u.reg_write(UC_X86_REG_EFLAGS,2)
  original=0x80005010;selector=[original];events=[];timer=[0];tsc=[0];done=[False];min_sp=[base+4096]
  def inp(uc,port,size,user):
   if port==0xcf8 and size==4:events.append(['in',port,selector[0]]);return selector[0]
   if port==0xcfc and size==4:
    value={0x80000900:c['pci_id'],0x80000904:c['command'],0x80000914:c['bar']}[selector[0]]
    events.append(['in',port,value]);return value
   assert port==0x8008 and size==4 and selector[0]==original
   n=timer[0];timer[0]+=1;assert timer[0]<=100001
   assert c['pci_id']==0x01b410de and c['command']&1 and c['bar']==0xc001
   return (c['start']+c['step']*max(0,n-c['delay']))&c['mask']
  def output(uc,port,size,value,user):
   assert port==0xcf8 and size==4,'No timer/SMBus/GPU control output permitted'
   selector[0]=value;events.append(['out',port,value])
  def step(uc,pc,size,user):
   min_sp[0]=min(min_sp[0],uc.reg_read(UC_X86_REG_ESP))
   if pc==base+o['hold']:done[0]=True;uc.emu_stop();return
   if bytes(uc.mem_read(pc,size))==b'\x0f\x31':
    assert tsc[0]<2
    value=(c['tsc_start']+(c['tsc_delta'] if tsc[0] else 0))&0xffffffffffffffff
    uc.reg_write(UC_X86_REG_EAX,value&0xffffffff);uc.reg_write(UC_X86_REG_EDX,value>>32)
    tsc[0]+=1;uc.reg_write(UC_X86_REG_EIP,pc+2)
  def write(uc,access,address,size,value,user):
   assert (fb<=address and address+size<=fb+3686400) or (base+0x5a0<=address and address+size<=base+0x5d4) or (base+0xe00<=address and address+size<=base+4096) or (address==base+0x540 and size==4),hex(address)
  u.hook_add(UC_HOOK_INSN,inp,None,1,0,UC_X86_INS_IN);u.hook_add(UC_HOOK_INSN,output,None,1,0,UC_X86_INS_OUT)
  u.hook_add(UC_HOOK_CODE,step);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start(base+o['probe'],base+o['code_end'],count=4000000)
  assert done[0] and selector[0]==original and min_sp[0]>=base+0xe00
  expected_events=[['in',0xcf8,original]]
  for reg,v in [(0x80000900,c['pci_id']),(0x80000904,c['command']),(0x80000914,c['bar'])]:expected_events.extend([['out',0xcf8,reg],['in',0xcfc,v]])
  expected_events.append(['out',0xcf8,original]);assert events==expected_events
  raw=list(struct.unpack('<10L',u.mem_read(base+0x5a4,40)));wanted=reference(c);assert raw==wanted,(c['name'],raw,wanted)
  assert timer[0]==raw[6] and tsc[0]==(2 if timer[0] else 0)
  assert u.mem_read(fb,3686400)==expected_framebuffer(raw,raw[7])
  assert u.mem_read(base-4096,4096)==u.mem_read(base+4096,4096)==b'\x5a'*4096
  assert u.mem_read(fb-4096,4096)==u.mem_read(fb+3686400,4096)==b'\xa5'*4096
  assert not u.reg_read(UC_X86_REG_EFLAGS)&0x200
  r['cases'].append({'name':c['name'],'inputs':c,'raw':raw,'timer_reads':timer[0],'rdtsc_count':tsc[0],
    'exact_pixels':True,'no_smbus_io':True,'pci_selector_restored':True,'memory_guards':True,'passed':True})
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['cases']),'linked timer/pixel cases; model only')

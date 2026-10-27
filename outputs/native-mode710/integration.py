"""710 post-transition instruction model: bounded bars, PCI/timer, no transaction.
Initialized CPU context and modeled I/O do not prove physical/cache behavior.
Fresh execution of exact710 pages; no closed runtime is reopened.
"""
import datetime,hashlib,json,os,struct,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]; P=Path('C:/xwn710/host001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
OUT=K/'integration001.json'; assert not OUT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
b=json.loads((K/'host001.json').read_text()); assert b['passed']
for n,h in b['files'].items():assert sha((P/n).read_bytes())==h
for n,h in b['sources'].items():assert sha((K/n).read_bytes())==h
sy=b['bridge_symbols']; old=Path('C:/xwn708/host001/bridge.bin').read_bytes()
oldrec=json.loads((W/'outputs/native-mode708/host001.json').read_text())
assert sha(old)==oldrec['files']['bridge.bin']
new=(P/'bridge.bin').read_bytes(); at=sy['bridge_checkpoint']
assert old[:at]==new[:at] and old[at+6:]==new[at+6:]
assert old[at:at+6]==bytes.fromhex('8d8500510000') and new[at]!=old[at]
for n,v in oldrec['bridge_symbols'].items():assert sy[n]==v
R={'passed':False,'scope':__doc__,'physical_access':False,'bridge_sha256':sha(new),
   'only_changed_bytes_range':[at,at+6],'all_previous_symbols_unchanged':True,
   'harness_sha256':sha(Path(__file__).read_bytes()),'cases':[]}
deadline=time.monotonic()+240
FB=0x3000000; SIZE=3686400
SELECT=[0x80010000,0x80010004,0x80010010,0x80000900,0x80000904,0x80000914,
        0x80000800,0x80000804,0x80000810,0x80000884]
VALUES=[0x02a010de,2,0xfd000000,0x01b410de,1,0xc001,0x01b210de,1,0,0x8001]
def run(name,page,refusal=None,pci_bad=None,request_bad=False,timer='normal'):
 assert time.monotonic()<deadline
 base=struct.unpack_from('<I',page,0x844)[0]; sp=base+0x8000; end=base+sy['bridge_hold']
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32)
 c.mem_map(base-4096,40960); c.mem_write(base-4096,b'G'*40960); c.mem_write(base,page)
 c.mem_map(FB-4096,SIZE+8192); c.mem_write(FB-4096,b'Z'*(SIZE+8192))
 if request_bad:c.mem_write(base+0x5004,pack(FB+4096))
 data=bytes(c.mem_read(base,0x6000))
 total=sum(struct.unpack_from('<I',data,i)[0] for i in range(0,0x6000,4) if i!=0x854 and not 0x880<=i<0x900)&0xffffffff
 c.mem_write(base+0x854,pack(total)); initial=bytes(c.mem_read(base,32768))
 c.reg_write(x.UC_X86_REG_GDTR,(0,base+0x800,31,0)); c.reg_write(x.UC_X86_REG_CR0,0x40000011)
 for reg,val in [(x.UC_X86_REG_CS,0x10),(x.UC_X86_REG_DS,0x18),(x.UC_X86_REG_ES,0x18),(x.UC_X86_REG_SS,0x18)]:c.reg_write(reg,val)
 c.reg_write(x.UC_X86_REG_EBP,base); c.reg_write(x.UC_X86_REG_ESP,sp); c.reg_write(x.UC_X86_REG_EFLAGS,2)
 pci=dict(zip(SELECT,VALUES))
 if pci_bad:pci[pci_bad[0]]=pci_bad[1]
 state={'selector':0x12345678,'timer_reads':0,'checkpoint':0}; trace=[]
 def pin(c,port,width,_):
  assert width==4
  if port==0xcf8:trace.append(['read',port]);return state['selector']
  if port==0xcfc:trace.append(['read',port,state['selector']]);return pci[state['selector']]
  assert port==0x8008,'unexpected native I/O read'
  n=state['timer_reads'];state['timer_reads']+=1
  first=0xfffffff0 if timer=='wrap' else 0x1000
  step={'normal':200,'wrap':200,'stall':0,'backwards':-1,'jump':33751,'minimum':1688,'maximum':33750}[timer]
  return (first+n*step)&0xffffffff
 def pout(c,port,width,value,_):
  assert port==0xcf8 and width==4,'unexpected native I/O write'
  trace.append(['write',port,value]);state['selector']=value
 def block(c,pc,size,_):
  assert not base+0x1000<=pc<base+0x1000+9916,'retained transaction executed'
  if pc==base+at:state['checkpoint']+=1
 c.hook_add(u.UC_HOOK_INSN,pin,None,1,0,x.UC_X86_INS_IN)
 c.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
 c.hook_add(u.UC_HOOK_BLOCK,block)
 # No GPU MMIO is mapped: any access fails this model immediately.
 c.emu_start(base+sy['bridge_post'],end,timeout=10000000,count=5000000)
 assert c.reg_read(x.UC_X86_REG_EIP)==end,(name,'execution bound')
 expected_trace=[['read',0xcf8]]
 for sel in SELECT:expected_trace.extend([['write',0xcf8,sel],['read',0xcfc,sel]])
 expected_trace.append(['write',0xcf8,0x12345678]);assert trace==expected_trace
 assert state['selector']==0x12345678 and c.reg_read(x.UC_X86_REG_ESP)==sp
 assert c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==0
 final=bytes(c.mem_read(base,32768));assert struct.unpack_from('<I',final,0x880)[0]==2
 assert struct.unpack_from('<I',final,0x8d0)[0]==(refusal or 5)
 for begin,last in [(0,0x880),(0x900,0x6000)]:assert final[begin:last]==initial[begin:last]
 assert c.mem_read(base-4096,4096)==b'G'*4096 and c.mem_read(base+32768,4096)==b'G'*4096
 assert c.mem_read(FB-4096,4096)==b'Z'*4096 and c.mem_read(FB+SIZE,4096)==b'Z'*4096
 color={None:0x00ffff,1:0xff0000,2:0xffff00,3:0xff00ff,4:0xff8000,5:0xffffff}[refusal]
 expected=bytearray(b'Z'*SIZE)
 for row0,rgb in [(8,0x00ff00),(48,color)]:
  for row in range(row0,row0+32):expected[row*5120+32:row*5120+5088]=pack(rgb)*1264
 assert c.mem_read(FB,SIZE)==expected,'whole framebuffer bounded-bar oracle'
 if refusal in (1,2,3,4):assert state['timer_reads']==0
 elif timer=='stall':assert state['timer_reads']==100001
 elif timer in ('backwards','jump','minimum','maximum'):assert state['timer_reads']==2
 else:assert state['timer_reads']==10
 assert state['checkpoint']==(0 if refusal else 1)
 R['cases'].append({'name':name,'refusal':refusal,'timer_reads':state['timer_reads'],
  'checkpoint_reached':not refusal,'no_payload_execution_or_MMIO_or_device_writes':True,
  'CF8_restored':True,'whole_framebuffer_and_guards_pass':True,'phase':2})
try:
 for layout in ('dual','relocated'):
  page=(P/layout/'page.bin').read_bytes()
  for timer in ('normal','wrap','minimum','maximum'):run(layout+'-'+timer,page,timer=timer)
  for timer in ('stall','backwards','jump'):run(layout+'-'+timer,page,refusal=5,timer=timer)
  run(layout+'-request-mismatch',page,refusal=4,request_bad=True)
  run(layout+'-GPU-prefetchable',page,pci_bad=(0x80010010,0xfd000008))
  for idx,value,code in [(0,0,1),(1,0,1),(2,0xfc000000,1),(3,0,2),(4,0,2),(5,0xd001,2),
    (6,0,3),(7,0,3),(8,0x9001,3),(8,0x8001,3),(9,0,3)]:
   run(layout+'-PCI-'+str(idx)+'-'+hex(value),page,refusal=code,pci_bad=(SELECT[idx],value))
 R['passed']=True
except BaseException as e:R['failure']=repr(e);raise
finally:
 R['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 OUT.write_text(json.dumps(R,indent=2)+'\n')
print('PASS',len(R['cases']),'fresh710 checkpoint models; no physical proof')

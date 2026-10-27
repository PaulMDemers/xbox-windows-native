"""716 exact relocated unlock/CR11 check models; no physical or cache proof.
Only selectors, CR1f57, PRAMDAC630 test/restore, sequencer1 and paired80d3 writes are permitted.
Only aligned32-bit PRAMDAC630=2 then3 data writes; no encoder/timing/clock writes; independent whole-image and I/O-order checks.
"""
import datetime,hashlib,json,os,struct,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn716/host001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
OUT=K/'integration001.json';assert not OUT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
b=json.loads((K/'host001.json').read_text());assert b['passed']
for n,h in b['files'].items():assert sha((P/n).read_bytes())==h
for n,h in b['sources'].items():assert sha((K/n).read_bytes())==h
ps={a[2]:int(a[0],16)-0x100000 for line in Path('C:/xwn716/payload001/symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
code_end=min(int(a[0],16)-0x100000 for line in Path('C:/xwn716/payload001/symbols.stdout').read_text().splitlines() if len(a:=line.split())==3 and a[1] in ('t','T') and int(a[0],16)-0x100000>ps['native_transaction704'])
sy=b['bridge_symbols'];FB=0x3000000;SIZE=3686400;GPU=0xfd000000
R={'passed':False,'scope':__doc__,'physical_access':False,'harness_sha256':sha(Path(__file__).read_bytes()),'cases':[]}
deadline=time.monotonic()+240
SELECT=[0x80010000,0x80010004,0x80010010,0x80000900,0x80000904,0x80000914,0x80000800,0x80000804,0x80000810,0x80000884]
VALUES=[0x02a010de,2,0xfd000000,0x01b410de,1,0xc001,0x01b210de,1,0,0x8001]
def run(name,page,refusal=None,pci_bad=None,req_bad=None,timer='normal',cr_bad=None,mm_bad=None,direct=False,null=None,flags=2,want=0x716,wait_mode='normal',seq1=1,drop_seq=None,changed_context=False,gate_drop=None,cr11_after=None,drop_unlock=False,reg630_mode="normal"):
 assert time.monotonic()<deadline
 base=struct.unpack_from('<I',page,0x844)[0];sp=base+0x8000;end=base+sy['bridge_hold'];op=base+0x5100
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32)
 c.mem_map(base-4096,40960);c.mem_write(base-4096,b'G'*40960);c.mem_write(base,page)
 c.mem_map(FB-4096,SIZE+8192);c.mem_write(FB-4096,b'Z'*(SIZE+8192));c.mem_map(GPU,0x800000)
 if req_bad:c.mem_write(base+0x5000+4*req_bad[0],pack(req_bad[1]))
 data=bytes(c.mem_read(base,0x6000));total=sum(struct.unpack_from('<I',data,i)[0] for i in range(0,0x6000,4) if i!=0x854 and not 0x880<=i<0x900)&0xffffffff
 c.mem_write(base+0x854,pack(total));initial=bytes(c.mem_read(base,32768))
 c.reg_write(x.UC_X86_REG_GDTR,(0,base+0x800,31,0));c.reg_write(x.UC_X86_REG_CR0,0x40000011)
 for reg,val in [(x.UC_X86_REG_CS,0x10),(x.UC_X86_REG_DS,0x18),(x.UC_X86_REG_ES,0x18),(x.UC_X86_REG_SS,0x18)]:c.reg_write(reg,val)
 c.reg_write(x.UC_X86_REG_EBP,base);c.reg_write(x.UC_X86_REG_ESP,sp);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 pci=dict(zip(SELECT,VALUES))
 if pci_bad:pci[pci_bad[0]]=pci_bad[1]
 state={'selector':0x12345678,'timer_reads':0,'payload_blocks':0,'wait_reads':0,'seq1':seq1,'gate':4,'unlock_requests':0,'reg630_writes':0,'after_unlock_cr11':0};trace=[];reads=[];writes=[];pair=[]
 cr=bytearray([0xa5]*256);cr[9]=0x25;cr[0x11]=9;cr[0x21]=255;cr[0x44]=0;cr[0x39]=255;cr[0x13]=0x80;cr[0x19]=0x51;cr[0x25]=0x10;cr[0x28]=0x83;cr[0x2d]=0xe0
 if cr_bad:cr[cr_bad[0]]=cr_bad[1]
 original_cr=bytes(cr)
 sels={0x6013d4:0x67,0xc03c4:0x72,0xc03ce:0x91};original_sels=dict(sels)
 mm={0x680508:0x3c20d,0x68050c:0x100a0400,0x680880:0x21101100,0x100200:0x3070003,0x600804:3,0x600800:FB,0x680838:1279,0x680818:719,0x680630:3}
 if mm_bad:mm[mm_bad[0]]=mm_bad[1]
 original630=mm[0x680630]
 def access(c,kind,addr,width,value,_):
  off=addr-GPU
  if kind==u.UC_MEM_WRITE:
   writes.append([off,value])
   if off==0x680630:
    assert width==4,'register630 must be one aligned32-bit access'
    n=state['reg630_writes'];assert n<2 and value==(2 if n==0 else 3)
    state['reg630_writes']+=1;pair.append(['reg630',value])
    dropped=(n==0 and reg630_mode=='drop-test') or (n==1 and reg630_mode=='drop-restore')
    if not dropped:mm[off]=(6 if reg630_mode=='coerce-test' and n==0 else 0 if reg630_mode=='coerce-restore' and n==1 else value)
    if reg630_mode=='CR11-side-effect' and n==1:cr[0x11]=0x89
    if reg630_mode=='pitch-side-effect' and n==1:cr[0x19]=0x10
    return
   assert width==1
   if off==0xc03c5:
    assert sels[0xc03c4]==1 and value in (0x21,1),'forbidden sequencer write'
    pair.append(['seq1',value])
    if not (drop_seq=='blank' and value==0x21) and not (drop_seq=='restore' and value==1):state['seq1']=value
   elif off==0x6013d5:
    index=sels[0x6013d4]
    if index==0x1f:
     assert value==0x57
     state['unlock_requests']+=1;pair.append(['unlock',0x57])
     if not drop_unlock and cr11_after is not None:cr[0x11]=cr11_after
     state['after_unlock_cr11']=cr[0x11]
    else:raise AssertionError('CR11/CR19/other geometry write prohibited')
   else:
    assert off in sels,'forbidden geometry/MMIO write'
    sels[off]=value
  else:
   reads.append([off,width])
   if off in sels:assert width==1;value=sels[off]
   elif off==0xc03c5:assert width==1 and sels[0xc03c4]==1;value=state['seq1']
   elif off==0x6013d5:assert width==1 and sels[0x6013d4]!=0x1f,'CR1f readback is not a write-key oracle';value=cr[sels[0x6013d4]]
   else:assert off in mm and width==4,'unexpected GPU read';value=mm[off]
   c.mem_write(addr,value.to_bytes(width,'little'))
 def pin(c,port,width,_):
  assert width==4
  if port==0xcf8:trace.append(['read',port]);return state['selector']
  if port==0xcfc:trace.append(['read',port,state['selector']]);return pci[state['selector']]
  assert port==0x8008,'unexpected device I/O read'
  if struct.unpack('<I',c.mem_read(op,4))[0]==3:
   n=state['wait_reads'];state['wait_reads']+=1
   first=0xfffffff0 if wait_mode=='wrap' else 0xfffff0 if wait_mode=='wrap24' else 0x1000
   step={'normal':33750,'wrap':33750,'wrap24':33750,'slow':337,'stall':0,'backwards':-1,'jump':33751,'last_read':0}[wait_mode]
   value=first+(n*3375000//1000000 if wait_mode=='last_read' else n*step)
   return value&(0xffffff if wait_mode=='wrap24' else 0xffffffff)
  n=state['timer_reads'];state['timer_reads']+=1
  first=0xfffffff0 if timer=='wrap' else 0x1000
  step={'normal':200,'wrap':200,'stall':0,'backwards':-1,'jump':33751,'minimum':1688,'maximum':33750}[timer]
  return (first+n*step)&0xffffffff
 def pout(c,port,width,value,_):
  if port==0x80d3:
   assert width==1 and value in (5,4),'unexpected output-gate request'
   pair.append(['gate',value])
   if gate_drop!=value:state['gate']=value
   if value==4 and changed_context:mm[0x680508]=0
   if value==4 and reg630_mode=='late-change':mm[0x680630]=2
   return
  assert port==0xcf8 and width==4,'forbidden device I/O write'
  trace.append(['write',port,value]);state['selector']=value
 def block(c,pc,size,_):
  if base+0x1000<=pc<base+0x1000+9916:
   state['payload_blocks']+=1
   assert pc<base+0x1000+code_end,'encoder/programming helper executed'
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,GPU,GPU+0x7fffff)
 c.hook_add(u.UC_HOOK_INSN,pin,None,1,0,x.UC_X86_INS_IN)
 c.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
 c.hook_add(u.UC_HOOK_BLOCK,block)
 start=base+sy['bridge_post']
 if direct:
  args=[base+0x5000,GPU,FB,op]
  if null is not None:args[null]=0
  c.reg_write(x.UC_X86_REG_ESP,sp-20);c.mem_write(sp-20,pack(end,*args))
  start=base+0x1000+ps['native_transaction704']
 c.emu_start(start,end,timeout=10000000,count=50000000)
 assert c.reg_read(x.UC_X86_REG_EIP)==end,(name,'execution bound')
 assert c.reg_read(x.UC_X86_REG_ESP)==(sp-16 if direct else sp)
 assert c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
 assert sels==original_sels,'indexed selectors not restored'
 final=bytes(c.mem_read(base,32768))
 for begin,last in [(0,0x880),(0x900,0x5100),(0x51d0,0x6000)]:assert final[begin:last]==initial[begin:last]
 for ptr in (base-4096,base+32768):assert c.mem_read(ptr,4096)==b'G'*4096
 for ptr in (FB-4096,FB+SIZE):assert c.mem_read(ptr,4096)==b'Z'*4096
 expected=bytearray(b'Z'*SIZE)
 if not direct:
  expected_trace=[['read',0xcf8]]
  for sel in SELECT:expected_trace.extend([['write',0xcf8,sel],['read',0xcfc,sel]])
  expected_trace.append(['write',0xcf8,0x12345678]);assert trace==expected_trace and state['selector']==0x12345678
  color=({1:0xff0000,2:0xffff00,3:0xff00ff,4:0xff8000,5:0xffffff}[refusal] if refusal else 0x00ff00 if want==0x716 else 0xff8000)
  for row0,rgb in [(8,0x00ff00),(48,color)]:
   for row in range(row0,row0+32):expected[row*5120+32:row*5120+5088]=pack(rgb)*1264
  assert struct.unpack_from('<I',final,0x880)[0]==(2 if refusal else 4)
  if refusal:
   assert not reads and not writes and not state['payload_blocks']
   assert struct.unpack_from('<I',final,0x8d0)[0]==refusal
  else:assert struct.unpack_from('<I',final,0x8d4)[0]==want
 else:assert not trace and not state['timer_reads'] and c.reg_read(x.UC_X86_REG_EAX)==want
 paired=want in (0x716,0x7162,0x7163,0x7164,0x7165,0x7167,0x7168) and not refusal
 unlock=paired and drop_seq!='blank'
 reg630_attempted=unlock and state['after_unlock_cr11']==original_cr[0x11]
 expected_pair=[['seq1',0x21],['gate',5]]+([['unlock',0x57]] if unlock else [])+([['reg630',2],['reg630',3]] if reg630_attempted else [])+[['gate',4],['seq1',1]]
 assert pair==(expected_pair if paired else []),'one exact unlock/restore sequence only'
 assert state['unlock_requests']==int(unlock)
 unlock_rejected=unlock and state['after_unlock_cr11']!=original_cr[0x11]
 if paired:
  assert state['seq1']==(0x21 if drop_seq=='restore' else 1)
  assert state['gate']==(5 if gate_drop==4 else 4)
 else:assert not state['wait_reads']
 if not refusal:
  assert state['payload_blocks']>0
  if null!=3:
   result=struct.unpack('<52I',c.mem_read(op,208));assert result[1]==want,(name,result)
   assert result[0]==(5 if paired else 1 if want in (5,0x7161,0x7166) else 0)
   assert result[4:11]==(0,)*7 and result[19:36]==(0,)*17
   if paired or want in (5,0x7161,0x7166):
    assert result[11:19]==(original_cr[0x11],original_cr[0x21],original_cr[3]&0xe0,original_cr[5]&0x60,original_cr[9]&0x9f,original_cr[0x16]&0x80,original_cr[0x2d]&0xe0,original_cr[0x11]&0x7f)
   elif want in (2,3,4):assert not reads and not writes
   if paired:
    assert result[2]==(1 if want==0x7164 else 0) and result[3]==1
    assert result[40:43]==(1,1 if drop_seq=='blank' else 0x21,0x21 if drop_seq=='restore' else 1)
    if drop_seq=='blank' or unlock_rejected or (reg630_attempted and (reg630_mode not in ('normal','late-change'))):assert result[36:40]==(0,)*4 and result[43]==0xffffffff and not state['wait_reads']
    else:
     status=2 if wait_mode=='stall' else 3 if wait_mode in ('jump','backwards','wrap24') else 0
     assert result[43]==status and result[39]==state['wait_reads']
     assert result[38]==(result[37]-result[36])&0xffffffff
     if not status:assert 3375000<=result[38]<=3408750 and 2<=result[39]<=1000001
     elif status==2:assert result[38]==0 and result[39]==1000001
     else:assert result[39]==2
   assert result[44:46]==((1,state['after_unlock_cr11']) if unlock else (0,0))
   baseline_reg630_read=paired or want==0x7166
   assert result[46:48]==((original630,2) if baseline_reg630_read else (0,0))
   assert result[50:52]==((1,1) if reg630_attempted else (0,0))
   if reg630_attempted:
    after=original630 if reg630_mode=='drop-test' else 6 if reg630_mode=='coerce-test' else 2
    restored=after if reg630_mode=='drop-restore' else 0 if reg630_mode=='coerce-restore' else original630
    assert result[48:50]==(after,restored) and mm[0x680630]==(2 if reg630_mode=='late-change' else restored)
   else:assert result[48:50]==(0,0) and mm[0x680630]==original630
   if not paired:
    assert result[2:4]==(0,0) and result[36:40]==(0,)*4 and result[41:43]==(0,0) and result[43]==0xffffffff
    assert result[40]==(seq1 if want in (0x7161,0x7166) else 0)
 assert c.mem_read(FB,SIZE)==expected,'whole framebuffer oracle'
 R['cases'].append({'name':name,'direct_call':direct,'refusal':refusal,'return':None if refusal else want,
  'payload_blocks':state['payload_blocks'],'GPU_reads':len(reads),'selector_writes':len(writes),
  'selector_trace_sha256':sha(json.dumps(writes).encode()),'selectors_restored':True,
  'GPU_data_write_scope':'aligned32-bit680630=2 then saved3 only; bit meaning unknown','blank_restore_pair':pair,'wait_reads':state['wait_reads'],'gate_drop_not_detectable_by_code':gate_drop,'unlock_requests':state['unlock_requests'],'key_causality_not_proved':True,'reg630_write_attempted':reg630_attempted,'PRAMDAC630_final':mm[0x680630],'whole_framebuffer_guards_pass':True})
try:
 for layout in ('dual','relocated'):
  page=(P/layout/'page.bin').read_bytes()
  for timer in ('normal','wrap','minimum','maximum'):run(layout+'-'+timer,page,timer=timer)
  for timer in ('stall','backwards','jump'):run(layout+'-'+timer,page,timer=timer,refusal=5)
  run(layout+'-bridge-fb-mismatch',page,req_bad=(1,FB+4096),refusal=4)
  for idx,value,code in [(0,0,1),(1,0,1),(2,0xfc000000,1),(3,0,2),(4,0,2),(5,0xd001,2),(6,0,3),(7,0,3),(8,0x9001,3),(8,0x8001,3),(9,0,3)]:
   run(layout+'-PCI-'+str(idx)+'-'+hex(value),page,refusal=code,pci_bad=(SELECT[idx],value))
  for reg,value in [(0x11,0x80),(0x21,0),(0x44,3),(9,0x80),(0x13,0),(0x19,0),(0x25,0x20),(0x28,0),(0x39,0)]:
   run(layout+'-CR-'+hex(reg),page,cr_bad=(reg,value),want=5)
  for reg in (0x680508,0x68050c,0x680880,0x100200,0x600804,0x600800,0x680838,0x680818):
   run(layout+'-MMIO-'+hex(reg),page,mm_bad=(reg,0),want=5)
  for idx in range(15):
   run(layout+'-request-'+str(idx),page,req_bad=(idx,0),direct=True,want=3)
  for idx in range(4):run(layout+'-null-'+str(idx),page,direct=True,null=idx,want=2)
  run(layout+'-IF',page,direct=True,flags=0x202,want=4)
  run(layout+'-direct-checkpoint',page,direct=True)
  for value in (0,0x21,0xff):run(layout+'-seq-baseline-'+str(value),page,seq1=value,want=0x7161)
  for mode in ('wrap','slow','last_read'):run(layout+'-wait-'+mode,page,wait_mode=mode)
  for mode in ('stall','backwards','jump','wrap24'):run(layout+'-wait-'+mode,page,wait_mode=mode,want=0x7163)
  run(layout+'-blank-write-dropped',page,drop_seq='blank',want=0x7162)
  run(layout+'-restore-write-dropped',page,drop_seq='restore',want=0x7164)
  run(layout+'-context-changed',page,changed_context=True,want=0x7164)
  for value in (4,5):run(layout+'-gate-drop-unobservable-'+str(value),page,gate_drop=value)
  run(layout+'-unlock-key-ignored-already-writable',page,drop_unlock=True)
  for value in (0,2,0xffffffff):run(layout+'-630-baseline-'+str(value),page,mm_bad=(0x680630,value),want=0x7166)
  for mode,code in [('drop-test',0x7167),('coerce-test',0x7167),('drop-restore',0x7164),('coerce-restore',0x7164),('CR11-side-effect',0x7168),('pitch-side-effect',0x7168),('late-change',0x7164)]:
   run(layout+'-PRAMDAC630-'+mode,page,reg630_mode=mode,want=code)
  run(layout+'-PRAMDAC630-fail-plus-visible-restore-fail',page,reg630_mode='drop-test',drop_seq='restore',want=0x7164)
  run(layout+'-PRAMDAC630-restore-fail-plus-context-fail',page,reg630_mode='drop-restore',changed_context=True,want=0x7164)
  run(layout+'-unlock-same-CR11',page,cr11_after=9)
  for value in (0,0x80,0x89,0xff):run(layout+'-unlock-CR11-changed-'+str(value),page,cr11_after=value,want=0x7165)
  run(layout+'-unlock-rejection-restore-fails',page,cr11_after=0,drop_seq='restore',want=0x7164)
  run(layout+'-unlock-rejection-context-fails',page,cr11_after=0,changed_context=True,want=0x7164)
 R['passed']=True
except BaseException as e:R['failure']=repr(e);raise
finally:
 R['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();OUT.write_text(json.dumps(R,indent=2)+'\n')
print('PASS',len(R['cases']),'PRAMDAC630 changed-readback/restore models; no physical proof')

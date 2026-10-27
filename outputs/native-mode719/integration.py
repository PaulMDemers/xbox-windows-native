"""719 exact relocated CR1b read-only boundary models; no physical or cache proof.
Only selectors, CR1f57, sequencer1 and paired80d3 writes are permitted.
CR1b data writes forbidden; no encoder/timing/clock writes; independent whole-image and I/O-order checks.
"""
import datetime,hashlib,json,os,struct,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn719/host001')
sys.path.insert(0,str(W/'work/python-packages'))
sys.path.insert(0,str(K))
from optical_oracle import paint_report
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
OUT=K/'integration001.json';assert not OUT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
b=json.loads((K/'host001.json').read_text());assert b['passed']
for n,h in b['files'].items():assert sha((P/n).read_bytes())==h
for n,h in b['sources'].items():assert sha((K/n).read_bytes())==h
ps={a[2]:int(a[0],16)-0x100000 for line in Path('C:/xwn719/payload002/symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
code_end=min(int(a[0],16)-0x100000 for line in Path('C:/xwn719/payload002/symbols.stdout').read_text().splitlines() if len(a:=line.split())==3 and a[1] in ('t','T') and int(a[0],16)-0x100000>ps['native_transaction704'])
sy=b['bridge_symbols'];FB=0x3000000;SIZE=3686400;GPU=0xfd000000
R={'passed':False,'scope':__doc__,'physical_access':False,'harness_sha256':sha(Path(__file__).read_bytes()),'cases':[]}
deadline=time.monotonic()+480
SELECT=[0x80010000,0x80010004,0x80010010,0x80000900,0x80000904,0x80000914,0x80000800,0x80000804,0x80000810,0x80000884]
VALUES=[0x02a010de,2,0xfd000000,0x01b410de,1,0xc001,0x01b210de,1,0,0x8001]
def run(name,page,refusal=None,pci_bad=None,req_bad=None,timer='normal',cr_bad=None,mm_bad=None,direct=False,null=None,flags=2,want=0x719,wait_mode='normal',seq1=1,drop_seq=None,changed_context=False,gate_drop=None,cr11_after=None,drop_unlock=False,change_at=None,change_value=5):
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
 state={'selector':0x12345678,'timer_reads':0,'payload_blocks':0,'wait_reads':0,'seq1':seq1,'gate':4,'unlock_requests':0,'cr1b_writes':0,'boundary':-1,'after_unlock_cr11':0};trace=[];reads=[];writes=[];pair=[]
 cr=bytearray([0xa5]*256);cr[9]=0x25;cr[0x11]=9;cr[0x21]=255;cr[0x44]=0;cr[0x39]=255;cr[0x13]=0x80;cr[0x19]=0x51;cr[0x25]=0x10;cr[0x28]=0x83;cr[0x2d]=0xe0;cr[0x1b]=0x85
 if cr_bad:cr[cr_bad[0]]=cr_bad[1]
 original_cr=bytes(cr)
 sels={0x6013d4:0x67,0xc03c4:0x72,0xc03ce:0x91};original_sels=dict(sels)
 mm={0x680508:0x3c20d,0x68050c:0x100a0400,0x680880:0x21101100,0x100200:0x3070003,0x600804:3,0x600800:FB,0x680838:1279,0x680818:719,0x680630:3}
 if mm_bad:mm[mm_bad[0]]=mm_bad[1]
 original1b=original_cr[0x1b]
 def boundary(index):
  state['boundary']=index
  if change_at==index:cr[0x1b]=change_value
 def access(c,kind,addr,width,value,_):
  off=addr-GPU
  if kind==u.UC_MEM_WRITE:
   writes.append([off,value])

   assert width==1
   if off==0xc03c5:
    assert sels[0xc03c4]==1 and value in (0x21,1),'forbidden sequencer write'
    pair.append(['seq1',value]);boundary(0 if value==0x21 else 4)
    if not (drop_seq=='blank' and value==0x21) and not (drop_seq=='restore' and value==1):state['seq1']=value
   elif off==0x6013d5:
    index=sels[0x6013d4]
    if index==0x1f:
     assert value==0x57
     state['unlock_requests']+=1;pair.append(['unlock',0x57]);boundary(2)
     if not drop_unlock and cr11_after is not None:cr[0x11]=cr11_after
     state['after_unlock_cr11']=cr[0x11]
    else:raise AssertionError('CR1b/CR11/CR19/CR22/other CRTC data write prohibited')
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
   pair.append(['gate',value]);boundary(1 if value==5 else 3)
   if gate_drop!=value:state['gate']=value
   if value==4 and changed_context:mm[0x680508]=0
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
 for begin,last in [(0,0x880),(0x900,0x5100),(0x51d4,0x6000)]:assert final[begin:last]==initial[begin:last]
 for ptr in (base-4096,base+32768):assert c.mem_read(ptr,4096)==b'G'*4096
 for ptr in (FB-4096,FB+SIZE):assert c.mem_read(ptr,4096)==b'Z'*4096
 expected=bytearray(b'Z'*SIZE)
 if not direct:
  expected_trace=[['read',0xcf8]]
  for sel in SELECT:expected_trace.extend([['write',0xcf8,sel],['read',0xcfc,sel]])
  expected_trace.append(['write',0xcf8,0x12345678]);assert trace==expected_trace and state['selector']==0x12345678
  color=({1:0xff0000,2:0xffff00,3:0xff00ff,4:0xff8000,5:0xffffff}[refusal] if refusal else 0x00ff00 if want==0x719 else 0xff8000)
  for row0,rgb in [(8,0x00ff00),(48,color)]:
   for row in range(row0,row0+32):expected[row*5120+32:row*5120+5088]=pack(rgb)*1264
  assert struct.unpack_from('<I',final,0x880)[0]==(2 if refusal else 4)
  if refusal:
   assert not reads and not writes and not state['payload_blocks']
   assert struct.unpack_from('<I',final,0x8d0)[0]==refusal
  else:assert struct.unpack_from('<I',final,0x8d4)[0]==want
 else:assert not trace and not state['timer_reads'] and c.reg_read(x.UC_X86_REG_EAX)==want
 paired=want in (0x719,0x7192,0x7194,0x7195,0x7197) and not refusal
 unlock=paired and drop_seq!='blank'
 expected_pair=[['seq1',0x21],['gate',5]]+([['unlock',0x57]] if unlock else [])+[['gate',4],['seq1',1]]
 assert pair==(expected_pair if paired else []),'exact setup/restore sequence only'
 assert state['unlock_requests']==int(unlock) and state['cr1b_writes']==0
 assert not state['wait_reads'],'payload must not enter wait'
 if paired:
  assert state['seq1']==(0x21 if drop_seq=='restore' else 1)
  assert state['gate']==(5 if gate_drop==4 else 4)
 if not refusal:
  assert state['payload_blocks']>0
  if null!=3:
   result=struct.unpack('<53I',c.mem_read(op,212));assert result[1]==want,(name,result)
   assert result[0]==(5 if paired else 1 if want in (5,0x7191,0x7196) else 0)
   assert result[4:11]==(0,)*7 and result[19:40]==(0,)*21
   assert result[43]==0xffffffff
   if paired or want in (5,0x7191,0x7196):
    assert result[11:19]==(original_cr[0x11],original_cr[0x21],original_cr[3]&0xe0,original_cr[5]&0x60,original_cr[9]&0x9f,original_cr[0x16]&0x80,original_cr[0x2d]&0xe0,original_cr[0x11]&0x7f)
   elif want in (2,3,4):assert not reads and not writes
   if paired:
    assert result[2]==(1 if want==0x7194 and drop_seq!='blank' else 0) and result[3]==1
    assert result[40:43]==(1,1 if drop_seq=='blank' else 0x21,0x21 if drop_seq=='restore' else 1)
    # Oracle independent of code offsets: model observed event sequence and skipped unlock.
    v=original1b;expected_samples=[v]
    for stage in range(5):
     if stage==2 and not unlock:expected_samples.append(0xffffffff);continue
     if change_at==stage:v=change_value
     expected_samples.append(v)
    assert result[46:52]==tuple(expected_samples),(name,result[46:52],expected_samples)
    assert result[52]==(63 if unlock else 55) and cr[0x1b]==v
   else:
    assert result[2:4]==(0,0) and result[41:43]==(0,0)
    assert result[40]==(seq1 if want in (0x7191,0x7196) else 0)
    assert result[46]==(original1b if want==0x7196 else 0)
    assert result[47:52]==((0xffffffff,)*5 if want in (0x7191,0x7196) else (0,)*5)
    assert result[52]==(1 if want==0x7196 else 0) and cr[0x1b]==original1b
   assert result[44:46]==((1,state['after_unlock_cr11']) if unlock else (0,0))
 if not direct:
  optical_words=[0x7190000d]+[struct.unpack_from('<I',final,o)[0] for o in (0x880,0x8d0,0x8d4,0x5100,0x5104,0x51b8,0x51bc,0x51c0,0x51c4,0x51c8,0x51cc,0x51d0)]
  paint_report(expected,optical_words)
 assert c.mem_read(FB,SIZE)==expected,'whole framebuffer including416-bit optical oracle'
 R['cases'].append({'name':name,'direct_call':direct,'refusal':refusal,'return':None if refusal else want,
  'payload_blocks':state['payload_blocks'],'GPU_reads':len(reads),'selector_writes':len(writes),
  'selector_trace_sha256':sha(json.dumps(writes).encode()),'selectors_restored':True,
  'GPU_data_write_scope':'NO CR1b data write; CR1f57 and SEQ1 setup/restore only','blank_restore_pair':pair,'wait_reads':state['wait_reads'],'gate_drop_not_detectable_by_code':gate_drop,'unlock_requests':state['unlock_requests'],'key_causality_not_proved':True,'cr1b_data_writes':state['cr1b_writes'],'change_at':change_at,'change_value':change_value,'CR1b_final':cr[0x1b],'whole_framebuffer_guards_pass':True,'optical_words':optical_words if not direct else None})
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
  for value in (0,0x21,0xff):run(layout+'-seq-baseline-'+str(value),page,seq1=value,want=0x7191)
  run(layout+'-blank-write-dropped',page,drop_seq='blank',want=0x7192)
  run(layout+'-restore-write-dropped',page,drop_seq='restore',want=0x7194)
  run(layout+'-context-changed',page,changed_context=True,want=0x7194)
  for value in (4,5):run(layout+'-gate-drop-unobservable-'+str(value),page,gate_drop=value)
  run(layout+'-unlock-key-ignored',page,drop_unlock=True)
  for value in (0,0x05,0xff):run(layout+'-1b-baseline-'+str(value),page,cr_bad=(0x1b,value),want=0x7196)
  for stage in range(5):
   for value in (0,5,255):
    run(layout+'-boundary-'+str(stage)+'-value-'+str(value),page,change_at=stage,change_value=value,want=0x7197)
  run(layout+'-change-plus-blank-fail',page,change_at=0,drop_seq='blank',want=0x7192)
  run(layout+'-change-plus-restore-fail',page,change_at=2,drop_seq='restore',want=0x7194)
  run(layout+'-change-plus-context-fail',page,change_at=3,changed_context=True,want=0x7194)
  run(layout+'-change-plus-unlock-check-fail',page,change_at=2,cr11_after=0x89,want=0x7195)
  run(layout+'-unlock-same-CR11',page,cr11_after=9)
  for value in (0,0x80,0x89,0xff):run(layout+'-unlock-CR11-changed-'+str(value),page,cr11_after=value,want=0x7195)
  run(layout+'-unlock-rejection-restore-fails',page,cr11_after=0,drop_seq='restore',want=0x7194)
  run(layout+'-unlock-rejection-context-fails',page,cr11_after=0,changed_context=True,want=0x7194)
 R['passed']=True
except BaseException as e:R['failure']=repr(e);raise
finally:
 R['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();OUT.write_text(json.dumps(R,indent=2)+'\n')
print('PASS',len(R['cases']),'CR1b setup-boundary read-only models; no physical proof')

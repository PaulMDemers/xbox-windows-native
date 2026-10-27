"""Exact relocated726 bridge/control with independent MMIO and optical models.
Starts at post-paging transition; diskless CPU fixtures separately test transition.
No hardware/caching semantics proof and no closed runtime reused.
"""
import datetime,hashlib,json,os,struct,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn726/host002')
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K))
from optical_oracle import paint_report
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
out=K/'integration001.json';assert not out.exists()
b=json.loads((K/'host002.json').read_text());assert b['passed']
for n,h in b['sources'].items():assert sha(K/n)==h
for n,h in b['files'].items():assert sha(P/n)==h
sy=b['bridge_symbols'];FB=0x3000000;SIZE=3686400;GPU=0xfd000000
SELECT=[0x80010000,0x80010004,0x80010010,0x80000900,0x80000904,0x80000914,0x80000800,0x80000804,0x80000810,0x80000884]
VALUES=[0x02a010de,2,0xfd000000,0x01b410de,1,0xc001,0x01b210de,1,0,0x8001]
R={'passed':False,'scope':__doc__,'physical_access':False,'harness_sha256':sha(Path(__file__)),'cases':[]};deadline=time.monotonic()+420
def run(name,layout='dual',want=0x726,nmm=2,refusal=0,pci_bad=None,timer='normal',cr_bad=None,mm_bad=None,fault='',direct=False,badarg=None,flags=2,cpu4=0,behavior='constant',seq=1):
 assert time.monotonic()<deadline
 page=(P/layout/'page.bin').read_bytes();base=struct.unpack_from('<I',page,0x844)[0];sp=base+0x8000;op=base+0x5100;end=base+sy['bridge_hold']
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(base-4096,40960);c.mem_write(base-4096,b'G'*40960);c.mem_write(base,page)
 c.mem_map(FB-4096,SIZE+8192);c.mem_write(FB-4096,b'Z'*(SIZE+8192));c.mem_map(GPU,0x800000)
 initial=bytes(c.mem_read(base,32768));c.reg_write(x.UC_X86_REG_GDTR,(0,base+0x800,31,0));c.reg_write(x.UC_X86_REG_CR0,0x40000011);c.reg_write(x.UC_X86_REG_CR4,cpu4)
 for reg,val in [(x.UC_X86_REG_CS,0x10),(x.UC_X86_REG_DS,0x18),(x.UC_X86_REG_ES,0x18),(x.UC_X86_REG_SS,0x18)]:c.reg_write(reg,val)
 c.reg_write(x.UC_X86_REG_EBP,base);c.reg_write(x.UC_X86_REG_ESP,sp);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 pci=dict(zip(SELECT,VALUES))
 if pci_bad:pci[pci_bad[0]]=pci_bad[1]
 state={'selector':0x12345678,'ticks':0,'seq':seq,'gate':0,'nmm':0,'after_output_reads':0};trace=[];mw=[];sw=[];outs=[];samples=[]
 cr={9:0x25,0x11:9,0x21:255,0x44:0,0x39:255,0x13:0x80,0x19:0x51,0x25:0x10,0x28:0x83,0x2d:0xe0,0x1b:0x85,0x14:0,0x17:0xe3,0x22:0xfe,0x1f:3}
 if cr_bad:cr[cr_bad[0]]=cr_bad[1]
 sels={0x6013d4:0x67,0xc03c4:0x72,0xc03ce:0x91};original_sels=sels.copy()
 mm={0x680630:3,0x680880:0x21101100,0x680508:0x3c20d,0x68050c:0x100a0400,0x100200:0x3070003,0x600804:3,0x600800:FB,0x680838:1279,0x680818:719}
 if mm_bad:mm[mm_bad[0]]=mm_bad[1]
 def access(uc,kind,addr,width,value,_):
  off=addr-GPU;assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  if kind==u.UC_MEM_WRITE:
   if off in sels:assert width==1;sels[off]=value
   elif off==0xc03c5:
    assert width==1 and sels[0xc03c4]==1 and value in (1,0x21);sw.append(value);state['seq']=value
   else:
    assert off==0x680630 and width==4,('forbidden GPU data write',hex(off),width,value)
    assert value==[2,3][len(mw)];mw.append((off,value));state['nmm']+=1
    if not (fault=='drop2' and value==2 or fault=='restore630' and value==3):mm[off]=value
    if fault=='wide2' and value==2:mm[off]=0x10002
   return
  if off in sels:assert width==1;value=sels[off]
  elif off==0xc03c5:
   assert width==1 and sels[0xc03c4]==1;value=state['seq']
   if fault=='blank' and state['gate']==5:value=1
   if fault=='restore_seq' and state['gate']==4:value=0x21
  elif off==0x6013d5:
   assert width==1 and sels[0x6013d4] in cr;i=sels[0x6013d4];value=cr[i]
   if state['gate']==4 and fault=='restore_cr'+str(i):value^=1
   if i==0x1b:
    if behavior=='coupled':value=5 if mm[0x680630]==2 else value
    if behavior=='blank':value=5 if state['gate']==5 else value
    if behavior=='late' and state['nmm'] and (state['gate']!=4 or state['after_output_reads']<4):value=5
    if state['gate']==4:
     if behavior=='oscillate' and state['after_output_reads'] in (2,4,6):value=5
     if fault=='restore1b':value=5
     state['after_output_reads']+=1
    samples.append((mm[0x680630],value))
  else:
   assert width==4 and off in mm;value=mm[off]
   if off==0x680630 and fault=='postblank630' and state['gate']==5 and not mw:value=2
  uc.mem_write(addr,value.to_bytes(width,'little'))
 def pin(uc,port,width,_):
  assert width==4
  if port==0xcf8:trace.append(['read',port]);return state['selector']
  if port==0xcfc:trace.append(['read',port,state['selector']]);return pci[state['selector']]
  assert port==0x8008;n=state['ticks'];state['ticks']+=1
  start=0xfffffff0 if timer=='wrap' else 0x1000;step={'normal':200,'wrap':200,'stall':0,'backwards':-1,'jump':33751,'minimum':1688,'maximum':33750}[timer]
  return (start+n*step)&0xffffffff
 def pout(uc,port,width,value,_):
  if port==0x80d3:
   assert width==1 and value==[5,4][len(outs)];outs.append(value);state['gate']=value
   return
  assert port==0xcf8 and width==4;trace.append(['write',port,value]);state['selector']=value
 def ramwrite(uc,kind,addr,size,value,_):
  if GPU<=addr<GPU+0x800000:return
  assert (base+0x880<=addr and addr+size<=base+0x900) or (op<=addr and addr+size<=op+172) or (base+0x6000<=addr and addr+size<=sp) or (FB<=addr and addr+size<=FB+SIZE),('outside admitted writes',hex(addr),size)
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,GPU,GPU+0x7fffff)
 c.hook_add(u.UC_HOOK_MEM_WRITE,ramwrite);c.hook_add(u.UC_HOOK_INSN,pin,None,1,0,x.UC_X86_INS_IN);c.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
 start=base+sy['bridge_post']
 if direct:
  args=[base+0x5000,GPU,FB,op]
  if badarg is not None:args[badarg]=0
  c.reg_write(x.UC_X86_REG_ESP,sp-20);c.mem_write(sp-20,pack(end,*args));start=struct.unpack_from('<I',page,0x850)[0]
 c.emu_start(start,end,timeout=10000000,count=50000000)
 assert c.reg_read(x.UC_X86_REG_EIP)==end,(name,'execution bound')
 assert c.reg_read(x.UC_X86_REG_ESP)==(sp-16 if direct else sp) and c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
 assert sels==original_sels
 final=bytes(c.mem_read(base,32768));v=list(struct.unpack_from('<43I',final,0x5100))
 assert state['nmm']==nmm,(name,state)
 assert mw==[(0x680630,v) for v in (2,3)][:nmm]
 assert sw in ([],[0x21,1]) and outs in ([],[5,4])
 for lo,hi in [(0,0x880),(0x900,0x5100),(0x51ac,0x6000)]:assert final[lo:hi]==initial[lo:hi]
 for pointer in (base-4096,base+32768):assert bytes(c.mem_read(pointer,4096))==b'G'*4096
 for pointer in (FB-4096,FB+SIZE):assert bytes(c.mem_read(pointer,4096))==b'Z'*4096
 if not refusal:
  assert (c.reg_read(x.UC_X86_REG_EAX) if direct else struct.unpack_from('<I',final,0x8d4)[0])==want,(name,hex(v[0]),hex(want))
  if badarg!=3:assert v[0]==want
  if want>=0x726:
   assert v[1]==nmm and v[2]==v[4] and not v[3]&0x200
  if nmm==2:
   # Independent explicit stage vectors; late samples are observations, not admission guesses.
   pairs=[(3,0x85),(3,0x85),(2,0x85),(3,0x85),(3,0x85),(3,0x85)]
   changes=0
   if behavior=='coupled':pairs[2]=(2,5)
   if behavior=='blank':pairs[1:4]=[(3,5),(2,5),(3,5)]
   if behavior=='late':pairs[2:5]=[(2,5),(3,5),(3,5)];changes=1
   if behavior=='oscillate':changes=6
   if fault=='drop2':pairs[2]=(3,0x85)
   if fault=='wide2':pairs[2]=(0x10002,0x85)
   if fault=='restore630':pairs[3:]=[(2,0x85)]*3
   if fault=='restore1b':pairs[4:]=[(3,5)]*2
   assert v[20:26]==[a for a,b in pairs] and v[26:32]==[b for a,b in pairs],(name,v[20:32],pairs)
   assert v[32:38]==[(a<<16)|b if a<=0xffff else 0xffffffff for a,b in pairs]
   assert v[38:40]==[32,changes]
  if want==0x726:assert v[18:20]==[1,1]
  if want>=0x726:assert v[42]==v[18]|(v[19]<<1)|((v[38]==32 and v[39]==0)<<2)|(v[38]<<8)|(v[1]<<16)
 expected_image=bytearray(b'Z'*SIZE)
 if not direct:
  expected_trace=[['read',0xcf8]]
  for sel in SELECT:expected_trace.extend([['write',0xcf8,sel],['read',0xcfc,sel]])
  expected_trace.append(['write',0xcf8,0x12345678]);assert trace==expected_trace and state['selector']==0x12345678
  phase=2 if refusal else 4;stage=refusal if refusal else 5
  assert struct.unpack_from('<I',final,0x880)[0]==phase and struct.unpack_from('<I',final,0x8d0)[0]==stage
  color={1:0xff0000,2:0xffff00,3:0xff00ff,4:0xff8000,5:0xffffff}[refusal] if refusal else 0x00ff00 if want==0x726 else 0xff8000
  for row0,rgb in [(8,0x00ff00),(48,color)]:
   for row in range(row0,row0+32):expected_image[row*5120+32:row*5120+5088]=pack(rgb)*1264
  words=[0x7260000d,phase,stage,0 if refusal else want,v[1],*v[32:38],v[39],v[42]]
  paint_report(expected_image,words)
 else:assert not trace and not state['ticks']
 assert bytes(c.mem_read(FB,SIZE))==expected_image
 R['cases'].append({'name':name,'layout':layout,'return':want,'refusal':refusal,'MMIO_writes':mw,'CRTC_data_writes':0,'sample_reads':samples,'raw_result':v,'all_pixels_and_guards_exact':True})
try:
 for layout in ('dual','relocated'):run('constant-'+layout,layout)
 for behavior in ('coupled','blank','late','oscillate'):run('behavior-'+behavior,behavior=behavior)
 for a,val in [(0x1b,5),(0x22,255),(0x19,0x50)]:run('baseline-cr'+hex(a),want=5 if a==0x19 else 0x7262,nmm=0,cr_bad=(a,val))
 run('baseline630',want=0x7262,nmm=0,mm_bad=(0x680630,2))
 run('baseline-seq',want=0x7262,nmm=0,seq=0)
 for fault,want,count in [('blank',0x7263,0),('postblank630',0x7263,0),('restore630',0x7265,2),('restore_seq',0x7265,2),('restore1b',0x7265,2),('drop2',0x7268,2),('wide2',0x7268,2)]:run(fault,want=want,nmm=count,fault=fault)
 for i in (0x11,0x22,0x19):run('restore-cr'+hex(i),want=0x7265,fault='restore_cr'+str(i))
 for stage,sel,val in [(1,SELECT[0],0),(1,SELECT[1],0),(1,SELECT[2],0),(2,SELECT[3],0),(2,SELECT[4],0),(2,SELECT[5],0),(3,SELECT[6],0),(3,SELECT[7],0),(3,SELECT[8],0x8001),(3,SELECT[9],0)]:run('pci-'+hex(sel),refusal=stage,pci_bad=(sel,val),nmm=0)
 for timer in ('stall','backwards','jump'):run('timer-'+timer,refusal=5,timer=timer,nmm=0)
 for timer in ('wrap','minimum','maximum'):run('timer-'+timer,timer=timer)
 for arg in range(4):run('null-'+str(arg),want=2,nmm=0,direct=True,badarg=arg)
 run('IF-refusal',want=4,nmm=0,direct=True,flags=0x202)
 run('PAE-refusal',want=0x7261,nmm=0,direct=True,cpu4=0x20)
 run('wrapper-baseline',want=5,nmm=0,mm_bad=(0x680508,0))
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:R['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,indent=2)+'\n')
print('PASS relocated726 integration cases',len(R['cases']))

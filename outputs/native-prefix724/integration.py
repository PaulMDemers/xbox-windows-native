"""Exact relocated724 bridge/prefix with independent MMIO and optical models.
Starts at post-paging transition; diskless CPU fixtures separately test transition.
No hardware/caching semantics proof and no closed runtime reused.
"""
import datetime,hashlib,json,os,struct,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn724/host001')
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K))
from optical_oracle import paint_report
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
out=K/'integration001.json';assert not out.exists()
b=json.loads((K/'host001.json').read_text());assert b['passed']
for n,h in b['sources'].items():assert sha(K/n)==h
for n,h in b['files'].items():assert sha(P/n)==h
sy=b['bridge_symbols'];FB=0x3000000;SIZE=3686400;GPU=0xfd000000
SELECT=[0x80010000,0x80010004,0x80010010,0x80000900,0x80000904,0x80000914,0x80000800,0x80000804,0x80000810,0x80000884]
VALUES=[0x02a010de,2,0xfd000000,0x01b410de,1,0xc001,0x01b210de,1,0,0x8001]
SETUP=[(0x680884,0),(0x680888,0),(0x68088c,0x10001000),(0x680890,0x10000000),(0x680894,0x10000000),(0x680898,0x10000000),(0x68089c,0x10000000),(0x680880,0x21101100),(0x680630,2),(0x68084c,0x00801080),(0x6808c4,0x40801080)]
CS=[(0x14,0),(0x17,0xe3),(0x19,0x10),(0x1b,5)]
R={'passed':False,'scope':__doc__,'physical_access':False,'harness_sha256':sha(Path(__file__)),'cases':[]};deadline=time.monotonic()+420
def run(name,layout='dual',want=0x724,nmm=11,ncr=4,first=0xffffffff,read_fault=0,refusal=0,pci_bad=None,timer='normal',cr_bad=None,mm_bad=None,fault='',direct=False,badarg=None,flags=2,cpu4=0):
 assert time.monotonic()<deadline
 page=(P/layout/'page.bin').read_bytes();base=struct.unpack_from('<I',page,0x844)[0];sp=base+0x8000;op=base+0x5100;end=base+sy['bridge_hold']
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(base-4096,40960);c.mem_write(base-4096,b'G'*40960);c.mem_write(base,page)
 c.mem_map(FB-4096,SIZE+8192);c.mem_write(FB-4096,b'Z'*(SIZE+8192));c.mem_map(GPU,0x800000)
 initial=bytes(c.mem_read(base,32768));c.reg_write(x.UC_X86_REG_GDTR,(0,base+0x800,31,0));c.reg_write(x.UC_X86_REG_CR0,0x40000011);c.reg_write(x.UC_X86_REG_CR4,cpu4)
 for reg,val in [(x.UC_X86_REG_CS,0x10),(x.UC_X86_REG_DS,0x18),(x.UC_X86_REG_ES,0x18),(x.UC_X86_REG_SS,0x18)]:c.reg_write(reg,val)
 c.reg_write(x.UC_X86_REG_EBP,base);c.reg_write(x.UC_X86_REG_ESP,sp);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 pci=dict(zip(SELECT,VALUES))
 if pci_bad:pci[pci_bad[0]]=pci_bad[1]
 state={'selector':0x12345678,'ticks':0,'seq':1,'gate':0,'nmm':0,'ncr':0,'pending':None,'unlocked':False};trace=[];mw=[];cw=[];sw=[];outs=[]
 cr={9:0x25,0x11:9,0x21:255,0x44:0,0x39:255,0x13:0x80,0x19:0x51,0x25:0x10,0x28:0x83,0x2d:0xe0,0x1b:0x85,0x14:0,0x17:0xe3,0x22:0xfe,0x1f:3}
 if cr_bad:cr[cr_bad[0]]=cr_bad[1]
 sels={0x6013d4:0x67,0xc03c4:0x72,0xc03ce:0x91};original_sels=sels.copy()
 mm={a:(3 if a==0x680630 else v) for a,v in SETUP}
 mm.update({0x680508:0x3c20d,0x68050c:0x100a0400,0x100200:0x3070003,0x600804:3,0x600800:FB,0x680838:1279,0x680818:719})
 if mm_bad:mm[mm_bad[0]]=mm_bad[1]
 def access(uc,kind,addr,width,value,_):
  off=addr-GPU;assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  if kind==u.UC_MEM_WRITE:
   if off in sels:assert width==1;sels[off]=value
   elif off==0xc03c5:
    assert width==1 and sels[0xc03c4]==1 and value in (1,0x21);sw.append(value);state['seq']=value
   elif off==0x6013d5:
    assert width==1;i=sels[0x6013d4];cw.append((i,value))
    if i==0x1f:assert value==0x57 and not state['unlocked'];state['unlocked']=True
    elif i==0x19 and value==0x51:
     assert state['ncr']>=3
     if fault!='restore_cr19':cr[i]=value
    else:
     assert state['nmm']==11 and (i,value)==CS[state['ncr']];state['ncr']+=1
     if fault!='drop_cr'+str(i):cr[i]=value
     if read_fault==100+state['ncr']:state['pending']=off
   else:
    assert width==4
    mw.append((off,value))
    if off==0x680630 and value==3:
     assert state['nmm']>=9
     if fault!='restore630':mm[off]=value
    else:
     assert (off,value)==SETUP[state['nmm']];state['nmm']+=1
     if fault!='drop_mm'+str(state['nmm']):mm[off]=value
     if read_fault==state['nmm']:state['pending']=off
   return
  if off in sels:
   assert width==1;value=sels[off]
   if off==0x6013d4 and fault=='selector' and state['gate']==4 and value==0x1f:value^=1
  elif off==0xc03c5:
   assert width==1 and sels[0xc03c4]==1;value=state['seq']
   if fault=='blank' and state['gate']==5:value=1
   if fault=='restore_seq' and state['gate']==4:value=0x21
  elif off==0x6013d5:
   assert width==1 and sels[0x6013d4] in cr;value=cr[sels[0x6013d4]]
   if fault=='unlock11' and state['unlocked'] and sels[0x6013d4]==0x11:value=0x89
  else:assert width==4 and off in mm;value=mm[off]
  if state['pending']==off:value^=1;state['pending']=None
  uc.mem_write(addr,value.to_bytes(width,'little'))
 def pin(uc,port,width,_):
  assert width==4
  if port==0xcf8:trace.append(['read',port]);return state['selector']
  if port==0xcfc:trace.append(['read',port,state['selector']]);return pci[state['selector']]
  assert port==0x8008;n=state['ticks'];state['ticks']+=1
  start=0xfffffff0 if timer=='wrap' else 0x1000;step={'normal':200,'wrap':200,'stall':0,'backwards':-1,'jump':33751,'minimum':1688,'maximum':33750}[timer]
  return (start+n*step)&0xffffffff
 def pout(uc,port,width,value,_):
  if port==0x80d3:assert width==1 and value==[5,4][len(outs)];outs.append(value);state['gate']=value;return
  assert port==0xcf8 and width==4;trace.append(['write',port,value]);state['selector']=value
 def ramwrite(uc,kind,addr,size,value,_):
  if GPU<=addr<GPU+0x800000:return
  assert (base+0x880<=addr and addr+size<=base+0x900) or (op<=addr and addr+size<=op+272) or (base+0x6000<=addr and addr+size<=sp) or (FB<=addr and addr+size<=FB+SIZE),('outside admitted writes',hex(addr),size)
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
 final=bytes(c.mem_read(base,32768));v=list(struct.unpack_from('<68I',final,0x5100))
 assert state['nmm']==nmm and state['ncr']==ncr,(name,state)
 assert mw==SETUP[:nmm]+([(0x680630,3)] if nmm>=9 else [])
 assert cw==([(0x1f,0x57)] if state['unlocked'] else [])+CS[:ncr]+([(0x19,0x51)] if ncr>=3 else [])
 assert sw in ([],[0x21,1]) and outs in ([],[5,4])
 for lo,hi in [(0,0x880),(0x900,0x5100),(0x5210,0x6000)]:assert final[lo:hi]==initial[lo:hi]
 for pointer in (base-4096,base+32768):assert bytes(c.mem_read(pointer,4096))==b'G'*4096
 for pointer in (FB-4096,FB+SIZE):assert bytes(c.mem_read(pointer,4096))==b'Z'*4096
 if not refusal:
  assert (c.reg_read(x.UC_X86_REG_EAX) if direct else struct.unpack_from('<I',final,0x8d4)[0])==want
  if badarg!=3:assert v[0]==want
  if want>=0x724:
   assert v[1:4]==[nmm,ncr,first] and v[4]==v[6] and not v[5]&0x200
  if want==0x724:
   assert v[19:21]==[1,1] and v[32:43]==[a[1] for a in SETUP]
   assert v[58:62]==[0,0xe3,0x10,5] and v[62:66]==[0,0xe3,0x51,5] and v[16:18]==[0xfe,0xfe]
  if first!=0xffffffff:
   expected=SETUP[first-1][1] if first<100 else CS[first-101][1]
   assert v[67]==expected and v[66]!=expected
 expected_image=bytearray(b'Z'*SIZE)
 if not direct:
  expected_trace=[['read',0xcf8]]
  for sel in SELECT:expected_trace.extend([['write',0xcf8,sel],['read',0xcfc,sel]])
  expected_trace.append(['write',0xcf8,0x12345678]);assert trace==expected_trace and state['selector']==0x12345678
  phase=2 if refusal else 4;stage=refusal if refusal else 5
  assert struct.unpack_from('<I',final,0x880)[0]==phase and struct.unpack_from('<I',final,0x8d0)[0]==stage
  color={1:0xff0000,2:0xffff00,3:0xff00ff,4:0xff8000,5:0xffffff}[refusal] if refusal else 0x00ff00 if want==0x724 else 0xff8000
  for row0,rgb in [(8,0x00ff00),(48,color)]:
   for row in range(row0,row0+32):expected_image[row*5120+32:row*5120+5088]=pack(rgb)*1264
  words=[0x7240000d,phase,stage,0 if refusal else want,v[1],v[2],v[3],v[66],v[67],v[20],v[64],v[65],v[17]]
  if want==0x724 and not refusal:assert words==[0x7240000d,4,5,0x724,11,4,0xffffffff,0xffffffff,0xffffffff,1,0x51,5,0xfe]
  paint_report(expected_image,words)
 else:assert not trace and not state['ticks']
 assert bytes(c.mem_read(FB,SIZE))==expected_image
 R['cases'].append({'name':name,'layout':layout,'return':want,'refusal':refusal,'MMIO_writes':mw,'CRTC_writes':cw,'raw_result':v,'all_pixels_and_guards_exact':True})
try:
 for layout in ('dual','relocated'):run('prefix-'+layout,layout)
 for i in range(1,12):run('mmio-read-mismatch'+str(i),want=0x7248,nmm=i,ncr=0,first=i,read_fault=i)
 for i in range(1,5):run('crtc-read-mismatch'+str(i),want=0x7248,ncr=i,first=100+i,read_fault=100+i)
 for a,val in [(0x1b,5),(0x22,255),(0x14,1),(0x17,0xe2)]:run('baseline-cr'+hex(a),want=0x7242,nmm=0,ncr=0,cr_bad=(a,val))
 for a,val in [(0x680884,1),(0x680630,2)]:run('baseline-mm'+hex(a),want=0x7242,nmm=0,ncr=0,mm_bad=(a,val))
 for fault,want,mm,cr in [('blank',0x7243,0,0),('unlock11',0x7245,0,0),('restore630',0x7245,11,4),('restore_cr19',0x7245,11,4),('restore_seq',0x7245,11,4)]:run(fault,want=want,nmm=mm,ncr=cr,fault=fault)
 run('dropped630',want=0x7248,nmm=9,ncr=0,first=9,fault='drop_mm9')
 run('droppedCR19',want=0x7248,ncr=3,first=103,fault='drop_cr25')
 run('droppedCR1b',want=0x7245,first=104,fault='drop_cr27')
 for stage,sel,val in [(1,SELECT[0],0),(1,SELECT[1],0),(1,SELECT[2],0),(2,SELECT[3],0),(2,SELECT[4],0),(2,SELECT[5],0),(3,SELECT[6],0),(3,SELECT[7],0),(3,SELECT[8],0x8001),(3,SELECT[9],0)]:run('pci-'+hex(sel),refusal=stage,pci_bad=(sel,val),nmm=0,ncr=0)
 for timer in ('stall','backwards','jump'):run('timer-'+timer,refusal=5,timer=timer,nmm=0,ncr=0)
 for timer in ('wrap','minimum','maximum'):run('timer-'+timer,timer=timer)
 for arg in range(4):run('null-'+str(arg),want=2,nmm=0,ncr=0,direct=True,badarg=arg)
 run('IF-refusal',want=4,nmm=0,ncr=0,direct=True,flags=0x202)
 run('PAE-refusal',want=0x7241,nmm=0,ncr=0,direct=True,cpu4=0x20)
 run('wrapper-baseline',want=5,nmm=0,ncr=0,mm_bad=(0x680508,0))
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:R['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,indent=2)+'\n')
print('PASS relocated724 integration cases',len(R['cases']))

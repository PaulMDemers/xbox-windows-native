"""Exact relocated752 bridge/prefix with independent MMIO and optical models.
Starts at post-paging transition; diskless CPU fixtures separately test transition.
No hardware/caching semantics proof and no closed runtime reused.
"""
import datetime,hashlib,json,os,struct,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn752/host001')
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K))
from optical_oracle import paint_report
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
out=K/'integration003.json';assert not out.exists()
b=json.loads((K/'host001.json').read_text());assert b['passed']
for n,h in b['sources'].items():assert sha(K/n)==h
for n,h in b['files'].items():assert sha(P/n)==h
sy=b['bridge_symbols'];FB=0x3000000;SIZE=3686400;GPU=0xfd000000
SELECT=[0x80010000,0x80010004,0x80010010,0x80000900,0x80000904,0x80000914,0x80000800,0x80000804,0x80000810,0x80000884]
VALUES=[0x02a010de,2,0xfd000000,0x01b410de,1,0xc001,0x01b210de,1,0,0x8001]
SETUP=[(0x680884,0),(0x680888,0),(0x68088c,0x10001000),(0x680890,0x10000000),(0x680894,0x10000000),(0x680898,0x10000000),(0x68089c,0x10000000),(0x680880,0x21101100),(0x680630,2),(0x68084c,0x00801080),(0x6808c4,0x40801080)]
H=[(0x680820,719),(0x680824,779),(0x680828,719),(0x680834,0),(0x68082c,738),(0x680830,770),(0x680838,719)]
HB=[1279,1649,1279,0,1389,1429,1279]
CS=[(0x14,0),(0x17,0xe3),(0x19,0x10),(0x1b,0x85)]
R={'passed':False,'scope':__doc__,'physical_access':False,'harness_sha256':sha(Path(__file__)),'cases':[]};deadline=time.monotonic()+420
def run(name,layout='dual',want=0x752,nmm=11,ncr=3,first=0xffffffff,read_fault=0,refusal=0,pci_bad=None,timer='normal',cr_bad=None,mm_bad=None,fault='',direct=False,badarg=None,flags=2,cpu4=0):
 assert time.monotonic()<deadline
 page=(P/layout/'page.bin').read_bytes();base=struct.unpack_from('<I',page,0x844)[0];sp=base+0x8000;op=base+0x5100;end=base+sy['bridge_hold']
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(base-4096,40960);c.mem_write(base-4096,b'G'*40960);c.mem_write(base,page)
 c.mem_map(FB-4096,SIZE+8192);c.mem_write(FB-4096,b'Z'*(SIZE+8192));c.mem_map(GPU,0x800000)
 initial=bytes(c.mem_read(base,32768));c.reg_write(x.UC_X86_REG_GDTR,(0,base+0x800,31,0));c.reg_write(x.UC_X86_REG_CR0,0x40000011);c.reg_write(x.UC_X86_REG_CR4,cpu4)
 for reg,val in [(x.UC_X86_REG_CS,0x10),(x.UC_X86_REG_DS,0x18),(x.UC_X86_REG_ES,0x18),(x.UC_X86_REG_SS,0x18)]:c.reg_write(reg,val)
 c.reg_write(x.UC_X86_REG_EBP,base);c.reg_write(x.UC_X86_REG_ESP,sp);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 pci=dict(zip(SELECT,VALUES))
 if pci_bad:pci[pci_bad[0]]=pci_bad[1]
 state={'c2writes':0,'c0writes':0,'c5writes':0,'c4writes':0,'selector':0x12345678,'ticks':0,'seq':1,'gate':0,'nmm':0,'ncr':0,'pending':None,'unlocked':False,'recovering':False};trace=[];mw=[];cw=[];sw=[];outs=[];checked=[]
 cr={2:0x9f,0:0xc8,4:0xa7,5:0x31,9:0x25,0x11:9,0x21:255,0x44:0,0x39:255,0x13:0x80,0x19:0x51,0x25:0x10,0x28:0x83,0x2d:0xe0,0x1b:0x85,0x14:0,0x17:0xe3,0x22:0xfe,0x1f:3,0x33:0x11}
 if cr_bad:cr[cr_bad[0]]=cr_bad[1]
 sels={0x6013d4:0x67,0xc03c4:0x72,0xc03ce:0x91};original_sels=sels.copy()
 mm={a:(3 if a==0x680630 else v) for a,v in SETUP}
 mm.update({0x680508:0x3c20d,0x68050c:0x100a0400,0x100200:0x3070003,0x600804:3,0x600800:FB,0x680838:1279,0x680818:719})
 mm.update(dict(zip([a for a,_ in H],HB)));hw={a:0 for a,_ in H};htrace=[];hrestore=[]
 if mm_bad:mm[mm_bad[0]]=mm_bad[1]
 def access(uc,kind,addr,width,value,_):
  off=addr-GPU;assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  if kind==u.UC_MEM_WRITE:
   if off in sels:assert width==1;sels[off]=value
   elif off==0xc03c5:
    assert width==1 and sels[0xc03c4]==1 and value in (1,0x21);sw.append(value);state['seq']=value
   elif off==0x6013d5:
    assert width==1;i=sels[0x6013d4];cw.append((i,value))
    if i==2:
     state['c2writes']+=1;assert state['c2writes']<=2
     assert value==(0x59 if state['c2writes']==1 else 0x9f)
     assert state['seq']==0x21 and state['gate']==5 and state['c4writes']==1 and state['c5writes']==1 and state['c0writes']==1 and not hrestore
     assert struct.unpack('<I',uc.mem_read(op+504,4))[0]==1 and not cr[0x11]&0x80
     if fault==('c2-drop-write' if state['c2writes']==1 else 'c2-drop-restore'):return
     cr[2]=value
     for idx2 in [0,4,5]:
      if state['c2writes']==1 and fault=='c2-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==0:
     state['c0writes']+=1;assert state['c0writes']<=2
     if state['c0writes']==2:assert state['c2writes']==2*struct.unpack('<I',uc.mem_read(op+504,4))[0]
     assert value==(0x5c if state['c0writes']==1 else 0xc8)
     assert state['seq']==0x21 and state['gate']==5 and state['c4writes']==1 and state['c5writes']==1 and not hrestore
     assert struct.unpack('<I',uc.mem_read(op+472,4))[0]==1 and not cr[0x11]&0x80
     if fault==('c0-drop-write' if state['c0writes']==1 else 'c0-drop-restore'):return
     cr[0]=value
     if state['c0writes']==1 and fault=='c0-c4-coupling':cr[4]^=1
     if state['c0writes']==1 and fault=='c0-c5-coupling':cr[5]^=1
    elif i==5:
     state['c5writes']+=1;assert state['c5writes']<=2
     if state['c5writes']==2:assert state['c0writes']==2*struct.unpack('<I',uc.mem_read(op+472,4))[0]
     assert value==(0x3e if state['c5writes']==1 else 0x31)
     assert state['seq']==0x21 and state['gate']==5 and state['c4writes']==1 and not hrestore
     assert struct.unpack('<I',uc.mem_read(op+452,4))[0]==1
     if fault==('c5-drop-write' if state['c5writes']==1 else 'c5-drop-restore'):return
     cr[5]=value
     if state['c5writes']==1 and fault=='c4-coupling':cr[4]^=1
    elif i==4:
     state['c4writes']+=1;assert state['c4writes']<=2
     if state['c4writes']==2:assert state['c5writes']==2*struct.unpack('<I',uc.mem_read(op+452,4))[0]
     assert value==(93 if state['c4writes']==1 else 0xa7)
     assert state['seq']==0x21 and state['gate']==5 and state['ncr']==3 and not hrestore
     assert list(struct.unpack('<3I',uc.mem_read(op+388,12)))==[7,7,0xffffffff]
     if fault==('c4-write' if state['c4writes']==1 else 'c4-restore-write'):return
     cr[4]=value
     if state['c4writes']==1 and fault=='c5-coupling':cr[5]^=1
    elif i==0x1f:assert value==0x57 and not state['unlocked'];state['unlocked']=True
    elif i==0x19 and value==0x51:
     state['recovering']=True
     assert state['ncr']>=3
     if fault!='restore_cr19':cr[i]=value
    else:
     assert state['nmm']==11 and (i,value)==CS[state['ncr']];state['ncr']+=1
     if fault!='drop_cr'+str(i):cr[i]=value
   elif off in dict(H):
    assert width==4;n=[a for a,_ in H].index(off);hw[off]+=1;assert hw[off]<=2
    assert value==(H[n][1] if hw[off]==1 else HB[n]) and state['seq']==0x21 and state['gate']==5
    htrace.append((off,value))
    if hw[off]==2:hrestore.append(n)
    if fault!=('h-drop-' if hw[off]==1 else 'h-restore-')+str(n):mm[off]=value
   else:
    assert width==4
    mw.append((off,value))
    if off==0x680630 and value==3:
     state['recovering']=True
     assert state['nmm']>=9
     if fault!='restore630':mm[off]=value
    else:
     assert (off,value)==SETUP[state['nmm']];state['nmm']+=1
     if fault!='drop_mm'+str(state['nmm']):mm[off]=value
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
   i=sels[0x6013d4]
   if i==2 and state['c2writes']==1 and fault=='c2-read':value^=1
   if i==2 and state['c2writes']==2 and fault=='c2-restore-read':value^=1
   if i in [0,4,5] and state['c2writes']==1 and fault=='c'+str(i)+'-after-c2-read':value^=1
   if i==0 and state['c0writes']==1 and fault=='c0-read':value^=1
   if i==0 and state['c0writes']==2 and fault=='c0-restore-read':value^=1
   if i==4 and state['c0writes']==1 and fault=='c4-after-c0-read':value^=1
   if i==5 and state['c0writes']==1 and fault=='c5-after-c0-read':value^=1
   if i==4 and state['c4writes']==1 and fault=='c4-read':value^=1
   if i==4 and state['c5writes']==1 and fault=='c4-after-read':value^=1
   if i==5 and state['c5writes']==1 and fault=='c5-low-read':value^=1
   if i==5 and state['c5writes']==1 and fault=='c5-high-read':value^=0x80
   if i==4 and state['c4writes']==2 and fault=='c4-restore-read':value^=1
   if i==5 and state['c4writes']==1 and fault=='c5-read':value^=1
   if i==5 and state['c4writes']==2 and fault=='c5-restore-read':value^=1
   if fault=='unlock11' and state['unlocked'] and sels[0x6013d4]==0x11:value=0x89
  elif off==0xc03cf:
   assert width==1 and sels[0xc03ce]==4;value=0
  else:assert width==4 and off in mm;value=mm[off]
  if struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x7528 and not state['recovering']:
   ix=next((n for n,(a,_) in enumerate(SETUP) if a==off),None)
   if off==0x6013d5:ix=next((11+n for n,(a,_) in enumerate(CS) if a==sels[0x6013d4]),None)
   if ix is not None:
    assert state['nmm']==11 and state['ncr']==3
    if read_fault==ix+1:value^=1
    if fault=='cr1b05' and ix==14:value=5
    checked.append([ix,value])
  if off in dict(H):
   n=[a for a,_ in H].index(off)
   if struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x7529 and not hrestore and fault=='h-read-'+str(n):value^=1
   if hrestore and fault=='h-cleanup-'+str(n):value^=1
  uc.mem_write(addr,value.to_bytes(width,'little'))
 def pin(uc,port,width,_):
  assert width==4
  if port==0xcf8:trace.append(['read',port]);return state['selector']
  if port==0xcfc:trace.append(['read',port,state['selector']]);return pci[state['selector']]
  assert port==0x8008;n=state['ticks'];state['ticks']+=1
  start=0xfffffff0 if timer=='wrap' else 0x1000;step={'normal':200,'wrap':200,'stall':0,'backwards':-1,'jump':33752,'minimum':1688,'maximum':33750}[timer]
  return (start+n*step)&0xffffffff
 def pout(uc,port,width,value,_):
  if port==0x80d3:
   assert width==1 and value==[5,4][len(outs)]
   if value==4:
    assert struct.unpack('<I',uc.mem_read(op+516,4))[0]==0 and cr[2]==0x9f
    assert struct.unpack('<I',uc.mem_read(op+484,4))[0]==0 and cr[0]==0xc8
    assert struct.unpack('<I',uc.mem_read(op+432,4))[0]==0 and cr[4]==0xa7 and cr[5]==0x31
    assert struct.unpack('<I',uc.mem_read(op+400,4))[0]==0
    assert [mm[a] for a,_ in H]==HB and list(struct.unpack('<7I',uc.mem_read(op+360,28)))==HB
   outs.append(value);state['gate']=value;return
  assert port==0xcf8 and width==4;trace.append(['write',port,value]);state['selector']=value
 def ramwrite(uc,kind,addr,size,value,_):
  if GPU<=addr<GPU+0x800000:return
  assert (base+0x880<=addr and addr+size<=base+0x900) or (op<=addr and addr+size<=op+532) or (base+0x6000<=addr and addr+size<=sp) or (FB<=addr and addr+size<=FB+SIZE),('outside admitted writes',hex(addr),size)
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
 final=bytes(c.mem_read(base,32768));v=list(struct.unpack_from('<133I',final,0x5100))
 assert state['nmm']==nmm and state['ncr']==ncr,(name,state)
 assert mw==SETUP[:nmm]+([(0x680630,3)] if nmm>=9 else [])
 assert cw==([(0x1f,0x57)] if state['unlocked'] else [])+CS[:ncr]+([(4,93)]+([(5,0x3e)]+([(0,0x5c)]+([(2,0x59),(2,0x9f)] if state['c2writes'] else [])+[(0,0xc8)] if state['c0writes'] else [])+[(5,0x31)] if state['c5writes'] else [])+[(4,0xa7)] if state['c4writes'] else [])+([(0x19,0x51)] if ncr>=3 else [])
 assert sw in ([],[0x21,1],[0x21]) and outs in ([],[5,4],[5])
 if htrace:
  assert len(htrace)==14 and htrace==H+[(H[i][0],HB[i]) for i in range(6,-1,-1)]
  assert hrestore==list(range(6,-1,-1))
  if fault.startswith(('h-restore-','h-cleanup-')):assert sw==[0x21] and outs==[5] and v[100]!=0 and v[101]==0
  elif fault in ['c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling','c5-drop-restore']:assert sw==[0x21] and outs==[5] and v[108]!=0 and v[101]==0
  elif fault in ['c0-restore-read','c0-drop-restore']:assert sw==[0x21] and outs==[5] and v[121]==1 and v[101]==0
  elif fault in ['c2-restore-read','c2-drop-restore']:assert sw==[0x21] and outs==[5] and v[129]==1 and v[101]==0
  else:assert v[100:102]==[0,1]
 if not refusal and want==0x752:assert v[83:90]==[b for _,b in H] and v[90:97]==HB and v[97:100]==[7,7,0xffffffff]
 if want==0x7529:
  hf=int(fault.rsplit('-',1)[1]);assert v[97:100]==[7,hf+1,hf] and v[83:83+hf]==[b for _,b in H[:hf]] and v[83+hf]!=H[hf][1] and v[84+hf:90]==[0xffffffff]*(6-hf)
 if state['c4writes']:
  assert state['c4writes']==2 and v[104]==0xa7 and v[107]==1 and v[109]==0x31
  assert v[105]==(92 if fault=='c4-read' else 0xa7 if fault=='c4-write' else 93)
  assert v[106]==(0xa6 if fault=='c4-restore-read' else 93 if fault=='c4-restore-write' else 0xa7)
  assert v[110]==(0x30 if fault in ['c5-read','c5-coupling'] else 0x31)
  assert v[111]==(0x3e if fault=='c5-drop-restore' else 0x30 if fault in ['c5-restore-read','c5-coupling'] else 0x31)
  assert v[108]==int(v[104]!=v[106])+2*int(v[109]!=v[111])
  assert (v[105]==93 and v[110]==0x31)==(v[1] in [0x752,0x752d,0x752e,0x75210])
 if state['c5writes']:
  assert state['c5writes']==2 and v[112:114]==[0x3e,1]
  assert v[114]==(0x31 if fault=='c5-drop-write' else 0x3f if fault=='c5-low-read' else 0xbe if fault=='c5-high-read' else 0x3e)
  assert v[115]==(92 if fault in ['c4-after-read','c4-coupling'] else 93)
 elif v[107]:assert v[112:116]==[0,0,0xffffffff,0xffffffff]
 if state['c0writes']:
  assert state['c0writes']==2 and v[116:119]==[0xc8,92,1]
  assert v[119]==(0xc8 if fault=='c0-drop-write' else 0x5d if fault=='c0-read' else 0x5c)
  assert v[120]==(0xc9 if fault=='c0-restore-read' else 0x5c if fault=='c0-drop-restore' else 0xc8)
  assert v[121]==int(v[120]!=v[116])
  assert v[122]==(92 if fault in ['c4-after-c0-read','c0-c4-coupling'] else 93)
  assert v[123]==(0x3f if fault in ['c5-after-c0-read','c0-c5-coupling'] else 0x3e)
 if state['c2writes']:
  assert state['c2writes']==2 and v[124:127]==[0x9f,89,1]
  assert v[127]==(0x9f if fault=='c2-drop-write' else 0x58 if fault=='c2-read' else 0x59)
  assert v[128]==(0x9e if fault=='c2-restore-read' else 0x59 if fault=='c2-drop-restore' else 0x9f)
  assert v[129]==int(v[128]!=v[124])
  for idx,n,target in [(0,130,0x5c),(4,131,93),(5,132,0x3e)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c2-read','c2-c'+str(idx)+'-coupling'] else target)
 for lo,hi in [(0,0x880),(0x900,0x5100),(0x5314,0x6000)]:assert final[lo:hi]==initial[lo:hi]
 for pointer in (base-4096,base+32768):assert bytes(c.mem_read(pointer,4096))==b'G'*4096
 for pointer in (FB-4096,FB+SIZE):assert bytes(c.mem_read(pointer,4096))==b'Z'*4096
 if not refusal:
  assert (c.reg_read(x.UC_X86_REG_EAX) if direct else struct.unpack_from('<I',final,0x8d4)[0])==want
  if badarg!=3:assert v[0]==want
  if want>=0x752:
   assert v[2:4]==[nmm,ncr] and v[4]==first
   assert v[8]==v[10] and not v[9]&0x200
  if nmm==11 and ncr==3:
   count=15 if first==0xffffffff else first+1
   assert v[7]==count and len(checked)==count
   assert [a for a,b in checked]==list(range(count))
   expected=[b for a,b in SETUP+CS]
   for i,value in checked:
    exp=expected[i]
    if i==first:exp^=0x80 if fault=='cr1b05' else 1
    assert value==exp,(name,i,value,exp)
   if first!=0xffffffff:assert v[5:7]==[expected[first],checked[-1][1]]
  if want==0x752:assert v[28:31]==[1,1,0] and v[1]==0x752
  if fault=='cr1b05':assert v[1]==0x7528 and v[28:31]==[1,1,0]
 expected_image=bytearray(b'Z'*SIZE)
 if not direct:
  expected_trace=[['read',0xcf8]]
  for sel in SELECT:expected_trace.extend([['write',0xcf8,sel],['read',0xcfc,sel]])
  expected_trace.append(['write',0xcf8,0x12345678]);assert trace==expected_trace and state['selector']==0x12345678
  phase=2 if refusal else 4;stage=refusal if refusal else 5
  assert struct.unpack_from('<I',final,0x880)[0]==phase and struct.unpack_from('<I',final,0x8d0)[0]==stage
  color={1:0xff0000,2:0xffff00,3:0xff00ff,4:0xff8000,5:0xffffff}[refusal] if refusal else 0x00ff00 if want==0x752 else 0xff8000
  for row0,rgb in [(8,0x00ff00),(48,color)]:
   for row in range(row0,row0+32):expected_image[row*5120+32:row*5120+5088]=pack(rgb)*1264
  words=[0x7520000d,0 if refusal else want,v[1],v[30],v[100],v[108],v[121],v[129],v[124],v[127],v[128],v[28],v[11]]
  paint_report(expected_image,words)
 else:assert not trace and not state['ticks']
 assert bytes(c.mem_read(FB,SIZE))==expected_image
 R['cases'].append({'name':name,'layout':layout,'return':want,'refusal':refusal,'MMIO_writes':mw,'horizontal_writes':htrace,'CRTC_writes':cw,'deferred_checks':checked,'raw_result':v,'all_pixels_and_guards_exact':True})
try:
 for layout in ('dual','relocated'):run('prefix-'+layout,layout)
 for i in range(15):run('first-mismatch-'+str(i),want=0x7528,first=i,read_fault=i+1)
 run('CR1b05-preservation-mismatch',want=0x7528,first=14,fault='cr1b05')
 for a,val in [(0x1b,5),(0x22,255),(0x14,1),(0x17,0xe2),(0x33,0)]:run('baseline-cr'+hex(a),want=0x7522,nmm=0,ncr=0,cr_bad=(a,val))
 for a,val in [(0x680884,1),(0x680630,2)]:run('baseline-mm'+hex(a),want=0x7522,nmm=0,ncr=0,mm_bad=(a,val))
 for fault,want,mm,cr in [('blank',0x7523,0,0),('unlock11',0x7525,0,0),('restore630',0x7525,11,3),('restore_cr19',0x7525,11,3),('restore_seq',0x7525,11,3)]:run(fault,want=want,nmm=mm,ncr=cr,fault=fault)
 for stage,sel,val in [(1,SELECT[0],0),(1,SELECT[1],0),(1,SELECT[2],0),(2,SELECT[3],0),(2,SELECT[4],0),(2,SELECT[5],0),(3,SELECT[6],0),(3,SELECT[7],0),(3,SELECT[8],0x8001),(3,SELECT[9],0)]:run('pci-'+hex(sel),refusal=stage,pci_bad=(sel,val),nmm=0,ncr=0)
 for timer in ('stall','backwards','jump'):run('timer-'+timer,refusal=5,timer=timer,nmm=0,ncr=0)
 for timer in ('wrap','minimum','maximum'):run('timer-'+timer,timer=timer)
 for arg in range(4):run('null-'+str(arg),want=2,nmm=0,ncr=0,direct=True,badarg=arg)
 run('IF-refusal',want=4,nmm=0,ncr=0,direct=True,flags=0x202)
 run('PAE-refusal',want=0x7521,nmm=0,ncr=0,direct=True,cpu4=0x20)
 run('wrapper-baseline',want=5,nmm=0,ncr=0,mm_bad=(0x680508,0))
 for a in [4,5]:run('CRTC-baseline-'+str(a),want=0x7522,nmm=0,ncr=0,cr_bad=(a,0))
 for fault in ['c4-read','c4-write','c5-read','c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling','c5-drop-restore']:
  want=0x752b if fault in ['c4-read','c4-write','c5-read'] else 0x752c
  run(fault,want=want,fault=fault)
 for fault in ['c5-drop-write','c5-low-read','c5-high-read','c4-after-read','c4-coupling']:run(fault,want=0x752d,fault=fault)
 run('CRTC-baseline-0',want=0x7522,nmm=0,ncr=0,cr_bad=(0,0))
 for fault in ['c0-read','c0-drop-write','c0-restore-read','c0-drop-restore','c4-after-c0-read','c5-after-c0-read','c0-c4-coupling','c0-c5-coupling']:run(fault,want=0x752f if fault in ['c0-restore-read','c0-drop-restore'] else 0x752e,fault=fault)
 run('CRTC-baseline-2',want=0x7522,nmm=0,ncr=0,cr_bad=(2,0))
 for fault in ['c2-read','c2-drop-write','c2-restore-read','c2-drop-restore','c0-after-c2-read','c4-after-c2-read','c5-after-c2-read','c2-c0-coupling','c2-c4-coupling','c2-c5-coupling']:run(fault,want=0x75211 if fault in ['c2-restore-read','c2-drop-restore'] else 0x75210,fault=fault)
 for n in range(7):
  run('horizontal-read-'+str(n),want=0x7529,fault='h-read-'+str(n))
  run('horizontal-cleanup-'+str(n),want=0x752a,fault='h-cleanup-'+str(n))
  if n!=3:
   run('horizontal-drop-'+str(n),want=0x7529,fault='h-drop-'+str(n))
   run('horizontal-restore-'+str(n),want=0x752a,fault='h-restore-'+str(n))
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:R['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,indent=2)+'\n')
print('PASS relocated752 integration cases',len(R['cases']))

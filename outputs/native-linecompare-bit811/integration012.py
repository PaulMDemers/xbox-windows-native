"""Exact relocated811 bridge/prefix with independent MMIO and optical models.
Starts at post-paging transition; diskless CPU fixtures separately test transition.
No hardware/caching semantics proof and no closed runtime reused.
"""
import datetime,hashlib,json,os,struct,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn811/host007')
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K))
from optical_oracle import paint_report
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
out=K/'integration010.json';assert not out.exists()
b=json.loads((K/'host007.json').read_text());assert b['passed']
for n,h in b['sources'].items():assert sha(K/n)==h
for n,h in b['files'].items():assert sha(P/n)==h
sy=b['bridge_symbols'];FB=0x3000000;SIZE=3686400;GPU=0xfd000000
SELECT=[0x80010000,0x80010004,0x80010010,0x80000900,0x80000904,0x80000914,0x80000800,0x80000804,0x80000810,0x80000884]
VALUES=[0x02a010de,2,0xfd000000,0x01b410de,1,0xc001,0x01b210de,1,0,0x8001]
SETUP=[(0x680884,0),(0x680888,0),(0x68088c,0x10001000),(0x680890,0x10000000),(0x680894,0x10000000),(0x680898,0x10000000),(0x68089c,0x10000000),(0x680880,0x21101100),(0x680630,2),(0x68084c,0x00801080),(0x6808c4,0x40801080)]
H=[(0x680820,719),(0x680824,779),(0x680828,719),(0x680834,0),(0x68082c,738),(0x680830,770),(0x680838,719)]
HB=[1279,1649,1279,0,1389,1429,1279]
V=[(0x680800,719),(0x680804,749),(0x68080c,724),(0x680810,729),(0x680818,719)]
CS=[(0x14,0),(0x17,0xe3),(0x19,0x10),(0x1b,0x85)]
R={'passed':False,'scope':__doc__,'physical_access':False,'harness_sha256':sha(Path(__file__)),'cases':[]};deadline=time.monotonic()+900
def run(name,layout='dual',want=0x811,nmm=11,ncr=3,first=0xffffffff,read_fault=0,refusal=0,pci_bad=None,timer='normal',cr_bad=None,mm_bad=None,fault='',direct=False,badarg=None,flags=2,cpu4=0,c1_original=0x9f):
 assert time.monotonic()<deadline
 page=(P/layout/'page.bin').read_bytes();base=struct.unpack_from('<I',page,0x844)[0];sp=base+0x8000;op=base+0x6800;end=base+sy['bridge_hold'];minstack=[sp]
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(base-4096,40960);c.mem_write(base-4096,b'G'*40960);c.mem_write(base,page)
 c.mem_map(FB-4096,SIZE+8192);c.mem_write(FB-4096,b'Z'*(SIZE+8192));c.mem_map(GPU,0x800000)
 initial=bytes(c.mem_read(base,32768));c.reg_write(x.UC_X86_REG_GDTR,(0,base+0x800,31,0));c.reg_write(x.UC_X86_REG_CR0,0x40000011);c.reg_write(x.UC_X86_REG_CR4,cpu4)
 for reg,val in [(x.UC_X86_REG_CS,0x10),(x.UC_X86_REG_DS,0x18),(x.UC_X86_REG_ES,0x18),(x.UC_X86_REG_SS,0x18)]:c.reg_write(reg,val)
 c.reg_write(x.UC_X86_REG_EBP,base);c.reg_write(x.UC_X86_REG_ESP,sp);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 pci=dict(zip(SELECT,VALUES))
 if pci_bad:pci[pci_bad[0]]=pci_bad[1]
 state={'cl9writes':0,'cl7writes':0,'cb15writes':0,'cb7writes':0,'cb9writes':0,'cd12writes':0,'cd7writes':0,'ct16writes':0,'ct6writes':0,'ct7writes':0,'c10writes':0,'c7writes':0,'vewrites':0,'sewrites':0,'sywrites':0,'vswrites':0,'vcwrites':0,'vtwrites':0,'vwrites':0,'c13writes':0,'c19bwrites':0,'c17bwrites':0,'c2bwrites':0,'c1writes':0,'c17writes':0,'c5bwrites':0,'c3writes':0,'c2writes':0,'c0writes':0,'c5writes':0,'c4writes':0,'selector':0x12345678,'ticks':0,'seq':1,'gate':0,'nmm':0,'ncr':0,'pending':None,'unlocked':False,'recovering':False};trace=[];mw=[];cw=[];sw=[];outs=[];checked=[]
 cr={1:c1_original,3:0x8c,2:0x9f,0:0xc8,4:0xa7,5:0x31,6:0xec,7:0xf0,9:0x60,0x10:0xd4,0x12:0xcf,0x15:0xcf,0x16:0xed,0x18:0xff,0x11:9,0x21:255,0x44:0,0x39:255,0x13:0x80,0x19:0x51,0x25:0x10,0x28:0x83,0x2d:0xe0,0x1b:0x85,0x14:0,0x17:0xe3,0x22:0xfe,0x1f:3,0x33:0x11}
 if cr_bad:cr[cr_bad[0]]=cr_bad[1]
 sels={0x6013d4:0x67,0xc03c4:0x72,0xc03ce:0x91};original_sels=sels.copy()
 mm={a:(3 if a==0x680630 else v) for a,v in SETUP}
 mm.update({0x680508:0x3c20d,0x68050c:0x100a0400,0x100200:0x3070003,0x600804:3,0x600800:FB,0x680838:1279,0x680818:719})
 mm.update(dict(zip([a for a,_ in H],HB)));hw={a:0 for a,_ in H};htrace=[];hrestore=[]
 mm.update(dict(V));mm.update({0x680808:719,0x680814:0});vtrace=[];vttrace=[];vctrace=[];vstrace=[];sytrace=[];setrace=[];vetrace=[]
 if mm_bad:mm[mm_bad[0]]=mm_bad[1]
 word=lambda i:struct.unpack('<I',c.mem_read(op+4*i,4))[0]
 def access(uc,kind,addr,width,value,_):
  off=addr-GPU;assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  if kind==u.UC_MEM_WRITE:
   if off in sels:assert width==1;sels[off]=value
   elif off==0xc03c5:
    assert width==1 and sels[0xc03c4]==1 and value in (1,0x21);sw.append(value);state['seq']=value
   elif off==0x6013d5:
    assert width==1;i=sels[0x6013d4];cw.append((i,value))
    if i==9 and state['cl7writes']==1 and word(1) in [0x81146,0x811]:
     state['cl9writes']+=1;n=state['cl9writes'];assert n<=2 and value==64
     assert [word(760),word(761),word(762)]==[64,64,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cl9-drop-write' if n==1 else 'cl9-drop-undo') or (n==2 and fault=='cl9-wrong-write-drop-undo'):return
     cr[9]=value
     if fault==('cl9-wrong-write' if n==1 else 'cl9-wrong-undo') or (n==1 and fault=='cl9-wrong-write-drop-undo'):cr[9]^=1
     if n==1 and fault.startswith('cl9-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,16,18,21,22,24,37][j-1]]^=1
    elif i==7 and state['cb15writes']==1 and word(1) in [0x81144,0x81146,0x811]:
     state['cl7writes']+=1;n=state['cl7writes'];assert n==1 or state['cl9writes']==2*word(762);assert n<=2 and value==62
     assert [word(730),word(731),word(732)]==[62,62,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cl7-drop-write' if n==1 else 'cl7-drop-undo') or (n==2 and fault=='cl7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('cl7-wrong-write' if n==1 else 'cl7-wrong-undo') or (n==1 and fault=='cl7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('cl7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,16,18,21,22,24,37][j-1]]^=1
    elif i==0x15:
     state['cb15writes']+=1;n=state['cb15writes'];assert n==1 or state['cl7writes']==2*word(732);assert n<=2 and value==[223,207][n-1]
     assert state['cb7writes']==1 and word(1) in [0x81142,0x81144,0x81146,0x811]
     assert [word(700),word(701),word(702)]==[207,223,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cb15-drop-write' if n==1 else 'cb15-drop-undo') or (n==2 and fault=='cb15-wrong-write-drop-undo'):return
     cr[21]=value
     if fault==('cb15-wrong-write' if n==1 else 'cb15-wrong-undo') or (n==1 and fault=='cb15-wrong-write-drop-undo'):cr[21]^=1
     if n==1 and fault.startswith('cb15-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,16,18,22,24,37][j-1]]^=1
    elif i==7 and state['cb9writes']==1:
     state['cb7writes']+=1;n=state['cb7writes'];assert n==1 or state['cb15writes']==2*word(702);assert n<=2 and value==[62,54][n-1]
     assert state['cd12writes']==1 and word(1) in [0x81140,0x81142,0x81144,0x81146,0x811]
     assert [word(670),word(671),word(672)]==[54,62,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cb7-drop-write' if n==1 else 'cb7-drop-undo') or (n==2 and fault=='cb7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('cb7-wrong-write' if n==1 else 'cb7-wrong-undo') or (n==1 and fault=='cb7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('cb7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,16,18,21,22,24,37][j-1]]^=1
    elif i==9:
     state['cb9writes']+=1;n=state['cb9writes'];assert n==1 or state['cb7writes']==2*word(672);assert n<=2 and value==[64,96][n-1]
     assert state['cd12writes']==1 and word(1) in [0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
     assert [word(640),word(641),word(642)]==[96,64,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cb9-drop-write' if n==1 else 'cb9-drop-undo') or (n==2 and fault=='cb9-wrong-write-drop-undo'):return
     cr[9]=value
     if fault==('cb9-wrong-write' if n==1 else 'cb9-wrong-undo') or (n==1 and fault=='cb9-wrong-write-drop-undo'):cr[9]^=1
     if n==1 and fault.startswith('cb9-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,16,18,21,22,24,37][j-1]]^=1
    elif i==0x12:
     state['cd12writes']+=1;n=state['cd12writes'];assert n==1 or state['cb9writes']==2*word(642);assert n<=2 and value==[223,207][n-1]
     assert state['cd7writes']==1 and state['ct16writes']==1 and word(1) in [0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
     assert [word(610),word(611),word(612)]==[207,223,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cd12-drop-write' if n==1 else 'cd12-drop-undo') or (n==2 and fault=='cd12-wrong-write-drop-undo'):return
     cr[18]=value
     if fault==('cd12-wrong-write' if n==1 else 'cd12-wrong-undo') or (n==1 and fault=='cd12-wrong-write-drop-undo'):cr[18]^=1
     if n==1 and fault.startswith('cd12-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,16,21,22,24,37][j-1]]^=1
    elif i==7 and state['ct16writes']==1:
     state['cd7writes']+=1;n=state['cd7writes'];assert n==1 or state['cd12writes']==2*word(612);assert n<=2 and value==[54,116][n-1]
     assert state['ct6writes']==1 and state['ct7writes']==1 and word(1) in [0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
     assert [word(580),word(581),word(582)]==[116,54,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cd7-drop-write' if n==1 else 'cd7-drop-undo') or (n==2 and fault=='cd7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('cd7-wrong-write' if n==1 else 'cd7-wrong-undo') or (n==1 and fault=='cd7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('cd7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,16,18,21,22,24,37][j-1]]^=1
    elif i==0x16:
     state['ct16writes']+=1;n=state['ct16writes'];assert n==1 or state['cd7writes']==2*word(582);assert n<=2 and value==[140,237][n-1]
     assert state['ct6writes']==1 and state['ct7writes']==1 and word(1) in [0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
     assert [word(550),word(551),word(552)]==[237,140,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('ct16-drop-write' if n==1 else 'ct16-drop-undo') or (n==2 and fault=='ct16-wrong-write-drop-undo'):return
     cr[0x16]=value
     if fault==('ct16-wrong-write' if n==1 else 'ct16-wrong-undo') or (n==1 and fault=='ct16-wrong-write-drop-undo'):cr[0x16]^=1
     if n==1 and fault.startswith('ct16-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,0x10,0x12,0x15,0x18,0x25][j-1]]^=1
    elif i==6:
     state['ct6writes']+=1;n=state['ct6writes'];assert n==1 or state['ct16writes']==2*word(552);assert n<=2 and value==[12,236][n-1]
     assert state['ct7writes']==1 and state['c10writes']==1 and word(1) in [0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
     assert [word(520),word(521),word(522)]==[236,12,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('ct6-drop-write' if n==1 else 'ct6-drop-undo') or (n==2 and fault=='ct6-wrong-write-drop-undo'):return
     cr[6]=value
     if fault==('ct6-wrong-write' if n==1 else 'ct6-wrong-undo') or (n==1 and fault=='ct6-wrong-write-drop-undo'):cr[6]^=1
     if n==1 and fault.startswith('ct6-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[7,9,0x10,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
    elif i==7 and state['c10writes']==1:
     state['ct7writes']+=1;n=state['ct7writes'];assert n==1 or state['ct6writes']==2*word(522);assert n<=2 and value==116
     assert state['c7writes']==1 and word(1) in [0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
     assert [word(490),word(491),word(492)]==[116,116,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('ct7-drop-write' if n==1 else 'ct7-drop-undo') or (n==2 and fault=='ct7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('ct7-wrong-write' if n==1 else 'ct7-wrong-undo') or (n==1 and fault=='ct7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('ct7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,0x10,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
    elif i==0x10:
     state['c10writes']+=1;n=state['c10writes'];assert n==1 or state['ct7writes']==2*word(492);assert n<=2 and value==(233 if n==1 else 212)
     assert state['c7writes']==1 and state['vewrites']==1 and word(1) in [0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
     assert [word(460),word(461),word(462)]==[212,233,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('c10-drop-write' if n==1 else 'c10-drop-undo'):return
     cr[0x10]=value
     if fault==('c10-wrong-write' if n==1 else 'c10-wrong-undo'):cr[0x10]^=1
     if n==1 and fault.startswith('c10-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
    elif i==7:
     state['c7writes']+=1;n=state['c7writes'];assert n==1 or state['c10writes']==2*word(462);assert n<=2 and value==(116 if n==1 else 240)
     assert state['vewrites']==1 and word(1) in [0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
     assert [word(430),word(431),word(432)]==[240,116,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('c7-drop-write' if n==1 else 'c7-drop-undo'):return
     cr[7]=value
     if fault==('c7-wrong-write' if n==1 else 'c7-wrong-undo'):cr[7]^=1
     if n==1 and fault.startswith('c7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,0x10,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
    elif i==0x13:
     state['c13writes']+=1;n=state['c13writes'];assert n==1 or state['vwrites']==2*word(234); assert n<=2 and value==(0x68 if n==1 else 0x80)
     assert state['seq']==0x21 and state['gate']==5 and not hrestore and state['c19bwrites']==1
     assert struct.unpack('<3I',uc.mem_read(op+864,12))==(0x80,0x68,1)
     assert struct.unpack('<I',uc.mem_read(op+888,4))[0]==0x30
     if fault==('c13-drop-write' if n==1 else 'c13-drop-undo'):return
     cr[0x13]=value
     if n==1 and fault=='c13-wrong-write':cr[0x13]^=1
     for idx2 in [0,1,2,3,4,5,0x19,0x17]:
      if n==1 and fault=='c13-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==0x19 and struct.unpack('<I',uc.mem_read(op+811,4))[0] and state['c19bwrites']<2:
     state['c19bwrites']+=1;n=state['c19bwrites'];assert state['c13writes']==2*struct.unpack('<I',uc.mem_read(op+872,4))[0];assert n<=2 and value==(0x30 if n==1 else 0x10)
     assert state['seq']==0x21 and state['gate']==5 and not hrestore and state['c17bwrites']==1
     assert struct.unpack('<3I',uc.mem_read(op+800,12))==(0x10,0x30,1)
     assert struct.unpack('<I',uc.mem_read(op+824,4))[0]==0x80
     if fault==('c19b-drop-write' if n==1 else 'c19b-drop-undo'):return
     cr[0x19]=value
     if n==1 and fault=='c19b-wrong-write':cr[0x19]^=1
     for idx2 in [0,1,2,3,4,5,0x13,0x17]:
      if n==1 and fault=='c19b-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==0x17 and struct.unpack('<I',uc.mem_read(op+760,4))[0] and state['c17bwrites']<2:
     state['c17bwrites']+=1;n=state['c17bwrites'];assert state['c19bwrites']==2*struct.unpack('<I',uc.mem_read(op+811,4))[0];assert n<=2 and value==(0xe3 if n==1 else 0x63)
     assert state['seq']==0x21 and state['gate']==5 and not hrestore and state['c2bwrites']==state['c1writes']==state['c17writes']==1
     assert state['c5bwrites']==1 and all(state['c'+str(i2)+'writes']==1 for i2 in [0,2,3,4,5])
     assert struct.unpack('<3I',uc.mem_read(op+752,12))==(0x63,0xe3,1)
     if fault==('c17b-drop-write' if n==1 else 'c17b-drop-undo'):return
     cr[0x17]=value
     if n==1 and fault=='c17b-wrong-write':cr[0x17]^=1
     for idx2 in [0,1,2,3,4,5]:
      if n==1 and fault=='c17b-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==2 and struct.unpack('<I',uc.mem_read(op+712,4))[0] and state['c2bwrites']<2:
     state['c2bwrites']+=1;n=state['c2bwrites'];assert state['c17bwrites']==2*struct.unpack('<I',uc.mem_read(op+760,4))[0];assert n<=2 and value==0x59
     assert state['seq']==0x21 and state['gate']==5 and not hrestore and state['c1writes']==state['c17writes']==1
     assert state['c5bwrites']==1 and all(state['c'+str(i2)+'writes']==1 for i2 in [0,2,3,4,5])
     assert struct.unpack('<3I',uc.mem_read(op+704,12))==(0x59,0x59,1)
     if fault==('c2b-drop-write' if n==1 else 'c2b-drop-undo') or (n==2 and fault=='c2b-wrong-write-drop-undo'):return
     cr[2]=value
     if n==1 and fault in ['c2b-wrong-write','c2b-wrong-write-drop-undo']:cr[2]^=1
     for idx2 in [0,1,3,4,5,0x17]:
      if n==1 and fault=='c2b-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==1:
     state['c1writes']+=1;n=state['c1writes'];assert state['c2bwrites']==2*struct.unpack('<I',uc.mem_read(op+712,4))[0];assert n<=2 and value==(0x59 if n==1 else c1_original)
     assert state['seq']==0x21 and state['gate']==5 and not hrestore and state['c17writes']==1
     assert state['c5bwrites']==1 and all(state['c'+str(i2)+'writes']==1 for i2 in [0,2,3,4,5])
     assert struct.unpack('<3I',uc.mem_read(op+656,12))==(c1_original,0x59,1)
     if fault==('c1-drop-write' if n==1 else 'c1-drop-undo'):return
     cr[1]=value
     if n==1 and fault=='c1-wrong-write':cr[1]^=1
     for idx2 in [0,2,3,4,5,0x17]:
      if n==1 and fault=='c1-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==0x17 and struct.unpack('<I',uc.mem_read(op+620,4))[0]:
     state['c17writes']+=1;n=state['c17writes'];assert state['c1writes']==2*struct.unpack('<I',uc.mem_read(op+664,4))[0];assert n<=2 and value==(0x63 if n==1 else 0xe3)
     assert state['seq']==0x21 and state['gate']==5 and not hrestore and state['c5bwrites']==1
     assert all(state['c'+str(i2)+'writes']==1 for i2 in [0,2,3,4,5])
     assert struct.unpack('<3I',uc.mem_read(op+612,12))==(0xe3,0x63,1)
     if fault==('c17-drop-write' if n==1 else 'c17-drop-undo'):return
     cr[0x17]=value
     if n==1 and fault=='c17-wrong-write':cr[0x17]^=1
     for idx2 in [0,2,3,4,5]:
      if n==1 and fault=='c17-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==5 and struct.unpack('<I',uc.mem_read(op+580,4))[0] and state['c5bwrites']<2:
     state['c5bwrites']+=1;n=state['c5bwrites'];assert state['c17writes']==2*struct.unpack('<I',uc.mem_read(op+620,4))[0]
     assert value==(0xbe if n==1 else 0x3e)
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     assert all(state['c'+str(i2)+'writes']==1 for i2 in [0,2,3,4,5])
     assert struct.unpack('<3I',uc.mem_read(op+572,12))==(0x3e,0xbe,1)
     if fault==('c5b-drop-write' if n==1 else 'c5b-drop-undo'):return
     cr[5]=value
     if n==1 and fault=='c5b-wrong-write':cr[5]^=1
     for idx2 in [0,2,3,4]:
      if n==1 and fault=='c5b-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==3:
     state['c3writes']+=1;assert state['c3writes']<=2
     if state['c3writes']==2:assert state['c5bwrites']==2*struct.unpack('<I',uc.mem_read(op+580,4))[0]
     assert value==(0x80 if state['c3writes']==1 else 0x8c)
     assert state['seq']==0x21 and state['gate']==5 and all(state['c'+str(i2)+'writes']==1 for i2 in [0,2,4,5]) and not hrestore
     assert struct.unpack('<I',uc.mem_read(op+540,4))[0]==1 and not cr[0x11]&0x80
     if fault==('c3-drop-write' if state['c3writes']==1 else 'c3-drop-restore'):return
     cr[3]=value
     for idx2 in [0,2,4,5]:
      if state['c3writes']==1 and fault=='c3-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==2:
     state['c2writes']+=1;assert state['c2writes']<=2
     if state['c2writes']==2:assert state['c3writes']==2*struct.unpack('<I',uc.mem_read(op+540,4))[0]
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
   elif off==0x680818:
    assert width==4 and state['seq']==0x21 and state['gate']==5 and state['sewrites']==1 and not hrestore
    assert word(1) in [0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
    state['vewrites']+=1;n=state['vewrites'];assert n==1 or state['c7writes']==2*word(432);assert n<=2 and value==(479 if n==1 else 719)
    assert [word(i) for i in [400,401,402]]==[719,479,1]
    vetrace.append((off,value))
    if fault==('ve-drop-write' if n==1 else 've-drop-undo'):return
    mm[off]=value
    if fault==('ve-wrong-write' if n==1 else 've-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('ve-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x680814,0x68080c,0x680810][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
   elif off==0x680810:
    assert width==4 and state['seq']==0x21 and state['gate']==5 and state['sywrites']==1 and not hrestore
    assert word(1) in [0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
    state['sewrites']+=1;n=state['sewrites'];assert n==1 or state['vewrites']==2*word(402); assert n<=2 and value==(492 if n==1 else 729)
    assert [word(i) for i in [370,371,372]]==[729,492,1]
    setrace.append((off,value))
    if fault==('se-drop-write' if n==1 else 'se-drop-undo'):return
    mm[off]=value
    if fault==('se-wrong-write' if n==1 else 'se-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('se-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x680814,0x68080c,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
   elif off==0x68080c:
    assert width==4 and state['seq']==0x21 and state['gate']==5 and state['vswrites']==1 and not hrestore
    assert word(1) in [0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
    state['sywrites']+=1;n=state['sywrites'];assert n==1 or state['sewrites']==2*word(372); assert n<=2 and value==(489 if n==1 else 724)
    assert [word(i) for i in [340,341,342]]==[724,489,1]
    sytrace.append((off,value))
    if fault==('sy-drop-write' if n==1 else 'sy-drop-undo'):return
    mm[off]=value
    if fault==('sy-wrong-write' if n==1 else 'sy-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('sy-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x680814,0x680810,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
   elif off==0x680814:
    assert width==4 and state['seq']==0x21 and state['gate']==5 and state['vcwrites']==1 and not hrestore
    assert word(1) in [0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
    state['vswrites']+=1;n=state['vswrites'];assert n==1 or state['sywrites']==2*word(342); assert n<=2 and value==0
    assert [word(i) for i in [310,311,312]]==[0,0,1]
    vstrace.append((off,value))
    if fault==('vs-drop-write' if n==1 else 'vs-drop-undo') or (n==2 and fault=='vs-wrong-write-drop-undo'):return
    mm[off]=value
    if fault==('vs-wrong-write' if n==1 else 'vs-wrong-undo') or (n==1 and fault=='vs-wrong-write-drop-undo'):mm[off]^=1
    if n==1 and fault.startswith('vs-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x68080c,0x680810,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
   elif off==0x680808:
    assert width==4 and state['seq']==0x21 and state['gate']==5 and state['vtwrites']==1 and not hrestore
    assert word(1) in [0x81126,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
    state['vcwrites']+=1;n=state['vcwrites'];assert n==1 or state['vswrites']==2*word(312); assert n<=2 and value==(479 if n==1 else 719)
    assert [word(i) for i in [280,281,282]]==[719,479,1]
    vctrace.append((off,value))
    if fault==('vc-drop-write' if n==1 else 'vc-drop-undo'):return
    mm[off]=value
    if fault==('vc-wrong-write' if n==1 else 'vc-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('vc-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x68080c,0x680810,0x680814,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
   elif off==0x680804:
    assert width==4 and state['seq']==0x21 and state['gate']==5 and state['vwrites']==1 and not hrestore
    assert word(1) in [0x81124,0x81126,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]
    state['vtwrites']+=1;n=state['vtwrites'];assert n==1 or state['vcwrites']==2*word(282); assert n<=2 and value==(524 if n==1 else 749)
    assert [word(i) for i in [256,257,258]]==[749,524,1]
    vttrace.append((off,value))
    if fault==('vt-drop-write' if n==1 else 'vt-drop-undo'):return
    mm[off]=value
    if fault==('vt-wrong-write' if n==1 else 'vt-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('vt-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=6
     if j<=4:mm[[0x680800,0x68080c,0x680810,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-5]]^=1
   elif off in dict(V):
    assert off==0x680800 and width==4 and state['seq']==0x21 and state['gate']==5
    assert state['c13writes']==1 and not hrestore
    state['vwrites']+=1;n=state['vwrites'];assert n==1 or state['vtwrites']==2*word(258); assert n<=2 and value==(479 if n==1 else 719)
    assert [word(i) for i in [232,233,234]]==[719,479,1]
    vtrace.append((off,value))
    if fault==('v-drop-write' if n==1 else 'v-drop-undo'):return
    mm[off]=value
    if fault==('v-wrong-write' if n==1 else 'v-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('v-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=6
     if j<=4:mm[V[j][0]]^=1
     else:cr[[0x13,0x19][j-5]]^=1
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
   if i in [9,6,7,16,18,21,22,24,37] and state['cl7writes']==1 and word(1) in [0x81146,0x811]:
    j=[9,6,7,16,18,21,22,24,37].index(i);phase=['before','after','undo'][state['cl9writes']]
    if fault=='cl9-'+phase+'-'+str(j):value^=1
   if i in [7,6,9,16,18,21,22,24,37] and state['cb15writes']==1 and word(1) in [0x81144,0x81146,0x811]:
    j=[7,6,9,16,18,21,22,24,37].index(i);phase=['before','after','undo'][state['cl7writes']]
    if fault=='cl7-'+phase+'-'+str(j):value^=1
   if i in [21,6,7,9,16,18,22,24,37] and state['cb7writes']==1 and word(1) in [0x81142,0x81144,0x81146,0x811]:
    j=[21,6,7,9,16,18,22,24,37].index(i);phase=['before','after','undo'][state['cb15writes']]
    if fault=='cb15-'+phase+'-'+str(j):value^=1
   if i in [7,6,9,16,18,21,22,24,37] and state['cb9writes']==1 and word(1) in [0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[7,6,9,16,18,21,22,24,37].index(i);phase=['before','after','undo'][state['cb7writes']]
    if fault=='cb7-'+phase+'-'+str(j):value^=1
   if i in [9,6,7,16,18,21,22,24,37] and state['cd12writes']==1 and word(1) in [0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[9,6,7,16,18,21,22,24,37].index(i);phase=['before','after','undo'][state['cb9writes']]
    if fault=='cb9-'+phase+'-'+str(j):value^=1
   if i in [18,6,7,9,16,21,22,24,37] and state['cd7writes']==1 and word(1) in [0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[18,6,7,9,16,21,22,24,37].index(i);phase=['before','after','undo'][state['cd12writes']]
    if fault=='cd12-'+phase+'-'+str(j):value^=1
   if i in [7,6,9,16,18,21,22,24,37] and state['ct16writes']==1 and word(1) in [0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[7,6,9,16,18,21,22,24,37].index(i);phase=['before','after','undo'][state['cd7writes']]
    if fault=='cd7-'+phase+'-'+str(j):value^=1
   if i in [0x16,6,7,9,0x10,0x12,0x15,0x18,0x25] and state['ct6writes']==1 and word(1) in [0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[0x16,6,7,9,0x10,0x12,0x15,0x18,0x25].index(i);phase=['before','after','undo'][state['ct16writes']]
    if fault=='ct16-'+phase+'-'+str(j):value^=1
   if i in [6,7,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['ct7writes']==1 and word(1) in [0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[6,7,9,0x10,0x12,0x15,0x16,0x18,0x25].index(i);phase=['before','after','undo'][state['ct6writes']]
    if fault=='ct6-'+phase+'-'+str(j):value^=1
   if i in [7,6,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['c10writes']==1 and word(1) in [0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[7,6,9,0x10,0x12,0x15,0x16,0x18,0x25].index(i);phase=['before','after','undo'][state['ct7writes']]
    if fault=='ct7-'+phase+'-'+str(j):value^=1
   if i in [0x10,6,7,9,0x12,0x15,0x16,0x18,0x25] and state['c7writes']==1 and word(1) in [0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[0x10,6,7,9,0x12,0x15,0x16,0x18,0x25].index(i);phase=['before','after','undo'][state['c10writes']]
    if fault=='c10-'+phase+'-'+str(j):value^=1
   if i in [7,6,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['vewrites']==1 and word(1) in [0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[7,6,9,0x10,0x12,0x15,0x16,0x18,0x25].index(i);phase=['before','after','undo'][state['c7writes']]
    if fault=='c7-'+phase+'-'+str(j):value^=1
   if i in [0x13,0x19] and state['sewrites']==1 and word(1) in [0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=7+[0x13,0x19].index(i);phase=['before','after','undo'][state['vewrites']]
    if fault=='ve-'+phase+'-'+str(j):value^=1
   if i in [0x13,0x19] and state['sywrites']==1 and word(1) in [0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=7+[0x13,0x19].index(i);phase=['before','after','undo'][state['sewrites']]
    if fault=='se-'+phase+'-'+str(j):value^=1
   if i in [0x13,0x19] and state['vswrites']==1 and word(1) in [0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=7+[0x13,0x19].index(i);phase=['before','after','undo'][state['sywrites']]
    if fault=='sy-'+phase+'-'+str(j):value^=1
   if i in [0x13,0x19] and state['vcwrites']==1 and word(1) in [0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=7+[0x13,0x19].index(i);phase=['before','after','undo'][state['vswrites']]
    if fault=='vs-'+phase+'-'+str(j):value^=1
   if i in [0x13,0x19] and state['vtwrites']==1 and word(1) in [0x81126,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=7+[0x13,0x19].index(i);phase=['before','after','undo'][state['vcwrites']]
    if fault=='vc-'+phase+'-'+str(j):value^=1
   if i in [0x13,0x19] and state['vwrites']==1 and word(1) in [0x81124,0x81126,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=5+[0x13,0x19].index(i);phase=['before','after','undo'][state['vtwrites']]
    if fault=='vt-'+phase+'-'+str(j):value^=1
   if i in [0x13,0x19] and state['c13writes']==1 and word(1) in [0x81122,0x81124,0x81126,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=5+[0x13,0x19].index(i);phase=['before','after','undo'][state['vwrites']]
    if fault=='v-'+phase+'-'+str(j):value^=1
   if struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x81120 and not struct.unpack('<I',uc.mem_read(op+872,4))[0] and state['c19bwrites']==1:
    if i==0x13 and fault=='c13-before-read':value^=1
    if i==0x19 and fault=='c19-before-c13-read':value^=1
   if i==0x13 and state['c13writes']==1 and fault=='c13-read':value^=1
   if i==0x13 and state['c13writes']==1 and fault=='c13-high-read':value^=0x80
   if i==0x13 and state['c13writes']==2 and state['c19bwrites']==1 and fault=='c13-undo-read':value^=1
   if i==0x19 and state['c13writes']==2 and state['c19bwrites']==1 and fault=='c19-undo-c13-read':value^=1
   if i in [0,1,2,3,4,5,0x19,0x17] and state['c13writes']==1 and fault=='c'+str(i)+'-after-c13-read':value^=1
   if struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x8111e and not struct.unpack('<I',uc.mem_read(op+811,4))[0] and state['c17bwrites']==1:
    if i==0x19 and fault=='c19b-before-read':value^=1
    if i==0x13 and fault=='c13-before-c19b-read':value^=1
   if i==0x19 and state['c19bwrites']==1 and fault=='c19b-read':value^=1
   if i==0x19 and state['c19bwrites']==1 and fault=='c19b-high-read':value^=0x20
   if i==0x19 and state['c19bwrites']==2 and state['c17bwrites']==1 and fault=='c19b-undo-read':value^=1
   if i==0x13 and state['c19bwrites']==2 and state['c17bwrites']==1 and fault=='c13-undo-c19b-read':value^=1
   if i in [0,1,2,3,4,5,0x13,0x17] and state['c19bwrites']==1 and fault=='c'+str(i)+'-after-c19b-read':value^=1
   if i==0x17 and struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x8111c and not struct.unpack('<I',uc.mem_read(op+760,4))[0] and state['c2bwrites']==1 and fault=='c17b-before-read':value^=1
   if i==0x17 and state['c17bwrites']==1 and fault=='c17b-read':value^=1
   if i==0x17 and state['c17bwrites']==1 and fault=='c17b-low-read':value^=0x80
   if i==0x17 and state['c17bwrites']==2 and state['c2bwrites']==1 and fault=='c17b-undo-read':value^=1
   if i in [0,1,2,3,4,5] and state['c17bwrites']==1 and fault=='c'+str(i)+'-after-c17b-read':value^=1
   if i==2 and struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x8111a and not struct.unpack('<I',uc.mem_read(op+712,4))[0] and state['c1writes']==1 and fault=='c2b-before-read':value^=1
   if i==2 and state['c2bwrites']==1 and fault=='c2b-read':value^=1
   if i==2 and state['c2bwrites']==1 and fault=='c2b-high-read':value^=0x80
   if i==2 and state['c2bwrites']==2 and state['c1writes']==1 and fault=='c2b-undo-read':value^=1
   if i in [0,1,3,4,5,0x17] and state['c2bwrites']==1 and fault=='c'+str(i)+'-after-c2b-read':value^=1
   if i==1 and state['c1writes']==1 and fault=='c1-read':value^=1
   if i==1 and state['c1writes']==1 and fault=='c1-high-read':value^=0x80
   if i==1 and state['c1writes']==2 and state['c17writes']==1 and fault=='c1-undo-read':value^=1
   if i in [0,2,3,4,5,0x17] and state['c1writes']==1 and fault=='c'+str(i)+'-after-c1-read':value^=1
   if i==0x17 and not state['recovering'] and struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x81116 and not struct.unpack('<I',uc.mem_read(op+620,4))[0] and fault=='c17-before-read':value^=1
   if i==0x17 and state['c17writes']==1 and fault=='c17-read':value^=1
   if i==0x17 and state['c17writes']==1 and fault=='c17-high-read':value^=0x80
   if i==0x17 and state['c17writes']==2 and state['c5bwrites']==1 and fault=='c17-undo-read':value^=1
   if i in [0,2,3,4,5] and state['c17writes']==1 and fault=='c'+str(i)+'-after-c17-read':value^=1
   if i==5 and state['c5bwrites']==1 and fault=='c5b-read':value^=1
   if i==5 and state['c5bwrites']==1 and fault=='c5b-high-read':value^=0x80
   if i==5 and state['c5bwrites']==2 and state['c3writes']==1 and fault=='c5b-undo-read':value^=1
   if i in [0,2,3,4] and state['c5bwrites']==1 and fault=='c'+str(i)+'-after-c5b-read':value^=1
   if i==3 and state['c3writes']==1 and fault=='c3-read':value^=1
   if i==3 and state['c3writes']==1 and fault=='c3-high-read':value^=0x80
   if i==3 and state['c3writes']==2 and fault=='c3-restore-read':value^=1
   if i in [0,2,4,5] and state['c3writes']==1 and fault=='c'+str(i)+'-after-c3-read':value^=1
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
  else:
   assert width==4 and off in mm;value=mm[off]
   if off in [0x680818,0x680800,0x680804,0x680808,0x680814,0x68080c,0x680810] and state['sewrites']==1 and word(1) in [0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[0x680818,0x680800,0x680804,0x680808,0x680814,0x68080c,0x680810].index(off);phase=['before','after','undo'][state['vewrites']]
    if fault=='ve-'+phase+'-'+str(j):value^=1
   if off in [0x680810,0x680800,0x680804,0x680808,0x680814,0x68080c,0x680818] and state['sywrites']==1 and word(1) in [0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[0x680810,0x680800,0x680804,0x680808,0x680814,0x68080c,0x680818].index(off);phase=['before','after','undo'][state['sewrites']]
    if fault=='se-'+phase+'-'+str(j):value^=1
   if off in [0x68080c,0x680800,0x680804,0x680808,0x680814,0x680810,0x680818] and state['vswrites']==1 and word(1) in [0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[0x68080c,0x680800,0x680804,0x680808,0x680814,0x680810,0x680818].index(off);phase=['before','after','undo'][state['sywrites']]
    if fault=='sy-'+phase+'-'+str(j):value^=1
   if off in [0x680814,0x680800,0x680804,0x680808,0x68080c,0x680810,0x680818] and state['vcwrites']==1 and word(1) in [0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[0x680814,0x680800,0x680804,0x680808,0x68080c,0x680810,0x680818].index(off);phase=['before','after','undo'][state['vswrites']]
    if fault=='vs-'+phase+'-'+str(j):value^=1
   if off in [0x680808,0x680800,0x680804,0x68080c,0x680810,0x680814,0x680818] and state['vtwrites']==1 and word(1) in [0x81126,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[0x680808,0x680800,0x680804,0x68080c,0x680810,0x680814,0x680818].index(off);phase=['before','after','undo'][state['vcwrites']]
    if fault=='vc-'+phase+'-'+str(j):value^=1
   if off in dict(V) and state['vwrites']==1 and word(1) in [0x81124,0x81126,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    j=[0x680804,0x680800,0x68080c,0x680810,0x680818].index(off);phase=['before','after','undo'][state['vtwrites']]
    if fault=='vt-'+phase+'-'+str(j):value^=1
   if off in dict(V) and state['c13writes']==1 and word(1) in [0x81122,0x81124,0x81126,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146,0x811]:
    assert state['seq']==0x21 and state['gate']==5 and not hrestore
    j=[a for a,_ in V].index(off);phase=['before','after','undo'][state['vwrites']]
    if fault=='v-'+phase+'-'+str(j):value^=1
  if struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x8118 and not state['recovering']:
   ix=next((n for n,(a,_) in enumerate(SETUP) if a==off),None)
   if off==0x6013d5:ix=next((11+n for n,(a,_) in enumerate(CS) if a==sels[0x6013d4]),None)
   if ix is not None:
    assert state['nmm']==11 and state['ncr']==3
    if read_fault==ix+1:value^=1
    if fault=='cr1b05' and ix==14:value=5
    checked.append([ix,value])
  if off in dict(H):
   n=[a for a,_ in H].index(off)
   if struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x8119 and not hrestore and fault=='h-read-'+str(n):value^=1
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
    assert word(765)==0 and (not word(762) or word(764)==word(760))
    assert word(735)==0 and (not word(732) or word(734)==word(730))
    assert word(705)==0 and (not word(702) or word(704)==word(700))
    assert word(675)==0 and (not word(672) or word(674)==word(670))
    assert word(645)==0 and (not word(642) or word(644)==word(640))
    assert word(615)==0 and (not word(612) or word(614)==word(610))
    assert word(585)==0 and (not word(582) or word(584)==word(580))
    assert word(555)==0 and (not word(552) or word(554)==word(550))
    assert word(525)==0 and (not word(522) or word(524)==word(520))
    assert word(495)==0 and (not word(492) or word(494)==word(490))
    assert word(465)==0 and (not word(462) or word(464)==word(460))
    assert word(435)==0 and (not word(432) or word(434)==word(430))
    assert word(405)==0 and (not word(402) or word(404)==word(400))
    assert mm[0x680818]==719
    assert word(375)==0 and (not word(372) or word(374)==word(370))
    assert mm[0x680810]==729
    assert word(345)==0 and (not word(342) or word(344)==word(340))
    assert mm[0x68080c]==724
    assert word(315)==0 and (not word(312) or word(314)==word(310))
    assert mm[0x680814]==0
    assert word(285)==0 and (not word(282) or word(284)==word(280))
    assert mm[0x680808]==719 and mm[0x680814]==0
    assert word(261)==0 and (not word(258) or word(260)==word(256))
    assert word(237)==0 and [mm[a] for a,_ in V]==[b for _,b in V]
    assert struct.unpack('<I',uc.mem_read(op+884,4))[0]==0
    assert struct.unpack('<I',uc.mem_read(op+820,4))[0]==0
    assert struct.unpack('<I',uc.mem_read(op+193*4,4))[0]==0
    assert struct.unpack('<I',uc.mem_read(op+724,4))[0]==0
    assert struct.unpack('<I',uc.mem_read(op+676,4))[0]==0 and cr[1]==c1_original
    assert struct.unpack('<I',uc.mem_read(op+632,4))[0]==0 and cr[0x17]==0xe3
    assert struct.unpack('<I',uc.mem_read(op+592,4))[0]==0
    assert struct.unpack('<I',uc.mem_read(op+552,4))[0]==0 and cr[3]==0x8c
    assert struct.unpack('<I',uc.mem_read(op+516,4))[0]==0 and cr[2]==0x9f
    assert struct.unpack('<I',uc.mem_read(op+484,4))[0]==0 and cr[0]==0xc8
    assert struct.unpack('<I',uc.mem_read(op+432,4))[0]==0 and cr[4]==0xa7 and cr[5]==0x31
    assert struct.unpack('<I',uc.mem_read(op+400,4))[0]==0
    assert [mm[a] for a,_ in H]==HB and list(struct.unpack('<7I',uc.mem_read(op+360,28)))==HB
   outs.append(value);state['gate']=value;return
  assert port==0xcf8 and width==4;trace.append(['write',port,value]);state['selector']=value
 def ramwrite(uc,kind,addr,size,value,_):
  if GPU<=addr<GPU+0x800000:return
  if base+0x7d00<=addr and addr+size<=sp:minstack[0]=min(minstack[0],addr)
  assert (base+0x880<=addr and addr+size<=base+0x900) or (op<=addr and addr+size<=op+3160) or (base+0x7d00<=addr and addr+size<=sp) or (FB<=addr and addr+size<=FB+SIZE),('outside admitted writes',hex(addr),size)
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,GPU,GPU+0x7fffff)
 c.hook_add(u.UC_HOOK_MEM_WRITE,ramwrite);c.hook_add(u.UC_HOOK_INSN,pin,None,1,0,x.UC_X86_INS_IN);c.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
 start=base+sy['bridge_post']
 if direct:
  args=[base+0x67c0,GPU,FB,op]
  if badarg is not None:args[badarg]=0
  c.reg_write(x.UC_X86_REG_ESP,sp-20);c.mem_write(sp-20,pack(end,*args));start=struct.unpack_from('<I',page,0x850)[0]
 c.emu_start(start,end,timeout=10000000,count=50000000)
 assert c.reg_read(x.UC_X86_REG_EIP)==end,(name,'execution bound')
 assert c.reg_read(x.UC_X86_REG_ESP)==(sp-16 if direct else sp) and c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
 assert sels==original_sels
 final=bytes(c.mem_read(base,32768));v=list(struct.unpack_from('<790I',final,0x6800))
 assert state['nmm']==nmm and state['ncr']==ncr,(name,state)
 assert mw==SETUP[:nmm]+([(0x680630,3)] if nmm>=9 else [])
 assert cw==([(0x1f,0x57)] if state['unlocked'] else [])+CS[:ncr]+([(4,93)]+([(5,0x3e)]+([(0,0x5c)]+([(2,0x59)]+([(3,0x80)]+([(5,0xbe)]+([(0x17,0x63)]+([(1,0x59)]+([(2,0x59)]+([(0x17,0xe3)]+([(0x19,0x30)]+([(0x13,0x68)]+([(7,116)]+([(16,233)]+([(7,116)]+([(6,12)]+([(22,140)]+([(7,54)]+([(18,223)]+([(9,64)]+([(7,62)]+([(21,223)]+([(7,62)]+([(9,64),(9,64)] if state['cl9writes'] else [])+[(7,62)] if state['cl7writes'] else [])+[(21,207)] if state['cb15writes'] else [])+[(7,54)] if state['cb7writes'] else [])+[(9,96)] if state['cb9writes'] else [])+[(18,207)] if state['cd12writes'] else [])+[(7,116)] if state['cd7writes'] else [])+[(22,237)] if state['ct16writes'] else [])+[(6,236)] if state['ct6writes'] else [])+[(7,116)] if state['ct7writes'] else [])+[(16,212)] if state['c10writes'] else [])+[(7,240)] if state['c7writes'] else [])+[(0x13,0x80)] if state['c13writes'] else [])+[(0x19,0x10)] if state['c19bwrites'] else [])+[(0x17,0x63)] if state['c17bwrites'] else [])+[(2,0x59)] if state['c2bwrites'] else [])+[(1,c1_original)] if state['c1writes'] else [])+[(0x17,0xe3)] if state['c17writes'] else [])+[(5,0x3e)] if state['c5bwrites'] else [])+[(3,0x8c)] if state['c3writes'] else [])+[(2,0x9f)] if state['c2writes'] else [])+[(0,0xc8)] if state['c0writes'] else [])+[(5,0x31)] if state['c5writes'] else [])+[(4,0xa7)] if state['c4writes'] else [])+([(0x19,0x51)] if ncr>=3 else [])
 assert sw in ([],[0x21,1],[0x21]) and outs in ([],[5,4],[5])
 if htrace:
  assert len(htrace)==14 and htrace==H+[(H[i][0],HB[i]) for i in range(6,-1,-1)]
  assert hrestore==list(range(6,-1,-1))
  if fault.startswith(('cl9-undo-','cl9-coupling-')) or fault in ['cl9-wrong-undo','cl9-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[765]!=0 and v[101]==0
  elif fault.startswith(('cl7-undo-','cl7-coupling-')) or fault in ['cl7-wrong-undo','cl7-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[735]!=0 and v[101]==0
  elif fault.startswith(('cb15-undo-','cb15-coupling-')) or fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[705]!=0 and v[101]==0
  elif fault.startswith(('cb7-undo-','cb7-coupling-')) or fault in ['cb7-drop-undo','cb7-wrong-undo','cb7-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[675]!=0 and v[101]==0
  elif fault.startswith(('cb9-undo-','cb9-coupling-')) or fault in ['cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[645]!=0 and v[101]==0
  elif fault.startswith(('cd12-undo-','cd12-coupling-')) or fault in ['cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[615]!=0 and v[101]==0
  elif fault.startswith(('cd7-undo-','cd7-coupling-')) or fault in ['cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[585]!=0 and v[101]==0
  elif fault.startswith(('ct16-undo-','ct16-coupling-')) or fault in ['ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[555]!=0 and v[101]==0
  elif fault.startswith(('ct6-undo-','ct6-coupling-')) or fault in ['ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[525]!=0 and v[101]==0
  elif fault.startswith(('ct7-undo-','ct7-coupling-')) or fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[495]!=0 and v[101]==0
  elif fault.startswith(('c10-undo-','c10-coupling-')) or fault in ['c10-drop-undo','c10-wrong-undo']:assert sw==[0x21] and outs==[5] and v[465]!=0 and v[101]==0
  elif fault.startswith(('c7-undo-','c7-coupling-')) or fault in ['c7-drop-undo','c7-wrong-undo']:assert sw==[0x21] and outs==[5] and v[435]!=0 and v[101]==0
  elif fault.startswith(('ve-undo-','ve-coupling-')) or fault in ['ve-drop-undo','ve-wrong-undo']:assert sw==[0x21] and outs==[5] and v[405]!=0 and v[101]==0
  elif fault.startswith(('se-undo-','se-coupling-')) or fault in ['se-drop-undo','se-wrong-undo']:assert sw==[0x21] and outs==[5] and v[375]!=0 and v[101]==0
  elif fault.startswith(('sy-undo-','sy-coupling-')) or fault in ['sy-drop-undo','sy-wrong-undo']:assert sw==[0x21] and outs==[5] and v[345]!=0 and v[101]==0
  elif fault.startswith(('vs-undo-','vs-coupling-')) or fault in ['vs-wrong-undo','vs-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[315]!=0 and v[101]==0
  elif fault.startswith(('vc-undo-','vc-coupling-')) or fault in ['vc-drop-undo','vc-wrong-undo']:assert sw==[0x21] and outs==[5] and v[285]!=0 and v[101]==0
  elif fault.startswith(('vt-undo-','vt-coupling-')) or fault in ['vt-drop-undo','vt-wrong-undo']:assert sw==[0x21] and outs==[5] and v[261]!=0 and v[101]==0
  elif fault.startswith(('v-undo-','v-coupling-')) or fault in ['v-drop-undo','v-wrong-undo']:assert sw==[0x21] and outs==[5] and v[237]!=0 and v[101]==0
  elif fault.startswith(('h-restore-','h-cleanup-')):assert sw==[0x21] and outs==[5] and v[100]!=0 and v[101]==0
  elif fault in ['c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling','c5-drop-restore']:assert sw==[0x21] and outs==[5] and v[108]!=0 and v[101]==0
  elif fault in ['c0-restore-read','c0-drop-restore']:assert sw==[0x21] and outs==[5] and v[121]==1 and v[101]==0
  elif fault in ['c2-restore-read','c2-drop-restore']:assert sw==[0x21] and outs==[5] and v[129]==1 and v[101]==0
  elif fault in ['c3-restore-read','c3-drop-restore']:assert sw==[0x21] and outs==[5] and v[138]==1 and v[101]==0
  elif fault in ['c5b-undo-read','c5b-drop-undo']:assert sw==[0x21] and outs==[5] and v[148]==1 and v[101]==0
  elif fault in ['c17-undo-read','c17-drop-undo']:assert sw==[0x21] and outs==[5] and v[158]==1 and v[101]==0
  elif fault in ['c1-undo-read','c1-drop-undo']:assert sw==[0x21] and outs==[5] and v[169]==1 and v[101]==0
  elif fault in ['c2b-undo-read','c2b-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[181]==1 and v[101]==0
  elif fault in ['c17b-undo-read','c17b-drop-undo']:assert sw==[0x21] and outs==[5] and v[193]==1 and v[101]==0
  elif fault in ['c13-undo-read','c13-drop-undo','c13-c25-coupling','c19-undo-c13-read']:assert sw==[0x21] and outs==[5] and v[221]!=0 and v[101]==0
  elif fault in ['c19b-undo-read','c19b-drop-undo','c19b-c19-coupling','c13-undo-c19b-read']:assert sw==[0x21] and outs==[5] and v[205]!=0 and v[101]==0
  else:assert v[100:102]==[0,1]
 if not refusal and want==0x811:assert v[83:90]==[b for _,b in H] and v[90:97]==HB and v[97:100]==[7,7,0xffffffff]
 if want==0x8119:
  hf=int(fault.rsplit('-',1)[1]);assert v[97:100]==[7,hf+1,hf] and v[83:83+hf]==[b for _,b in H[:hf]] and v[83+hf]!=H[hf][1] and v[84+hf:90]==[0xffffffff]*(6-hf)
 if state['c4writes']:
  assert state['c4writes']==2 and v[104]==0xa7 and v[107]==1 and v[109]==0x31
  assert v[105]==(92 if fault=='c4-read' else 0xa7 if fault=='c4-write' else 93)
  assert v[106]==(0xa6 if fault=='c4-restore-read' else 93 if fault=='c4-restore-write' else 0xa7)
  assert v[110]==(0x30 if fault in ['c5-read','c5-coupling'] else 0x31)
  assert v[111]==(0x3e if fault=='c5-drop-restore' else 0x30 if fault in ['c5-restore-read','c5-coupling'] else 0x31)
  assert v[108]==int(v[104]!=v[106])+2*int(v[109]!=v[111])
  assert (v[105]==93 and v[110]==0x31)==(v[1] in [0x811,0x811d,0x811e,0x81110,0x81112,0x81114,0x81116,0x81118,0x8111a,0x8111c,0x8111e,0x81120,0x81122,0x81124,0x81126,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146])
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
 if state['c3writes']:
  assert state['c3writes']==2 and v[133:136]==[0x8c,0x80,1]
  assert v[136]==(0x8c if fault=='c3-drop-write' else 0x81 if fault=='c3-read' else 0 if fault=='c3-high-read' else 0x80)
  assert v[137]==(0x8d if fault=='c3-restore-read' else 0x80 if fault=='c3-drop-restore' else 0x8c)
  assert v[138]==int(v[137]!=v[133])
  for idx,n,target in [(0,139,0x5c),(2,140,0x59),(4,141,93),(5,142,0x3e)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c3-read','c3-c'+str(idx)+'-coupling'] else target)
 if state['c5bwrites']:
  assert state['c5bwrites']==2 and v[143:146]==[0x3e,0xbe,1]
  assert v[146]==(0x3e if fault in ['c5b-drop-write','c5b-high-read'] else 0xbf if fault in ['c5b-read','c5b-wrong-write'] else 0xbe)
  assert v[147]==(0xbe if fault=='c5b-drop-undo' else 0x3f if fault=='c5b-undo-read' else 0x3e)
  assert v[148]==int(v[147]!=v[143])
  for idx,n,target in [(0,149,0x5c),(2,150,0x59),(3,151,0x80),(4,152,93)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c5b-read','c5b-c'+str(idx)+'-coupling'] else target)
 if v[1] in [0x811,0x81116,0x81118,0x8111a,0x8111c,0x8111e,0x81120,0x81122,0x81124,0x81126,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146] and not refusal and want!=5:
  assert v[153]==(0xe2 if fault=='c17-before-read' else 0xe3)
  assert v[155]==int(fault!='c17-before-read') and state['c17writes']==2*v[155]
  if v[155]:
   assert v[154]==0x63
   assert v[156]==(0xe3 if fault in ['c17-drop-write','c17-high-read'] else 0x62 if fault in ['c17-read','c17-wrong-write'] else 0x63)
   assert v[157]==(0x63 if fault=='c17-drop-undo' else 0xe2 if fault=='c17-undo-read' else 0xe3)
   assert v[158]==int(v[157]!=v[153])
   for idx,n,target in [(0,159,0x5c),(2,160,0x59),(3,161,0x80),(4,162,93),(5,163,0xbe)]:
    assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c17-read','c17-c'+str(idx)+'-coupling'] else target)
 if state['c1writes']:
  assert state['c1writes']==2 and v[164:167]==[c1_original,0x59,1]
  assert v[167]==(c1_original if fault=='c1-drop-write' else 0xd9 if fault=='c1-high-read' else 0x58 if fault in ['c1-read','c1-wrong-write'] else 0x59)
  assert v[168]==(0x59 if fault=='c1-drop-undo' else c1_original^1 if fault=='c1-undo-read' else c1_original)
  assert v[169]==int(v[168]!=v[164])
  for idx,n,target in [(0,170,0x5c),(2,171,0x59),(3,172,0x80),(4,173,93),(5,174,0xbe),(0x17,175,0x63)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c1-read','c1-c'+str(idx)+'-coupling'] else target)
 if state['c2bwrites']:
  assert state['c2bwrites']==2 and v[176:179]==[0x59,0x59,1]
  assert v[179]==(0xd9 if fault=='c2b-high-read' else 0x58 if fault in ['c2b-read','c2b-wrong-write','c2b-wrong-write-drop-undo'] else 0x59)
  assert v[180]==(0x58 if fault in ['c2b-undo-read','c2b-wrong-write-drop-undo'] else 0x59)
  assert v[181]==int(v[180]!=v[176])
  for idx,n,target in [(0,182,0x5c),(1,183,0x59),(3,184,0x80),(4,185,93),(5,186,0xbe),(0x17,187,0x63)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c2b-read','c2b-c'+str(idx)+'-coupling'] else target)
 elif fault=='c2b-before-read':assert v[176:188]==[0x58,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 else:assert v[176:188]==([0]*12 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff])
 if state['c17bwrites']:
  assert state['c17bwrites']==2 and v[188:191]==[0x63,0xe3,1]
  assert v[191]==(0x63 if fault in ['c17b-drop-write','c17b-low-read'] else 0xe2 if fault in ['c17b-read','c17b-wrong-write'] else 0xe3)
  assert v[192]==(0xe3 if fault=='c17b-drop-undo' else 0x62 if fault=='c17b-undo-read' else 0x63)
  assert v[193]==int(v[192]!=v[188])
  for idx,n,target in [(0,194,0x5c),(1,195,0x59),(2,196,0x59),(3,197,0x80),(4,198,93),(5,199,0xbe)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c17b-read','c17b-c'+str(idx)+'-coupling'] else target)
 elif fault=='c17b-before-read':assert v[188:200]==[0x62,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 else:assert v[188:200]==([0]*12 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff])
 if state['c19bwrites']:
  assert state['c19bwrites']==2 and v[200:203]==[0x10,0x30,1]
  assert v[203]==(0x10 if fault in ['c19b-drop-write','c19b-high-read'] else 0x31 if fault in ['c19b-read','c19b-wrong-write'] else 0x30)
  assert v[204]==(0x30 if fault=='c19b-drop-undo' else 0x11 if fault=='c19b-undo-read' else 0x10)
  assert v[206]==128 and v[215]==(104 if fault=='c13-drop-undo' else 129 if fault in ['c19b-c19-coupling','c13-undo-c19b-read'] else 128)
  assert v[205]==int(v[204]!=v[200])+2*int(v[215]!=v[206])
  for idx,n,target in [(0x13,207,128),(0x17,208,227),(0,209,92),(1,210,89),(2,211,89),(3,212,128),(4,213,93),(5,214,190)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c19b-read','c19b-c'+str(idx)+'-coupling'] else target)
 elif fault in ['c19b-before-read','c13-before-c19b-read']:
  assert v[200]==(17 if fault=='c19b-before-read' else 16) and v[206]==(129 if fault=='c13-before-c19b-read' else 128)
  assert v[201:206]==[0,0,0xffffffff,0xffffffff,0] and v[207:216]==[0xffffffff]*9
 else:assert v[200:216]==([0]*16 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0,0]+[0xffffffff]*9)
 if state['c13writes']:
  assert state['c13writes']==2 and v[216:219]==[0x80,0x68,1]
  assert v[219]==(0x80 if fault=='c13-drop-write' else 0xe8 if fault=='c13-high-read' else 0x69 if fault in ['c13-read','c13-wrong-write'] else 0x68)
  assert v[220]==(0x68 if fault=='c13-drop-undo' else 0x81 if fault=='c13-undo-read' else 0x80)
  assert v[222]==48 and v[231]==(49 if fault in ['c13-c25-coupling','c19-undo-c13-read','v-coupling-6','vt-coupling-6','vc-coupling-8','vs-coupling-8','sy-coupling-8','se-coupling-8','ve-coupling-8'] else 48)
  assert v[221]==int(v[220]!=v[216])+2*int(v[231]!=v[222])
  for idx,n,target in [(0x19,223,48),(0x17,224,227),(0,225,92),(1,226,89),(2,227,89),(3,228,128),(4,229,93),(5,230,190)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c13-read','c13-c'+str(idx)+'-coupling'] else target)
 elif fault in ['c13-before-read','c19-before-c13-read']:
  assert v[216]==(129 if fault=='c13-before-read' else 128) and v[222]==(49 if fault=='c19-before-c13-read' else 48)
  assert v[217:222]==[0,0,0xffffffff,0xffffffff,0] and v[223:232]==[0xffffffff]*9
 else:assert v[216:232]==([0]*16 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0,0]+[0xffffffff]*9)
 # Expected values depend on the injected fault, not the returned success code.
 reached=state['c13writes'] and v[1] in [0x811,0x81122,0x81124,0x81126,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached:
  vb=[719,749,724,729,719,104,48];before=vb.copy();attempted=not fault.startswith('v-before-')
  if not attempted:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[232]]+[v[238+3*i] for i in range(6)]==before
  assert v[233:235]==([479,1] if attempted else [0,0])
  assert vtrace==([(0x680800,479),(0x680800,719)] if attempted else [])
  after=[479]+vb[1:];undo=vb.copy()
  if attempted:
   if fault=='v-drop-write':after[0]=719
   if fault=='v-wrong-write':after[0]^=1
   if fault.startswith('v-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('v-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('v-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='v-drop-undo':undo[0]=479
   if fault=='v-wrong-undo':undo[0]^=1
   if fault.startswith('vt-coupling-') and int(fault.rsplit('-',1)[1])>=2:undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='vt-drop-undo':undo[1]=524
   if fault=='vt-wrong-undo':undo[1]^=1
   if fault.startswith('vc-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={3:2,4:3,6:4,7:5,8:6}.get(j)
    if k is not None:undo[k]^=1
   if fault.startswith('vs-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={4:2,5:3,6:4,7:5,8:6}.get(j)
    if k is not None:undo[k]^=1
   if fault.startswith('sy-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={5:3,6:4,7:5,8:6}.get(j)
    if k is not None:undo[k]^=1
   if fault=='sy-drop-undo':undo[2]=489
   if fault=='sy-wrong-undo':undo[2]^=1
   if fault.startswith('se-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={6:4,7:5,8:6}.get(j)
    if k is not None:undo[k]^=1
   if fault=='se-drop-undo':undo[3]=492
   if fault=='se-wrong-undo':undo[3]^=1
   if fault.startswith('ve-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={7:5,8:6}.get(j)
    if k is not None:undo[k]^=1
   if fault=='ve-drop-undo':undo[4]=479
   if fault=='ve-wrong-undo':undo[4]^=1
   assert [v[235]]+[v[239+3*i] for i in range(6)]==after
   assert [v[236]]+[v[240+3*i] for i in range(6)]==undo
   assert v[237]==sum(1<<i for i in range(7) if undo[i]!=vb[i])
  else:assert v[235:238]==[0xffffffff,0xffffffff,0] and all(v[i]==0xffffffff for i in [239,240,242,243,245,246,248,249,251,252,254,255])
 else:
  assert not vtrace
  assert v[232:256]==([0]*24 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*6)
 reached_vt=state['c13writes'] and v[1] in [0x811,0x81124,0x81126,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_vt:
  ref=[749,479,724,729,719,104,48];before=ref.copy();attempted_vt=not fault.startswith('vt-before-')
  if not attempted_vt:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[256]]+[v[262+3*i] for i in range(6)]==before
  assert v[257:259]==([524,1] if attempted_vt else [0,0])
  assert vttrace==([(0x680804,524),(0x680804,749)] if attempted_vt else [])
  if attempted_vt:
   after=[524]+ref[1:];undo=ref.copy()
   if fault=='vt-drop-write':after[0]=749
   if fault=='vt-wrong-write':after[0]^=1
   if fault.startswith('vt-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('vt-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('vt-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='vt-drop-undo':undo[0]=524
   if fault=='vt-wrong-undo':undo[0]^=1
   if fault.startswith('vc-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,3:2,4:3,6:4,7:5,8:6}.get(j)
    if k is not None:undo[k]^=1
   if fault.startswith('vs-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,4:2,5:3,6:4,7:5,8:6}.get(j)
    if k is not None:undo[k]^=1
   if fault.startswith('sy-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,5:3,6:4,7:5,8:6}.get(j)
    if k is not None:undo[k]^=1
   if fault=='sy-drop-undo':undo[2]=489
   if fault=='sy-wrong-undo':undo[2]^=1
   if fault.startswith('se-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,6:4,7:5,8:6}.get(j)
    if k is not None:undo[k]^=1
   if fault=='se-drop-undo':undo[3]=492
   if fault=='se-wrong-undo':undo[3]^=1
   if fault.startswith('ve-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,7:5,8:6}.get(j)
    if k is not None:undo[k]^=1
   if fault=='ve-drop-undo':undo[4]=479
   if fault=='ve-wrong-undo':undo[4]^=1
   assert [v[259]]+[v[263+3*i] for i in range(6)]==after
   assert [v[260]]+[v[264+3*i] for i in range(6)]==undo
   assert v[261]==sum(1<<i for i in range(7) if undo[i]!=ref[i])
  else:assert v[259:262]==[0xffffffff,0xffffffff,0] and all(v[i]==0xffffffff for i in [263,264,266,267,269,270,272,273,275,276,278,279])
 else:
  assert not vttrace
  assert v[256:280]==([0]*24 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*6)
 reached_vc=state['c13writes'] and v[1] in [0x811,0x81126,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_vc:
  ref=[719,479,524,724,729,0,719,104,48];before=ref.copy();attempted_vc=not fault.startswith('vc-before-')
  if not attempted_vc:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[280]]+[v[286+3*i] for i in range(8)]==before
  assert v[281:283]==([479,1] if attempted_vc else [0,0])
  assert vctrace==([(0x680808,479),(0x680808,719)] if attempted_vc else [])
  if attempted_vc:
   after=[479]+ref[1:];undo=ref.copy()
   if fault=='vc-drop-write':after[0]=719
   if fault=='vc-wrong-write':after[0]^=1
   if fault.startswith('vc-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('vc-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('vc-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='vc-drop-undo':undo[0]=479
   if fault=='vc-wrong-undo':undo[0]^=1
   if fault.startswith('vs-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,4:3,5:4,6:6,7:7,8:8}.get(j)
    if k is not None:undo[k]^=1
   if fault in ['vs-wrong-undo','vs-wrong-write-drop-undo']:undo[5]^=1
   if fault.startswith('sy-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,5:4,6:6,7:7,8:8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='sy-drop-undo':undo[3]=489
   if fault=='sy-wrong-undo':undo[3]^=1
   if fault.startswith('se-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,6:6,7:7,8:8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='se-drop-undo':undo[4]=492
   if fault=='se-wrong-undo':undo[4]^=1
   if fault.startswith('ve-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,7:7,8:8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='ve-drop-undo':undo[6]=479
   if fault=='ve-wrong-undo':undo[6]^=1
   assert [v[283]]+[v[287+3*i] for i in range(8)]==after
   assert [v[284]]+[v[288+3*i] for i in range(8)]==undo
   assert v[285]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[283:286]==[0xffffffff,0xffffffff,0] and all(v[287+3*i:289+3*i]==[0xffffffff]*2 for i in range(8))
 else:
  assert not vctrace
  assert v[280:310]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 reached_vs=state['c13writes'] and v[1] in [0x811,0x81128,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_vs:
  ref=[0,479,524,479,724,729,719,104,48];before=ref.copy();attempted_vs=not fault.startswith('vs-before-')
  if not attempted_vs:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[310]]+[v[316+3*i] for i in range(8)]==before
  assert v[311:313]==([0,1] if attempted_vs else [0,0])
  assert vstrace==([(0x680814,0),(0x680814,0)] if attempted_vs else [])
  if attempted_vs:
   after=ref.copy();undo=ref.copy()
   if fault in ['vs-wrong-write','vs-wrong-write-drop-undo']:after[0]=1
   if fault.startswith('vs-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('vs-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('vs-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault in ['vs-wrong-undo','vs-wrong-write-drop-undo']:undo[0]=1
   if fault.startswith('sy-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,3:3,5:5,6:6,7:7,8:8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='sy-drop-undo':undo[4]=489
   if fault=='sy-wrong-undo':undo[4]^=1
   if fault.startswith('se-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,3:3,6:6,7:7,8:8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='se-drop-undo':undo[5]=492
   if fault=='se-wrong-undo':undo[5]^=1
   if fault.startswith('ve-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,3:3,7:7,8:8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='ve-drop-undo':undo[6]=479
   if fault=='ve-wrong-undo':undo[6]^=1
   assert [v[313]]+[v[317+3*i] for i in range(8)]==after
   assert [v[314]]+[v[318+3*i] for i in range(8)]==undo
   assert v[315]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[313:316]==[0xffffffff,0xffffffff,0] and all(v[317+3*i:319+3*i]==[0xffffffff]*2 for i in range(8))
 else:
  assert not vstrace
  assert v[310:340]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 reached_sy=state['c13writes'] and v[1] in [0x811,0x8112a,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_sy:
  ref=[724,479,524,479,0,729,719,104,48];before=ref.copy();attempted_sy=not fault.startswith('sy-before-')
  if not attempted_sy:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[340]]+[v[346+3*i] for i in range(8)]==before
  assert v[341:343]==([489,1] if attempted_sy else [0,0])
  assert sytrace==([(0x68080c,489),(0x68080c,724)] if attempted_sy else [])
  if attempted_sy:
   after=[489]+ref[1:];undo=ref.copy()
   if fault=='sy-drop-write':after[0]=724
   if fault=='sy-wrong-write':after[0]^=1
   if fault.startswith('sy-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('sy-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('sy-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='sy-drop-undo':undo[0]=489
   if fault=='sy-wrong-undo':undo[0]^=1
   if fault.startswith('se-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,3:3,4:4,6:6,7:7,8:8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='se-drop-undo':undo[5]=492
   if fault=='se-wrong-undo':undo[5]^=1
   if fault.startswith('ve-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,3:3,4:4,7:7,8:8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='ve-drop-undo':undo[6]=479
   if fault=='ve-wrong-undo':undo[6]^=1
   assert [v[343]]+[v[347+3*i] for i in range(8)]==after
   assert [v[344]]+[v[348+3*i] for i in range(8)]==undo
   assert v[345]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[343:346]==[0xffffffff,0xffffffff,0] and all(v[347+3*i:349+3*i]==[0xffffffff]*2 for i in range(8))
 else:
  assert not sytrace
  assert v[340:370]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 reached_se=state['c13writes'] and v[1] in [0x811,0x8112c,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_se:
  ref=[729,479,524,479,0,489,719,104,48];before=ref.copy();attempted_se=not fault.startswith('se-before-')
  if not attempted_se:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[370]]+[v[376+3*i] for i in range(8)]==before
  assert v[371:373]==([492,1] if attempted_se else [0,0])
  assert setrace==([(0x680810,492),(0x680810,729)] if attempted_se else [])
  if attempted_se:
   after=[492]+ref[1:];undo=ref.copy()
   if fault=='se-drop-write':after[0]=729
   if fault=='se-wrong-write':after[0]^=1
   if fault.startswith('se-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('se-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('se-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='se-drop-undo':undo[0]=492
   if fault=='se-wrong-undo':undo[0]^=1
   assert [v[373]]+[v[377+3*i] for i in range(8)]==after
   if fault.startswith('ve-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,3:3,4:4,5:5,7:7,8:8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='ve-drop-undo':undo[6]=479
   if fault=='ve-wrong-undo':undo[6]^=1
   assert [v[374]]+[v[378+3*i] for i in range(8)]==undo
   assert v[375]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[373:376]==[0xffffffff,0xffffffff,0] and all(v[377+3*i:379+3*i]==[0xffffffff]*2 for i in range(8))
 else:
  assert not setrace
  assert v[370:400]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 reached_ve=state['c13writes'] and v[1] in [0x811,0x8112e,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_ve:
  ref=[719,479,524,479,0,489,492,104,48];before=ref.copy();attempted_ve=not fault.startswith('ve-before-')
  if not attempted_ve:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[400]]+[v[406+3*i] for i in range(8)]==before
  assert v[401:403]==([479,1] if attempted_ve else [0,0])
  assert vetrace==([(0x680818,479),(0x680818,719)] if attempted_ve else [])
  if attempted_ve:
   after=[479]+ref[1:];undo=ref.copy()
   if fault=='ve-drop-write':after[0]=719
   if fault=='ve-wrong-write':after[0]^=1
   if fault.startswith('ve-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('ve-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('ve-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='ve-drop-undo':undo[0]=479
   if fault=='ve-wrong-undo':undo[0]^=1
   assert [v[403]]+[v[407+3*i] for i in range(8)]==after
   assert [v[404]]+[v[408+3*i] for i in range(8)]==undo
   assert v[405]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[403:406]==[0xffffffff,0xffffffff,0] and all(v[407+3*i:409+3*i]==[0xffffffff]*2 for i in range(8))
 else:
  assert not vetrace
  assert v[400:430]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 reached_c7=state['c13writes'] and v[1] in [0x811,0x81130,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_c7:
  ref=[240,236,96,212,207,207,237,255,16];before=ref.copy()
  attempted_c7=not fault.startswith('c7-before-')
  if not attempted_c7:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[430]]+[v[436+3*i] for i in range(8)]==before
  assert v[431:433]==([116,1] if attempted_c7 else [0,0]) and state['c7writes']==2*int(attempted_c7)
  if attempted_c7:
   after=[116]+ref[1:];undo=ref.copy()
   if fault=='c7-drop-write':after[0]=240
   if fault=='c7-wrong-write':after[0]^=1
   if fault.startswith('c7-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('c7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('c7-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='c7-drop-undo':undo[0]=116
   if fault=='c7-wrong-undo':undo[0]^=1
   if fault.startswith('cl9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cl7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb15-drop-undo':undo[5]=223
   if fault=='cb15-wrong-undo':undo[5]=206
   if fault=='cb15-wrong-write-drop-undo':undo[5]=222
   if fault.startswith('cb15-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cb7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb9-drop-undo':undo[2]=64
   if fault=='cb9-wrong-undo':undo[2]=97
   if fault=='cb9-wrong-write-drop-undo':undo[2]=65
   if fault.startswith('cb9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cd12-drop-undo':undo[4]=223
   if fault=='cd12-wrong-undo':undo[4]=206
   if fault=='cd12-wrong-write-drop-undo':undo[4]=222
   if fault.startswith('cd12-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 2, 5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cd7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={2: 2, 4: 4, 5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='ct16-drop-undo':undo[6]=140
   if fault=='ct16-wrong-undo':undo[6]=236
   if fault=='ct16-wrong-write-drop-undo':undo[6]=141
   if fault.startswith('ct16-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 2, 5: 4, 6: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='ct6-drop-undo':undo[1]=12
   if fault=='ct6-wrong-undo':undo[1]=237
   if fault=='ct6-wrong-write-drop-undo':undo[1]=13
   if fault.startswith('ct6-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={2: 2, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('ct7-coupling-'):
    j=int(fault.rsplit('-',1)[1])
    if j!=3:undo[j]^=1
   if fault=='c10-drop-undo':undo[3]=233
   if fault=='c10-wrong-undo':undo[3]^=1
   if fault.startswith('c10-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1:1,3:2,4:4,5:5,6:6,7:7,8:8}
    if j in mapping:undo[mapping[j]]^=1
   assert [v[433]]+[v[437+3*i] for i in range(8)]==after
   assert [v[434]]+[v[438+3*i] for i in range(8)]==undo
   assert v[435]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[433:436]==[0xffffffff,0xffffffff,0] and all(v[437+3*i:439+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[430:460]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 # New CR10 fields and complete neighbor tuple, independent constants.
 reached_c10=state['c13writes'] and v[1] in [0x811,0x81132,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_c10:
  ref=[212,236,116,96,207,207,237,255,16];before=ref.copy()
  attempted_c10=not fault.startswith('c10-before-')
  if not attempted_c10:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[460]]+[v[466+3*i] for i in range(8)]==before
  assert v[461:463]==([233,1] if attempted_c10 else [0,0]) and state['c10writes']==2*int(attempted_c10)
  if attempted_c10:
   after=[233]+ref[1:];undo=ref.copy()
   if fault=='c10-drop-write':after[0]=212
   if fault=='c10-wrong-write':after[0]^=1
   if fault.startswith('c10-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('c10-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('c10-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='c10-drop-undo':undo[0]=233
   if fault=='c10-wrong-undo':undo[0]^=1
   if fault.startswith('cl9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cl7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb15-drop-undo':undo[5]=223
   if fault=='cb15-wrong-undo':undo[5]=206
   if fault=='cb15-wrong-write-drop-undo':undo[5]=222
   if fault.startswith('cb15-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cb7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb9-drop-undo':undo[3]=64
   if fault=='cb9-wrong-undo':undo[3]=97
   if fault=='cb9-wrong-write-drop-undo':undo[3]=65
   if fault.startswith('cb9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cd12-drop-undo':undo[4]=223
   if fault=='cd12-wrong-undo':undo[4]=206
   if fault=='cd12-wrong-write-drop-undo':undo[4]=222
   if fault.startswith('cd12-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cd7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={2: 3, 4: 4, 5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='ct16-drop-undo':undo[6]=140
   if fault=='ct16-wrong-undo':undo[6]=236
   if fault=='ct16-wrong-write-drop-undo':undo[6]=141
   if fault.startswith('ct16-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 5: 4, 6: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='ct6-drop-undo':undo[1]=12
   if fault=='ct6-wrong-undo':undo[1]=237
   if fault=='ct6-wrong-write-drop-undo':undo[1]=13
   if fault.startswith('ct6-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={2: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:undo[2]^=1
   if fault.startswith('ct7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1:1,2:3,4:4,5:5,6:6,7:7,8:8}
    if j in mapping:undo[mapping[j]]^=1
   assert [v[463]]+[v[467+3*i] for i in range(8)]==after
   assert [v[464]]+[v[468+3*i] for i in range(8)]==undo
   assert v[465]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[463:466]==[0xffffffff,0xffffffff,0] and all(v[467+3*i:469+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[460:490]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 # Exact new shared-CR07 tuple with independently specified constants.
 reached_ct7=state['c13writes'] and v[1] in [0x811,0x81134,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_ct7:
  ref=[116,236,96,233,207,207,237,255,16];before=ref.copy()
  attempted_ct7=not fault.startswith('ct7-before-')
  if not attempted_ct7:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[490]]+[v[496+3*i] for i in range(8)]==before
  assert v[491:493]==([116,1] if attempted_ct7 else [0,0]) and state['ct7writes']==2*int(attempted_ct7)
  if attempted_ct7:
   after=ref.copy();undo=ref.copy()
   if fault in ['ct7-wrong-write','ct7-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('ct7-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('ct7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('ct7-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:undo[0]^=1
   if fault.startswith('cl9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cl7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb15-drop-undo':undo[5]=223
   if fault=='cb15-wrong-undo':undo[5]=206
   if fault=='cb15-wrong-write-drop-undo':undo[5]=222
   if fault.startswith('cb15-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={4: 3, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cb7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb9-drop-undo':undo[2]=64
   if fault=='cb9-wrong-undo':undo[2]=97
   if fault=='cb9-wrong-write-drop-undo':undo[2]=65
   if fault.startswith('cb9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cd12-drop-undo':undo[4]=223
   if fault=='cd12-wrong-undo':undo[4]=206
   if fault=='cd12-wrong-write-drop-undo':undo[4]=222
   if fault.startswith('cd12-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 2, 4: 3, 5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cd7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={2: 2, 3: 3, 4: 4, 5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='ct16-drop-undo':undo[6]=140
   if fault=='ct16-wrong-undo':undo[6]=236
   if fault=='ct16-wrong-write-drop-undo':undo[6]=141
   if fault.startswith('ct16-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 2, 4: 3, 5: 4, 6: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='ct6-drop-undo':undo[1]=12
   if fault=='ct6-wrong-undo':undo[1]=237
   if fault=='ct6-wrong-write-drop-undo':undo[1]=13
   if fault.startswith('ct6-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   assert [v[493]]+[v[497+3*i] for i in range(8)]==after
   assert [v[494]]+[v[498+3*i] for i in range(8)]==undo
   assert v[495]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[493:496]==[0xffffffff,0xffffffff,0] and all(v[497+3*i:499+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[490:520]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 # Independent CR06 tuple: total 524 -> low byte 12, saved byte 236.
 reached_ct6=state['c13writes'] and v[1] in [0x811,0x81136,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_ct6:
  ref=[236,116,96,233,207,207,237,255,16];before=ref.copy()
  attempted_ct6=not fault.startswith('ct6-before-')
  if not attempted_ct6:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[520]]+[v[526+3*i] for i in range(8)]==before
  assert v[521:523]==([12,1] if attempted_ct6 else [0,0]) and state['ct6writes']==2*int(attempted_ct6)
  if attempted_ct6:
   after=ref.copy();after[0]=12;undo=ref.copy()
   if fault=='ct6-drop-write':after[0]=236
   if fault in ['ct6-wrong-write','ct6-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('ct6-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('ct6-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('ct6-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='ct6-drop-undo':undo[0]=12
   if fault=='ct6-wrong-undo':undo[0]=237
   if fault.startswith('cl9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cl7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb15-drop-undo':undo[5]=223
   if fault=='cb15-wrong-undo':undo[5]=206
   if fault=='cb15-wrong-write-drop-undo':undo[5]=222
   if fault.startswith('cb15-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={4: 3, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cb7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb9-drop-undo':undo[2]=64
   if fault=='cb9-wrong-undo':undo[2]=97
   if fault=='cb9-wrong-write-drop-undo':undo[2]=65
   if fault.startswith('cb9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cd12-drop-undo':undo[4]=223
   if fault=='cd12-wrong-undo':undo[4]=206
   if fault=='cd12-wrong-write-drop-undo':undo[4]=222
   if fault.startswith('cd12-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={3: 2, 4: 3, 5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cd7-drop-undo':undo[1]=54
   if fault=='cd7-wrong-undo':undo[1]=117
   if fault=='cd7-wrong-write-drop-undo':undo[1]=55
   if fault.startswith('cd7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={2: 2, 3: 3, 4: 4, 5: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='ct16-drop-undo':undo[6]=140
   if fault=='ct16-wrong-undo':undo[6]=236
   if fault=='ct16-wrong-write-drop-undo':undo[6]=141
   if fault.startswith('ct16-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='ct6-wrong-write-drop-undo':undo[0]=13
   assert [v[523]]+[v[527+3*i] for i in range(8)]==after
   assert [v[524]]+[v[528+3*i] for i in range(8)]==undo
   assert v[525]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[523:526]==[0xffffffff,0xffffffff,0] and all(v[527+3*i:529+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[520:550]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 # Independent CR16 tuple: saved ED, preserve bit7, total524 low7 =>8C.
 reached_ct16=state['c13writes'] and v[1] in [0x811,0x81138,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_ct16:
  ref=[237,12,116,96,233,207,207,255,16];before=ref.copy()
  attempted_ct16=not fault.startswith('ct16-before-')
  if not attempted_ct16:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[550]]+[v[556+3*i] for i in range(8)]==before
  assert v[551:553]==([140,1] if attempted_ct16 else [0,0]) and state['ct16writes']==2*int(attempted_ct16)
  if attempted_ct16:
   after=ref.copy();after[0]=140;undo=ref.copy()
   if fault=='ct16-drop-write':after[0]=237
   if fault in ['ct16-wrong-write','ct16-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('ct16-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('ct16-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('ct16-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='ct16-drop-undo':undo[0]=140
   if fault=='ct16-wrong-undo':undo[0]=236
   if fault.startswith('cl9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 4, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cl7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 4, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb15-drop-undo':undo[6]=223
   if fault=='cb15-wrong-undo':undo[6]=206
   if fault=='cb15-wrong-write-drop-undo':undo[6]=222
   if fault.startswith('cb15-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 4: 4, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cb7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 4, 5: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb9-drop-undo':undo[3]=64
   if fault=='cb9-wrong-undo':undo[3]=97
   if fault=='cb9-wrong-write-drop-undo':undo[3]=65
   if fault.startswith('cb9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 4, 5: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cd12-drop-undo':undo[5]=223
   if fault=='cd12-wrong-undo':undo[5]=206
   if fault=='cd12-wrong-write-drop-undo':undo[5]=222
   if fault.startswith('cd12-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 4: 4, 5: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cd7-drop-undo':undo[2]=54
   if fault=='cd7-wrong-undo':undo[2]=117
   if fault=='cd7-wrong-write-drop-undo':undo[2]=55
   if fault.startswith('cd7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 2: 3, 3: 4, 4: 5, 5: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='ct16-wrong-write-drop-undo':undo[0]=141
   assert [v[553]]+[v[557+3*i] for i in range(8)]==after
   assert [v[554]]+[v[558+3*i] for i in range(8)]==undo
   assert v[555]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[553:556]==[0xffffffff,0xffffffff,0] and all(v[557+3*i:559+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[550:580]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 # Independently specified CR07 display-end target and complete neighboring tuple.
 reached_cd7=state['c13writes'] and v[1] in [0x811,0x8113a,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_cd7:
  ref=[116,12,96,233,207,207,140,255,16];before=ref.copy()
  attempted_cd7=not fault.startswith('cd7-before-')
  if not attempted_cd7:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[580]]+[v[586+3*i] for i in range(8)]==before
  assert v[581:583]==([54,1] if attempted_cd7 else [0,0]) and state['cd7writes']==2*int(attempted_cd7)
  if attempted_cd7:
   after=ref.copy();after[0]=54;undo=ref.copy()
   if fault=='cd7-drop-write':after[0]=116
   if fault in ['cd7-wrong-write','cd7-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cd7-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cd7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cd7-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='cd7-drop-undo':undo[0]=54
   if fault=='cd7-wrong-undo':undo[0]=117
   if fault.startswith('cl9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cl7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb15-drop-undo':undo[5]=223
   if fault=='cb15-wrong-undo':undo[5]=206
   if fault=='cb15-wrong-write-drop-undo':undo[5]=222
   if fault.startswith('cb15-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 4: 3, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cb7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 5: 5, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb9-drop-undo':undo[2]=64
   if fault=='cb9-wrong-undo':undo[2]=97
   if fault=='cb9-wrong-write-drop-undo':undo[2]=65
   if fault.startswith('cb9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 5: 5, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cd12-drop-undo':undo[4]=223
   if fault=='cd12-wrong-undo':undo[4]=206
   if fault=='cd12-wrong-write-drop-undo':undo[4]=222
   if fault.startswith('cd12-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 2, 4: 3, 5: 5, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cd7-wrong-write-drop-undo':undo[0]=55
   assert [v[583]]+[v[587+3*i] for i in range(8)]==after
   assert [v[584]]+[v[588+3*i] for i in range(8)]==undo
   assert v[585]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[583:586]==[0xffffffff,0xffffffff,0] and all(v[587+3*i:589+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[580:610]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 # Independently specified complete CR12 transaction tuple.
 reached_cd12=state['c13writes'] and v[1] in [0x811,0x8113c,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_cd12:
  ref=[207,12,54,96,233,207,140,255,16];before=ref.copy()
  attempted_cd12=not fault.startswith('cd12-before-')
  if not attempted_cd12:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[610]]+[v[616+3*i] for i in range(8)]==before
  assert v[611:613]==([223,1] if attempted_cd12 else [0,0]) and state['cd12writes']==2*int(attempted_cd12)
  if attempted_cd12:
   after=ref.copy();after[0]=223;undo=ref.copy()
   if fault=='cd12-drop-write':after[0]=207
   if fault in ['cd12-wrong-write','cd12-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cd12-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cd12-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cd12-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='cd12-drop-undo':undo[0]=223
   if fault=='cd12-wrong-undo':undo[0]=206
   if fault.startswith('cl9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 4, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cl7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 4, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb15-drop-undo':undo[5]=223
   if fault=='cb15-wrong-undo':undo[5]=206
   if fault=='cb15-wrong-write-drop-undo':undo[5]=222
   if fault.startswith('cb15-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 4: 4, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb7-drop-undo':undo[2]=62
   if fault=='cb7-wrong-undo':undo[2]=55
   if fault=='cb7-wrong-write-drop-undo':undo[2]=63
   if fault.startswith('cb7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 4, 5: 5, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb9-drop-undo':undo[3]=64
   if fault=='cb9-wrong-undo':undo[3]=97
   if fault=='cb9-wrong-write-drop-undo':undo[3]=65
   if fault.startswith('cb9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 2: 2, 3: 4, 5: 5, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cd12-wrong-write-drop-undo':undo[0]=222
   assert [v[613]]+[v[617+3*i] for i in range(8)]==after
   assert [v[614]]+[v[618+3*i] for i in range(8)]==undo
   assert v[615]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[613:616]==[0xffffffff,0xffffffff,0] and all(v[617+3*i:619+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[610:640]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 # Complete CR09 transaction tuple, independently specified.
 reached_cb9=state['c13writes'] and v[1] in [0x811,0x8113e,0x81140,0x81142,0x81144,0x81146]
 if reached_cb9:
  ref=[96,12,54,233,223,207,140,255,16];before=ref.copy()
  attempted_cb9=not fault.startswith('cb9-before-')
  if not attempted_cb9:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[640]]+[v[646+3*i] for i in range(8)]==before
  assert v[641:643]==([64,1] if attempted_cb9 else [0,0]) and state['cb9writes']==2*int(attempted_cb9)
  if attempted_cb9:
   after=ref.copy();after[0]=64;undo=ref.copy()
   if fault=='cb9-drop-write':after[0]=96
   if fault in ['cb9-wrong-write','cb9-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cb9-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cb9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cb9-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='cb9-drop-undo':undo[0]=64
   if fault=='cb9-wrong-undo':undo[0]=97
   if fault.startswith('cl9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 4: 4, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cl7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 4: 4, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb15-drop-undo':undo[5]=223
   if fault=='cb15-wrong-undo':undo[5]=206
   if fault=='cb15-wrong-write-drop-undo':undo[5]=222
   if fault.startswith('cb15-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 4: 3, 5: 4, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb7-drop-undo':undo[2]=62
   if fault=='cb7-wrong-undo':undo[2]=55
   if fault=='cb7-wrong-write-drop-undo':undo[2]=63
   if fault.startswith('cb7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb9-wrong-write-drop-undo':undo[0]=65
   assert [v[643]]+[v[647+3*i] for i in range(8)]==after
   assert [v[644]]+[v[648+3*i] for i in range(8)]==undo
   assert v[645]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[643:646]==[0xffffffff,0xffffffff,0] and all(v[647+3*i:649+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[640:670]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 # Complete new transaction, independent literals and masks.
 reached_cb7=state['c13writes'] and v[1] in [0x811,0x81140,0x81142,0x81144,0x81146]
 if reached_cb7:
  ref=[54,12,64,233,223,207,140,255,16];before=ref.copy()
  attempted_cb7=not fault.startswith('cb7-before-')
  if not attempted_cb7:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[670]]+[v[676+3*i] for i in range(8)]==before
  assert v[671:673]==([62,1] if attempted_cb7 else [0,0]) and state['cb7writes']==2*int(attempted_cb7)
  if attempted_cb7:
   after=ref.copy();after[0]=62;undo=ref.copy()
   if fault=='cb7-drop-write':after[0]=54
   if fault in ['cb7-wrong-write','cb7-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cb7-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cb7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cb7-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='cb7-drop-undo':undo[0]=62
   if fault=='cb7-wrong-undo':undo[0]=55
   if fault in ['cl9-wrong-undo','cl9-wrong-write-drop-undo']:undo[2]=65
   if fault.startswith('cl9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 4: 4, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault.startswith('cl7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 2: 2, 3: 3, 4: 4, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb15-drop-undo':undo[5]=223
   if fault=='cb15-wrong-undo':undo[5]=206
   if fault=='cb15-wrong-write-drop-undo':undo[5]=222
   if fault.startswith('cb15-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 2, 4: 3, 5: 4, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb7-wrong-write-drop-undo':undo[0]=63
   assert [v[673]]+[v[677+3*i] for i in range(8)]==after
   assert [v[674]]+[v[678+3*i] for i in range(8)]==undo
   assert v[675]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[673:676]==[0xffffffff,0xffffffff,0] and all(v[677+3*i:679+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[670:700]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 # Complete CR15 transaction, independently enumerated literals and masks.
 reached_cb15=state['c13writes'] and v[1] in [0x811,0x81142,0x81144,0x81146]
 if reached_cb15:
  ref=[207,12,62,64,233,223,140,255,16];before=ref.copy()
  attempted_cb15=not fault.startswith('cb15-before-')
  if not attempted_cb15:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[700]]+[v[706+3*i] for i in range(8)]==before
  assert v[701:703]==([223,1] if attempted_cb15 else [0,0]) and state['cb15writes']==2*int(attempted_cb15)
  if attempted_cb15:
   after=ref.copy();after[0]=223;undo=ref.copy()
   if fault=='cb15-drop-write':after[0]=207
   if fault in ['cb15-wrong-write','cb15-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cb15-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cb15-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cb15-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='cb15-drop-undo':undo[0]=223
   if fault=='cb15-wrong-undo':undo[0]=206
   if fault=='cb15-wrong-write-drop-undo':undo[0]=222
   if fault in ['cl9-wrong-undo','cl9-wrong-write-drop-undo']:undo[3]=65
   if fault.startswith('cl9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 4, 4: 5, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault in ['cl7-wrong-undo','cl7-wrong-write-drop-undo']:undo[2]=63
   if fault.startswith('cl7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 2: 3, 3: 4, 4: 5, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   assert [v[703]]+[v[707+3*i] for i in range(8)]==after
   assert [v[704]]+[v[708+3*i] for i in range(8)]==undo
   assert v[705]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[703:706]==[0xffffffff,0xffffffff,0] and all(v[707+3*i:709+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[700:730]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 # Same-value operation: missing write/undo is observably identical here.
 reached_cl7=state['c13writes'] and v[1] in [0x811,0x81144,0x81146]
 if reached_cl7:
  ref=[62,12,64,233,223,223,140,255,16];before=ref.copy()
  attempted_cl7=not fault.startswith('cl7-before-')
  if not attempted_cl7:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[730]]+[v[736+3*i] for i in range(8)]==before
  assert v[731:733]==([62,1] if attempted_cl7 else [0,0]) and state['cl7writes']==2*int(attempted_cl7)
  if attempted_cl7:
   after=ref.copy();undo=ref.copy()
   if fault in ['cl7-wrong-write','cl7-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cl7-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cl7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cl7-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault in ['cl7-wrong-undo','cl7-wrong-write-drop-undo']:undo[0]=63
   if fault in ['cl9-wrong-undo','cl9-wrong-write-drop-undo']:undo[2]=65
   if fault.startswith('cl9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   assert [v[733]]+[v[737+3*i] for i in range(8)]==after
   assert [v[734]]+[v[738+3*i] for i in range(8)]==undo
   assert v[735]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[733:736]==[0xffffffff,0xffffffff,0] and all(v[737+3*i:739+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[730:760]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 # Same-value operation: missing write/undo is observably identical here.
 reached_cl9=state['c13writes'] and v[1] in [0x811,0x81146]
 if reached_cl9:
  ref=[64,12,62,233,223,223,140,255,16];before=ref.copy()
  attempted_cl9=not fault.startswith('cl9-before-')
  if not attempted_cl9:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[760]]+[v[766+3*i] for i in range(8)]==before
  assert v[761:763]==([64,1] if attempted_cl9 else [0,0]) and state['cl9writes']==2*int(attempted_cl9)
  if attempted_cl9:
   after=ref.copy();undo=ref.copy()
   if fault in ['cl9-wrong-write','cl9-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cl9-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cl9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cl9-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault in ['cl9-wrong-undo','cl9-wrong-write-drop-undo']:undo[0]=65
   assert [v[763]]+[v[767+3*i] for i in range(8)]==after
   assert [v[764]]+[v[768+3*i] for i in range(8)]==undo
   assert v[765]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[763:766]==[0xffffffff,0xffffffff,0] and all(v[767+3*i:769+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[760:790]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
 for lo,hi in [(0,0x880),(0x900,0x6800),(0x7458,0x7d04)]:assert final[lo:hi]==initial[lo:hi]
 for pointer in (base-4096,base+32768):assert bytes(c.mem_read(pointer,4096))==b'G'*4096
 for pointer in (FB-4096,FB+SIZE):assert bytes(c.mem_read(pointer,4096))==b'Z'*4096
 if not refusal:
  assert (c.reg_read(x.UC_X86_REG_EAX) if direct else struct.unpack_from('<I',final,0x8d4)[0])==want
  if badarg!=3:assert v[0]==want
  if want>=0x811:
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
  if want==0x811:assert v[28:31]==[1,1,0] and v[1]==0x811
  if fault=='cr1b05':assert v[1]==0x8118 and v[28:31]==[1,1,0]
 expected_image=bytearray(b'Z'*SIZE)
 if not direct:
  expected_trace=[['read',0xcf8]]
  for sel in SELECT:expected_trace.extend([['write',0xcf8,sel],['read',0xcfc,sel]])
  expected_trace.append(['write',0xcf8,0x12345678]);assert trace==expected_trace and state['selector']==0x12345678
  phase=2 if refusal else 4;stage=refusal if refusal else 5
  assert struct.unpack_from('<I',final,0x880)[0]==phase and struct.unpack_from('<I',final,0x8d0)[0]==stage
  color={1:0xff0000,2:0xffff00,3:0xff00ff,4:0xff8000,5:0xffffff}[refusal] if refusal else 0x00ff00 if want==0x811 else 0xff8000
  for row0,rgb in [(8,0x00ff00),(48,color)]:
   for row in range(row0,row0+32):expected_image[row*5120+32:row*5120+5088]=pack(rgb)*1264
  words=[0x8110000d,0 if refusal else want,v[30],v[100],v[108],v[645],v[675],v[705],v[735],v[765],v[760],v[763],v[764]]
  paint_report(expected_image,words)
 else:assert not trace and not state['ticks']
 assert bytes(c.mem_read(FB,SIZE))==expected_image
 R['cases'].append({'name':name,'layout':layout,'return':want,'refusal':refusal,'MMIO_writes':mw,'vertical_valid_end_writes':vetrace,'vertical_sync_end_writes':setrace,'vertical_sync_start_writes':sytrace,'vertical_valid_start_writes':vstrace,'vertical_crtc_writes':vctrace,'vertical_total_writes':vttrace,'vertical_writes':vtrace,'horizontal_writes':htrace,'CRTC_writes':cw,'deferred_checks':checked,'raw_result':v,'all_pixels_and_guards_exact':True,'stack_bytes_written_from_top':sp-minstack[0],'admitted_stack_bytes':768})
try:
 for phase in ['before','after','undo']:
  for j in range(9):run('cl9-'+phase+'-'+str(j),want=0x81147 if phase=='undo' else 0x81146,fault='cl9-'+phase+'-'+str(j))
 for j in range(1,9):run('cl9-coupling-'+str(j),want=0x81147,fault='cl9-coupling-'+str(j))
 for f in ['cl9-drop-write','cl9-wrong-write','cl9-drop-undo','cl9-wrong-undo','cl9-wrong-write-drop-undo']:
  run(f,want=0x811 if f in ['cl9-drop-write','cl9-drop-undo'] else 0x81146 if f=='cl9-wrong-write' else 0x81147,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('cl7-'+phase+'-'+str(j),want=0x81145 if phase=='undo' else 0x81144,fault='cl7-'+phase+'-'+str(j))
 for j in range(1,9):run('cl7-coupling-'+str(j),want=0x81145,fault='cl7-coupling-'+str(j))
 for f in ['cl7-drop-write','cl7-wrong-write','cl7-drop-undo','cl7-wrong-undo','cl7-wrong-write-drop-undo']:
  run(f,want=0x811 if f in ['cl7-drop-write','cl7-drop-undo'] else 0x81144 if f=='cl7-wrong-write' else 0x81145,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('cb15-'+phase+'-'+str(j),want=0x81143 if phase=='undo' else 0x81142,fault='cb15-'+phase+'-'+str(j))
 for j in range(1,9):run('cb15-coupling-'+str(j),want=0x81143,fault='cb15-coupling-'+str(j))
 for f in ['cb15-drop-write','cb15-wrong-write','cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:
  run(f,want=0x81142 if f in ['cb15-drop-write','cb15-wrong-write'] else 0x81143,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('cb7-'+phase+'-'+str(j),want=0x81141 if phase=='undo' else 0x81140,fault='cb7-'+phase+'-'+str(j))
 for j in range(1,9):run('cb7-coupling-'+str(j),want=0x81141,fault='cb7-coupling-'+str(j))
 for f in ['cb7-drop-write','cb7-wrong-write','cb7-drop-undo','cb7-wrong-undo','cb7-wrong-write-drop-undo']:
  run(f,want=0x81140 if f in ['cb7-drop-write','cb7-wrong-write'] else 0x81141,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('cb9-'+phase+'-'+str(j),want=0x8113f if phase=='undo' else 0x8113e,fault='cb9-'+phase+'-'+str(j))
 for j in range(1,9):run('cb9-coupling-'+str(j),want=0x8113f,fault='cb9-coupling-'+str(j))
 for f in ['cb9-drop-write','cb9-wrong-write','cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:
  run(f,want=0x8113e if f in ['cb9-drop-write','cb9-wrong-write'] else 0x8113f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('cd12-'+phase+'-'+str(j),want=0x8113d if phase=='undo' else 0x8113c,fault='cd12-'+phase+'-'+str(j))
 for j in range(1,9):run('cd12-coupling-'+str(j),want=0x8113d,fault='cd12-coupling-'+str(j))
 for f in ['cd12-drop-write','cd12-wrong-write','cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo']:
  run(f,want=0x8113c if f in ['cd12-drop-write','cd12-wrong-write'] else 0x8113d,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('cd7-'+phase+'-'+str(j),want=0x8113b if phase=='undo' else 0x8113a,fault='cd7-'+phase+'-'+str(j))
 for j in range(1,9):run('cd7-coupling-'+str(j),want=0x8113b,fault='cd7-coupling-'+str(j))
 for f in ['cd7-drop-write','cd7-wrong-write','cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo']:
  run(f,want=0x8113a if f in ['cd7-drop-write','cd7-wrong-write'] else 0x8113b,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('ct16-'+phase+'-'+str(j),want=0x81139 if phase=='undo' else 0x81138,fault='ct16-'+phase+'-'+str(j))
 for j in range(1,9):run('ct16-coupling-'+str(j),want=0x81139,fault='ct16-coupling-'+str(j))
 for f in ['ct16-drop-write','ct16-wrong-write','ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo']:
  run(f,want=0x81138 if f in ['ct16-drop-write','ct16-wrong-write'] else 0x81139,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('ct6-'+phase+'-'+str(j),want=0x81137 if phase=='undo' else 0x81136,fault='ct6-'+phase+'-'+str(j))
 for j in range(1,9):run('ct6-coupling-'+str(j),want=0x81137,fault='ct6-coupling-'+str(j))
 for f in ['ct6-drop-write','ct6-wrong-write','ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo']:
  run(f,want=0x81136 if f in ['ct6-drop-write','ct6-wrong-write'] else 0x81137,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('ct7-'+phase+'-'+str(j),want=0x81135 if phase=='undo' else 0x81134,fault='ct7-'+phase+'-'+str(j))
 for j in range(1,9):run('ct7-coupling-'+str(j),want=0x81135,fault='ct7-coupling-'+str(j))
 for f in ['ct7-drop-write','ct7-wrong-write','ct7-drop-undo','ct7-wrong-undo','ct7-wrong-write-drop-undo']:
  run(f,want=0x811 if f in ['ct7-drop-write','ct7-drop-undo'] else 0x81134 if f=='ct7-wrong-write' else 0x81135,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('c10-'+phase+'-'+str(j),want=0x81133 if phase=='undo' else 0x81132,fault='c10-'+phase+'-'+str(j))
 for j in range(1,9):run('c10-coupling-'+str(j),want=0x81133,fault='c10-coupling-'+str(j))
 for f in ['c10-drop-write','c10-wrong-write','c10-drop-undo','c10-wrong-undo']:run(f,want=0x81133 if f.endswith('undo') else 0x81132,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('c7-'+phase+'-'+str(j),want=0x81131 if phase=='undo' else 0x81130,fault='c7-'+phase+'-'+str(j))
 for j in range(1,9):run('c7-coupling-'+str(j),want=0x81131,fault='c7-coupling-'+str(j))
 for f in ['c7-drop-write','c7-wrong-write','c7-drop-undo','c7-wrong-undo']:run(f,want=0x81131 if f.endswith('undo') else 0x81130,fault=f)
 for phase in ['before','after','undo']:
  for j in range(7):run('v-'+phase+'-'+str(j),want=0x81123 if phase=='undo' else 0x81122,fault='v-'+phase+'-'+str(j))
 for j in range(1,7):run('v-coupling-'+str(j),want=0x81123,fault='v-coupling-'+str(j))
 for f in ['v-drop-write','v-wrong-write','v-drop-undo','v-wrong-undo']:run(f,want=0x81123 if f.endswith('undo') else 0x81122,fault=f)
 for phase in ['before','after','undo']:
  for j in range(7):run('vt-'+phase+'-'+str(j),want=0x81125 if phase=='undo' else 0x81124,fault='vt-'+phase+'-'+str(j))
 for j in range(1,7):run('vt-coupling-'+str(j),want=0x81125,fault='vt-coupling-'+str(j))
 for f in ['vt-drop-write','vt-wrong-write','vt-drop-undo','vt-wrong-undo']:run(f,want=0x81125 if f.endswith('undo') else 0x81124,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('vc-'+phase+'-'+str(j),want=0x81127 if phase=='undo' else 0x81126,fault='vc-'+phase+'-'+str(j))
 for j in range(1,9):run('vc-coupling-'+str(j),want=0x81127,fault='vc-coupling-'+str(j))
 for f in ['vc-drop-write','vc-wrong-write','vc-drop-undo','vc-wrong-undo']:run(f,want=0x81127 if f.endswith('undo') else 0x81126,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('vs-'+phase+'-'+str(j),want=0x81129 if phase=='undo' else 0x81128,fault='vs-'+phase+'-'+str(j))
 for j in range(1,9):run('vs-coupling-'+str(j),want=0x81129,fault='vs-coupling-'+str(j))
 for f in ['vs-drop-write','vs-wrong-write','vs-drop-undo','vs-wrong-undo','vs-wrong-write-drop-undo']:run(f,want=0x811 if f in ['vs-drop-write','vs-drop-undo'] else 0x81129 if f.endswith('undo') else 0x81128,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('sy-'+phase+'-'+str(j),want=0x8112b if phase=='undo' else 0x8112a,fault='sy-'+phase+'-'+str(j))
 for j in range(1,9):run('sy-coupling-'+str(j),want=0x8112b,fault='sy-coupling-'+str(j))
 for f in ['sy-drop-write','sy-wrong-write','sy-drop-undo','sy-wrong-undo']:run(f,want=0x8112b if f.endswith('undo') else 0x8112a,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('se-'+phase+'-'+str(j),want=0x8112d if phase=='undo' else 0x8112c,fault='se-'+phase+'-'+str(j))
 for j in range(1,9):run('se-coupling-'+str(j),want=0x8112d,fault='se-coupling-'+str(j))
 for f in ['se-drop-write','se-wrong-write','se-drop-undo','se-wrong-undo']:run(f,want=0x8112d if f.endswith('undo') else 0x8112c,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('ve-'+phase+'-'+str(j),want=0x8112f if phase=='undo' else 0x8112e,fault='ve-'+phase+'-'+str(j))
 for j in range(1,9):run('ve-coupling-'+str(j),want=0x8112f,fault='ve-coupling-'+str(j))
 for f in ['ve-drop-write','ve-wrong-write','ve-drop-undo','ve-wrong-undo']:run(f,want=0x8112f if f.endswith('undo') else 0x8112e,fault=f)
 for layout in ('dual','relocated'):run('prefix-'+layout,layout)
 for i in range(15):run('first-mismatch-'+str(i),want=0x8118,first=i,read_fault=i+1)
 run('CR1b05-preservation-mismatch',want=0x8118,first=14,fault='cr1b05')
 for a,val in [(0x1b,5),(0x22,255),(0x14,1),(0x17,0xe2),(0x33,0)]:run('baseline-cr'+hex(a),want=0x8112,nmm=0,ncr=0,cr_bad=(a,val))
 for a,val in [(0x680884,1),(0x680630,2)]:run('baseline-mm'+hex(a),want=0x8112,nmm=0,ncr=0,mm_bad=(a,val))
 for fault,want,mm,cr in [('blank',0x8113,0,0),('unlock11',0x8115,0,0),('restore630',0x8115,11,3),('restore_cr19',0x8115,11,3),('restore_seq',0x8115,11,3)]:run(fault,want=want,nmm=mm,ncr=cr,fault=fault)
 for stage,sel,val in [(1,SELECT[0],0),(1,SELECT[1],0),(1,SELECT[2],0),(2,SELECT[3],0),(2,SELECT[4],0),(2,SELECT[5],0),(3,SELECT[6],0),(3,SELECT[7],0),(3,SELECT[8],0x8001),(3,SELECT[9],0)]:run('pci-'+hex(sel),refusal=stage,pci_bad=(sel,val),nmm=0,ncr=0)
 for timer in ('stall','backwards','jump'):run('timer-'+timer,refusal=5,timer=timer,nmm=0,ncr=0)
 for timer in ('wrap','minimum','maximum'):run('timer-'+timer,timer=timer)
 for arg in range(4):run('null-'+str(arg),want=2,nmm=0,ncr=0,direct=True,badarg=arg)
 run('IF-refusal',want=4,nmm=0,ncr=0,direct=True,flags=0x202)
 run('PAE-refusal',want=0x8111,nmm=0,ncr=0,direct=True,cpu4=0x20)
 run('wrapper-baseline',want=5,nmm=0,ncr=0,mm_bad=(0x680508,0))
 for a in [4,5]:run('CRTC-baseline-'+str(a),want=0x8112,nmm=0,ncr=0,cr_bad=(a,0))
 for fault in ['c4-read','c4-write','c5-read','c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling','c5-drop-restore']:
  want=0x811b if fault in ['c4-read','c4-write','c5-read'] else 0x811c
  run(fault,want=want,fault=fault)
 for fault in ['c5-drop-write','c5-low-read','c5-high-read','c4-after-read','c4-coupling']:run(fault,want=0x811d,fault=fault)
 run('CRTC-baseline-0',want=0x8112,nmm=0,ncr=0,cr_bad=(0,0))
 for fault in ['c0-read','c0-drop-write','c0-restore-read','c0-drop-restore','c4-after-c0-read','c5-after-c0-read','c0-c4-coupling','c0-c5-coupling']:run(fault,want=0x811f if fault in ['c0-restore-read','c0-drop-restore'] else 0x811e,fault=fault)
 run('CRTC-baseline-2',want=0x8112,nmm=0,ncr=0,cr_bad=(2,0))
 for fault in ['c2-read','c2-drop-write','c2-restore-read','c2-drop-restore','c0-after-c2-read','c4-after-c2-read','c5-after-c2-read','c2-c0-coupling','c2-c4-coupling','c2-c5-coupling']:run(fault,want=0x81111 if fault in ['c2-restore-read','c2-drop-restore'] else 0x81110,fault=fault)
 run('CRTC-baseline-3',want=0x8112,nmm=0,ncr=0,cr_bad=(3,0))
 for fault in ['c3-read','c3-high-read','c3-drop-write','c3-restore-read','c3-drop-restore']+['c'+str(i)+'-after-c3-read' for i in [0,2,4,5]]+['c3-c'+str(i)+'-coupling' for i in [0,2,4,5]]:run(fault,want=0x81113 if fault in ['c3-restore-read','c3-drop-restore'] else 0x81112,fault=fault)
 for fault in ['c5b-read','c5b-high-read','c5b-drop-write','c5b-wrong-write']+['c'+str(i)+'-after-c5b-read' for i in [0,2,3,4]]+['c5b-c'+str(i)+'-coupling' for i in [0,2,3,4]]+['c5b-undo-read','c5b-drop-undo']:run(fault,want=0x81115 if fault in ['c5b-undo-read','c5b-drop-undo'] else 0x81114,fault=fault)
 for fault in ['c17-before-read','c17-read','c17-high-read','c17-drop-write','c17-wrong-write']+['c'+str(i)+'-after-c17-read' for i in [0,2,3,4,5]]+['c17-c'+str(i)+'-coupling' for i in [0,2,3,4,5]]+['c17-undo-read','c17-drop-undo']:run(fault,want=0x81117 if fault in ['c17-undo-read','c17-drop-undo'] else 0x81116,fault=fault)
 for fault in ['c1-read','c1-high-read','c1-drop-write','c1-wrong-write']+['c'+str(i)+'-after-c1-read' for i in [0,2,3,4,5,0x17]]+['c1-c'+str(i)+'-coupling' for i in [0,2,3,4,5,0x17]]+['c1-undo-read','c1-drop-undo']:run(fault,want=0x81119 if fault in ['c1-undo-read','c1-drop-undo'] else 0x81118,fault=fault)
 for value in [0,255]:run('CR01-own-value-'+str(value),c1_original=value)
 for fault in ['c2b-before-read','c2b-read','c2b-high-read','c2b-wrong-write','c2b-wrong-write-drop-undo']+['c'+str(i)+'-after-c2b-read' for i in [0,1,3,4,5,0x17]]+['c2b-c'+str(i)+'-coupling' for i in [0,1,3,4,5,0x17]]+['c2b-undo-read','c2b-drop-write','c2b-drop-undo']:
  run(fault,want=0x8111b if fault in ['c2b-undo-read','c2b-wrong-write-drop-undo'] else 0x811 if fault in ['c2b-drop-write','c2b-drop-undo'] else 0x8111a,fault=fault)
 for fault in ['c17b-before-read','c17b-read','c17b-low-read','c17b-drop-write','c17b-wrong-write']+['c'+str(i)+'-after-c17b-read' for i in [0,1,2,3,4,5]]+['c17b-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5]]+['c17b-undo-read','c17b-drop-undo']:
  run(fault,want=0x8111d if fault in ['c17b-undo-read','c17b-drop-undo'] else 0x8111c,fault=fault)
 for fault in ['c19b-before-read','c13-before-c19b-read','c19b-read','c19b-high-read','c19b-drop-write','c19b-wrong-write']+['c'+str(i)+'-after-c19b-read' for i in [0,1,2,3,4,5,0x13,0x17]]+['c19b-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5,0x13,0x17]]+['c19b-undo-read','c19b-drop-undo','c13-undo-c19b-read']:
  run(fault,want=0x8111f if fault in ['c19b-undo-read','c19b-drop-undo','c19b-c19-coupling','c13-undo-c19b-read'] else 0x8111e,fault=fault)
 for fault in ['c13-before-read','c19-before-c13-read','c13-read','c13-high-read','c13-drop-write','c13-wrong-write']+['c'+str(i)+'-after-c13-read' for i in [0,1,2,3,4,5,0x19,0x17]]+['c13-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5,0x19,0x17]]+['c13-undo-read','c13-drop-undo','c19-undo-c13-read']:
  run(fault,want=0x81121 if fault in ['c13-undo-read','c13-drop-undo','c13-c25-coupling','c19-undo-c13-read'] else 0x81120,fault=fault)
 for n in range(7):
  run('horizontal-read-'+str(n),want=0x8119,fault='h-read-'+str(n))
  run('horizontal-cleanup-'+str(n),want=0x811a,fault='h-cleanup-'+str(n))
  if n!=3:
   run('horizontal-drop-'+str(n),want=0x8119,fault='h-drop-'+str(n))
   run('horizontal-restore-'+str(n),want=0x811a,fault='h-restore-'+str(n))
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:R['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,separators=(',',':'))+'\n')
print('PASS relocated811 integration cases',len(R['cases']))

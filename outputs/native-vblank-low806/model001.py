"""Actual806 native ELF with horizontal transaction, pre-enable recovery and fault injection.
Control-flow and access contracts only; no modeled transition proves hardware behavior.
"""
import datetime,hashlib,json,struct,sys,os,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn806/measure003/original-native')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'model001.json';assert not out.exists()
b=(P/'native.bin').read_bytes()
sy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}
R={'passed':False,'scope':__doc__,'ELF_sha256':sha(P/'native.elf'),'harness_sha256':sha(Path(__file__)),'cases':[]}
GPU=0xfd000000;deadline=time.monotonic()+180

SETUP=[(0x680884,0),(0x680888,0),(0x68088c,0x10001000),(0x680890,0x10000000),(0x680894,0x10000000),(0x680898,0x10000000),(0x68089c,0x10000000),(0x680880,0x21101100),(0x680630,2),(0x68084c,0x00801080),(0x6808c4,0x40801080)]
H=[(0x680820,719),(0x680824,779),(0x680828,719),(0x680834,0),(0x68082c,738),(0x680830,770),(0x680838,719)]
HB=[1279,1649,1279,0,1389,1429,1279]
V=[(0x680800,719),(0x680804,749),(0x68080c,724),(0x680810,729),(0x680818,719)]
CS=[(0x14,0),(0x17,0xe3),(0x19,0x10),(0x1b,0x85)]
def run(name,flags=0x46,cpu0=0x4001003b,cpu3=0,cpu4=0x610,fault="",baseline="",c1_original=0x9f):
 assert time.monotonic()<deadline
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)
 c.mem_map(0x200000,0x40000)

 c.mem_write(0x200000,b'G'*0x40000);c.mem_map(GPU,0x1000000)
 c.mem_write(0x208000,struct.pack('<II',0x20ff00,0x201000))
 c.reg_write(x.UC_X86_REG_ESP,0x208000);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 sels={0x6013d4:0x67,0xc03c4:0x72,0xc03ce:0x91};original=sels.copy()
 mm=dict(SETUP);mm.update(dict(V));mm.update({0x680808:719,0x680814:0});mm[0x680630]=3;mm.update(dict(zip([a for a,_ in H],HB)));hw={a:0 for a,_ in H};hr=[]
 cr={7:0xf0,6:0xec,9:0x60,0x10:0xd4,0x12:0xcf,0x15:0xcf,0x16:0xed,0x18:0xff,0x25:0x10,0x13:0x80,1:c1_original,3:0x8c,2:0x9f,0:0xc8,4:0xa7,5:0x31,0x11:9,0x14:0,0x17:0xe3,0x19:0x51,0x1b:0x85,0x22:0xfe,0x33:0x11,0x1f:0}
 sq=1;gr=0
 if baseline=='c3':cr[3]^=1
 if baseline=='c2':cr[2]^=1
 if baseline=='c0':cr[0]^=1
 if baseline=='c4':cr[4]^=1
 if baseline=='c5':cr[5]^=1
 if baseline=='gr':gr=1
 if baseline=='cr22':cr[0x22]=0xff
 if baseline=='cr33':cr[0x33]=0
 if baseline=='seq':sq=0
 if baseline=='cr11':cr[0x11]=0x89
 if baseline=='mm':mm[0x680884]=1
 if baseline=='cr':cr[0x19]=0
 if baseline=='cr1b':cr[0x1b]=5
 if baseline.startswith('h-'):mm[H[int(baseline[2:])][0]]^=1
 state={'cb15writes':0,'cb7writes':0,'cb9writes':0,'cd12writes':0,'cd7writes':0,'ct16writes':0,'ct6writes':0,'ct7writes':0,'c10writes':0,'c7writes':0,'vewrites':0,'sewrites':0,'sywrites':0,'vswrites':0,'vcwrites':0,'vtwrites':0,'vwrites':0,'c13writes':0,'c19bwrites':0,'c17bwrites':0,'c2bwrites':0,'c1writes':0,'c17writes':0,'c5bwrites':0,'c3writes':0,'c2writes':0,'c0writes':0,'c5writes':0,'c4writes':0,'sq':sq,'gr':gr,'recovering':False,'unlock':False}
 writes=[];reads=[];ports=[];steps=[0,0]
 word=lambda n:struct.unpack('<I',c.mem_read(0x201000+n*4,4))[0]
 def access(uc,kind,addr,width,value,_):
  off=addr-GPU;assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  if off in sels:
   assert width==1
   if kind==u.UC_MEM_WRITE:sels[off]=value;return
   val=sels[off]
   if fault=='selector' and state['recovering'] and val==original[off]:val^=1
  elif off==0x6013d5:
   assert width==1;idx=sels[0x6013d4];assert idx in cr
   if kind==u.UC_MEM_WRITE:
    assert idx in [0x15,9,0x12,0x16,6,0x10,7,1,3,2,0,4,5,0x13,0x1f,0x14,0x17,0x19]
    if idx==0x15 and state['cb7writes']==1 and word(1) in [0x80642,0x806]:
     state['cb15writes']+=1;n=state['cb15writes'];assert n<=2
     assert [word(700),word(701),word(702)]==[207,223,1] and value==[223,207][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',21,value])
     if fault==('cb15-drop-write' if n==1 else 'cb15-drop-undo') or (n==2 and fault=='cb15-wrong-write-drop-undo'):return
     cr[21]=value
     if fault==('cb15-wrong-write' if n==1 else 'cb15-wrong-undo') or (n==1 and fault=='cb15-wrong-write-drop-undo'):cr[21]^=1
     if n==1 and fault.startswith('cb15-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,16,18,22,24,37][j-1]]^=1
     return
    if idx==7 and state['cb9writes']==1 and word(1) in [0x80640,0x80642,0x806]:
     state['cb7writes']+=1;n=state['cb7writes'];assert n<=2
     if n==2:assert state['cb15writes']==2*word(702)
     assert [word(670),word(671),word(672)]==[54,62,1] and value==[62,54][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',7,value])
     if fault==('cb7-drop-write' if n==1 else 'cb7-drop-undo') or (n==2 and fault=='cb7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('cb7-wrong-write' if n==1 else 'cb7-wrong-undo') or (n==1 and fault=='cb7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('cb7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,16,18,21,22,24,37][j-1]]^=1
     return
    if idx==9:
     assert state['cd12writes']==1 and state['cd7writes']==1 and word(1) in [0x8063e,0x80640,0x80642,0x806]
     state['cb9writes']+=1;n=state['cb9writes'];assert n<=2
     if n==2:assert state['cb7writes']==2*word(672)
     assert [word(640),word(641),word(642)]==[96,64,1] and value==[64,96][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',9,value])
     if fault==('cb9-drop-write' if n==1 else 'cb9-drop-undo') or (n==2 and fault=='cb9-wrong-write-drop-undo'):return
     cr[9]=value
     if fault==('cb9-wrong-write' if n==1 else 'cb9-wrong-undo') or (n==1 and fault=='cb9-wrong-write-drop-undo'):cr[9]^=1
     if n==1 and fault.startswith('cb9-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,16,18,21,22,24,37][j-1]]^=1
     return
    if idx==0x12:
     assert state['cd7writes']==1 and state['ct16writes']==1 and word(1) in [0x8063c,0x8063e,0x80640,0x80642,0x806]
     state['cd12writes']+=1;n=state['cd12writes'];assert n<=2
     if n==2:assert state['cb9writes']==2*word(642)
     assert [word(610),word(611),word(612)]==[207,223,1] and value==[223,207][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',18,value])
     if fault==('cd12-drop-write' if n==1 else 'cd12-drop-undo') or (n==2 and fault=='cd12-wrong-write-drop-undo'):return
     cr[18]=value
     if fault==('cd12-wrong-write' if n==1 else 'cd12-wrong-undo') or (n==1 and fault=='cd12-wrong-write-drop-undo'):cr[18]^=1
     if n==1 and fault.startswith('cd12-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,16,21,22,24,37][j-1]]^=1
     return
    if idx==7 and state['ct16writes']==1:
     assert state['ct6writes']==1 and state['ct7writes']==1 and word(1) in [0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]
     state['cd7writes']+=1;n=state['cd7writes'];assert n<=2
     if n==2:assert state['cd12writes']==2*word(612)
     assert [word(580),word(581),word(582)]==[116,54,1] and value==[54,116][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',7,value])
     if fault==('cd7-drop-write' if n==1 else 'cd7-drop-undo') or (n==2 and fault=='cd7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('cd7-wrong-write' if n==1 else 'cd7-wrong-undo') or (n==1 and fault=='cd7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('cd7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,16,18,21,22,24,37][j-1]]^=1
     return
    if idx==0x16:
     assert state['ct6writes']==1 and state['ct7writes']==1 and word(1) in [0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]
     state['ct16writes']+=1;n=state['ct16writes'];assert n<=2
     if n==2:assert state['cd7writes']==2*word(582)
     assert [word(550),word(551),word(552)]==[237,140,1] and value==[140,237][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',0x16,value])
     if fault==('ct16-drop-write' if n==1 else 'ct16-drop-undo') or (n==2 and fault=='ct16-wrong-write-drop-undo'):return
     cr[0x16]=value
     if fault==('ct16-wrong-write' if n==1 else 'ct16-wrong-undo') or (n==1 and fault=='ct16-wrong-write-drop-undo'):cr[0x16]^=1
     if n==1 and fault.startswith('ct16-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,0x10,0x12,0x15,0x18,0x25][j-1]]^=1
     return
    if idx==6:
     assert state['ct7writes']==1 and state['c10writes']==1 and word(1) in [0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]
     state['ct6writes']+=1;n=state['ct6writes'];assert n<=2
     if n==2:assert state['ct16writes']==2*word(552)
     assert [word(520),word(521),word(522)]==[236,12,1] and value==[12,236][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',6,value])
     if fault==('ct6-drop-write' if n==1 else 'ct6-drop-undo') or (n==2 and fault=='ct6-wrong-write-drop-undo'):return
     cr[6]=value
     if fault==('ct6-wrong-write' if n==1 else 'ct6-wrong-undo') or (n==1 and fault=='ct6-wrong-write-drop-undo'):cr[6]^=1
     if n==1 and fault.startswith('ct6-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[7,9,0x10,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
     return
    if idx==0x10:
     assert state['c7writes']==1 and state['vewrites']==1 and word(1) in [0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]
     state['c10writes']+=1;n=state['c10writes'];assert n<=2
     if n==2:assert state['ct7writes']==2*word(492)
     assert [word(460),word(461),word(462)]==[212,233,1] and value==(233 if n==1 else 212)
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',0x10,value])
     if fault==('c10-drop-write' if n==1 else 'c10-drop-undo'):return
     cr[0x10]=value
     if fault==('c10-wrong-write' if n==1 else 'c10-wrong-undo'):cr[0x10]^=1
     if n==1 and fault.startswith('c10-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
     return
    if idx==7 and state['c10writes']==1:
     assert state['c7writes']==1 and word(1) in [0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]
     state['ct7writes']+=1;n=state['ct7writes'];assert n<=2
     if n==2:assert state['ct6writes']==2*word(522)
     assert [word(490),word(491),word(492)]==[116,116,1] and value==116
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',7,value])
     if fault==('ct7-drop-write' if n==1 else 'ct7-drop-undo') or (n==2 and fault=='ct7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('ct7-wrong-write' if n==1 else 'ct7-wrong-undo') or (n==1 and fault=='ct7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('ct7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,0x10,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
     return
    if idx==7:
     assert state['vewrites']==1 and word(1) in [0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]
     state['c7writes']+=1;n=state['c7writes'];assert n<=2
     if n==2:assert state['c10writes']==2*word(462)
     assert [word(430),word(431),word(432)]==[240,116,1] and value==(116 if n==1 else 240)
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',7,value])
     if fault==('c7-drop-write' if n==1 else 'c7-drop-undo'):return
     cr[7]=value
     if fault==('c7-wrong-write' if n==1 else 'c7-wrong-undo'):cr[7]^=1
     if n==1 and fault.startswith('c7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,0x10,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
     return
    if idx==0x13:
     state['c13writes']+=1;n=state['c13writes'];assert n==1 or state['vwrites']==2*word(234); assert n<=2 and value==(0x68 if n==1 else 0x80)
     assert state['sq']==0x21 and ports==[5] and not hr and state['c19bwrites']==1 and state['c17bwrites']==1
     assert [word(216),word(217),word(218),word(222)]==[0x80,0x68,1,0x30]
     writes.append(['cr',idx,value])
     if fault==('c13-drop-write' if n==1 else 'c13-drop-undo'):return
     cr[idx]=value
     if n==1 and fault=='c13-wrong-write':cr[idx]^=1
     for idx2 in [0,1,2,3,4,5,0x19,0x17]:
      if n==1 and fault=='c13-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==0x19 and word(202) and state['c19bwrites']<2:
     state['c19bwrites']+=1;n=state['c19bwrites'];assert state['c13writes']==2*word(218)
     assert n<=2 and value==(0x30 if n==1 else 0x10)
     assert state['sq']==0x21 and ports==[5] and not hr and state['c17bwrites']==1
     assert [word(200),word(201),word(202),word(206)]==[0x10,0x30,1,0x80]
     writes.append(['cr',idx,value])
     if fault==('c19b-drop-write' if n==1 else 'c19b-drop-undo'):return
     cr[idx]=value
     if n==1 and fault=='c19b-wrong-write':cr[idx]^=1
     for idx2 in [0,1,2,3,4,5,0x13,0x17]:
      if n==1 and fault=='c19b-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==0x17 and word(190) and state['c17bwrites']<2:
     state['c17bwrites']+=1;n=state['c17bwrites'];assert state['c19bwrites']==2*word(202)
     assert n<=2 and value==(0xe3 if n==1 else 0x63)
     assert state['sq']==0x21 and ports==[5] and not hr and state['c2bwrites']==state['c1writes']==state['c17writes']==1
     assert state['c5bwrites']==1 and all(state['c'+str(i)+'writes']==1 for i in [0,2,3,4,5])
     assert [word(188),word(189),word(190)]==[0x63,0xe3,1]
     writes.append(['cr',idx,value])
     if fault==('c17b-drop-write' if n==1 else 'c17b-drop-undo'):return
     cr[idx]=value
     if n==1 and fault=='c17b-wrong-write':cr[idx]^=1
     for idx2 in [0,1,2,3,4,5]:
      if n==1 and fault=='c17b-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==2 and word(178) and state['c2bwrites']<2:
     state['c2bwrites']+=1;n=state['c2bwrites'];assert state['c17bwrites']==2*word(190)
     assert n<=2 and value==0x59
     assert state['sq']==0x21 and ports==[5] and not hr and state['c1writes']==state['c17writes']==1
     assert state['c5bwrites']==1 and all(state['c'+str(i)+'writes']==1 for i in [0,2,3,4,5])
     assert word(176)==word(177)==0x59 and word(178)==1
     writes.append(['cr',idx,value])
     if fault==('c2b-drop-write' if n==1 else 'c2b-drop-undo') or (n==2 and fault=='c2b-wrong-write-drop-undo'):return
     cr[idx]=value
     if n==1 and fault in ['c2b-wrong-write','c2b-wrong-write-drop-undo']:cr[idx]^=1
     for idx2 in [0,1,3,4,5,0x17]:
      if n==1 and fault=='c2b-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==1:
     state['c1writes']+=1;n=state['c1writes'];assert state['c2bwrites']==2*word(178)
     assert n<=2 and value==(0x59 if n==1 else c1_original)
     assert state['sq']==0x21 and ports==[5] and not hr and state['c17writes']==1
     assert state['c5bwrites']==1 and all(state['c'+str(i)+'writes']==1 for i in [0,2,3,4,5])
     assert word(164)==c1_original and word(165)==0x59 and word(166)==1
     writes.append(['cr',idx,value])
     if fault==('c1-drop-write' if n==1 else 'c1-drop-undo'):return
     cr[idx]=value
     if n==1 and fault=='c1-wrong-write':cr[idx]^=1
     for idx2 in [0,2,3,4,5,0x17]:
      if n==1 and fault=='c1-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==0x17 and word(155):
     state['c17writes']+=1;n=state['c17writes'];assert state['c1writes']==2*word(166)
     assert n<=2 and value==(0x63 if n==1 else 0xe3)
     assert state['sq']==0x21 and ports==[5] and not hr and state['c5bwrites']==1
     assert all(state['c'+str(i)+'writes']==1 for i in [0,2,3,4,5])
     assert word(146)==0xbe and word(153)==0xe3 and word(154)==0x63
     writes.append(['cr',idx,value])
     if fault==('c17-drop-write' if n==1 else 'c17-drop-undo'):return
     cr[idx]=value
     if n==1 and fault=='c17-wrong-write':cr[idx]^=1
     for idx2 in [0,2,3,4,5]:
      if n==1 and fault=='c17-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==5 and word(145) and state['c5bwrites']<2:
     state['c5bwrites']+=1;n=state['c5bwrites'];assert state['c17writes']==2*word(155)
     assert value==(0xbe if n==1 else 0x3e)
     assert state['sq']==0x21 and ports==[5] and not hr
     assert all(state['c'+str(i)+'writes']==1 for i in [0,2,3,4,5])
     assert word(136)==0x80 and word(142)==0x3e and word(143)==0x3e and word(144)==0xbe
     writes.append(['cr',5,value])
     if fault==('c5b-drop-write' if n==1 else 'c5b-drop-undo'):return
     cr[5]=value
     if n==1 and fault=='c5b-wrong-write':cr[5]^=1
     for idx2 in [0,2,3,4]:
      if n==1 and fault=='c5b-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==3:
     state['c3writes']+=1;assert state['c3writes']<=2
     if state['c3writes']==2:assert state['c5bwrites']==2*word(145)
     assert value==(0x80 if state['c3writes']==1 else 0x8c)
     assert state['sq']==0x21 and ports==[5] and all(state['c'+str(i)+'writes']==1 for i in [0,2,4,5]) and not hr
     assert word(127)==0x59 and word(130)==0x5c and word(131)==93 and word(132)==0x3e and word(135)==1 and not cr[0x11]&0x80
     writes.append(['cr',3,value])
     if fault==('c3-drop-write' if state['c3writes']==1 else 'c3-drop-restore'):return
     cr[3]=value
     for idx2 in [0,2,4,5]:
      if state['c3writes']==1 and fault=='c3-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==2:
     state['c2writes']+=1;assert state['c2writes']<=2
     if state['c2writes']==2:assert state['c3writes']==2*word(135)
     assert value==(0x59 if state['c2writes']==1 else 0x9f)
     assert state['sq']==0x21 and ports==[5] and state['c4writes']==1 and state['c5writes']==1 and state['c0writes']==1 and not hr
     assert word(119)==0x5c and word(122)==93 and word(123)==0x3e and word(126)==1 and not cr[0x11]&0x80
     writes.append(['cr',2,value])
     if fault==('c2-drop-write' if state['c2writes']==1 else 'c2-drop-restore'):return
     cr[2]=value
     for idx2 in [0,4,5]:
      if state['c2writes']==1 and fault=='c2-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==0:
     state['c0writes']+=1;assert state['c0writes']<=2
     if state['c0writes']==2:assert state['c2writes']==2*word(126)
     assert value==(0x5c if state['c0writes']==1 else 0xc8)
     assert state['sq']==0x21 and ports==[5] and state['c4writes']==1 and state['c5writes']==1 and not hr
     assert word(114)==0x3e and word(115)==93 and word(118)==1 and not cr[0x11]&0x80
     writes.append(['cr',0,value])
     if fault==('c0-drop-write' if state['c0writes']==1 else 'c0-drop-restore'):return
     cr[0]=value
     if state['c0writes']==1 and fault=='c0-c4-coupling':cr[4]^=1
     if state['c0writes']==1 and fault=='c0-c5-coupling':cr[5]^=1
     return
    if idx==5:
     state['c5writes']+=1;assert state['c5writes']<=2
     if state['c5writes']==2:assert state['c0writes']==2*word(118)
     assert value==(0x3e if state['c5writes']==1 else 0x31)
     assert state['sq']==0x21 and ports==[5] and state['c4writes']==1 and not hr
     assert word(105)==93 and word(110)==0x31 and word(113)==1
     writes.append(['cr',5,value])
     if fault==('c5-drop-write' if state['c5writes']==1 else 'c5-drop-restore'):return
     cr[5]=value
     if state['c5writes']==1 and fault=='c4-coupling':cr[4]^=1
     return
    if idx==4:
     state['c4writes']+=1;assert state['c4writes']<=2
     if state['c4writes']==2:assert state['c5writes']==2*word(113)
     assert value==(93 if state['c4writes']==1 else 0xa7)
     assert state['sq']==0x21 and ports==[5] and not (cr[0x11]&0x80)
     assert word(98)==7 and word(99)==0xffffffff and not hr
     writes.append(['cr',4,value])
     if fault==('c4-write' if state['c4writes']==1 else 'c4-restore-write'):return
     cr[4]=value
     if state['c4writes']==1 and fault=='c5-coupling':cr[5]^=1
     return
    assert value==dict(CS).get(idx) or (idx,value) in [(0x1f,0x57),(0x19,0x51)]
    writes.append(['cr',idx,value])
    if idx==0x1f:state['unlock']=True
    if idx==0x19 and value==0x51:
     state['recovering']=True
     if fault=='cleanup-13':return
    cr[idx]=value;return
   val=cr[idx]
   if idx in [21,6,7,9,16,18,22,24,37] and state['cb7writes']==1 and word(1) in [0x80642,0x806]:
    j=[21,6,7,9,16,18,22,24,37].index(idx);phase=['before','after','undo'][state['cb15writes']]
    if fault=='cb15-'+phase+'-'+str(j):val^=1

   if idx in [7,6,9,16,18,21,22,24,37] and state['cb9writes']==1 and word(1) in [0x80640,0x80642,0x806]:
    j=[7,6,9,16,18,21,22,24,37].index(idx);phase=['before','after','undo'][state['cb7writes']]
    if fault=='cb7-'+phase+'-'+str(j):val^=1

   if idx in [9,6,7,16,18,21,22,24,37] and state['cd12writes']==1 and word(1) in [0x8063e,0x80640,0x80642,0x806]:
    j=[9,6,7,16,18,21,22,24,37].index(idx);phase=['before','after','undo'][state['cb9writes']]
    if fault=='cb9-'+phase+'-'+str(j):val^=1

   if idx in [18,6,7,9,16,21,22,24,37] and state['cd7writes']==1 and word(1) in [0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=[18,6,7,9,16,21,22,24,37].index(idx);phase=['before','after','undo'][state['cd12writes']]
    if fault=='cd12-'+phase+'-'+str(j):val^=1

   if idx in [7,6,9,16,18,21,22,24,37] and state['ct16writes']==1 and word(1) in [0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=[7,6,9,16,18,21,22,24,37].index(idx);phase=['before','after','undo'][state['cd7writes']]
    if fault=='cd7-'+phase+'-'+str(j):val^=1

   if idx in [0x16,6,7,9,0x10,0x12,0x15,0x18,0x25] and state['ct6writes']==1 and word(1) in [0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=[0x16,6,7,9,0x10,0x12,0x15,0x18,0x25].index(idx);phase=['before','after','undo'][state['ct16writes']]
    if fault=='ct16-'+phase+'-'+str(j):val^=1

   if idx in [6,7,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['ct7writes']==1 and word(1) in [0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=[6,7,9,0x10,0x12,0x15,0x16,0x18,0x25].index(idx);phase=['before','after','undo'][state['ct6writes']]
    if fault=='ct6-'+phase+'-'+str(j):val^=1

   if idx in [7,6,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['c10writes']==1 and word(1) in [0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=[7,6,9,0x10,0x12,0x15,0x16,0x18,0x25].index(idx);phase=['before','after','undo'][state['ct7writes']]
    if fault=='ct7-'+phase+'-'+str(j):val^=1

   if idx in [0x10,6,7,9,0x12,0x15,0x16,0x18,0x25] and state['c7writes']==1 and word(1) in [0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=[0x10,6,7,9,0x12,0x15,0x16,0x18,0x25].index(idx);phase=['before','after','undo'][state['c10writes']]
    if fault=='c10-'+phase+'-'+str(j):val^=1

   if idx in [7,6,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['vewrites']==1 and word(1) in [0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=[7,6,9,0x10,0x12,0x15,0x16,0x18,0x25].index(idx);phase=['before','after','undo'][state['c7writes']]
    if fault=='c7-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['sewrites']==1 and word(1) in [0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vewrites']]
    if fault=='ve-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['sywrites']==1 and word(1) in [0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['sewrites']]
    if fault=='se-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['vswrites']==1 and word(1) in [0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['sywrites']]
    if fault=='sy-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['vcwrites']==1 and word(1) in [0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vswrites']]
    if fault=='vs-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['vtwrites']==1 and word(1) in [0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vcwrites']]
    if fault=='vc-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['vwrites']==1 and word(1) in [0x80624,0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=5+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vtwrites']]
    if fault=='vt-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['c13writes']==1 and word(1) in [0x80622,0x80624,0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    j=5+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vwrites']]
    if fault=='v-'+phase+'-'+str(j):val^=1

   if word(1)==0x80620 and not word(218) and state['c19bwrites']==1:
    if idx==0x13 and fault=='c13-before-read':val^=1
    if idx==0x19 and fault=='c19-before-c13-read':val^=1
   if idx==0x13 and state['c13writes']==1 and fault=='c13-read':val^=1
   if idx==0x13 and state['c13writes']==1 and fault=='c13-high-read':val^=0x80
   if idx==0x13 and state['c13writes']==2 and state['c19bwrites']==1 and fault=='c13-undo-read':val^=1
   if idx==0x19 and state['c13writes']==2 and state['c19bwrites']==1 and fault=='c19-undo-c13-read':val^=1
   if idx in [0,1,2,3,4,5,0x19,0x17] and state['c13writes']==1 and fault=='c'+str(idx)+'-after-c13-read':val^=1
   if word(1)==0x8061e and not word(202) and state['c17bwrites']==1:
    if idx==0x19 and fault=='c19b-before-read':val^=1
    if idx==0x13 and fault=='c13-before-c19b-read':val^=1
   if idx==0x19 and state['c19bwrites']==1 and fault=='c19b-read':val^=1
   if idx==0x19 and state['c19bwrites']==1 and fault=='c19b-high-read':val^=0x20
   if idx==0x19 and state['c19bwrites']==2 and state['c17bwrites']==1 and fault=='c19b-undo-read':val^=1
   if idx==0x13 and state['c19bwrites']==2 and state['c17bwrites']==1 and fault=='c13-undo-c19b-read':val^=1
   if idx in [0,1,2,3,4,5,0x13,0x17] and state['c19bwrites']==1 and fault=='c'+str(idx)+'-after-c19b-read':val^=1
   if idx==0x17 and word(1)==0x8061c and not word(190) and state['c2bwrites']==1 and fault=='c17b-before-read':val^=1
   if idx==0x17 and state['c17bwrites']==1 and fault=='c17b-read':val^=1
   if idx==0x17 and state['c17bwrites']==1 and fault=='c17b-low-read':val^=0x80
   if idx==0x17 and state['c17bwrites']==2 and state['c2bwrites']==1 and fault=='c17b-undo-read':val^=1
   if idx in [0,1,2,3,4,5] and state['c17bwrites']==1 and fault=='c'+str(idx)+'-after-c17b-read':val^=1
   if idx==2 and word(1)==0x8061a and not word(178) and state['c1writes']==1 and fault=='c2b-before-read':val^=1
   if idx==2 and state['c2bwrites']==1 and fault=='c2b-read':val^=1
   if idx==2 and state['c2bwrites']==1 and fault=='c2b-high-read':val^=0x80
   if idx==2 and state['c2bwrites']==2 and state['c1writes']==1 and fault=='c2b-undo-read':val^=1
   if idx in [0,1,3,4,5,0x17] and state['c2bwrites']==1 and fault=='c'+str(idx)+'-after-c2b-read':val^=1
   if idx==1 and state['c1writes']==1 and fault=='c1-read':val^=1
   if idx==1 and state['c1writes']==1 and fault=='c1-high-read':val^=0x80
   if idx==1 and state['c1writes']==2 and state['c17writes']==1 and fault=='c1-undo-read':val^=1
   if idx in [0,2,3,4,5,0x17] and state['c1writes']==1 and fault=='c'+str(idx)+'-after-c1-read':val^=1
   if idx==0x17 and word(1)==0x80616 and not word(155) and not state['recovering'] and fault=='c17-before-read':val^=1
   if idx==0x17 and state['c17writes']==1 and fault=='c17-read':val^=1
   if idx==0x17 and state['c17writes']==1 and fault=='c17-high-read':val^=0x80
   if idx==0x17 and state['c17writes']==2 and state['c5bwrites']==1 and fault=='c17-undo-read':val^=1
   if idx in [0,2,3,4,5] and state['c17writes']==1 and fault=='c'+str(idx)+'-after-c17-read':val^=1
   if idx==5 and state['c5bwrites']==1 and fault=='c5b-read':val^=1
   if idx==5 and state['c5bwrites']==1 and fault=='c5b-high-read':val^=0x80
   if idx==5 and state['c5bwrites']==2 and state['c3writes']==1 and fault=='c5b-undo-read':val^=1
   if idx in [0,2,3,4] and state['c5bwrites']==1 and fault=='c'+str(idx)+'-after-c5b-read':val^=1
   if idx==3 and state['c3writes']==1 and fault=='c3-read':val^=1
   if idx==3 and state['c3writes']==1 and fault=='c3-high-read':val^=0x80
   if idx==3 and state['c3writes']==2 and fault=='c3-restore-read':val^=1
   if idx in [0,2,4,5] and state['c3writes']==1 and fault=='c'+str(idx)+'-after-c3-read':val^=1
   if idx==2 and state['c2writes']==1 and fault=='c2-read':val^=1
   if idx==2 and state['c2writes']==2 and fault=='c2-restore-read':val^=1
   if idx in [0,4,5] and state['c2writes']==1 and fault=='c'+str(idx)+'-after-c2-read':val^=1
   if idx==0 and state['c0writes']==1 and fault=='c0-read':val^=1
   if idx==0 and state['c0writes']==2 and fault=='c0-restore-read':val^=1
   if idx==4 and state['c0writes']==1 and fault=='c4-after-c0-read':val^=1
   if idx==5 and state['c0writes']==1 and fault=='c5-after-c0-read':val^=1
   if idx==4 and state['c4writes']==1 and fault=='c4-read':val^=1
   if idx==4 and state['c5writes']==1 and fault=='c4-after-read':val^=1
   if idx==5 and state['c5writes']==1 and fault=='c5-low-read':val^=1
   if idx==5 and state['c5writes']==1 and fault=='c5-high-read':val^=0x80
   if idx==4 and state['c4writes']==2 and fault=='c4-restore-read':val^=1
   if idx==5 and state['c4writes']==1 and fault=='c5-read':val^=1
   if idx==5 and state['c4writes']==2 and fault=='c5-restore-read':val^=1
   if fault=='unlock' and state['unlock'] and idx==0x11 and not state['recovering']:val^=1
   if word(1)==0x8068 and not state['recovering'] and idx in dict(CS):
    n=11+[i for i,_ in CS].index(idx)
    if fault=='check-'+str(n):val^=1
    assert word(2)==11 and word(3)==3
   if state['recovering']:
    bit={0x11:16,0x22:18,0x33:19}.get(idx)
    if bit is not None and fault=='cleanup-'+str(bit):val^=1
  elif off==0xc03c5:
   assert width==1 and sels[0xc03c4]==1
   if kind==u.UC_MEM_WRITE:
    assert value in [1,0x21];writes.append(['sq',1,value])
    if value==0x21 and fault=='blank':return
    if value==1 and fault=='cleanup-15':return
    state['sq']=value;return
   val=state['sq']
  elif off==0xc03cf:
   assert width==1 and kind==u.UC_MEM_READ and sels[0xc03ce]==4
   val=state['gr']^(1 if state['recovering'] and fault=='cleanup-17' else 0)
  elif off in [0x680808,0x680814]:
   assert width==4 and state['sq']==0x21 and ports==[5] and not hr and state['vtwrites']==1
   assert word(1) in [0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]
   if kind==u.UC_MEM_WRITE and off==0x680814:
    assert state['vcwrites']==1 and word(1) in [0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]
    state['vswrites']+=1;n=state['vswrites'];assert n<=2
    if n==2:assert state['sywrites']==2*word(342)
    assert [word(310),word(311),word(312)]==[0,0,1] and value==0
    writes.append(['vs',off,value])
    if fault==('vs-drop-write' if n==1 else 'vs-drop-undo') or (n==2 and fault=='vs-wrong-write-drop-undo'):return
    mm[off]=value
    if fault==('vs-wrong-write' if n==1 else 'vs-wrong-undo') or (n==1 and fault=='vs-wrong-write-drop-undo'):mm[off]^=1
    if n==1 and fault.startswith('vs-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x68080c,0x680810,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
    return
   if kind==u.UC_MEM_WRITE:
    assert off==0x680808
    state['vcwrites']+=1;n=state['vcwrites'];assert n<=2
    if n==2:assert state['vswrites']==2*word(312)
    assert [word(280),word(281),word(282)]==[719,479,1] and value==(479 if n==1 else 719)
    writes.append(['vc',off,value])
    if fault==('vc-drop-write' if n==1 else 'vc-drop-undo'):return
    mm[off]=value
    if fault==('vc-wrong-write' if n==1 else 'vc-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('vc-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x68080c,0x680810,0x680814,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
    return
   val=mm[off];j=0 if off==0x680808 else 5;phase=['before','after','undo'][state['vcwrites']]
   if state['sewrites']==1 and word(1) in [0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    sj=4 if off==0x680814 else 3;sp=['before','after','undo'][state['vewrites']]
    if fault=='ve-'+sp+'-'+str(sj):val^=1

   if state['sywrites']==1 and word(1) in [0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    sj=4 if off==0x680814 else 3;sp=['before','after','undo'][state['sewrites']]
    if fault=='se-'+sp+'-'+str(sj):val^=1

   if state['vswrites']==1 and word(1) in [0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    sj=4 if off==0x680814 else 3;sp=['before','after','undo'][state['sywrites']]
    if fault=='sy-'+sp+'-'+str(sj):val^=1

   if fault=='vc-'+phase+'-'+str(j):val^=1
   if state['vcwrites']==1 and word(1) in [0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    sj=0 if off==0x680814 else 3;sp=['before','after','undo'][state['vswrites']]
    if fault=='vs-'+sp+'-'+str(sj):val^=1

  elif off in dict(V):
   assert width==4;j=[a for a,_ in V].index(off)
   assert state['sq']==0x21 and ports==[5] and not hr and state['c13writes']==1
   assert word(1) in [0x80622,0x80624,0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]
   if kind==u.UC_MEM_WRITE and off==0x68080c:
    assert state['vswrites']==1 and word(1) in [0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]
    state['sywrites']+=1;n=state['sywrites'];assert n<=2
    if n==2:assert state['sewrites']==2*word(372)
    assert [word(340),word(341),word(342)]==[724,489,1] and value==(489 if n==1 else 724)
    writes.append(['sy',off,value])
    if fault==('sy-drop-write' if n==1 else 'sy-drop-undo'):return
    mm[off]=value
    if fault==('sy-wrong-write' if n==1 else 'sy-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('sy-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x680814,0x680810,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
    return
   if kind==u.UC_MEM_WRITE and off==0x680810:
    assert state['sywrites']==1 and word(1) in [0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]
    state['sewrites']+=1;n=state['sewrites'];assert n<=2
    if n==2:assert state['vewrites']==2*word(402)
    assert [word(370),word(371),word(372)]==[729,492,1] and value==(492 if n==1 else 729)
    writes.append(['se',off,value])
    if fault==('se-drop-write' if n==1 else 'se-drop-undo'):return
    mm[off]=value
    if fault==('se-wrong-write' if n==1 else 'se-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('se-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x680814,0x68080c,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
    return
   if kind==u.UC_MEM_WRITE and off==0x680818:
    assert state['sewrites']==1 and word(1) in [0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]
    state['vewrites']+=1;n=state['vewrites'];assert n<=2
    if n==2:assert state['c7writes']==2*word(432)
    assert [word(400),word(401),word(402)]==[719,479,1] and value==(479 if n==1 else 719)
    writes.append(['ve',off,value])
    if fault==('ve-drop-write' if n==1 else 've-drop-undo'):return
    mm[off]=value
    if fault==('ve-wrong-write' if n==1 else 've-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('ve-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x680814,0x68080c,0x680810][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
    return
   if kind==u.UC_MEM_WRITE and off==0x680804:
    assert state['vwrites']==1 and word(1) in [0x80624,0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]
    state['vtwrites']+=1;n=state['vtwrites'];assert n<=2
    if n==2:assert state['vcwrites']==2*word(282)
    assert [word(256),word(257),word(258)]==[749,524,1] and value==(524 if n==1 else 749)
    writes.append(['vt',off,value])
    if fault==('vt-drop-write' if n==1 else 'vt-drop-undo'):return
    mm[off]=value
    if fault==('vt-wrong-write' if n==1 else 'vt-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('vt-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=6
     if j<=4:mm[[0x680800,0x68080c,0x680810,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-5]]^=1
    return
   if kind==u.UC_MEM_WRITE:
    assert off==0x680800
    state['vwrites']+=1;n=state['vwrites'];assert n<=2
    if n==2:assert state['vtwrites']==2*word(258)
    assert word(232)==719 and word(233)==479 and word(234)==1 and value==(479 if n==1 else 719)
    writes.append(['v',off,value])
    if fault==('v-drop-write' if n==1 else 'v-drop-undo'):return
    mm[off]=value
    if fault==('v-wrong-write' if n==1 else 'v-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('v-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=6
     if j<=4:mm[V[j][0]]^=1
     else:cr[[0x13,0x19][j-5]]^=1
    return
   val=mm[off];phase=['before','after','undo'][state['vwrites']]
   if state['sewrites']==1 and word(1) in [0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    sj={0x680800:1,0x680804:2,0x68080c:5,0x680810:6,0x680818:0}[off]
    sp=['before','after','undo'][state['vewrites']]
    if fault=='ve-'+sp+'-'+str(sj):val^=1

   if state['sywrites']==1 and word(1) in [0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    sj={0x680800:1,0x680804:2,0x68080c:5,0x680810:0,0x680818:6}[off]
    sp=['before','after','undo'][state['sewrites']]
    if fault=='se-'+sp+'-'+str(sj):val^=1

   if state['vswrites']==1 and word(1) in [0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    sj={0x680800:1,0x680804:2,0x68080c:0,0x680810:5,0x680818:6}[off]
    sp=['before','after','undo'][state['sywrites']]
    if fault=='sy-'+sp+'-'+str(sj):val^=1

   if state['vcwrites']==1 and word(1) in [0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    sj={0x680800:1,0x680804:2,0x68080c:4,0x680810:5,0x680818:6}[off]
    sp=['before','after','undo'][state['vswrites']]
    if fault=='vs-'+sp+'-'+str(sj):val^=1

   if state['vtwrites']==1 and word(1) in [0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    cj={0x680800:1,0x680804:2,0x68080c:3,0x680810:4,0x680818:6}[off]
    cp=['before','after','undo'][state['vcwrites']]
    if fault=='vc-'+cp+'-'+str(cj):val^=1

   if state['vwrites']==1 and word(1) in [0x80624,0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642,0x806]:
    tj=[0x680804,0x680800,0x68080c,0x680810,0x680818].index(off)
    tp=['before','after','undo'][state['vtwrites']]
    if fault=='vt-'+tp+'-'+str(tj):val^=1

   if fault=='v-'+phase+'-'+str(j):val^=1
  elif off in dict(H):
   assert width==4;n=[a for a,_ in H].index(off)
   if kind==u.UC_MEM_WRITE:
    hw[off]+=1;assert hw[off]<=2
    target=H[n][1] if hw[off]==1 else HB[n]
    assert value==target and state['sq']==0x21 and ports==[5]
    writes.append(['h',off,value])
    if hw[off]==2:hr.append(n)
    if fault==('h-write-' if hw[off]==1 else 'h-restore-write-')+str(n):return
    mm[off]=value;return
   val=mm[off]
   if word(1)==0x8069 and word(98)<=6 and not hr and fault=='h-read-'+str(n):val^=1
   if hr and fault=='h-restore-read-'+str(n):val^=1
   # When no horizontal writes occurred, recovery still checks all seven words.
   if not hw[off] and state['unlock'] and word(1)==0x8068 and fault=='h-pre-restore-'+str(n):val^=1
  else:
   assert off in mm and width==4
   if kind==u.UC_MEM_WRITE:
    assert value==dict(SETUP)[off] or (off,value)==(0x680630,3)
    writes.append(['mm',off,value])
    if (off,value)==(0x680630,3):
     state['recovering']=True
     if fault=='cleanup-14':cr[0x1b]^=1
     if fault=='cleanup-8':return
    mm[off]=value;return
   val=mm[off]
   n=[i for i,_ in SETUP].index(off)
   if word(1)==0x8068 and not state['recovering']:
    assert word(2)==11 and word(3)==3
    if fault=='check-'+str(n):val^=1
   if state['recovering'] and fault=='cleanup-'+str(n) and n!=8:val^=1
  if off==0x6013d5 and state['recovering'] and fault in ['cleanup-11','cleanup-12']:
   if sels[0x6013d4]==CS[int(fault.split('-')[1])-11][0]:val^=1
  reads.append([off,sels.get(off-1),val,word(1),bool(state['recovering'])])
  uc.mem_write(addr,val.to_bytes(width,'little'))
 regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_EBX,x.UC_X86_REG_ESP,x.UC_X86_REG_EBP,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI]
 def code(uc,pc,n,_):
  steps[0]+=1
  if n>15:raise AssertionError(('invalid-instruction',hex(pc),n,bytes(uc.mem_read(pc,16)).hex()))
  raw=bytes(uc.mem_read(pc,n));assert raw[:2]!=b'\x0f\x22'
  if raw[:2]==b'\x0f\x20':
   mod=raw[2];assert mod>>6==3;reg=(mod>>3)&7;assert reg in (0,3,4)
   uc.reg_write(regs[mod&7],{0:cpu0,3:cpu3,4:cpu4}[reg]);uc.reg_write(x.UC_X86_REG_EIP,pc+n)
  if not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200:steps[1]+=1
 def ramwrite(uc,kind,addr,size,val,_):
  if GPU<=addr<GPU+0x1000000:return
  assert 0x201000<=addr and addr+size<=0x201b68 or 0x207000<=addr and addr+size<=0x208008,(hex(addr),size)
 def pout(uc,port,size,val,_):
  assert (port,size)==(0x80d3,1) and val in [4,5]
  assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  ports.append(val)
  if val==4:
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
   assert word(375)==0 and (not word(372) or word(374)==word(370))
   assert word(345)==0 and (not word(342) or word(344)==word(340))
   assert word(315)==0 and (not word(312) or word(314)==word(310))
   assert word(285)==0 and (not word(282) or word(284)==word(280))
   assert mm[0x680808]==719 and mm[0x680814]==0
   assert word(261)==0 and (not word(258) or word(260)==word(256))
   assert word(237)==0 and (not word(234) or word(236)==word(232))
   assert [mm[a] for a,_ in V]==[b for _,b in V]
   assert word(221)==0 and (not word(218) or (word(220)==word(216) and word(231)==word(222)))
   assert word(205)==0 and (not word(202) or (word(204)==word(200) and word(215)==word(206)))
   assert word(193)==0 and (not word(190) or word(192)==word(188))
   assert word(181)==0 and (not word(178) or word(180)==word(176))
   assert word(169)==0 and cr[1]==c1_original and (not word(166) or word(168)==c1_original)
   assert word(158)==0 and cr[0x17]==0xe3 and (not word(155) or word(157)==0xe3)
   assert word(148)==0 and (not word(145) or word(147)==0x3e)
   assert word(138)==0 and cr[3]==0x8c and word(137)==0x8c
   assert word(129)==0 and cr[2]==0x9f and word(128)==0x9f
   assert word(121)==0 and cr[0]==0xc8 and word(120)==0xc8
   assert word(108)==0 and cr[4]==0xa7 and cr[5]==0x31
   assert word(106)==0xa7 and word(111)==0x31
   assert word(100)==0 and word(97) in [0,7]
   assert list(mm[a] for a,_ in H)==HB, 'output enabled with wrong timing'
   assert list(c.mem_read(0x201000+90*4,28))==list(struct.pack('<7I',*HB))
   state['recovering']=True
 def pin(*args):raise AssertionError('Unexpected input port')
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,GPU,GPU+0xffffff)
 c.hook_add(u.UC_HOOK_MEM_WRITE,ramwrite);c.hook_add(u.UC_HOOK_CODE,code)
 c.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
 c.hook_add(u.UC_HOOK_INSN,pin,None,1,0,x.UC_X86_INS_IN)
 def invalid(uc,access,addr,size,value,_):
  raise AssertionError(('unmapped',hex(uc.reg_read(x.UC_X86_REG_EIP)),hex(addr),size,hex(uc.reg_read(x.UC_X86_REG_ESP))))
 c.hook_add(u.UC_HOOK_MEM_INVALID,invalid)
 try:c.emu_start(sy['probe806'],0x20ff00,timeout=2000000,count=30000)
 except Exception as exc:
  raise AssertionError((name,str(exc),hex(c.reg_read(x.UC_X86_REG_EIP)),hex(c.reg_read(x.UC_X86_REG_ESP)),steps,writes[-5:])) from exc
 assert c.reg_read(x.UC_X86_REG_EIP)==0x20ff00 and c.reg_read(x.UC_X86_REG_ESP)==0x208004,(name,hex(c.reg_read(x.UC_X86_REG_EIP)),hex(c.reg_read(x.UC_X86_REG_ESP)),steps)
 v=list(struct.unpack('<730I',c.mem_read(0x201000,2920)))
 assert v[8]==v[10] and not v[9]&0x200 and v[8]&0x200==flags&0x200
 assert v[11:14]==[cpu0,cpu3,cpu4] and c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
 assert bytes(c.mem_read(0x200000,4096))==b'G'*4096
 assert bytes(c.mem_read(0x201b68,0x5498))==b'G'*0x5498
 assert bytes(c.mem_read(0x208008,0xff8))==b'G'*0xff8 and sels==original
 cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or bool(flags&0x200) or cpu4&0x20
 if cpu_bad:
  assert v[0:2]==[0x8061]*2 and not writes and not ports and not reads
 elif baseline:
  assert v[0:2]==[0x8062]*2 and not writes and not ports and v[28]==1
 else:
  umask=(1 if fault in ['c13-undo-read','c13-drop-undo'] else 0)|(2 if fault in ['c13-c25-coupling','c19-undo-c13-read','v-coupling-6','vt-coupling-6','vc-coupling-8','vs-coupling-8','sy-coupling-8','se-coupling-8','ve-coupling-8'] else 0)
  ubad=bool(umask)
  vmask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('v-undo-','v-coupling-')) else 1 if fault in ['v-drop-undo','v-wrong-undo'] else 0
  if fault.startswith('vt-coupling-') and int(fault.rsplit('-',1)[1])>=2:vmask|=1<<int(fault.rsplit('-',1)[1])
  if fault in ['vt-drop-undo','vt-wrong-undo']:vmask|=2
  if fault.startswith('vc-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={3:2,4:3,6:4,7:5,8:6}.get(j)
   if k is not None:vmask|=1<<k
  if fault.startswith('vs-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={4:2,5:3,6:4,7:5,8:6}.get(j)
   if k is not None:vmask|=1<<k
  if fault.startswith('sy-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={5: 3, 6: 4, 7: 5, 8: 6}.get(j)
   if k is not None:vmask|=1<<k
  if fault in ['sy-drop-undo','sy-wrong-undo']:vmask|=4
  if fault.startswith('se-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={6: 4, 7: 5, 8: 6}.get(j)
   if k is not None:vmask|=1<<k
  if fault in ['se-drop-undo','se-wrong-undo']:vmask|=8
  if fault.startswith('ve-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={7: 5, 8: 6}.get(j)
   if k is not None:vmask|=1<<k
  if fault in ['ve-drop-undo','ve-wrong-undo']:vmask|=16
  vbad=bool(vmask)
  qmask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('vt-undo-','vt-coupling-')) else 1 if fault in ['vt-drop-undo','vt-wrong-undo'] else 0
  if fault.startswith('vc-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1:1,3:2,4:3,6:4,7:5,8:6}.get(j)
   if k is not None:qmask|=1<<k
  if fault.startswith('vs-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1:1,4:2,5:3,6:4,7:5,8:6}.get(j)
   if k is not None:qmask|=1<<k
  if fault.startswith('sy-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1: 1, 5: 3, 6: 4, 7: 5, 8: 6}.get(j)
   if k is not None:qmask|=1<<k
  if fault in ['sy-drop-undo','sy-wrong-undo']:qmask|=4
  if fault.startswith('se-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1: 1, 6: 4, 7: 5, 8: 6}.get(j)
   if k is not None:qmask|=1<<k
  if fault in ['se-drop-undo','se-wrong-undo']:qmask|=8
  if fault.startswith('ve-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1: 1, 7: 5, 8: 6}.get(j)
   if k is not None:qmask|=1<<k
  if fault in ['ve-drop-undo','ve-wrong-undo']:qmask|=16
  qbad=bool(qmask)
  wmask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('vc-undo-','vc-coupling-')) else 1 if fault in ['vc-drop-undo','vc-wrong-undo'] else 0
  if fault.startswith('vs-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,4:3,5:4,6:6,7:7,8:8}.get(j)
   if k is not None:wmask|=1<<k
  if fault in ['vs-wrong-undo','vs-wrong-write-drop-undo']:wmask|=32
  if fault.startswith('sy-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 5: 4, 6: 6, 7: 7, 8: 8}.get(j)
   if k is not None:wmask|=1<<k
  if fault in ['sy-drop-undo','sy-wrong-undo']:wmask|=8
  if fault.startswith('se-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 6: 6, 7: 7, 8: 8}.get(j)
   if k is not None:wmask|=1<<k
  if fault in ['se-drop-undo','se-wrong-undo']:wmask|=16
  if fault.startswith('ve-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 7: 7, 8: 8}.get(j)
   if k is not None:wmask|=1<<k
  if fault in ['ve-drop-undo','ve-wrong-undo']:wmask|=64
  wbad=bool(wmask)
  xmask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('vs-undo-','vs-coupling-')) else 1 if fault in ['vs-wrong-undo','vs-wrong-write-drop-undo'] else 0
  if fault.startswith('sy-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 3: 3, 5: 5, 6: 6, 7: 7, 8: 8}.get(j)
   if k is not None:xmask|=1<<k
  if fault in ['sy-drop-undo','sy-wrong-undo']:xmask|=16
  if fault.startswith('se-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 3: 3, 6: 6, 7: 7, 8: 8}.get(j)
   if k is not None:xmask|=1<<k
  if fault in ['se-drop-undo','se-wrong-undo']:xmask|=32
  if fault.startswith('ve-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 3: 3, 7: 7, 8: 8}.get(j)
   if k is not None:xmask|=1<<k
  if fault in ['ve-drop-undo','ve-wrong-undo']:xmask|=64
  xbad=bool(xmask)
  ymask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('sy-undo-','sy-coupling-')) else 1 if fault in ['sy-drop-undo','sy-wrong-undo'] else 0
  if fault.startswith('se-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 3: 3, 4: 4, 6: 6, 7: 7, 8: 8}.get(j)
   if k is not None:ymask|=1<<k
  if fault in ['se-drop-undo','se-wrong-undo']:ymask|=32
  if fault.startswith('ve-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 3: 3, 4: 4, 7: 7, 8: 8}.get(j)
   if k is not None:ymask|=1<<k
  if fault in ['ve-drop-undo','ve-wrong-undo']:ymask|=64
  ybad=bool(ymask)
  endmask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('se-undo-','se-coupling-')) else 1 if fault in ['se-drop-undo','se-wrong-undo'] else 0
  if fault.startswith('ve-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 7: 7, 8: 8}.get(j)
   if k is not None:endmask|=1<<k
  if fault in ['ve-drop-undo','ve-wrong-undo']:endmask|=64
  endbad=bool(endmask)
  vemask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('ve-undo-','ve-coupling-')) else 1 if fault in ['ve-drop-undo','ve-wrong-undo'] else 0
  vebad=bool(vemask)
  c7mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('c7-undo-','c7-coupling-')) else 1 if fault in ['c7-drop-undo','c7-wrong-undo'] else 0
  # Persistent CR10 corruption is visible in CR07's later neighbor recovery.
  if fault in ['c10-drop-undo','c10-wrong-undo']:c7mask|=8
  if fault.startswith('c10-coupling-'):c7mask|=[0,2,0,4,16,32,64,128,256][int(fault.rsplit('-',1)[1])]
  if fault.startswith('ct7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);c7mask|={1:2,2:4,3:0,4:16,5:32,6:64,7:128,8:256}[j]
  if fault in ['ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo']:c7mask|=2
  if fault.startswith('ct6-coupling-'):
   j=int(fault.rsplit('-',1)[1]);c7mask|={1:0,2:4,3:0,4:16,5:32,6:64,7:128,8:256}[j]
  if fault in ['ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo']:c7mask|=64
  if fault.startswith('ct16-coupling-'):
   j=int(fault.rsplit('-',1)[1]);c7mask|={1: 0, 2: 0, 3: 4, 4: 0, 5: 16, 6: 32, 7: 128, 8: 256}[j]
  if fault in ['cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo']:c7mask|=0
  if fault.startswith('cd7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);c7mask|={1: 0, 2: 4, 3: 0, 4: 16, 5: 32, 6: 0, 7: 128, 8: 256}[j]
  if fault in ['cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo']:c7mask|=16
  if fault.startswith('cd12-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={3: 2, 5: 5, 7: 7, 8: 8}
   if j in mapping:c7mask|=1<<mapping[j]
  if fault in ['cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:c7mask|=4
  if fault.startswith('cb9-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={5: 5, 7: 7, 8: 8}
   if j in mapping:c7mask|=1<<mapping[j]
  if fault.startswith('cb7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={5: 5, 7: 7, 8: 8}
   if j in mapping:c7mask|=1<<mapping[j]
  if fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:c7mask|=32
  if fault.startswith('cb15-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={7: 7, 8: 8}
   if j in mapping:c7mask|=1<<mapping[j]
  c7bad=bool(c7mask)
  c10mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('c10-undo-','c10-coupling-')) else 1 if fault in ['c10-drop-undo','c10-wrong-undo'] else 0
  if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:c10mask|=4
  if fault.startswith('ct7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);c10mask|={1:2,2:8,3:0,4:16,5:32,6:64,7:128,8:256}[j]
  if fault in ['ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo']:c10mask|=2
  if fault.startswith('ct6-coupling-'):
   j=int(fault.rsplit('-',1)[1]);c10mask|={1:0,2:8,3:0,4:16,5:32,6:64,7:128,8:256}[j]
  if fault in ['ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo']:c10mask|=64
  if fault.startswith('ct16-coupling-'):
   j=int(fault.rsplit('-',1)[1]);c10mask|={1: 0, 2: 0, 3: 8, 4: 0, 5: 16, 6: 32, 7: 128, 8: 256}[j]
  if fault in ['cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo']:c10mask|=0
  if fault.startswith('cd7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);c10mask|={1: 0, 2: 8, 3: 0, 4: 16, 5: 32, 6: 0, 7: 128, 8: 256}[j]
  if fault in ['cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo']:c10mask|=16
  if fault.startswith('cd12-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 5: 5, 7: 7, 8: 8}
   if j in mapping:c10mask|=1<<mapping[j]
  if fault in ['cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:c10mask|=8
  if fault.startswith('cb9-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={5: 5, 7: 7, 8: 8}
   if j in mapping:c10mask|=1<<mapping[j]
  if fault.startswith('cb7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={5: 5, 7: 7, 8: 8}
   if j in mapping:c10mask|=1<<mapping[j]
  if fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:c10mask|=32
  if fault.startswith('cb15-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={7: 7, 8: 8}
   if j in mapping:c10mask|=1<<mapping[j]
  c10bad=bool(c10mask)
  ct7mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('ct7-undo-','ct7-coupling-')) else 1 if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo'] else 0
  if fault in ['ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo']:ct7mask|=2
  if fault.startswith('ct6-coupling-'):
   j=int(fault.rsplit('-',1)[1]);ct7mask|={1:0,2:4,3:8,4:16,5:32,6:64,7:128,8:256}[j]
  if fault in ['ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo']:ct7mask|=64
  if fault.startswith('ct16-coupling-'):
   j=int(fault.rsplit('-',1)[1]);ct7mask|={1: 0, 2: 0, 3: 4, 4: 8, 5: 16, 6: 32, 7: 128, 8: 256}[j]
  if fault in ['cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo']:ct7mask|=0
  if fault.startswith('cd7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);ct7mask|={1: 0, 2: 4, 3: 8, 4: 16, 5: 32, 6: 0, 7: 128, 8: 256}[j]
  if fault in ['cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo']:ct7mask|=16
  if fault.startswith('cd12-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={3: 2, 4: 3, 5: 5, 7: 7, 8: 8}
   if j in mapping:ct7mask|=1<<mapping[j]
  if fault in ['cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:ct7mask|=4
  if fault.startswith('cb9-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 5: 5, 7: 7, 8: 8}
   if j in mapping:ct7mask|=1<<mapping[j]
  if fault.startswith('cb7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 5: 5, 7: 7, 8: 8}
   if j in mapping:ct7mask|=1<<mapping[j]
  if fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:ct7mask|=32
  if fault.startswith('cb15-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={4: 3, 7: 7, 8: 8}
   if j in mapping:ct7mask|=1<<mapping[j]
  ct7bad=bool(ct7mask)
  ct6mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('ct6-undo-','ct6-coupling-')) else 1 if fault in ['ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo'] else 0
  if fault in ['ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo']:ct6mask|=64
  if fault.startswith('ct16-coupling-'):
   j=int(fault.rsplit('-',1)[1]);ct6mask|={1: 0, 2: 2, 3: 4, 4: 8, 5: 16, 6: 32, 7: 128, 8: 256}[j]
  if fault in ['cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo']:ct6mask|=2
  if fault.startswith('cd7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);ct6mask|={1: 0, 2: 4, 3: 8, 4: 16, 5: 32, 6: 0, 7: 128, 8: 256}[j]
  if fault in ['cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo']:ct6mask|=16
  if fault.startswith('cd12-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={3: 2, 4: 3, 5: 5, 7: 7, 8: 8}
   if j in mapping:ct6mask|=1<<mapping[j]
  if fault in ['cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:ct6mask|=4
  if fault.startswith('cb9-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 5: 5, 7: 7, 8: 8}
   if j in mapping:ct6mask|=1<<mapping[j]
  if fault.startswith('cb7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={3: 3, 5: 5, 7: 7, 8: 8}
   if j in mapping:ct6mask|=1<<mapping[j]
  if fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:ct6mask|=32
  if fault.startswith('cb15-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={4: 3, 7: 7, 8: 8}
   if j in mapping:ct6mask|=1<<mapping[j]
  ct6bad=bool(ct6mask)
  ct16mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('ct16-undo-','ct16-coupling-')) else 1 if fault in ['ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo'] else 0
  if fault in ['cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo']:ct16mask|=4
  if fault.startswith('cd7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);ct16mask|={1: 2, 2: 8, 3: 16, 4: 32, 5: 64, 6: 0, 7: 128, 8: 256}[j]
  if fault in ['cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo']:ct16mask|=32
  if fault.startswith('cd12-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 4: 4, 5: 6, 7: 7, 8: 8}
   if j in mapping:ct16mask|=1<<mapping[j]
  if fault in ['cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:ct16mask|=8
  if fault.startswith('cb9-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 4, 5: 6, 7: 7, 8: 8}
   if j in mapping:ct16mask|=1<<mapping[j]
  if fault.startswith('cb7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 4, 5: 6, 7: 7, 8: 8}
   if j in mapping:ct16mask|=1<<mapping[j]
  if fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:ct16mask|=64
  if fault.startswith('cb15-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 4: 4, 7: 7, 8: 8}
   if j in mapping:ct16mask|=1<<mapping[j]
  ct16bad=bool(ct16mask)
  cd7mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('cd7-undo-','cd7-coupling-')) else 1 if fault in ['cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo'] else 0
  if fault in ['cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo']:cd7mask|=16
  if fault.startswith('cd12-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 2, 4: 3, 5: 5, 6: 6, 7: 7, 8: 8}
   if j in mapping:cd7mask|=1<<mapping[j]
  if fault in ['cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:cd7mask|=4
  if fault.startswith('cb9-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 5: 5, 6: 6, 7: 7, 8: 8}
   if j in mapping:cd7mask|=1<<mapping[j]
  if fault.startswith('cb7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 5: 5, 6: 6, 7: 7, 8: 8}
   if j in mapping:cd7mask|=1<<mapping[j]
  if fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:cd7mask|=32
  if fault.startswith('cb15-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 4: 3, 6: 6, 7: 7, 8: 8}
   if j in mapping:cd7mask|=1<<mapping[j]
  cd7bad=bool(cd7mask)
  cd12mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('cd12-undo-','cd12-coupling-')) else 1 if fault in ['cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo'] else 0
  if fault in ['cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:cd12mask|=8
  if fault.startswith('cb9-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 2: 2, 3: 4, 5: 5, 6: 6, 7: 7, 8: 8}
   if j in mapping:cd12mask|=1<<mapping[j]
  if fault in ['cb7-drop-undo','cb7-wrong-undo','cb7-wrong-write-drop-undo']:cd12mask|=4
  if fault.startswith('cb7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 4, 5: 5, 6: 6, 7: 7, 8: 8}
   if j in mapping:cd12mask|=1<<mapping[j]
  if fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:cd12mask|=32
  if fault.startswith('cb15-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 4: 4, 6: 6, 7: 7, 8: 8}
   if j in mapping:cd12mask|=1<<mapping[j]
  cd12bad=bool(cd12mask)
  cb9mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('cb9-undo-','cb9-coupling-')) else 1 if fault in ['cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo'] else 0
  if fault in ['cb7-drop-undo','cb7-wrong-undo','cb7-wrong-write-drop-undo']:cb9mask|=4
  if fault.startswith('cb7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8}
   if j in mapping:cb9mask|=1<<mapping[j]
  if fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:cb9mask|=32
  if fault.startswith('cb15-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 4: 3, 5: 4, 6: 6, 7: 7, 8: 8}
   if j in mapping:cb9mask|=1<<mapping[j]
  cb9bad=bool(cb9mask)
  cb7mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('cb7-undo-','cb7-coupling-')) else 1 if fault in ['cb7-drop-undo','cb7-wrong-undo','cb7-wrong-write-drop-undo'] else 0
  if fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:cb7mask|=32
  if fault.startswith('cb15-coupling-'):
   j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 2, 4: 3, 5: 4, 6: 6, 7: 7, 8: 8}
   if j in mapping:cb7mask|=1<<mapping[j]
  cb7bad=bool(cb7mask)
  cb15mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('cb15-undo-','cb15-coupling-')) else 1 if fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo'] else 0
  cb15bad=bool(cb15mask)
  tmask=(1 if fault in ['c19b-undo-read','c19b-drop-undo'] else 0)|(2 if fault in ['c19b-c19-coupling','c13-undo-c19b-read','c13-drop-undo'] else 0)
  tbad=bool(tmask)
  sbad=fault in ['c17b-undo-read','c17b-drop-undo']
  rbad=fault in ['c2b-undo-read','c2b-wrong-write-drop-undo']
  fbad=fault in ['c1-undo-read','c1-drop-undo']
  dbad=fault in ['c17-undo-read','c17-drop-undo']
  nbad=fault in ['c5b-undo-read','c5b-drop-undo']
  hbad=fault.startswith(('h-restore-read-','h-restore-write-'))
  ebad=fault in ['c3-restore-read','c3-drop-restore']
  bbad=fault in ['c2-restore-read','c2-drop-restore']
  zbad=fault in ['c0-restore-read','c0-drop-restore']
  cbad=fault in ['c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling','c5-drop-restore']
  assert ports==([5] if hbad or cbad or zbad or bbad or ebad or nbad or dbad or fbad or rbad or sbad or tbad or ubad or vbad or qbad or wbad or xbad or ybad or endbad or vebad or c7bad or c10bad or ct7bad or ct6bad or ct16bad or cd7bad or cd12bad or cb9bad or cb7bad or cb15bad else [5,4]),(name,ports)
  forward=0x8063 if fault=='blank' else 0x8064 if fault=='unlock' else 0x8068 if fault.startswith('check-') else 0x8069 if fault.startswith(('h-read-','h-write-')) else 0x806b if fault in ['c4-read','c4-write','c5-read','c5-coupling'] else 0x806d if fault in ['c5-drop-write','c5-low-read','c5-high-read','c4-after-read','c4-coupling'] else 0x806e if fault in ['c0-read','c0-drop-write','c4-after-c0-read','c5-after-c0-read','c0-c4-coupling','c0-c5-coupling'] else 0x80610 if fault in ['c2-read','c2-drop-write','c0-after-c2-read','c4-after-c2-read','c5-after-c2-read','c2-c0-coupling','c2-c4-coupling','c2-c5-coupling'] else 0x80612 if fault in ['c3-read','c3-high-read','c3-drop-write']+['c'+str(i)+'-after-c3-read' for i in [0,2,4,5]]+['c3-c'+str(i)+'-coupling' for i in [0,2,4,5]] else 0x80614 if fault in ['c5b-read','c5b-high-read','c5b-drop-write','c5b-wrong-write']+['c'+str(i)+'-after-c5b-read' for i in [0,2,3,4]]+['c5b-c'+str(i)+'-coupling' for i in [0,2,3,4]] else 0x80616 if fault in ['c17-before-read','c17-read','c17-high-read','c17-drop-write','c17-wrong-write']+['c'+str(i)+'-after-c17-read' for i in [0,2,3,4,5]]+['c17-c'+str(i)+'-coupling' for i in [0,2,3,4,5]] else 0x80618 if fault in ['c1-read','c1-high-read','c1-drop-write','c1-wrong-write']+['c'+str(i)+'-after-c1-read' for i in [0,2,3,4,5,0x17]]+['c1-c'+str(i)+'-coupling' for i in [0,2,3,4,5,0x17]] else 0x8061a if fault in ['c2b-before-read','c2b-read','c2b-high-read','c2b-wrong-write','c2b-wrong-write-drop-undo']+['c'+str(i)+'-after-c2b-read' for i in [0,1,3,4,5,0x17]]+['c2b-c'+str(i)+'-coupling' for i in [0,1,3,4,5,0x17]] else 0x8061c if fault in ['c17b-before-read','c17b-read','c17b-low-read','c17b-drop-write','c17b-wrong-write']+['c'+str(i)+'-after-c17b-read' for i in [0,1,2,3,4,5]]+['c17b-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5]] else 0x8061e if fault in ['c19b-before-read','c13-before-c19b-read','c19b-read','c19b-high-read','c19b-drop-write','c19b-wrong-write']+['c'+str(i)+'-after-c19b-read' for i in [0,1,2,3,4,5,0x13,0x17]]+['c19b-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5,0x13,0x17]] else 0x80620 if fault in ['c13-before-read','c19-before-c13-read','c13-read','c13-high-read','c13-drop-write','c13-wrong-write']+['c'+str(i)+'-after-c13-read' for i in [0,1,2,3,4,5,0x19,0x17]]+['c13-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5,0x19,0x17]] else 0x80622 if fault.startswith(('v-before-','v-after-','v-coupling-')) or fault in ['v-drop-write','v-wrong-write'] else 0x80624 if fault.startswith(('vt-before-','vt-after-','vt-coupling-')) or fault in ['vt-drop-write','vt-wrong-write'] else 0x80626 if fault.startswith(('vc-before-','vc-after-','vc-coupling-')) or fault in ['vc-drop-write','vc-wrong-write'] else 0x80628 if fault.startswith(('vs-before-','vs-after-','vs-coupling-')) or fault in ['vs-wrong-write','vs-wrong-write-drop-undo'] else 0x8062a if fault.startswith(('sy-before-','sy-after-','sy-coupling-')) or fault in ['sy-drop-write','sy-wrong-write'] else 0x8062c if fault.startswith(('se-before-','se-after-','se-coupling-')) or fault in ['se-drop-write','se-wrong-write'] else 0x8062e if fault.startswith(('ve-before-','ve-after-','ve-coupling-')) or fault in ['ve-drop-write','ve-wrong-write'] else 0x80630 if fault.startswith(('c7-before-','c7-after-','c7-coupling-')) or fault in ['c7-drop-write','c7-wrong-write'] else 0x80632 if fault.startswith(('c10-before-','c10-after-','c10-coupling-')) or fault in ['c10-drop-write','c10-wrong-write'] else 0x80634 if fault.startswith(('ct7-before-','ct7-after-','ct7-coupling-')) or fault in ['ct7-wrong-write','ct7-wrong-write-drop-undo'] else 0x80636 if fault.startswith(('ct6-before-','ct6-after-','ct6-coupling-')) or fault in ['ct6-drop-write','ct6-wrong-write','ct6-wrong-write-drop-undo'] else 0x80638 if fault.startswith(('ct16-before-','ct16-after-','ct16-coupling-')) or fault in ['ct16-drop-write','ct16-wrong-write','ct16-wrong-write-drop-undo'] else 0x8063a if fault.startswith(('cd7-before-','cd7-after-','cd7-coupling-')) or fault in ['cd7-drop-write','cd7-wrong-write','cd7-wrong-write-drop-undo'] else 0x8063c if fault.startswith(('cd12-before-','cd12-after-','cd12-coupling-')) or fault in ['cd12-drop-write','cd12-wrong-write','cd12-wrong-write-drop-undo'] else 0x8063e if fault.startswith(('cb9-before-','cb9-after-','cb9-coupling-')) or fault in ['cb9-drop-write','cb9-wrong-write','cb9-wrong-write-drop-undo'] else 0x80640 if fault.startswith(('cb7-before-','cb7-after-','cb7-coupling-')) or fault in ['cb7-drop-write','cb7-wrong-write','cb7-wrong-write-drop-undo'] else 0x80642 if fault.startswith(('cb15-before-','cb15-after-','cb15-coupling-')) or fault in ['cb15-drop-write','cb15-wrong-write','cb15-wrong-write-drop-undo'] else 0x806
  assert v[1]==forward,(name,v)
  fullprefix=forward in [0x806,0x8068,0x8069,0x806b,0x806d,0x806e,0x80610,0x80612,0x80614,0x80616,0x80618,0x8061a,0x8061c,0x8061e,0x80620,0x80622,0x80624,0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
  if fullprefix:
   assert v[2:4]==[11,3]
   fail=int(fault.split('-')[1]) if fault.startswith('check-') else None
   assert v[4]==(fail if fail is not None else 0xffffffff) and v[7]==(fail+1 if fail is not None else 15)
   checked=v[42:53]+v[68:72];expected=[b for _,b in SETUP+CS]
   for n,value in enumerate(checked):
    assert value==(0xffffffff if fail is not None and n>fail else expected[n]^(1 if n==fail else 0)),(name,n,value)
   if fail is not None:assert v[5:7]==[expected[fail],expected[fail]^1]
  else:assert v[2:4]==[0,0] and v[7]==0
  horizontal_ran=forward in [0x806,0x8069,0x806b,0x806d,0x806e,0x80610,0x80612,0x80614,0x80616,0x80618,0x8061a,0x8061c,0x8061e,0x80620,0x80622,0x80624,0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
  expectedwrites=[['sq',1,0x21]]
  if fault!='blank':expectedwrites+=[['cr',0x1f,0x57]]
  if fullprefix:expectedwrites += [['mm',a,b] for a,b in SETUP]+[['cr',a,b] for a,b in CS[:3]]
  if horizontal_ran:
   expectedwrites += [['h',a,b] for a,b in H]
   if forward!=0x8069:
    expectedwrites += [['cr',4,93]]
    if forward!=0x806b:
     expectedwrites += [['cr',5,0x3e]]
     if forward!=0x806d:
      expectedwrites += [['cr',0,0x5c]]
      if forward!=0x806e:
       expectedwrites += [['cr',2,0x59]]
       if forward!=0x80610:
        expectedwrites += [['cr',3,0x80]]
        if forward!=0x80612:
         expectedwrites += [['cr',5,0xbe]]
         if forward!=0x80614 and fault!='c17-before-read':
          expectedwrites += [['cr',0x17,0x63]]
          if forward!=0x80616:
           expectedwrites += [['cr',1,0x59]]
           if forward!=0x80618 and fault!='c2b-before-read':
            expectedwrites += [['cr',2,0x59]]
            if forward!=0x8061a and fault!='c17b-before-read':
             expectedwrites += [['cr',0x17,0xe3]]
             if forward!=0x8061c and fault not in ['c19b-before-read','c13-before-c19b-read']:
              expectedwrites += [['cr',0x19,0x30]]
              if forward!=0x8061e and fault not in ['c13-before-read','c19-before-c13-read']:expectedwrites += [['cr',0x13,0x68]]+([['v',0x680800,479]]+([['vt',0x680804,524]]+([['vc',0x680808,479]]+([['vs',0x680814,0]]+([['sy',0x68080c,489]]+([['se',0x680810,492]]+([['ve',0x680818,479]]+([['cr',7,116]]+([['cr',0x10,233]]+([['cr',7,116]]+([['cr',6,12]]+([['cr',22,140]]+([['cr',7,54]]+([['cr',18,223]]+([['cr',9,64]]+([['cr',7,62]]+([['cr',21,223],['cr',21,207]] if forward in [0x806,0x80642] and not fault.startswith('cb15-before-') else [])+[['cr',7,54]] if forward in [0x806,0x80640,0x80642] and not fault.startswith('cb7-before-') else [])+[['cr',9,96]] if forward in [0x806,0x8063e,0x80640,0x80642] and not fault.startswith('cb9-before-') else [])+[['cr',18,207]] if forward in [0x806,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('cd12-before-') else [])+[['cr',7,116]] if forward in [0x806,0x8063a,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('cd7-before-') else [])+[['cr',22,237]] if forward in [0x806,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('ct16-before-') else [])+[['cr',6,236]] if forward in [0x806,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('ct6-before-') else [])+[['cr',7,116]] if forward in [0x806,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('ct7-before-') else [])+[['cr',0x10,212]] if forward in [0x806,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('c10-before-') else [])+[['cr',7,240]] if forward in [0x806,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('c7-before-') else [])+[['ve',0x680818,719]] if forward in [0x806,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('ve-before-') else [])+[['se',0x680810,729]] if forward in [0x806,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('se-before-') else [])+[['sy',0x68080c,724]] if forward in [0x806,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('sy-before-') else [])+[['vs',0x680814,0]] if forward in [0x806,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('vs-before-') else [])+[['vc',0x680808,719]] if forward in [0x806,0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('vc-before-') else [])+[['vt',0x680804,749]] if forward in [0x806,0x80624,0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('vt-before-') else [])+[['v',0x680800,719]] if forward in [0x806,0x80622,0x80624,0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642] and not fault.startswith('v-before-') else [])+[['cr',0x13,0x80]]
              expectedwrites += [['cr',0x19,0x10]]
             expectedwrites += [['cr',0x17,0x63]]
            expectedwrites += [['cr',2,0x59]]
           expectedwrites += [['cr',1,c1_original]]
          expectedwrites += [['cr',0x17,0xe3]]
         expectedwrites += [['cr',5,0x3e]]
        expectedwrites += [['cr',3,0x8c]]
       expectedwrites += [['cr',2,0x9f]]
      expectedwrites += [['cr',0,0xc8]]
     expectedwrites += [['cr',5,0x31]]
    expectedwrites += [['cr',4,0xa7]]
   expectedwrites += [['h',H[i][0],HB[i]] for i in range(6,-1,-1)]
   assert v[97]==7 and hr==list(range(6,-1,-1))
   hf=int(fault.rsplit('-',1)[1]) if forward==0x8069 else None
   assert v[98]==(7 if hf is None else hf+1) and v[99]==(0xffffffff if hf is None else hf)
   target=[b for _,b in H];got=v[83:90]
   assert got[:(7 if hf is None else hf)]==target[:(7 if hf is None else hf)]
   if hf is not None:
    assert got[hf]!=target[hf] and v[102:104]==[target[hf],got[hf]]
    assert got[hf+1:]==[0xffffffff]*(6-hf)
  else:
   assert v[97:100]==[0,0,0xffffffff] and v[83:90]==[0xffffffff]*7
  if fullprefix:expectedwrites += [['cr',0x19,0x51],['mm',0x680630,3]]
  if not (hbad or cbad or zbad or bbad or ebad or nbad or dbad or fbad or rbad or sbad or tbad or ubad or vbad or qbad or wbad or xbad or ybad or endbad or vebad or c7bad or c10bad or ct7bad or ct6bad or ct16bad or cd7bad or cd12bad or cb9bad or cb7bad or cb15bad):expectedwrites += [['sq',1,1]]
  assert writes==expectedwrites,(name,writes,expectedwrites)
  mask=(1<<int(fault.split('-')[1])) if fault.startswith('cleanup-') else (1<<15 if hbad or cbad or zbad or bbad or ebad or nbad or dbad or fbad or rbad or sbad or tbad or ubad or vbad or qbad or wbad or xbad or ybad or endbad or vebad or c7bad or c10bad or ct7bad or ct6bad or ct16bad or cd7bad or cd12bad or cb9bad or cb7bad or cb15bad else 0)
  if fault=='c17-drop-undo':mask|=1<<12
  assert v[30]==mask and v[29]==(not mask),(name,v[30],mask)
  hm=1<<int(fault.rsplit('-',1)[1]) if hbad else 0
  assert v[100:102]==[hm,int(not (hbad or cbad or zbad or bbad or ebad or nbad or dbad or fbad or rbad or sbad or tbad or ubad or vbad or qbad or wbad or xbad or ybad or endbad or vebad or c7bad or c10bad or ct7bad or ct6bad or ct16bad or cd7bad or cd12bad or cb9bad or cb7bad or cb15bad))],(name,v[100:102])
  assert v[76:83]==HB
  for n,val in enumerate(v[90:97]):assert (val!=HB[n])==bool(hm&(1<<n))
  assert v[0]==(0x8066 if fault=='selector' else 0x80643 if cb15bad else 0x80641 if cb7bad else 0x8063f if cb9bad else 0x8063d if cd12bad else 0x8063b if cd7bad else 0x80639 if ct16bad else 0x80637 if ct6bad else 0x80635 if ct7bad else 0x80633 if c10bad else 0x80631 if c7bad else 0x8062f if vebad else 0x8062d if endbad else 0x8062b if ybad else 0x80629 if xbad else 0x80627 if wbad else 0x80625 if qbad else 0x80623 if vbad else 0x80621 if ubad else 0x8061f if tbad else 0x8061d if sbad else 0x8061b if rbad else 0x80619 if fbad else 0x80617 if dbad else 0x80615 if nbad else 0x80613 if ebad else 0x80611 if bbad else 0x806f if zbad else 0x806c if cbad else 0x806a if hbad else 0x8065 if mask else forward)
  assert v[28]==(fault!='selector')
  assert v[104]==0xa7 and v[109]==0x31
  cran=horizontal_ran and forward!=0x8069
  assert v[107]==int(cran) and state['c4writes']==(2 if cran else 0)
  assert v[108]==(1 if fault in ['c4-restore-read','c4-restore-write'] else 2 if fault in ['c5-restore-read','c5-coupling','c5-drop-restore'] else 0)
  assert v[106]==(0xa6 if fault=='c4-restore-read' else 93 if fault=='c4-restore-write' else 0xa7)
  assert v[111]==(0x3e if fault=='c5-drop-restore' else 0x30 if fault in ['c5-restore-read','c5-coupling'] else 0x31)
  if cran:
   assert v[105]==(92 if fault=='c4-read' else 0xa7 if fault=='c4-write' else 93)
   assert v[110]==(0x30 if fault in ['c5-read','c5-coupling'] else 0x31)
  else:assert v[105]==v[110]==0xffffffff
  c5ran=cran and forward!=0x806b
  assert state['c5writes']==2*int(c5ran) and v[113]==int(c5ran)
  if c5ran:
   assert v[112]==0x3e
   assert v[114]==(0x31 if fault=='c5-drop-write' else 0x3f if fault=='c5-low-read' else 0xbe if fault=='c5-high-read' else 0x3e)
   assert v[115]==(92 if fault in ['c4-after-read','c4-coupling'] else 93)
  else:assert v[112:116]==[0,0,0xffffffff,0xffffffff]
  c0ran=c5ran and forward!=0x806d
  assert v[116]==0xc8 and state['c0writes']==2*int(c0ran) and v[118]==int(c0ran)
  assert v[120]==(0xc9 if fault=='c0-restore-read' else 0x5c if fault=='c0-drop-restore' else 0xc8)
  assert v[121]==int(zbad)
  if c0ran:
   assert v[117]==0x5c
   assert v[119]==(0xc8 if fault=='c0-drop-write' else 0x5d if fault=='c0-read' else 0x5c)
   assert v[122]==(92 if fault in ['c4-after-c0-read','c0-c4-coupling'] else 93)
   assert v[123]==(0x3f if fault in ['c5-after-c0-read','c0-c5-coupling'] else 0x3e)
  else:assert v[117:120]==[0,0,0xffffffff] and v[122:124]==[0xffffffff]*2
  c2ran=c0ran and forward!=0x806e
  assert v[124]==0x9f and state['c2writes']==2*int(c2ran) and v[126]==int(c2ran)
  assert v[128]==(0x9e if fault=='c2-restore-read' else 0x59 if fault=='c2-drop-restore' else 0x9f)
  assert v[129]==int(bbad)
  if c2ran:
   assert v[125]==0x59
   assert v[127]==(0x9f if fault=='c2-drop-write' else 0x58 if fault=='c2-read' else 0x59)
   for idx,n,expected in [(0,130,0x5c),(4,131,93),(5,132,0x3e)]:
    assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c2-read','c2-c'+str(idx)+'-coupling'] else expected)
  else:assert v[125:128]==[0,0,0xffffffff] and v[130:133]==[0xffffffff]*3
  c3ran=c2ran and forward!=0x80610
  assert v[133]==0x8c and state['c3writes']==2*int(c3ran) and v[135]==int(c3ran)
  assert v[137]==(0x8d if fault=='c3-restore-read' else 0x80 if fault=='c3-drop-restore' else 0x8c)
  assert v[138]==int(ebad)
  if c3ran:
   assert v[134]==0x80
   assert v[136]==(0x8c if fault=='c3-drop-write' else 0x81 if fault=='c3-read' else 0 if fault=='c3-high-read' else 0x80)
   for idx,n,expected in [(0,139,0x5c),(2,140,0x59),(4,141,93),(5,142,0x3e)]:
    assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c3-read','c3-c'+str(idx)+'-coupling'] else expected)
  else:assert v[134:137]==[0,0,0xffffffff] and v[139:143]==[0xffffffff]*4
  c5bran=c3ran and forward!=0x80612
  assert v[145]==int(c5bran) and state['c5bwrites']==2*int(c5bran)
  assert v[148]==int(nbad)
  if c5bran:
   assert v[143:146]==[0x3e,0xbe,1]
   assert v[146]==(0x3e if fault in ['c5b-drop-write','c5b-high-read'] else 0xbf if fault in ['c5b-read','c5b-wrong-write'] else 0xbe)
   assert v[147]==(0xbe if fault=='c5b-drop-undo' else 0x3f if fault=='c5b-undo-read' else 0x3e)
   for idx,n,expected in [(0,149,0x5c),(2,150,0x59),(3,151,0x80),(4,152,93)]:
    assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c5b-read','c5b-c'+str(idx)+'-coupling'] else expected)
  else:assert v[143:153]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
  c17ran=c5bran and forward!=0x80614
  assert v[155]==int(c17ran and fault!='c17-before-read') and state['c17writes']==2*v[155]
  assert v[158]==int(dbad)
  if c17ran:
   assert v[153]==(0xe2 if fault=='c17-before-read' else 0xe3)
   if v[155]:
    assert v[154]==0x63
    assert v[156]==(0xe3 if fault in ['c17-drop-write','c17-high-read'] else 0x62 if fault in ['c17-read','c17-wrong-write'] else 0x63)
    assert v[157]==(0x63 if fault=='c17-drop-undo' else 0xe2 if fault=='c17-undo-read' else 0xe3)
    for idx,n,expected in [(0,159,0x5c),(2,160,0x59),(3,161,0x80),(4,162,93),(5,163,0xbe)]:
     assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c17-read','c17-c'+str(idx)+'-coupling'] else expected)
   else:assert v[154:164]==[0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
  else:assert v[153:164]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
  c1ran=c17ran and forward!=0x80616
  assert v[166]==int(c1ran) and state['c1writes']==2*v[166] and v[169]==int(fbad)
  if c1ran:
   assert v[164:167]==[c1_original,0x59,1]
   assert v[167]==(c1_original if fault=='c1-drop-write' else 0xd9 if fault=='c1-high-read' else 0x58 if fault in ['c1-read','c1-wrong-write'] else 0x59)
   assert v[168]==(0x59 if fault=='c1-drop-undo' else c1_original^1 if fault=='c1-undo-read' else c1_original)
   for idx,n,expected in [(0,170,0x5c),(2,171,0x59),(3,172,0x80),(4,173,93),(5,174,0xbe),(0x17,175,0x63)]:
    assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c1-read','c1-c'+str(idx)+'-coupling'] else expected)
  else:assert v[164:176]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
  c2bran=c1ran and forward!=0x80618
  assert v[178]==int(c2bran and fault!='c2b-before-read') and state['c2bwrites']==2*v[178] and v[181]==int(rbad)
  if c2bran:
   assert v[176]==(0x58 if fault=='c2b-before-read' else 0x59)
   if v[178]:
    assert v[177]==0x59
    assert v[179]==(0xd9 if fault=='c2b-high-read' else 0x58 if fault in ['c2b-read','c2b-wrong-write','c2b-wrong-write-drop-undo'] else 0x59)
    assert v[180]==(0x58 if fault in ['c2b-undo-read','c2b-wrong-write-drop-undo'] else 0x59)
    for idx,n,expected in [(0,182,0x5c),(1,183,0x59),(3,184,0x80),(4,185,93),(5,186,0xbe),(0x17,187,0x63)]:
     assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c2b-read','c2b-c'+str(idx)+'-coupling'] else expected)
   else:assert v[177:188]==[0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
  else:assert v[176:188]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
  c17bran=c2bran and forward!=0x8061a
  assert v[190]==int(c17bran and fault!='c17b-before-read') and state['c17bwrites']==2*v[190] and v[193]==int(sbad)
  if c17bran:
   assert v[188]==(0x62 if fault=='c17b-before-read' else 0x63)
   if v[190]:
    assert v[189]==0xe3
    assert v[191]==(0x63 if fault in ['c17b-low-read','c17b-drop-write'] else 0xe2 if fault in ['c17b-read','c17b-wrong-write'] else 0xe3)
    assert v[192]==(0xe3 if fault=='c17b-drop-undo' else 0x62 if fault=='c17b-undo-read' else 0x63)
    for idx,n,expected in [(0,194,0x5c),(1,195,0x59),(2,196,0x59),(3,197,0x80),(4,198,93),(5,199,0xbe)]:
     assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c17b-read','c17b-c'+str(idx)+'-coupling'] else expected)
   else:assert v[189:200]==[0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
  else:assert v[188:200]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
  c19bran=c17bran and forward!=0x8061c
  assert v[202]==int(c19bran and fault not in ['c19b-before-read','c13-before-c19b-read']) and state['c19bwrites']==2*v[202] and v[205]==tmask
  if c19bran:
   assert v[200]==(0x11 if fault=='c19b-before-read' else 0x10)
   assert v[206]==(0x81 if fault=='c13-before-c19b-read' else 0x80)
   if v[202]:
    assert v[201]==0x30
    assert v[203]==(0x10 if fault in ['c19b-high-read','c19b-drop-write'] else 0x31 if fault in ['c19b-read','c19b-wrong-write'] else 0x30)
    assert v[204]==(0x30 if fault=='c19b-drop-undo' else 0x11 if fault=='c19b-undo-read' else 0x10)
    assert v[215]==(0x68 if fault=='c13-drop-undo' else 0x81 if fault in ['c19b-c19-coupling','c13-undo-c19b-read'] else 0x80)
    for idx,n,expected in [(0x13,207,0x80),(0x17,208,0xe3),(0,209,0x5c),(1,210,0x59),(2,211,0x59),(3,212,0x80),(4,213,93),(5,214,0xbe)]:
     assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c19b-read','c19b-c'+str(idx)+'-coupling'] else expected)
   else:assert v[201:206]==[0,0,0xffffffff,0xffffffff,0] and v[207:216]==[0xffffffff]*9
  else:assert v[200:216]==[0,0,0,0xffffffff,0xffffffff,0,0]+[0xffffffff]*9
  c13ran=c19bran and forward!=0x8061e
  assert v[218]==int(c13ran and fault not in ['c13-before-read','c19-before-c13-read']) and state['c13writes']==2*v[218] and v[221]==umask
  if c13ran:
   assert v[216]==(0x81 if fault=='c13-before-read' else 0x80)
   assert v[222]==(0x31 if fault=='c19-before-c13-read' else 0x30)
   if v[218]:
    assert v[217]==0x68
    assert v[219]==(0x80 if fault=='c13-drop-write' else 0xe8 if fault=='c13-high-read' else 0x69 if fault in ['c13-read','c13-wrong-write'] else 0x68)
    assert v[220]==(0x68 if fault=='c13-drop-undo' else 0x81 if fault=='c13-undo-read' else 0x80)
    assert v[231]==(0x31 if fault in ['c13-c25-coupling','c19-undo-c13-read','v-coupling-6','vt-coupling-6','vc-coupling-8','vs-coupling-8','sy-coupling-8','se-coupling-8','ve-coupling-8'] else 0x30)
    for idx,n,expected in [(0x19,223,0x30),(0x17,224,0xe3),(0,225,0x5c),(1,226,0x59),(2,227,0x59),(3,228,0x80),(4,229,93),(5,230,0xbe)]:
     assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c13-read','c13-c'+str(idx)+'-coupling'] else expected)
   else:assert v[217:222]==[0,0,0xffffffff,0xffffffff,0] and v[223:232]==[0xffffffff]*9
  else:assert v[216:232]==[0,0,0,0xffffffff,0xffffffff,0,0]+[0xffffffff]*9
 # Independent expected tail, not a projection inferred from returned status.
 reached=not cpu_bad and not baseline and forward in [0x806,0x80622,0x80624,0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
 if reached:
  vb=[719,749,724,729,719,104,48]
  attempted=not fault.startswith('v-before-')
  before=vb.copy()
  if not attempted:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[232]]+[v[238+3*i] for i in range(6)]==before
  assert v[233:235]==([479,1] if attempted else [0,0])
  assert state['vwrites']==2*int(attempted)
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
    j=int(fault.rsplit('-',1)[1]);k={5: 3, 6: 4, 7: 5, 8: 6}.get(j)
    if k is not None:undo[k]^=1
   if fault=='sy-drop-undo':undo[2]=489
   if fault=='sy-wrong-undo':undo[2]^=1
   if fault.startswith('se-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={6: 4, 7: 5, 8: 6}.get(j)
    if k is not None:undo[k]^=1
   if fault=='se-drop-undo':undo[3]=492
   if fault=='se-wrong-undo':undo[3]^=1
   if fault.startswith('ve-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={7: 5, 8: 6}.get(j)
    if k is not None:undo[k]^=1
   if fault=='ve-drop-undo':undo[4]=479
   if fault=='ve-wrong-undo':undo[4]^=1
   assert [v[235]]+[v[239+3*i] for i in range(6)]==after
   assert [v[236]]+[v[240+3*i] for i in range(6)]==undo
   assert v[237]==sum(1<<i for i in range(7) if undo[i]!=vb[i])==vmask
  else:assert v[235:238]==[0xffffffff,0xffffffff,0] and all(v[i]==0xffffffff for i in [239,240,242,243,245,246,248,249,251,252,254,255])
 else:
  assert v[232:238]==[0,0,0,0xffffffff,0xffffffff,0] and v[238:256]==[0,0xffffffff,0xffffffff]*6
 # New stage expected values and order are specified independently of code/result status.
 reached_vt=not cpu_bad and not baseline and forward in [0x806,0x80624,0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
 if reached_vt:
  ref=[749,479,724,729,719,104,48];before=ref.copy()
  attempted_vt=not fault.startswith('vt-before-')
  if not attempted_vt:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[256]]+[v[262+3*i] for i in range(6)]==before
  assert v[257:259]==([524,1] if attempted_vt else [0,0]) and state['vtwrites']==2*int(attempted_vt)
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
    j=int(fault.rsplit('-',1)[1]);k={1: 1, 5: 3, 6: 4, 7: 5, 8: 6}.get(j)
    if k is not None:undo[k]^=1
   if fault=='sy-drop-undo':undo[2]=489
   if fault=='sy-wrong-undo':undo[2]^=1
   if fault.startswith('se-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1: 1, 6: 4, 7: 5, 8: 6}.get(j)
    if k is not None:undo[k]^=1
   if fault=='se-drop-undo':undo[3]=492
   if fault=='se-wrong-undo':undo[3]^=1
   if fault.startswith('ve-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1: 1, 7: 5, 8: 6}.get(j)
    if k is not None:undo[k]^=1
   if fault=='ve-drop-undo':undo[4]=479
   if fault=='ve-wrong-undo':undo[4]^=1
   assert [v[259]]+[v[263+3*i] for i in range(6)]==after
   assert [v[260]]+[v[264+3*i] for i in range(6)]==undo
   assert v[261]==sum(1<<i for i in range(7) if undo[i]!=ref[i])==qmask
  else:assert v[259:262]==[0xffffffff,0xffffffff,0] and all(v[i]==0xffffffff for i in [263,264,266,267,269,270,272,273,275,276,278,279])
 else:assert v[256:262]==[0,0,0,0xffffffff,0xffffffff,0] and v[262:280]==[0,0xffffffff,0xffffffff]*6
 # Independently specified NVVCRTC baseline, mutation, recovery and neighbors.
 reached_vc=not cpu_bad and not baseline and forward in [0x806,0x80626,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
 if reached_vc:
  ref=[719,479,524,724,729,0,719,104,48];before=ref.copy()
  attempted_vc=not fault.startswith('vc-before-')
  if not attempted_vc:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[280]]+[v[286+3*i] for i in range(8)]==before
  assert v[281:283]==([479,1] if attempted_vc else [0,0]) and state['vcwrites']==2*int(attempted_vc)
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
    j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 5: 4, 6: 6, 7: 7, 8: 8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='sy-drop-undo':undo[3]=489
   if fault=='sy-wrong-undo':undo[3]^=1
   if fault.startswith('se-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 6: 6, 7: 7, 8: 8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='se-drop-undo':undo[4]=492
   if fault=='se-wrong-undo':undo[4]^=1
   if fault.startswith('ve-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 7: 7, 8: 8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='ve-drop-undo':undo[6]=479
   if fault=='ve-wrong-undo':undo[6]^=1
   assert [v[283]]+[v[287+3*i] for i in range(8)]==after
   assert [v[284]]+[v[288+3*i] for i in range(8)]==undo
   assert v[285]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==wmask
  else:assert v[283:286]==[0xffffffff,0xffffffff,0] and all(v[287+3*i:289+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[280:286]==[0,0,0,0xffffffff,0xffffffff,0] and v[286:310]==[0,0xffffffff,0xffffffff]*8
 # Independently specified NVVVALIDSTART same-value attempt and recovery.
 reached_vs=not cpu_bad and not baseline and forward in [0x806,0x80628,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
 if reached_vs:
  ref=[0,479,524,479,724,729,719,104,48];before=ref.copy()
  attempted_vs=not fault.startswith('vs-before-')
  if not attempted_vs:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[310]]+[v[316+3*i] for i in range(8)]==before
  assert v[311:313]==([0,1] if attempted_vs else [0,0]) and state['vswrites']==2*int(attempted_vs)
  if attempted_vs:
   after=ref.copy();undo=ref.copy()
   if fault in ['vs-wrong-write','vs-wrong-write-drop-undo']:after[0]=1
   if fault.startswith('vs-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('vs-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('vs-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault in ['vs-wrong-undo','vs-wrong-write-drop-undo']:undo[0]=1
   if fault.startswith('sy-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 3: 3, 5: 5, 6: 6, 7: 7, 8: 8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='sy-drop-undo':undo[4]=489
   if fault=='sy-wrong-undo':undo[4]^=1
   if fault.startswith('se-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 3: 3, 6: 6, 7: 7, 8: 8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='se-drop-undo':undo[5]=492
   if fault=='se-wrong-undo':undo[5]^=1
   if fault.startswith('ve-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 3: 3, 7: 7, 8: 8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='ve-drop-undo':undo[6]=479
   if fault=='ve-wrong-undo':undo[6]^=1
   assert [v[313]]+[v[317+3*i] for i in range(8)]==after
   assert [v[314]]+[v[318+3*i] for i in range(8)]==undo
   assert v[315]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==xmask
  else:assert v[313:316]==[0xffffffff,0xffffffff,0] and all(v[317+3*i:319+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[310:316]==[0,0,0,0xffffffff,0xffffffff,0] and v[316:340]==[0,0xffffffff,0xffffffff]*8
 # Independently specified NVVSYNCSTART transition and neighbor recovery.
 reached_sy=not cpu_bad and not baseline and forward in [0x806,0x8062a,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
 if reached_sy:
  ref=[724,479,524,479,0,729,719,104,48];before=ref.copy()
  attempted_sy=not fault.startswith('sy-before-')
  if not attempted_sy:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[340]]+[v[346+3*i] for i in range(8)]==before
  assert v[341:343]==([489,1] if attempted_sy else [0,0]) and state['sywrites']==2*int(attempted_sy)
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
    j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 3: 3, 4: 4, 6: 6, 7: 7, 8: 8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='se-drop-undo':undo[5]=492
   if fault=='se-wrong-undo':undo[5]^=1
   if fault.startswith('ve-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 3: 3, 4: 4, 7: 7, 8: 8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='ve-drop-undo':undo[6]=479
   if fault=='ve-wrong-undo':undo[6]^=1
   assert [v[343]]+[v[347+3*i] for i in range(8)]==after
   assert [v[344]]+[v[348+3*i] for i in range(8)]==undo
   assert v[345]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==ymask
  else:assert v[343:346]==[0xffffffff,0xffffffff,0] and all(v[347+3*i:349+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[340:346]==[0,0,0,0xffffffff,0xffffffff,0] and v[346:370]==[0,0xffffffff,0xffffffff]*8
 # Independently specified NVVSYNCEND values and neighbor recovery.
 reached_se=not cpu_bad and not baseline and forward in [0x806,0x8062c,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
 if reached_se:
  ref=[729,479,524,479,0,489,719,104,48];before=ref.copy()
  attempted_se=not fault.startswith('se-before-')
  if not attempted_se:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[370]]+[v[376+3*i] for i in range(8)]==before
  assert v[371:373]==([492,1] if attempted_se else [0,0]) and state['sewrites']==2*int(attempted_se)
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
    j=int(fault.rsplit('-',1)[1]);k={1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 7: 7, 8: 8}.get(j)
    if k is not None:undo[k]^=1
   if fault=='ve-drop-undo':undo[6]=479
   if fault=='ve-wrong-undo':undo[6]^=1
   assert [v[374]]+[v[378+3*i] for i in range(8)]==undo
   assert v[375]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==endmask
  else:assert v[373:376]==[0xffffffff,0xffffffff,0] and all(v[377+3*i:379+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[370:376]==[0,0,0,0xffffffff,0xffffffff,0] and v[376:400]==[0,0xffffffff,0xffffffff]*8
 # Independent NVVVALIDEND constants, neighbors, and reverse recovery.
 reached_ve=not cpu_bad and not baseline and forward in [0x806,0x8062e,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
 if reached_ve:
  ref=[719,479,524,479,0,489,492,104,48];before=ref.copy()
  attempted_ve=not fault.startswith('ve-before-')
  if not attempted_ve:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[400]]+[v[406+3*i] for i in range(8)]==before
  assert v[401:403]==([479,1] if attempted_ve else [0,0]) and state['vewrites']==2*int(attempted_ve)
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
   assert v[405]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==vemask
  else:assert v[403:406]==[0xffffffff,0xffffffff,0] and all(v[407+3*i:409+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[400:406]==[0,0,0,0xffffffff,0xffffffff,0] and v[406:430]==[0,0xffffffff,0xffffffff]*8
 # Independent shared-overflow bit constants and complete neighboring bytes.
 reached_c7=not cpu_bad and not baseline and forward in [0x806,0x80630,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
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
   assert v[435]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==c7mask
  else:assert v[433:436]==[0xffffffff,0xffffffff,0] and all(v[437+3*i:439+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[430:436]==[0,0,0,0xffffffff,0xffffffff,0] and v[436:460]==[0,0xffffffff,0xffffffff]*8
 # New CR10 fields and complete neighbor tuple, independent constants.
 reached_c10=not cpu_bad and not baseline and forward in [0x806,0x80632,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
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
   assert v[465]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==c10mask
  else:assert v[463:466]==[0xffffffff,0xffffffff,0] and all(v[467+3*i:469+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[460:466]==[0,0,0,0xffffffff,0xffffffff,0] and v[466:490]==[0,0xffffffff,0xffffffff]*8
 # Exact new shared-CR07 tuple with independently specified constants.
 reached_ct7=not cpu_bad and not baseline and forward in [0x806,0x80634,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
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
   assert v[495]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==ct7mask
  else:assert v[493:496]==[0xffffffff,0xffffffff,0] and all(v[497+3*i:499+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[490:496]==[0,0,0,0xffffffff,0xffffffff,0] and v[496:520]==[0,0xffffffff,0xffffffff]*8
 # Independent CR06 tuple: total 524 -> low byte 12, saved byte 236.
 reached_ct6=not cpu_bad and not baseline and forward in [0x806,0x80636,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
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
   assert v[525]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==ct6mask
  else:assert v[523:526]==[0xffffffff,0xffffffff,0] and all(v[527+3*i:529+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[520:526]==[0,0,0,0xffffffff,0xffffffff,0] and v[526:550]==[0,0xffffffff,0xffffffff]*8
 # Independent CR16 tuple: saved ED, preserve bit7, total524 low7 =>8C.
 reached_ct16=not cpu_bad and not baseline and forward in [0x806,0x80638,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
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
   assert v[555]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==ct16mask
  else:assert v[553:556]==[0xffffffff,0xffffffff,0] and all(v[557+3*i:559+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[550:556]==[0,0,0,0xffffffff,0xffffffff,0] and v[556:580]==[0,0xffffffff,0xffffffff]*8
 # Independently specified CR07 display-end target and complete neighboring tuple.
 reached_cd7=not cpu_bad and not baseline and forward in [0x806,0x8063a,0x8063c,0x8063e,0x80640,0x80642]
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
   assert v[585]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==cd7mask
  else:assert v[583:586]==[0xffffffff,0xffffffff,0] and all(v[587+3*i:589+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[580:586]==[0,0,0,0xffffffff,0xffffffff,0] and v[586:610]==[0,0xffffffff,0xffffffff]*8
 # Independently specified complete CR12 transaction tuple.
 reached_cd12=not cpu_bad and not baseline and forward in [0x806,0x8063c,0x8063e,0x80640,0x80642]
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
   assert v[615]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==cd12mask
  else:assert v[613:616]==[0xffffffff,0xffffffff,0] and all(v[617+3*i:619+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[610:616]==[0,0,0,0xffffffff,0xffffffff,0] and v[616:640]==[0,0xffffffff,0xffffffff]*8
 # Complete CR09 transaction tuple, independently specified.
 reached_cb9=not cpu_bad and not baseline and forward in [0x806,0x8063e,0x80640,0x80642]
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
   assert v[645]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==cb9mask
  else:assert v[643:646]==[0xffffffff,0xffffffff,0] and all(v[647+3*i:649+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[640:646]==[0,0,0,0xffffffff,0xffffffff,0] and v[646:670]==[0,0xffffffff,0xffffffff]*8
 # Complete new transaction, independent literals and masks.
 reached_cb7=not cpu_bad and not baseline and forward in [0x806,0x80640,0x80642]
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
   if fault=='cb15-drop-undo':undo[5]=223
   if fault=='cb15-wrong-undo':undo[5]=206
   if fault=='cb15-wrong-write-drop-undo':undo[5]=222
   if fault.startswith('cb15-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1: 1, 3: 2, 4: 3, 5: 4, 6: 6, 7: 7, 8: 8}
    if j in mapping:undo[mapping[j]]^=1
   if fault=='cb7-wrong-write-drop-undo':undo[0]=63
   assert [v[673]]+[v[677+3*i] for i in range(8)]==after
   assert [v[674]]+[v[678+3*i] for i in range(8)]==undo
   assert v[675]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==cb7mask
  else:assert v[673:676]==[0xffffffff,0xffffffff,0] and all(v[677+3*i:679+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[670:676]==[0,0,0,0xffffffff,0xffffffff,0] and v[676:700]==[0,0xffffffff,0xffffffff]*8
 # Complete CR15 transaction, independently enumerated literals and masks.
 reached_cb15=not cpu_bad and not baseline and forward in [0x806,0x80642]
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
   assert [v[703]]+[v[707+3*i] for i in range(8)]==after
   assert [v[704]]+[v[708+3*i] for i in range(8)]==undo
   assert v[705]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==cb15mask
  else:assert v[703:706]==[0xffffffff,0xffffffff,0] and all(v[707+3*i:709+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[700:706]==[0,0,0,0xffffffff,0xffffffff,0] and v[706:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append({'name':name,'raw_result':v,'writes':writes,'ports':ports,'reads':reads,'instructions':steps[0],'critical_instructions':steps[1]})
try:
 run('baseline-deferred-read-success')
 for phase in ['before','after','undo']:
  for j in range(9):run('cb15-'+phase+'-'+str(j),fault='cb15-'+phase+'-'+str(j))
 for j in range(1,9):run('cb15-coupling-'+str(j),fault='cb15-coupling-'+str(j))
 for f in ['cb15-drop-write','cb15-wrong-write','cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('cb7-'+phase+'-'+str(j),fault='cb7-'+phase+'-'+str(j))
 for j in range(1,9):run('cb7-coupling-'+str(j),fault='cb7-coupling-'+str(j))
 for f in ['cb7-drop-write','cb7-wrong-write','cb7-drop-undo','cb7-wrong-undo','cb7-wrong-write-drop-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('cb9-'+phase+'-'+str(j),fault='cb9-'+phase+'-'+str(j))
 for j in range(1,9):run('cb9-coupling-'+str(j),fault='cb9-coupling-'+str(j))
 for f in ['cb9-drop-write','cb9-wrong-write','cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('cd12-'+phase+'-'+str(j),fault='cd12-'+phase+'-'+str(j))
 for j in range(1,9):run('cd12-coupling-'+str(j),fault='cd12-coupling-'+str(j))
 for f in ['cd12-drop-write','cd12-wrong-write','cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('cd7-'+phase+'-'+str(j),fault='cd7-'+phase+'-'+str(j))
 for j in range(1,9):run('cd7-coupling-'+str(j),fault='cd7-coupling-'+str(j))
 for f in ['cd7-drop-write','cd7-wrong-write','cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('ct16-'+phase+'-'+str(j),fault='ct16-'+phase+'-'+str(j))
 for j in range(1,9):run('ct16-coupling-'+str(j),fault='ct16-coupling-'+str(j))
 for f in ['ct16-drop-write','ct16-wrong-write','ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('ct6-'+phase+'-'+str(j),fault='ct6-'+phase+'-'+str(j))
 for j in range(1,9):run('ct6-coupling-'+str(j),fault='ct6-coupling-'+str(j))
 for f in ['ct6-drop-write','ct6-wrong-write','ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('ct7-'+phase+'-'+str(j),fault='ct7-'+phase+'-'+str(j))
 for j in range(1,9):run('ct7-coupling-'+str(j),fault='ct7-coupling-'+str(j))
 for f in ['ct7-drop-write','ct7-wrong-write','ct7-drop-undo','ct7-wrong-undo','ct7-wrong-write-drop-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('c10-'+phase+'-'+str(j),fault='c10-'+phase+'-'+str(j))
 for j in range(1,9):run('c10-coupling-'+str(j),fault='c10-coupling-'+str(j))
 for f in ['c10-drop-write','c10-wrong-write','c10-drop-undo','c10-wrong-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('c7-'+phase+'-'+str(j),fault='c7-'+phase+'-'+str(j))
 for j in range(1,9):run('c7-coupling-'+str(j),fault='c7-coupling-'+str(j))
 for f in ['c7-drop-write','c7-wrong-write','c7-drop-undo','c7-wrong-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('ve-'+phase+'-'+str(j),fault='ve-'+phase+'-'+str(j))
 for j in range(1,9):run('ve-coupling-'+str(j),fault='ve-coupling-'+str(j))
 for f in ['ve-drop-write','ve-wrong-write','ve-drop-undo','ve-wrong-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('se-'+phase+'-'+str(j),fault='se-'+phase+'-'+str(j))
 for j in range(1,9):run('se-coupling-'+str(j),fault='se-coupling-'+str(j))
 for f in ['se-drop-write','se-wrong-write','se-drop-undo','se-wrong-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('sy-'+phase+'-'+str(j),fault='sy-'+phase+'-'+str(j))
 for j in range(1,9):run('sy-coupling-'+str(j),fault='sy-coupling-'+str(j))
 for f in ['sy-drop-write','sy-wrong-write','sy-drop-undo','sy-wrong-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('vs-'+phase+'-'+str(j),fault='vs-'+phase+'-'+str(j))
 for j in range(1,9):run('vs-coupling-'+str(j),fault='vs-coupling-'+str(j))
 for f in ['vs-drop-write','vs-wrong-write','vs-drop-undo','vs-wrong-undo','vs-wrong-write-drop-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(9):run('vc-'+phase+'-'+str(j),fault='vc-'+phase+'-'+str(j))
 for j in range(1,9):run('vc-coupling-'+str(j),fault='vc-coupling-'+str(j))
 for f in ['vc-drop-write','vc-wrong-write','vc-drop-undo','vc-wrong-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(7):run('vt-'+phase+'-'+str(j),fault='vt-'+phase+'-'+str(j))
 for j in range(1,7):run('vt-coupling-'+str(j),fault='vt-coupling-'+str(j))
 for f in ['vt-drop-write','vt-wrong-write','vt-drop-undo','vt-wrong-undo']:run(f,fault=f)
 for phase in ['before','after','undo']:
  for j in range(7):run('v-'+phase+'-'+str(j),fault='v-'+phase+'-'+str(j))
 for j in range(1,7):run('v-coupling-'+str(j),fault='v-coupling-'+str(j))
 for f in ['v-drop-write','v-wrong-write','v-drop-undo','v-wrong-undo']:run(f,fault=f)
 for flags in [2,0x202,0x246]:run('flags-'+hex(flags),flags=flags)
 for n in range(15):run('first-mismatch-'+str(n),fault='check-'+str(n))
 for n in range(20):run('cleanup-bit-'+str(n),fault='cleanup-'+str(n))
 for fault in ['blank','unlock','selector']:run(fault,fault=fault)
 for bline in ['gr','cr22','cr33','seq','cr11','mm','cr','cr1b']:run('baseline-refused-'+bline,baseline=bline)
 for value in [0,1,0x80010031,0x80000000]:run('CPU-refused-'+hex(value),cpu0=value)
 run('PAE-refused',cpu4=0x630)
 run('alternate-CR3',cpu3=0x23000)
 for bline in ['c4','c5']:run('crtc-baseline-'+bline,baseline=bline)
 for fault in ['c4-read','c4-write','c4-restore-read','c4-restore-write','c5-read','c5-restore-read','c5-coupling','c5-drop-restore']:run(fault,fault=fault)
 for fault in ['c5-drop-write','c5-low-read','c5-high-read','c4-after-read','c4-coupling']:run(fault,fault=fault)
 run('crtc-baseline-c0',baseline='c0')
 for fault in ['c0-read','c0-drop-write','c0-restore-read','c0-drop-restore','c4-after-c0-read','c5-after-c0-read','c0-c4-coupling','c0-c5-coupling']:run(fault,fault=fault)
 run('crtc-baseline-c2',baseline='c2')
 for fault in ['c2-read','c2-drop-write','c2-restore-read','c2-drop-restore','c0-after-c2-read','c4-after-c2-read','c5-after-c2-read','c2-c0-coupling','c2-c4-coupling','c2-c5-coupling']:run(fault,fault=fault)
 run('crtc-baseline-c3',baseline='c3')
 for fault in ['c3-read','c3-high-read','c3-drop-write','c3-restore-read','c3-drop-restore']+['c'+str(i)+'-after-c3-read' for i in [0,2,4,5]]+['c3-c'+str(i)+'-coupling' for i in [0,2,4,5]]:run(fault,fault=fault)
 for fault in ['c5b-read','c5b-high-read','c5b-drop-write','c5b-wrong-write']+['c'+str(i)+'-after-c5b-read' for i in [0,2,3,4]]+['c5b-c'+str(i)+'-coupling' for i in [0,2,3,4]]+['c5b-undo-read','c5b-drop-undo']:run(fault,fault=fault)
 for fault in ['c17-before-read','c17-read','c17-high-read','c17-drop-write','c17-wrong-write']+['c'+str(i)+'-after-c17-read' for i in [0,2,3,4,5]]+['c17-c'+str(i)+'-coupling' for i in [0,2,3,4,5]]+['c17-undo-read','c17-drop-undo']:run(fault,fault=fault)
 for fault in ['c1-read','c1-high-read','c1-drop-write','c1-wrong-write']+['c'+str(i)+'-after-c1-read' for i in [0,2,3,4,5,0x17]]+['c1-c'+str(i)+'-coupling' for i in [0,2,3,4,5,0x17]]+['c1-undo-read','c1-drop-undo']:run(fault,fault=fault)
 for value in [0,255]:run('CR01-own-value-'+str(value),c1_original=value)
 for fault in ['c2b-before-read','c2b-read','c2b-high-read','c2b-wrong-write','c2b-wrong-write-drop-undo']+['c'+str(i)+'-after-c2b-read' for i in [0,1,3,4,5,0x17]]+['c2b-c'+str(i)+'-coupling' for i in [0,1,3,4,5,0x17]]+['c2b-undo-read','c2b-drop-write','c2b-drop-undo']:run(fault,fault=fault)
 for fault in ['c17b-before-read','c17b-read','c17b-low-read','c17b-drop-write','c17b-wrong-write']+['c'+str(i)+'-after-c17b-read' for i in [0,1,2,3,4,5]]+['c17b-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5]]+['c17b-undo-read','c17b-drop-undo']:run(fault,fault=fault)
 for fault in ['c19b-before-read','c13-before-c19b-read','c19b-read','c19b-high-read','c19b-drop-write','c19b-wrong-write']+['c'+str(i)+'-after-c19b-read' for i in [0,1,2,3,4,5,0x13,0x17]]+['c19b-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5,0x13,0x17]]+['c19b-undo-read','c19b-drop-undo','c13-undo-c19b-read']:run(fault,fault=fault)
 for fault in ['c13-before-read','c19-before-c13-read','c13-read','c13-high-read','c13-drop-write','c13-wrong-write']+['c'+str(i)+'-after-c13-read' for i in [0,1,2,3,4,5,0x19,0x17]]+['c13-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5,0x19,0x17]]+['c13-undo-read','c13-drop-undo','c19-undo-c13-read']:run(fault,fault=fault)
 for n in range(7):
  run('horizontal-read-'+str(n),fault='h-read-'+str(n))
  run('horizontal-recovery-read-'+str(n),fault='h-restore-read-'+str(n))
  run('horizontal-baseline-'+str(n),baseline='h-'+str(n))
  if n!=3: # HVALIDSTART is already zero, so dropping that write is unobservable.
   run('horizontal-dropped-write-'+str(n),fault='h-write-'+str(n))
   run('horizontal-dropped-restore-'+str(n),fault='h-restore-write-'+str(n))
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:R['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,separators=(',',':'))+'\n')
print('PASS actual806 native ELF',len(R['cases']),'cases; no physical timing/semantics claim')

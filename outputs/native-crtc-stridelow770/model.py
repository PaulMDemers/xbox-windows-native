"""Actual770 native ELF with horizontal transaction, pre-enable recovery and fault injection.
Control-flow and access contracts only; no modeled transition proves hardware behavior.
"""
import datetime,hashlib,json,struct,sys,os,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn770/payload001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'model001.json';assert not out.exists()
b=(P/'payload.bin').read_bytes()
sy={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}
R={'passed':False,'scope':__doc__,'ELF_sha256':sha(P/'native.elf'),'harness_sha256':sha(Path(__file__)),'cases':[]}
GPU=0xfd000000;deadline=time.monotonic()+90

SETUP=[(0x680884,0),(0x680888,0),(0x68088c,0x10001000),(0x680890,0x10000000),(0x680894,0x10000000),(0x680898,0x10000000),(0x68089c,0x10000000),(0x680880,0x21101100),(0x680630,2),(0x68084c,0x00801080),(0x6808c4,0x40801080)]
H=[(0x680820,719),(0x680824,779),(0x680828,719),(0x680834,0),(0x68082c,738),(0x680830,770),(0x680838,719)]
HB=[1279,1649,1279,0,1389,1429,1279]
CS=[(0x14,0),(0x17,0xe3),(0x19,0x10),(0x1b,0x85)]
def run(name,flags=0x46,cpu0=0x4001003b,cpu3=0,cpu4=0x610,fault="",baseline="",c1_original=0x9f):
 assert time.monotonic()<deadline
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,b)
 c.mem_map(0x200000,0x40000)

 c.mem_write(0x200000,b'G'*0x40000);c.mem_map(GPU,0x1000000)
 c.mem_write(0x208000,struct.pack('<II',0x20ff00,0x201000))
 c.reg_write(x.UC_X86_REG_ESP,0x208000);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 sels={0x6013d4:0x67,0xc03c4:0x72,0xc03ce:0x91};original=sels.copy()
 mm=dict(SETUP);mm[0x680630]=3;mm.update(dict(zip([a for a,_ in H],HB)));hw={a:0 for a,_ in H};hr=[]
 cr={0x13:0x80,1:c1_original,3:0x8c,2:0x9f,0:0xc8,4:0xa7,5:0x31,0x11:9,0x14:0,0x17:0xe3,0x19:0x51,0x1b:0x85,0x22:0xfe,0x33:0x11,0x1f:0}
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
 state={'c13writes':0,'c19bwrites':0,'c17bwrites':0,'c2bwrites':0,'c1writes':0,'c17writes':0,'c5bwrites':0,'c3writes':0,'c2writes':0,'c0writes':0,'c5writes':0,'c4writes':0,'sq':sq,'gr':gr,'recovering':False,'unlock':False}
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
    assert idx in [1,3,2,0,4,5,0x13,0x1f,0x14,0x17,0x19]
    if idx==0x13:
     state['c13writes']+=1;n=state['c13writes'];assert n<=2 and value==(0x68 if n==1 else 0x80)
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
   if word(1)==0x77020 and not word(218) and state['c19bwrites']==1:
    if idx==0x13 and fault=='c13-before-read':val^=1
    if idx==0x19 and fault=='c19-before-c13-read':val^=1
   if idx==0x13 and state['c13writes']==1 and fault=='c13-read':val^=1
   if idx==0x13 and state['c13writes']==1 and fault=='c13-high-read':val^=0x80
   if idx==0x13 and state['c13writes']==2 and state['c19bwrites']==1 and fault=='c13-undo-read':val^=1
   if idx==0x19 and state['c13writes']==2 and state['c19bwrites']==1 and fault=='c19-undo-c13-read':val^=1
   if idx in [0,1,2,3,4,5,0x19,0x17] and state['c13writes']==1 and fault=='c'+str(idx)+'-after-c13-read':val^=1
   if word(1)==0x7701e and not word(202) and state['c17bwrites']==1:
    if idx==0x19 and fault=='c19b-before-read':val^=1
    if idx==0x13 and fault=='c13-before-c19b-read':val^=1
   if idx==0x19 and state['c19bwrites']==1 and fault=='c19b-read':val^=1
   if idx==0x19 and state['c19bwrites']==1 and fault=='c19b-high-read':val^=0x20
   if idx==0x19 and state['c19bwrites']==2 and state['c17bwrites']==1 and fault=='c19b-undo-read':val^=1
   if idx==0x13 and state['c19bwrites']==2 and state['c17bwrites']==1 and fault=='c13-undo-c19b-read':val^=1
   if idx in [0,1,2,3,4,5,0x13,0x17] and state['c19bwrites']==1 and fault=='c'+str(idx)+'-after-c19b-read':val^=1
   if idx==0x17 and word(1)==0x7701c and not word(190) and state['c2bwrites']==1 and fault=='c17b-before-read':val^=1
   if idx==0x17 and state['c17bwrites']==1 and fault=='c17b-read':val^=1
   if idx==0x17 and state['c17bwrites']==1 and fault=='c17b-low-read':val^=0x80
   if idx==0x17 and state['c17bwrites']==2 and state['c2bwrites']==1 and fault=='c17b-undo-read':val^=1
   if idx in [0,1,2,3,4,5] and state['c17bwrites']==1 and fault=='c'+str(idx)+'-after-c17b-read':val^=1
   if idx==2 and word(1)==0x7701a and not word(178) and state['c1writes']==1 and fault=='c2b-before-read':val^=1
   if idx==2 and state['c2bwrites']==1 and fault=='c2b-read':val^=1
   if idx==2 and state['c2bwrites']==1 and fault=='c2b-high-read':val^=0x80
   if idx==2 and state['c2bwrites']==2 and state['c1writes']==1 and fault=='c2b-undo-read':val^=1
   if idx in [0,1,3,4,5,0x17] and state['c2bwrites']==1 and fault=='c'+str(idx)+'-after-c2b-read':val^=1
   if idx==1 and state['c1writes']==1 and fault=='c1-read':val^=1
   if idx==1 and state['c1writes']==1 and fault=='c1-high-read':val^=0x80
   if idx==1 and state['c1writes']==2 and state['c17writes']==1 and fault=='c1-undo-read':val^=1
   if idx in [0,2,3,4,5,0x17] and state['c1writes']==1 and fault=='c'+str(idx)+'-after-c1-read':val^=1
   if idx==0x17 and word(1)==0x77016 and not word(155) and not state['recovering'] and fault=='c17-before-read':val^=1
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
   if word(1)==0x7708 and not state['recovering'] and idx in dict(CS):
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
   if word(1)==0x7709 and word(98)<=6 and not hr and fault=='h-read-'+str(n):val^=1
   if hr and fault=='h-restore-read-'+str(n):val^=1
   # When no horizontal writes occurred, recovery still checks all seven words.
   if not hw[off] and state['unlock'] and word(1)==0x7708 and fault=='h-pre-restore-'+str(n):val^=1
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
   if word(1)==0x7708 and not state['recovering']:
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
  assert 0x201000<=addr and addr+size<=0x2013a0 or 0x207000<=addr and addr+size<=0x208008,(hex(addr),size)
 def pout(uc,port,size,val,_):
  assert (port,size)==(0x80d3,1) and val in [4,5]
  assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  ports.append(val)
  if val==4:
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
 try:c.emu_start(sy['probe770'],0x20ff00,timeout=2000000,count=15000)
 except Exception as exc:
  raise AssertionError((name,str(exc),hex(c.reg_read(x.UC_X86_REG_EIP)),hex(c.reg_read(x.UC_X86_REG_ESP)),steps,writes[-5:])) from exc
 assert c.reg_read(x.UC_X86_REG_EIP)==0x20ff00 and c.reg_read(x.UC_X86_REG_ESP)==0x208004
 v=list(struct.unpack('<232I',c.mem_read(0x201000,928)))
 assert v[8]==v[10] and not v[9]&0x200 and v[8]&0x200==flags&0x200
 assert v[11:14]==[cpu0,cpu3,cpu4] and c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
 assert bytes(c.mem_read(0x200000,4096))==b'G'*4096
 assert bytes(c.mem_read(0x2013a0,0x5c60))==b'G'*0x5c60
 assert bytes(c.mem_read(0x208008,0xff8))==b'G'*0xff8 and sels==original
 cpu_bad=(cpu0&0xe0000001)!=0x40000001 or cpu3!=0 or flags&0x200 or cpu4&0x20
 if cpu_bad:
  assert v[0:2]==[0x7701]*2 and not writes and not ports and not reads
 elif baseline:
  assert v[0:2]==[0x7702]*2 and not writes and not ports and v[28]==1
 else:
  umask=(1 if fault in ['c13-undo-read','c13-drop-undo'] else 0)|(2 if fault in ['c13-c25-coupling','c19-undo-c13-read'] else 0)
  ubad=bool(umask)
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
  assert ports==([5] if hbad or cbad or zbad or bbad or ebad or nbad or dbad or fbad or rbad or sbad or tbad or ubad else [5,4]),(name,ports)
  forward=0x7703 if fault=='blank' else 0x7704 if fault=='unlock' else 0x7708 if fault.startswith('check-') else 0x7709 if fault.startswith(('h-read-','h-write-')) else 0x770b if fault in ['c4-read','c4-write','c5-read','c5-coupling'] else 0x770d if fault in ['c5-drop-write','c5-low-read','c5-high-read','c4-after-read','c4-coupling'] else 0x770e if fault in ['c0-read','c0-drop-write','c4-after-c0-read','c5-after-c0-read','c0-c4-coupling','c0-c5-coupling'] else 0x77010 if fault in ['c2-read','c2-drop-write','c0-after-c2-read','c4-after-c2-read','c5-after-c2-read','c2-c0-coupling','c2-c4-coupling','c2-c5-coupling'] else 0x77012 if fault in ['c3-read','c3-high-read','c3-drop-write']+['c'+str(i)+'-after-c3-read' for i in [0,2,4,5]]+['c3-c'+str(i)+'-coupling' for i in [0,2,4,5]] else 0x77014 if fault in ['c5b-read','c5b-high-read','c5b-drop-write','c5b-wrong-write']+['c'+str(i)+'-after-c5b-read' for i in [0,2,3,4]]+['c5b-c'+str(i)+'-coupling' for i in [0,2,3,4]] else 0x77016 if fault in ['c17-before-read','c17-read','c17-high-read','c17-drop-write','c17-wrong-write']+['c'+str(i)+'-after-c17-read' for i in [0,2,3,4,5]]+['c17-c'+str(i)+'-coupling' for i in [0,2,3,4,5]] else 0x77018 if fault in ['c1-read','c1-high-read','c1-drop-write','c1-wrong-write']+['c'+str(i)+'-after-c1-read' for i in [0,2,3,4,5,0x17]]+['c1-c'+str(i)+'-coupling' for i in [0,2,3,4,5,0x17]] else 0x7701a if fault in ['c2b-before-read','c2b-read','c2b-high-read','c2b-wrong-write','c2b-wrong-write-drop-undo']+['c'+str(i)+'-after-c2b-read' for i in [0,1,3,4,5,0x17]]+['c2b-c'+str(i)+'-coupling' for i in [0,1,3,4,5,0x17]] else 0x7701c if fault in ['c17b-before-read','c17b-read','c17b-low-read','c17b-drop-write','c17b-wrong-write']+['c'+str(i)+'-after-c17b-read' for i in [0,1,2,3,4,5]]+['c17b-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5]] else 0x7701e if fault in ['c19b-before-read','c13-before-c19b-read','c19b-read','c19b-high-read','c19b-drop-write','c19b-wrong-write']+['c'+str(i)+'-after-c19b-read' for i in [0,1,2,3,4,5,0x13,0x17]]+['c19b-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5,0x13,0x17]] else 0x77020 if fault in ['c13-before-read','c19-before-c13-read','c13-read','c13-high-read','c13-drop-write','c13-wrong-write']+['c'+str(i)+'-after-c13-read' for i in [0,1,2,3,4,5,0x19,0x17]]+['c13-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5,0x19,0x17]] else 0x770
  assert v[1]==forward,(name,v)
  fullprefix=forward in [0x770,0x7708,0x7709,0x770b,0x770d,0x770e,0x77010,0x77012,0x77014,0x77016,0x77018,0x7701a,0x7701c,0x7701e,0x77020]
  if fullprefix:
   assert v[2:4]==[11,3]
   fail=int(fault.split('-')[1]) if fault.startswith('check-') else None
   assert v[4]==(fail if fail is not None else 0xffffffff) and v[7]==(fail+1 if fail is not None else 15)
   checked=v[42:53]+v[68:72];expected=[b for _,b in SETUP+CS]
   for n,value in enumerate(checked):
    assert value==(0xffffffff if fail is not None and n>fail else expected[n]^(1 if n==fail else 0)),(name,n,value)
   if fail is not None:assert v[5:7]==[expected[fail],expected[fail]^1]
  else:assert v[2:4]==[0,0] and v[7]==0
  horizontal_ran=forward in [0x770,0x7709,0x770b,0x770d,0x770e,0x77010,0x77012,0x77014,0x77016,0x77018,0x7701a,0x7701c,0x7701e,0x77020]
  expectedwrites=[['sq',1,0x21]]
  if fault!='blank':expectedwrites+=[['cr',0x1f,0x57]]
  if fullprefix:expectedwrites += [['mm',a,b] for a,b in SETUP]+[['cr',a,b] for a,b in CS[:3]]
  if horizontal_ran:
   expectedwrites += [['h',a,b] for a,b in H]
   if forward!=0x7709:
    expectedwrites += [['cr',4,93]]
    if forward!=0x770b:
     expectedwrites += [['cr',5,0x3e]]
     if forward!=0x770d:
      expectedwrites += [['cr',0,0x5c]]
      if forward!=0x770e:
       expectedwrites += [['cr',2,0x59]]
       if forward!=0x77010:
        expectedwrites += [['cr',3,0x80]]
        if forward!=0x77012:
         expectedwrites += [['cr',5,0xbe]]
         if forward!=0x77014 and fault!='c17-before-read':
          expectedwrites += [['cr',0x17,0x63]]
          if forward!=0x77016:
           expectedwrites += [['cr',1,0x59]]
           if forward!=0x77018 and fault!='c2b-before-read':
            expectedwrites += [['cr',2,0x59]]
            if forward!=0x7701a and fault!='c17b-before-read':
             expectedwrites += [['cr',0x17,0xe3]]
             if forward!=0x7701c and fault not in ['c19b-before-read','c13-before-c19b-read']:
              expectedwrites += [['cr',0x19,0x30]]
              if forward!=0x7701e and fault not in ['c13-before-read','c19-before-c13-read']:expectedwrites += [['cr',0x13,0x68],['cr',0x13,0x80]]
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
   hf=int(fault.rsplit('-',1)[1]) if forward==0x7709 else None
   assert v[98]==(7 if hf is None else hf+1) and v[99]==(0xffffffff if hf is None else hf)
   target=[b for _,b in H];got=v[83:90]
   assert got[:(7 if hf is None else hf)]==target[:(7 if hf is None else hf)]
   if hf is not None:
    assert got[hf]!=target[hf] and v[102:104]==[target[hf],got[hf]]
    assert got[hf+1:]==[0xffffffff]*(6-hf)
  else:
   assert v[97:100]==[0,0,0xffffffff] and v[83:90]==[0xffffffff]*7
  if fullprefix:expectedwrites += [['cr',0x19,0x51],['mm',0x680630,3]]
  if not (hbad or cbad or zbad or bbad or ebad or nbad or dbad or fbad or rbad or sbad or tbad or ubad):expectedwrites += [['sq',1,1]]
  assert writes==expectedwrites,(name,writes,expectedwrites)
  mask=(1<<int(fault.split('-')[1])) if fault.startswith('cleanup-') else (1<<15 if hbad or cbad or zbad or bbad or ebad or nbad or dbad or fbad or rbad or sbad or tbad or ubad else 0)
  if fault=='c17-drop-undo':mask|=1<<12
  assert v[30]==mask and v[29]==(not mask),(name,v[30],mask)
  hm=1<<int(fault.rsplit('-',1)[1]) if hbad else 0
  assert v[100:102]==[hm,int(not (hbad or cbad or zbad or bbad or ebad or nbad or dbad or fbad or rbad or sbad or tbad or ubad))],(name,v[100:102])
  assert v[76:83]==HB
  for n,val in enumerate(v[90:97]):assert (val!=HB[n])==bool(hm&(1<<n))
  assert v[0]==(0x7706 if fault=='selector' else 0x77021 if ubad else 0x7701f if tbad else 0x7701d if sbad else 0x7701b if rbad else 0x77019 if fbad else 0x77017 if dbad else 0x77015 if nbad else 0x77013 if ebad else 0x77011 if bbad else 0x770f if zbad else 0x770c if cbad else 0x770a if hbad else 0x7705 if mask else forward)
  assert v[28]==(fault!='selector')
  assert v[104]==0xa7 and v[109]==0x31
  cran=horizontal_ran and forward!=0x7709
  assert v[107]==int(cran) and state['c4writes']==(2 if cran else 0)
  assert v[108]==(1 if fault in ['c4-restore-read','c4-restore-write'] else 2 if fault in ['c5-restore-read','c5-coupling','c5-drop-restore'] else 0)
  assert v[106]==(0xa6 if fault=='c4-restore-read' else 93 if fault=='c4-restore-write' else 0xa7)
  assert v[111]==(0x3e if fault=='c5-drop-restore' else 0x30 if fault in ['c5-restore-read','c5-coupling'] else 0x31)
  if cran:
   assert v[105]==(92 if fault=='c4-read' else 0xa7 if fault=='c4-write' else 93)
   assert v[110]==(0x30 if fault in ['c5-read','c5-coupling'] else 0x31)
  else:assert v[105]==v[110]==0xffffffff
  c5ran=cran and forward!=0x770b
  assert state['c5writes']==2*int(c5ran) and v[113]==int(c5ran)
  if c5ran:
   assert v[112]==0x3e
   assert v[114]==(0x31 if fault=='c5-drop-write' else 0x3f if fault=='c5-low-read' else 0xbe if fault=='c5-high-read' else 0x3e)
   assert v[115]==(92 if fault in ['c4-after-read','c4-coupling'] else 93)
  else:assert v[112:116]==[0,0,0xffffffff,0xffffffff]
  c0ran=c5ran and forward!=0x770d
  assert v[116]==0xc8 and state['c0writes']==2*int(c0ran) and v[118]==int(c0ran)
  assert v[120]==(0xc9 if fault=='c0-restore-read' else 0x5c if fault=='c0-drop-restore' else 0xc8)
  assert v[121]==int(zbad)
  if c0ran:
   assert v[117]==0x5c
   assert v[119]==(0xc8 if fault=='c0-drop-write' else 0x5d if fault=='c0-read' else 0x5c)
   assert v[122]==(92 if fault in ['c4-after-c0-read','c0-c4-coupling'] else 93)
   assert v[123]==(0x3f if fault in ['c5-after-c0-read','c0-c5-coupling'] else 0x3e)
  else:assert v[117:120]==[0,0,0xffffffff] and v[122:124]==[0xffffffff]*2
  c2ran=c0ran and forward!=0x770e
  assert v[124]==0x9f and state['c2writes']==2*int(c2ran) and v[126]==int(c2ran)
  assert v[128]==(0x9e if fault=='c2-restore-read' else 0x59 if fault=='c2-drop-restore' else 0x9f)
  assert v[129]==int(bbad)
  if c2ran:
   assert v[125]==0x59
   assert v[127]==(0x9f if fault=='c2-drop-write' else 0x58 if fault=='c2-read' else 0x59)
   for idx,n,expected in [(0,130,0x5c),(4,131,93),(5,132,0x3e)]:
    assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c2-read','c2-c'+str(idx)+'-coupling'] else expected)
  else:assert v[125:128]==[0,0,0xffffffff] and v[130:133]==[0xffffffff]*3
  c3ran=c2ran and forward!=0x77010
  assert v[133]==0x8c and state['c3writes']==2*int(c3ran) and v[135]==int(c3ran)
  assert v[137]==(0x8d if fault=='c3-restore-read' else 0x80 if fault=='c3-drop-restore' else 0x8c)
  assert v[138]==int(ebad)
  if c3ran:
   assert v[134]==0x80
   assert v[136]==(0x8c if fault=='c3-drop-write' else 0x81 if fault=='c3-read' else 0 if fault=='c3-high-read' else 0x80)
   for idx,n,expected in [(0,139,0x5c),(2,140,0x59),(4,141,93),(5,142,0x3e)]:
    assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c3-read','c3-c'+str(idx)+'-coupling'] else expected)
  else:assert v[134:137]==[0,0,0xffffffff] and v[139:143]==[0xffffffff]*4
  c5bran=c3ran and forward!=0x77012
  assert v[145]==int(c5bran) and state['c5bwrites']==2*int(c5bran)
  assert v[148]==int(nbad)
  if c5bran:
   assert v[143:146]==[0x3e,0xbe,1]
   assert v[146]==(0x3e if fault in ['c5b-drop-write','c5b-high-read'] else 0xbf if fault in ['c5b-read','c5b-wrong-write'] else 0xbe)
   assert v[147]==(0xbe if fault=='c5b-drop-undo' else 0x3f if fault=='c5b-undo-read' else 0x3e)
   for idx,n,expected in [(0,149,0x5c),(2,150,0x59),(3,151,0x80),(4,152,93)]:
    assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c5b-read','c5b-c'+str(idx)+'-coupling'] else expected)
  else:assert v[143:153]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
  c17ran=c5bran and forward!=0x77014
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
  c1ran=c17ran and forward!=0x77016
  assert v[166]==int(c1ran) and state['c1writes']==2*v[166] and v[169]==int(fbad)
  if c1ran:
   assert v[164:167]==[c1_original,0x59,1]
   assert v[167]==(c1_original if fault=='c1-drop-write' else 0xd9 if fault=='c1-high-read' else 0x58 if fault in ['c1-read','c1-wrong-write'] else 0x59)
   assert v[168]==(0x59 if fault=='c1-drop-undo' else c1_original^1 if fault=='c1-undo-read' else c1_original)
   for idx,n,expected in [(0,170,0x5c),(2,171,0x59),(3,172,0x80),(4,173,93),(5,174,0xbe),(0x17,175,0x63)]:
    assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c1-read','c1-c'+str(idx)+'-coupling'] else expected)
  else:assert v[164:176]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
  c2bran=c1ran and forward!=0x77018
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
  c17bran=c2bran and forward!=0x7701a
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
  c19bran=c17bran and forward!=0x7701c
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
  c13ran=c19bran and forward!=0x7701e
  assert v[218]==int(c13ran and fault not in ['c13-before-read','c19-before-c13-read']) and state['c13writes']==2*v[218] and v[221]==umask
  if c13ran:
   assert v[216]==(0x81 if fault=='c13-before-read' else 0x80)
   assert v[222]==(0x31 if fault=='c19-before-c13-read' else 0x30)
   if v[218]:
    assert v[217]==0x68
    assert v[219]==(0x80 if fault=='c13-drop-write' else 0xe8 if fault=='c13-high-read' else 0x69 if fault in ['c13-read','c13-wrong-write'] else 0x68)
    assert v[220]==(0x68 if fault=='c13-drop-undo' else 0x81 if fault=='c13-undo-read' else 0x80)
    assert v[231]==(0x31 if fault in ['c13-c25-coupling','c19-undo-c13-read'] else 0x30)
    for idx,n,expected in [(0x19,223,0x30),(0x17,224,0xe3),(0,225,0x5c),(1,226,0x59),(2,227,0x59),(3,228,0x80),(4,229,93),(5,230,0xbe)]:
     assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c13-read','c13-c'+str(idx)+'-coupling'] else expected)
   else:assert v[217:222]==[0,0,0xffffffff,0xffffffff,0] and v[223:232]==[0xffffffff]*9
  else:assert v[216:232]==[0,0,0,0xffffffff,0xffffffff,0,0]+[0xffffffff]*9
 R['cases'].append({'name':name,'raw_result':v,'writes':writes,'ports':ports,'reads':reads,'instructions':steps[0],'critical_instructions':steps[1]})
try:
 run('baseline-deferred-read-success')
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
print('PASS actual770 native ELF',len(R['cases']),'cases; no physical timing/semantics claim')

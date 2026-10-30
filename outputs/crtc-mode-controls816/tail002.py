"""Actual816 compiled full inherited prefix regression with independently checked CR18 boundary.
Control-flow and access contracts only; no modeled transition proves hardware behavior.
"""
import datetime,hashlib,json,struct,sys,os,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn816/build002')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'tail002.json';assert not out.exists()
b=(P/'probe.obj').read_bytes()
R={'passed':False,'scope':__doc__,'object_sha256':sha(P/'probe.obj'),'harness_sha256':sha(Path(__file__)),'cases':[]}
GPU=0xfd000000;deadline=time.monotonic()+240

SETUP=[(0x680884,0),(0x680888,0),(0x68088c,0x10001000),(0x680890,0x10000000),(0x680894,0x10000000),(0x680898,0x10000000),(0x68089c,0x10000000),(0x680880,0x21101100),(0x680630,2),(0x68084c,0x00801080),(0x6808c4,0x40801080)]
H=[(0x680820,719),(0x680824,779),(0x680828,719),(0x680834,0),(0x68082c,738),(0x680830,770),(0x680838,719)]
HB=[1279,1649,1279,0,1389,1429,1279]
V=[(0x680800,719),(0x680804,749),(0x68080c,724),(0x680810,729),(0x680818,719)]
CS=[(0x14,0),(0x17,0xe3),(0x19,0x10),(0x1b,0x85)]
def run(name,flags=0x246,cpu0=0x80010031,cpu3=0xf000,cpu4=0x610,fault="",baseline="",c1_original=0x9f):
 assert time.monotonic()<deadline
 machine,nsec,_,symptr,nsyms,optsz,_=struct.unpack_from('<HHLLLHH',b);assert machine==0x14c and not optsz
 strings=b[symptr+18*nsyms:];sections=[];symbols={};indices={};i=0
 for j in range(nsec):
  h=struct.unpack_from('<8sLLLLLLHHL',b,20+40*j)
  sections.append({'base':0x100000+j*0x10000,'size':h[3],'raw':h[4],'reloc':h[5],'count':h[7]})
 while i<nsyms:
  symbol_name,value,sec,typ,storage,aux=struct.unpack_from('<8sLhHBB',b,symptr+18*i)
  symbol_name=(strings[struct.unpack('<L',symbol_name[4:])[0]:] if symbol_name[:4]==b'\0'*4 else symbol_name).split(b'\0')[0].decode()
  if sec>0:indices[i]=sections[sec-1]['base']+value;symbols[symbol_name]=indices[i]
  elif symbol_name=='_memcpy':indices[i]=0x300000
  elif symbol_name=='_memset':indices[i]=0x300100
  i+=aux+1
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32)
 c.mem_map(0x300000,4096)
 # Harness cdecl memcpy, preserves ESI/EDI. This is not the nxdk libc implementation.
 c.mem_write(0x300000,bytes.fromhex('57568b7c240c8b7424108b4c241489f8fcf3a45e5fc3'))
 c.mem_write(0x300100,bytes.fromhex('578b7c24088b44240c8b4c241089fafcf3aa89d05fc3'))
 for s in sections:
  c.mem_map(s['base'],0x10000)
  if s['size']:c.mem_write(s['base'],b[s['raw']:s['raw']+s['size']])
 for s in sections:
  for j in range(s['count']):
   off,idx,typ=struct.unpack_from('<LLH',b,s['reloc']+j*10);assert idx in indices
   addr=s['base']+off;old=struct.unpack('<L',c.mem_read(addr,4))[0]
   assert typ in (6,20)
   value=old+indices[idx]-(addr+4 if typ==20 else 0)
   c.mem_write(addr,struct.pack('<L',value&0xffffffff))
 c.mem_map(0x200000,0x40000)

 c.mem_write(0x200000,b'G'*0x40000);c.mem_map(GPU,0x1000000)
 c.mem_write(0x208000,struct.pack('<II',0x20ff00,0x201000))
 c.reg_write(x.UC_X86_REG_ESP,0x208000);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 sels={0x6013d4:0x67,0xc03c4:0x72,0xc03ce:0x91};original=sels.copy()
 mm=dict(SETUP);mm.update(dict(V));mm.update({0x680808:719,0x680814:0});mm[0x680630]=3;mm.update(dict(zip([a for a,_ in H],HB)));hw={a:0 for a,_ in H};hr=[]
 cr={7:0xf0,6:0xec,9:0x60,0x10:0xd4,0x12:0xcf,0x15:0xcf,0x16:0xed,0x18:0xff,0x25:0x10,0x13:0x80,1:c1_original,3:0x8c,2:0x9f,0:0xc8,4:0xa7,5:0x31,0x11:9,0x14:0,0x17:0xe3,0x19:0x51,0x1b:0x85,0x22:0xfe,0x33:0x11,0x1f:0}
 cr.update({0x1a:0x38,0x28:0x83,0x2d:0xe0})
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
 state={'mc_phase':None,'mc_ret':None,'mc_step':-1,'mc_trace':[],'cl18writes':0,'cl18reads':[],'cl9writes':0,'cl7writes':0,'cb15writes':0,'cb7writes':0,'cb9writes':0,'cd12writes':0,'cd7writes':0,'ct16writes':0,'ct6writes':0,'ct7writes':0,'c10writes':0,'c7writes':0,'vewrites':0,'sewrites':0,'sywrites':0,'vswrites':0,'vcwrites':0,'vtwrites':0,'vwrites':0,'c13writes':0,'c19bwrites':0,'c17bwrites':0,'c2bwrites':0,'c1writes':0,'c17writes':0,'c5bwrites':0,'c3writes':0,'c2writes':0,'c0writes':0,'c5writes':0,'c4writes':0,'sq':sq,'gr':gr,'recovering':False,'unlock':False}
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
   if state['mc_phase']:
    regs_mc=[26,37,40,45,19,25,23,24,7,9];assert idx in regs_mc
    j=regs_mc.index(idx);phase=state['mc_phase'];i=state['mc_step']
    assert state['sq']==0x21 and ports==[5]
    if kind==u.UC_MEM_WRITE:
     assert j<4
     if phase=='forward':
      assert j==i+1 and word(834)==j+1;value_expected=[60,16,131,224][j]
     else:
      assert j==(word(834)-1 if i==-1 else i-1);value_expected=word(820+j)
     assert value==value_expected;state['mc_step']=j;i=j
     state['mc_trace'].append([phase,i,'write',idx,value])
     if fault==f'mc-{phase}-drop-{i}':return
     cr[idx]=value
     if fault==f'mc-{phase}-wrong-{i}':cr[idx]^=1
     if phase=='forward' and fault.startswith(f'mc-couple-{i}-'):cr[regs_mc[int(fault.rsplit('-',1)[1])]]^=1
     return
    val=cr[idx]
    label='before' if phase=='forward' and i==-1 else phase
    if fault==f'mc-{label}-read-{i}-{j}':val^=1
    state['mc_trace'].append([label,i,'read',idx,val]);uc.mem_write(addr,bytes([val]));return
   if kind==u.UC_MEM_WRITE:
    assert idx in [0x18,0x15,9,0x12,0x16,6,0x10,7,1,3,2,0,4,5,0x13,0x1f,0x14,0x17,0x19]
    if idx==0x18:
     assert state['cl9writes']==1 and word(1) in [0x81648,0x816,0x81650,0x81651,0x81652,0x81653]
     state['cl18writes']+=1;n=state['cl18writes'];assert n<=2
     assert [word(790),word(791),word(792)]==[255,255,1] and value==255
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',24,value])
     if fault==('cl18-drop-write' if n==1 else 'cl18-drop-undo') or (n==2 and fault=='cl18-wrong-write-drop-undo'):return
     cr[24]=value
     if fault==('cl18-wrong-write' if n==1 else 'cl18-wrong-undo') or (n==1 and fault=='cl18-wrong-write-drop-undo'):cr[24]^=1
     if n==1 and fault.startswith('cl18-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,16,18,21,22,37][j-1]]^=1
     return
    if idx==9 and state['cl7writes']==1 and word(1) in [0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
     state['cl9writes']+=1;n=state['cl9writes'];assert n<=2
     assert [word(760),word(761),word(762)]==[64,64,1] and value==64
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',9,value])
     if fault==('cl9-drop-write' if n==1 else 'cl9-drop-undo') or (n==2 and fault=='cl9-wrong-write-drop-undo'):return
     cr[9]=value
     if fault==('cl9-wrong-write' if n==1 else 'cl9-wrong-undo') or (n==1 and fault=='cl9-wrong-write-drop-undo'):cr[9]^=1
     if n==1 and fault.startswith('cl9-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,16,18,21,22,24,37][j-1]]^=1
     return
    if idx==7 and state['cb15writes']==1 and word(1) in [0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
     state['cl7writes']+=1;n=state['cl7writes'];assert n<=2
     if n==2:assert state['cl9writes']==2*word(762)
     assert [word(730),word(731),word(732)]==[62,62,1] and value==62
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',7,value])
     if fault==('cl7-drop-write' if n==1 else 'cl7-drop-undo') or (n==2 and fault=='cl7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('cl7-wrong-write' if n==1 else 'cl7-wrong-undo') or (n==1 and fault=='cl7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('cl7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,16,18,21,22,24,37][j-1]]^=1
     return
    if idx==0x15 and state['cb7writes']==1 and word(1) in [0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
     state['cb15writes']+=1;n=state['cb15writes'];assert n<=2
     if n==2:assert state['cl7writes']==2*word(732)
     assert [word(700),word(701),word(702)]==[207,223,1] and value==[223,207][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',21,value])
     if fault==('cb15-drop-write' if n==1 else 'cb15-drop-undo') or (n==2 and fault=='cb15-wrong-write-drop-undo'):return
     cr[21]=value
     if fault==('cb15-wrong-write' if n==1 else 'cb15-wrong-undo') or (n==1 and fault=='cb15-wrong-write-drop-undo'):cr[21]^=1
     if n==1 and fault.startswith('cb15-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,16,18,22,24,37][j-1]]^=1
     return
    if idx==7 and state['cb9writes']==1 and word(1) in [0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
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
     assert state['cd12writes']==1 and state['cd7writes']==1 and word(1) in [0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
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
     assert state['cd7writes']==1 and state['ct16writes']==1 and word(1) in [0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
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
     assert state['ct6writes']==1 and state['ct7writes']==1 and word(1) in [0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
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
     assert state['ct6writes']==1 and state['ct7writes']==1 and word(1) in [0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
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
     assert state['ct7writes']==1 and state['c10writes']==1 and word(1) in [0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
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
     assert state['c7writes']==1 and state['vewrites']==1 and word(1) in [0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
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
     assert state['c7writes']==1 and word(1) in [0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
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
     assert state['vewrites']==1 and word(1) in [0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
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
   if idx in [24,6,7,9,16,18,21,22,37] and state['cl9writes']==1 and word(1) in [0x81648,0x816,0x81650,0x81651,0x81652,0x81653]:
    j=[24,6,7,9,16,18,21,22,37].index(idx);phase=['before','after','undo'][state['cl18writes']]
    if fault=='cl18-'+phase+'-'+str(j):val^=1
    state['cl18reads'].append([phase,j,val])
   if idx in [9,6,7,16,18,21,22,24,37] and state['cl7writes']==1 and word(1) in [0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=[9,6,7,16,18,21,22,24,37].index(idx);phase=['before','after','undo'][state['cl9writes']]
    if fault=='cl9-'+phase+'-'+str(j):val^=1

   if idx in [7,6,9,16,18,21,22,24,37] and state['cb15writes']==1 and word(1) in [0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=[7,6,9,16,18,21,22,24,37].index(idx);phase=['before','after','undo'][state['cl7writes']]
    if fault=='cl7-'+phase+'-'+str(j):val^=1

   if idx in [21,6,7,9,16,18,22,24,37] and state['cb7writes']==1 and word(1) in [0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=[21,6,7,9,16,18,22,24,37].index(idx);phase=['before','after','undo'][state['cb15writes']]
    if fault=='cb15-'+phase+'-'+str(j):val^=1

   if idx in [7,6,9,16,18,21,22,24,37] and state['cb9writes']==1 and word(1) in [0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=[7,6,9,16,18,21,22,24,37].index(idx);phase=['before','after','undo'][state['cb7writes']]
    if fault=='cb7-'+phase+'-'+str(j):val^=1

   if idx in [9,6,7,16,18,21,22,24,37] and state['cd12writes']==1 and word(1) in [0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=[9,6,7,16,18,21,22,24,37].index(idx);phase=['before','after','undo'][state['cb9writes']]
    if fault=='cb9-'+phase+'-'+str(j):val^=1

   if idx in [18,6,7,9,16,21,22,24,37] and state['cd7writes']==1 and word(1) in [0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=[18,6,7,9,16,21,22,24,37].index(idx);phase=['before','after','undo'][state['cd12writes']]
    if fault=='cd12-'+phase+'-'+str(j):val^=1

   if idx in [7,6,9,16,18,21,22,24,37] and state['ct16writes']==1 and word(1) in [0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=[7,6,9,16,18,21,22,24,37].index(idx);phase=['before','after','undo'][state['cd7writes']]
    if fault=='cd7-'+phase+'-'+str(j):val^=1

   if idx in [0x16,6,7,9,0x10,0x12,0x15,0x18,0x25] and state['ct6writes']==1 and word(1) in [0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=[0x16,6,7,9,0x10,0x12,0x15,0x18,0x25].index(idx);phase=['before','after','undo'][state['ct16writes']]
    if fault=='ct16-'+phase+'-'+str(j):val^=1

   if idx in [6,7,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['ct7writes']==1 and word(1) in [0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=[6,7,9,0x10,0x12,0x15,0x16,0x18,0x25].index(idx);phase=['before','after','undo'][state['ct6writes']]
    if fault=='ct6-'+phase+'-'+str(j):val^=1

   if idx in [7,6,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['c10writes']==1 and word(1) in [0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=[7,6,9,0x10,0x12,0x15,0x16,0x18,0x25].index(idx);phase=['before','after','undo'][state['ct7writes']]
    if fault=='ct7-'+phase+'-'+str(j):val^=1

   if idx in [0x10,6,7,9,0x12,0x15,0x16,0x18,0x25] and state['c7writes']==1 and word(1) in [0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=[0x10,6,7,9,0x12,0x15,0x16,0x18,0x25].index(idx);phase=['before','after','undo'][state['c10writes']]
    if fault=='c10-'+phase+'-'+str(j):val^=1

   if idx in [7,6,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['vewrites']==1 and word(1) in [0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=[7,6,9,0x10,0x12,0x15,0x16,0x18,0x25].index(idx);phase=['before','after','undo'][state['c7writes']]
    if fault=='c7-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['sewrites']==1 and word(1) in [0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vewrites']]
    if fault=='ve-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['sywrites']==1 and word(1) in [0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['sewrites']]
    if fault=='se-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['vswrites']==1 and word(1) in [0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['sywrites']]
    if fault=='sy-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['vcwrites']==1 and word(1) in [0x81628,0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vswrites']]
    if fault=='vs-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['vtwrites']==1 and word(1) in [0x81626,0x81628,0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vcwrites']]
    if fault=='vc-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['vwrites']==1 and word(1) in [0x81624,0x81626,0x81628,0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=5+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vtwrites']]
    if fault=='vt-'+phase+'-'+str(j):val^=1

   if idx in [0x13,0x19] and state['c13writes']==1 and word(1) in [0x81622,0x81624,0x81626,0x81628,0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    j=5+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vwrites']]
    if fault=='v-'+phase+'-'+str(j):val^=1

   if word(1)==0x81620 and not word(218) and state['c19bwrites']==1:
    if idx==0x13 and fault=='c13-before-read':val^=1
    if idx==0x19 and fault=='c19-before-c13-read':val^=1
   if idx==0x13 and state['c13writes']==1 and fault=='c13-read':val^=1
   if idx==0x13 and state['c13writes']==1 and fault=='c13-high-read':val^=0x80
   if idx==0x13 and state['c13writes']==2 and state['c19bwrites']==1 and fault=='c13-undo-read':val^=1
   if idx==0x19 and state['c13writes']==2 and state['c19bwrites']==1 and fault=='c19-undo-c13-read':val^=1
   if idx in [0,1,2,3,4,5,0x19,0x17] and state['c13writes']==1 and fault=='c'+str(idx)+'-after-c13-read':val^=1
   if word(1)==0x8161e and not word(202) and state['c17bwrites']==1:
    if idx==0x19 and fault=='c19b-before-read':val^=1
    if idx==0x13 and fault=='c13-before-c19b-read':val^=1
   if idx==0x19 and state['c19bwrites']==1 and fault=='c19b-read':val^=1
   if idx==0x19 and state['c19bwrites']==1 and fault=='c19b-high-read':val^=0x20
   if idx==0x19 and state['c19bwrites']==2 and state['c17bwrites']==1 and fault=='c19b-undo-read':val^=1
   if idx==0x13 and state['c19bwrites']==2 and state['c17bwrites']==1 and fault=='c13-undo-c19b-read':val^=1
   if idx in [0,1,2,3,4,5,0x13,0x17] and state['c19bwrites']==1 and fault=='c'+str(idx)+'-after-c19b-read':val^=1
   if idx==0x17 and word(1)==0x8161c and not word(190) and state['c2bwrites']==1 and fault=='c17b-before-read':val^=1
   if idx==0x17 and state['c17bwrites']==1 and fault=='c17b-read':val^=1
   if idx==0x17 and state['c17bwrites']==1 and fault=='c17b-low-read':val^=0x80
   if idx==0x17 and state['c17bwrites']==2 and state['c2bwrites']==1 and fault=='c17b-undo-read':val^=1
   if idx in [0,1,2,3,4,5] and state['c17bwrites']==1 and fault=='c'+str(idx)+'-after-c17b-read':val^=1
   if idx==2 and word(1)==0x8161a and not word(178) and state['c1writes']==1 and fault=='c2b-before-read':val^=1
   if idx==2 and state['c2bwrites']==1 and fault=='c2b-read':val^=1
   if idx==2 and state['c2bwrites']==1 and fault=='c2b-high-read':val^=0x80
   if idx==2 and state['c2bwrites']==2 and state['c1writes']==1 and fault=='c2b-undo-read':val^=1
   if idx in [0,1,3,4,5,0x17] and state['c2bwrites']==1 and fault=='c'+str(idx)+'-after-c2b-read':val^=1
   if idx==1 and state['c1writes']==1 and fault=='c1-read':val^=1
   if idx==1 and state['c1writes']==1 and fault=='c1-high-read':val^=0x80
   if idx==1 and state['c1writes']==2 and state['c17writes']==1 and fault=='c1-undo-read':val^=1
   if idx in [0,2,3,4,5,0x17] and state['c1writes']==1 and fault=='c'+str(idx)+'-after-c1-read':val^=1
   if idx==0x17 and word(1)==0x81616 and not word(155) and not state['recovering'] and fault=='c17-before-read':val^=1
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
   if word(1)==0x8168 and not state['recovering'] and idx in dict(CS):
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
   assert word(1) in [0x81626,0x81628,0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
   if kind==u.UC_MEM_WRITE and off==0x680814:
    assert state['vcwrites']==1 and word(1) in [0x81628,0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
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
   if state['sewrites']==1 and word(1) in [0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    sj=4 if off==0x680814 else 3;sp=['before','after','undo'][state['vewrites']]
    if fault=='ve-'+sp+'-'+str(sj):val^=1

   if state['sywrites']==1 and word(1) in [0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    sj=4 if off==0x680814 else 3;sp=['before','after','undo'][state['sewrites']]
    if fault=='se-'+sp+'-'+str(sj):val^=1

   if state['vswrites']==1 and word(1) in [0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    sj=4 if off==0x680814 else 3;sp=['before','after','undo'][state['sywrites']]
    if fault=='sy-'+sp+'-'+str(sj):val^=1

   if fault=='vc-'+phase+'-'+str(j):val^=1
   if state['vcwrites']==1 and word(1) in [0x81628,0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    sj=0 if off==0x680814 else 3;sp=['before','after','undo'][state['vswrites']]
    if fault=='vs-'+sp+'-'+str(sj):val^=1

  elif off in dict(V):
   assert width==4;j=[a for a,_ in V].index(off)
   assert state['sq']==0x21 and ports==[5] and not hr and state['c13writes']==1
   assert word(1) in [0x81622,0x81624,0x81626,0x81628,0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
   if kind==u.UC_MEM_WRITE and off==0x68080c:
    assert state['vswrites']==1 and word(1) in [0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
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
    assert state['sywrites']==1 and word(1) in [0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
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
    assert state['sewrites']==1 and word(1) in [0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
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
    assert state['vwrites']==1 and word(1) in [0x81624,0x81626,0x81628,0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]
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
   if state['sewrites']==1 and word(1) in [0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    sj={0x680800:1,0x680804:2,0x68080c:5,0x680810:6,0x680818:0}[off]
    sp=['before','after','undo'][state['vewrites']]
    if fault=='ve-'+sp+'-'+str(sj):val^=1

   if state['sywrites']==1 and word(1) in [0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    sj={0x680800:1,0x680804:2,0x68080c:5,0x680810:0,0x680818:6}[off]
    sp=['before','after','undo'][state['sewrites']]
    if fault=='se-'+sp+'-'+str(sj):val^=1

   if state['vswrites']==1 and word(1) in [0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    sj={0x680800:1,0x680804:2,0x68080c:0,0x680810:5,0x680818:6}[off]
    sp=['before','after','undo'][state['sywrites']]
    if fault=='sy-'+sp+'-'+str(sj):val^=1

   if state['vcwrites']==1 and word(1) in [0x81628,0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    sj={0x680800:1,0x680804:2,0x68080c:4,0x680810:5,0x680818:6}[off]
    sp=['before','after','undo'][state['vswrites']]
    if fault=='vs-'+sp+'-'+str(sj):val^=1

   if state['vtwrites']==1 and word(1) in [0x81626,0x81628,0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
    cj={0x680800:1,0x680804:2,0x68080c:3,0x680810:4,0x680818:6}[off]
    cp=['before','after','undo'][state['vcwrites']]
    if fault=='vc-'+cp+'-'+str(cj):val^=1

   if state['vwrites']==1 and word(1) in [0x81624,0x81626,0x81628,0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x816,0x81648,0x81650,0x81651,0x81652,0x81653]:
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
   if word(1)==0x8169 and word(98)<=6 and not hr and fault=='h-read-'+str(n):val^=1
   if hr and fault=='h-restore-read-'+str(n):val^=1
   # When no horizontal writes occurred, recovery still checks all seven words.
   if not hw[off] and state['unlock'] and word(1)==0x8168 and fault=='h-pre-restore-'+str(n):val^=1
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
   if word(1)==0x8168 and not state['recovering']:
    assert word(2)==11 and word(3)==3
    if fault=='check-'+str(n):val^=1
   if state['recovering'] and fault=='cleanup-'+str(n) and n!=8:val^=1
  if off==0x6013d5 and state['recovering'] and fault in ['cleanup-11','cleanup-12']:
   if sels[0x6013d4]==CS[int(fault.split('-')[1])-11][0]:val^=1
  reads.append([off,sels.get(off-1),val,word(1),bool(state['recovering'])])
  uc.mem_write(addr,val.to_bytes(width,'little'))
 regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_EBX,x.UC_X86_REG_ESP,x.UC_X86_REG_EBP,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI]
 def code(uc,pc,n,_):
  if pc==state['mc_ret']:state['mc_phase']=None;state['mc_ret']=None
  if pc in [symbols['_controls_forward816'],symbols['_controls_restore816']]:
   state['mc_phase']='forward' if pc==symbols['_controls_forward816'] else 'undo'
   state['mc_ret']=struct.unpack('<I',uc.mem_read(uc.reg_read(x.UC_X86_REG_ESP),4))[0]
   state['mc_step']=-1
  steps[0]+=1
  if n>15:raise AssertionError(('invalid-instruction',hex(pc),n,bytes(uc.mem_read(pc,16)).hex()))
  raw=bytes(uc.mem_read(pc,n));assert raw[:2]!=b'\x0f\x22'
  if raw[:2]==b'\x0f\x20':
   mod=raw[2];assert mod>>6==3;reg=(mod>>3)&7;assert reg in (0,3,4)
   uc.reg_write(regs[mod&7],{0:cpu0,3:cpu3,4:cpu4}[reg]);uc.reg_write(x.UC_X86_REG_EIP,pc+n)
  if not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200:steps[1]+=1
 def ramwrite(uc,kind,addr,size,val,_):
  if GPU<=addr<GPU+0x1000000:return
  assert 0x201000<=addr and addr+size<=0x201e54 or 0x207000<=addr and addr+size<=0x208008,(hex(addr),size)
 def pout(uc,port,size,val,_):
  assert (port,size)==(0x80d3,1) and val in [4,5]
  assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  ports.append(val)
  if val==4:
   assert word(915)==0
   assert word(795)==0 and (not word(792) or word(794)==word(790))
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
 try:c.emu_start(symbols['_probe816'],0x20ff00,timeout=2000000,count=60000)
 except Exception as exc:
  raise AssertionError((name,str(exc),hex(c.reg_read(x.UC_X86_REG_EIP)),hex(c.reg_read(x.UC_X86_REG_ESP)),steps,writes[-5:])) from exc
 assert c.reg_read(x.UC_X86_REG_EIP)==0x20ff00 and c.reg_read(x.UC_X86_REG_ESP)==0x208004,(name,hex(c.reg_read(x.UC_X86_REG_EIP)),hex(c.reg_read(x.UC_X86_REG_ESP)),steps)
 v=list(struct.unpack('<917I',c.mem_read(0x201000,3668)))
 assert bytes(c.mem_read(0x200000,4096))==b'G'*4096
 assert bytes(c.mem_read(0x201e54,0x51ac))==b'G'*0x51ac
 assert bytes(c.mem_read(0x208008,0xff8))==b'G'*0xff8 and sels==original
 assert v[8]==v[10] and v[11:14]==[cpu0,cpu3,cpu4]
 mc=v[820:];trace=state['mc_trace'];regs_mc=[26,37,40,45,19,25,23,24,7,9]
 if cpu0!=0x80010031 or cpu4&0x20:
  assert mc==[0]*15+[0xffffffff]*80+[0,0] and not trace
 else:
  # Independently replay the observed accesses against the protocol, deriving
  # forward and recovery masks from observed values rather than status colors.
  obs=[t[4] for t in trace[:10]];assert [t[2] for t in trace[:10]]==['read']*10
  assert mc[:10]==obs
  fm=sum(1<<j for j,(a,b) in enumerate(zip(obs,[56,16,131,224,104,48,227,255,62,64])) if a!=b)
  pos=10;attempts=0;stage=0x81650
  while not fm and attempts<4:
   i=attempts;stage=0x81650+i
   assert trace[pos]==['forward',i,'write',regs_mc[i],[60,16,131,224][i]];pos+=1;attempts+=1
   readings=trace[pos:pos+10];pos+=10
   assert [t[:4] for t in readings]==[['forward',i,'read',r] for r in regs_mc]
   vals=[t[4] for t in readings];assert mc[15+10*i:25+10*i]==vals
   expected=[([60,16,131,224][j] if j<=i else obs[j]) for j in range(10)]
   fm=sum(1<<j for j,(a,b) in enumerate(zip(vals,expected)) if a!=b)
  assert mc[14]==attempts and mc[96]==fm
  assert v[1]==(stage if fm else 0x816)
  um=0
  for i in reversed(range(attempts)):
   assert trace[pos]==['undo',i,'write',regs_mc[i],obs[i]];pos+=1
   readings=trace[pos:pos+10];pos+=10
   assert [t[:4] for t in readings]==[['undo',i,'read',r] for r in regs_mc]
   vals=[t[4] for t in readings];assert mc[55+10*i:65+10*i]==vals
   expected=[([60,16,131,224][j] if j<i else obs[j]) for j in range(10)]
   um|=sum(1<<j for j,(a,b) in enumerate(zip(vals,expected)) if a!=b)
  assert pos==len(trace) and mc[95]==um
  assert mc[15+10*attempts:55]==[0xffffffff]*(40-10*attempts)
  assert mc[55+10*attempts:95]==[0xffffffff]*(40-10*attempts)
  assert (4 in ports)==(um==0 and all(v[n]==0 for n in [100,108,121,129,138,148,158,169,181,193,205,221,237,261,285,315,345,375,405,435,465,495,525,555,585,615,645,675,705,735,765,795]))
  if um:assert v[0]==0x81654
  if not fault:assert v[:2]==[0x816,0x816] and not um and attempts==4
 R['cases'].append(dict(name=name,raw_result=v,ports=ports,control_trace=trace))
try:
 for flags in [0x246,0x46]:run('clean-'+hex(flags),flags=flags)
 run('cpu-unpaged',cpu0=0x10031);run('cpu-pae',cpu4=0x630)
 for j in range(10):run(f'mc-before-read--1-{j}',fault=f'mc-before-read--1-{j}')
 for phase in ['forward','undo']:
  for i in range(4):
   for j in range(10):run(f'mc-{phase}-read-{i}-{j}',fault=f'mc-{phase}-read-{i}-{j}')
   for f in ['drop','wrong']:run(f'mc-{phase}-{f}-{i}',fault=f'mc-{phase}-{f}-{i}')
 for i in range(4):
  for j in range(10):
   if j!=i:run(f'mc-couple-{i}-{j}',fault=f'mc-couple-{i}-{j}')
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:
 R['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,separators=(',',':'))+'\n')
print('PASS816 compiled four-control fault cases:',len(R['cases']))

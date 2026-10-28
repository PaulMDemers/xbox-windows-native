"""Extend relocated765 validation with independent CR17 enable/recovery cases."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration004.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
rep("state={'c2bwrites':0","state={'c17bwrites':0,'c2bwrites':0")
rep('    if i==2 and', '''    if i==0x17 and struct.unpack('<I',uc.mem_read(op+760,4))[0] and state['c17bwrites']<2:
     state['c17bwrites']+=1;n=state['c17bwrites'];assert n<=2 and value==(0xe3 if n==1 else 0x63)
     assert state['seq']==0x21 and state['gate']==5 and not hrestore and state['c2bwrites']==state['c1writes']==state['c17writes']==1
     assert state['c5bwrites']==1 and all(state['c'+str(i2)+'writes']==1 for i2 in [0,2,3,4,5])
     assert struct.unpack('<3I',uc.mem_read(op+752,12))==(0x63,0xe3,1)
     if fault==('c17b-drop-write' if n==1 else 'c17b-drop-undo'):return
     cr[0x17]=value
     if n==1 and fault=='c17b-wrong-write':cr[0x17]^=1
     for idx2 in [0,1,2,3,4,5]:
      if n==1 and fault=='c17b-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==2 and''')
rep("state['c2bwrites']+=1;n=state['c2bwrites'];assert", "state['c2bwrites']+=1;n=state['c2bwrites'];assert state['c17bwrites']==2*struct.unpack('<I',uc.mem_read(op+760,4))[0];assert")
rep('   i=sels[0x6013d4]\n', '''   i=sels[0x6013d4]
   if i==0x17 and struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x7651c and not struct.unpack('<I',uc.mem_read(op+760,4))[0] and state['c2bwrites']==1 and fault=='c17b-before-read':value^=1
   if i==0x17 and state['c17bwrites']==1 and fault=='c17b-read':value^=1
   if i==0x17 and state['c17bwrites']==1 and fault=='c17b-low-read':value^=0x80
   if i==0x17 and state['c17bwrites']==2 and state['c2bwrites']==1 and fault=='c17b-undo-read':value^=1
   if i in [0,1,2,3,4,5] and state['c17bwrites']==1 and fault=='c'+str(i)+'-after-c17b-read':value^=1
''')
rep('   if value==4:\n', "   if value==4:\n    assert struct.unpack('<I',uc.mem_read(op+772,4))[0]==0\n")
rep('addr+size<=op+752','addr+size<=op+800');rep("'<188I'","'<200I'")
rep('[(2,0x59),(2,0x59)] if state', "[(2,0x59)]+([(0x17,0xe3),(0x17,0x63)] if state['c17bwrites'] else [])+[(2,0x59)] if state")
rep('  else:assert v[100:102]==[0,1]', "  elif fault in ['c17b-undo-read','c17b-drop-undo']:assert sw==[0x21] and outs==[5] and v[193]==1 and v[101]==0\n  else:assert v[100:102]==[0,1]")
rep('0x7651a]','0x7651a,0x7651c]')
rep(' for lo,hi in [(0,0x880)', ''' if state['c17bwrites']:
  assert state['c17bwrites']==2 and v[188:191]==[0x63,0xe3,1]
  assert v[191]==(0x63 if fault in ['c17b-drop-write','c17b-low-read'] else 0xe2 if fault in ['c17b-read','c17b-wrong-write'] else 0xe3)
  assert v[192]==(0xe3 if fault=='c17b-drop-undo' else 0x62 if fault=='c17b-undo-read' else 0x63)
  assert v[193]==int(v[192]!=v[188])
  for idx,n,target in [(0,194,0x5c),(1,195,0x59),(2,196,0x59),(3,197,0x80),(4,198,93),(5,199,0xbe)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c17b-read','c17b-c'+str(idx)+'-coupling'] else target)
 elif fault=='c17b-before-read':assert v[188:200]==[0x62,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 else:assert v[188:200]==([0]*12 if refusal or want<0x765 else [0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff])
 for lo,hi in [(0,0x880)''')
rep('(0x53f0,0x6000)','(0x5420,0x6000)')
rep('v[158],v[169],v[181],v[176],v[179],v[180]','v[169],v[181],v[193],v[188],v[191],v[192]')
rep(' for n in range(7):', ''' for fault in ['c17b-before-read','c17b-read','c17b-low-read','c17b-drop-write','c17b-wrong-write']+['c'+str(i)+'-after-c17b-read' for i in [0,1,2,3,4,5]]+['c17b-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5]]+['c17b-undo-read','c17b-drop-undo']:
  run(fault,want=0x7651d if fault in ['c17b-undo-read','c17b-drop-undo'] else 0x7651c,fault=fault)
 for n in range(7):''')
p.write_text(s,newline='\n')

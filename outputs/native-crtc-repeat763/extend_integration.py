"""Extend independent relocated execution for the later same-value CR02 step."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration004.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
rep("state={'c1writes':0","state={'c2bwrites':0,'c1writes':0")
rep('    if i==1:', '''    if i==2 and struct.unpack('<I',uc.mem_read(op+712,4))[0] and state['c2bwrites']<2:
     state['c2bwrites']+=1;n=state['c2bwrites'];assert n<=2 and value==0x59
     assert state['seq']==0x21 and state['gate']==5 and not hrestore and state['c1writes']==state['c17writes']==1
     assert state['c5bwrites']==1 and all(state['c'+str(i2)+'writes']==1 for i2 in [0,2,3,4,5])
     assert struct.unpack('<3I',uc.mem_read(op+704,12))==(0x59,0x59,1)
     if fault==('c2b-drop-write' if n==1 else 'c2b-drop-undo') or (n==2 and fault=='c2b-wrong-write-drop-undo'):return
     cr[2]=value
     if n==1 and fault in ['c2b-wrong-write','c2b-wrong-write-drop-undo']:cr[2]^=1
     for idx2 in [0,1,3,4,5,0x17]:
      if n==1 and fault=='c2b-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==1:''')
rep("state['c1writes']+=1;n=state['c1writes'];assert", "state['c1writes']+=1;n=state['c1writes'];assert state['c2bwrites']==2*struct.unpack('<I',uc.mem_read(op+712,4))[0];assert")
rep('   i=sels[0x6013d4]\n', '''   i=sels[0x6013d4]
   if i==2 and struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x7631a and not struct.unpack('<I',uc.mem_read(op+712,4))[0] and state['c1writes']==1 and fault=='c2b-before-read':value^=1
   if i==2 and state['c2bwrites']==1 and fault=='c2b-read':value^=1
   if i==2 and state['c2bwrites']==1 and fault=='c2b-high-read':value^=0x80
   if i==2 and state['c2bwrites']==2 and state['c1writes']==1 and fault=='c2b-undo-read':value^=1
   if i in [0,1,3,4,5,0x17] and state['c2bwrites']==1 and fault=='c'+str(i)+'-after-c2b-read':value^=1
''')
rep('   if value==4:\n', "   if value==4:\n    assert struct.unpack('<I',uc.mem_read(op+724,4))[0]==0\n")
rep('addr+size<=op+704','addr+size<=op+752');rep("'<176I'","'<188I'")
rep('([(1,0x59),(1,c1_original)]', '([(1,0x59)]+([(2,0x59),(2,0x59)] if state[\'c2bwrites\'] else [])+[(1,c1_original)]')
rep('  else:assert v[100:102]==[0,1]', "  elif fault in ['c2b-undo-read','c2b-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[181]==1 and v[101]==0\n  else:assert v[100:102]==[0,1]")
rep('0x76318]','0x76318,0x7631a]')
rep(' for lo,hi in [(0,0x880)', ''' if state['c2bwrites']:
  assert state['c2bwrites']==2 and v[176:179]==[0x59,0x59,1]
  assert v[179]==(0xd9 if fault=='c2b-high-read' else 0x58 if fault in ['c2b-read','c2b-wrong-write','c2b-wrong-write-drop-undo'] else 0x59)
  assert v[180]==(0x58 if fault in ['c2b-undo-read','c2b-wrong-write-drop-undo'] else 0x59)
  assert v[181]==int(v[180]!=v[176])
  for idx,n,target in [(0,182,0x5c),(1,183,0x59),(3,184,0x80),(4,185,93),(5,186,0xbe),(0x17,187,0x63)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c2b-read','c2b-c'+str(idx)+'-coupling'] else target)
 elif fault=='c2b-before-read':assert v[176:188]==[0x58,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 else:assert v[176:188]==([0]*12 if refusal or want<0x763 else [0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff])
 for lo,hi in [(0,0x880)''')
rep('(0x53c0,0x6000)','(0x53f0,0x6000)')
rep('v[138],v[158],v[169],v[164],v[167],v[168]', 'v[158],v[169],v[181],v[176],v[179],v[180]')
rep(' for n in range(7):\n', ''' for fault in ['c2b-before-read','c2b-read','c2b-high-read','c2b-wrong-write','c2b-wrong-write-drop-undo']+['c'+str(i)+'-after-c2b-read' for i in [0,1,3,4,5,0x17]]+['c2b-c'+str(i)+'-coupling' for i in [0,1,3,4,5,0x17]]+['c2b-undo-read','c2b-drop-write','c2b-drop-undo']:
  run(fault,want=0x7631b if fault in ['c2b-undo-read','c2b-wrong-write-drop-undo'] else 0x763 if fault in ['c2b-drop-write','c2b-drop-undo'] else 0x7631a,fault=fault)
 for n in range(7):
''')
p.write_text(s,newline='\n')

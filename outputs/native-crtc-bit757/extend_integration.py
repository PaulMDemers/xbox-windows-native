"""Extend native relocated integration for distinct second CR05 write/undo."""
from pathlib import Path
p=Path(__file__).resolve().parent/'integration004.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep("state={'c3writes':0,","state={'c5bwrites':0,'c3writes':0,")
rep('    if i==3:', '''    if i==5 and struct.unpack('<I',uc.mem_read(op+580,4))[0] and state['c5bwrites']<2:
     state['c5bwrites']+=1;n=state['c5bwrites'];assert value==(0xbe if n==1 else 0x3e)
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     assert all(state['c'+str(i2)+'writes']==1 for i2 in [0,2,3,4,5])
     assert struct.unpack('<3I',uc.mem_read(op+572,12))==(0x3e,0xbe,1)
     if fault==('c5b-drop-write' if n==1 else 'c5b-drop-undo'):return
     cr[5]=value
     if n==1 and fault=='c5b-wrong-write':cr[5]^=1
     for idx2 in [0,2,3,4]:
      if n==1 and fault=='c5b-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==3:''')
rep("     state['c3writes']+=1;assert state['c3writes']<=2", "     state['c3writes']+=1;assert state['c3writes']<=2\n     if state['c3writes']==2:assert state['c5bwrites']==2*struct.unpack('<I',uc.mem_read(op+580,4))[0]")
rep("   if i==3 and state['c3writes']==1 and fault=='c3-read':value^=1", '''   if i==5 and state['c5bwrites']==1 and fault=='c5b-read':value^=1
   if i==5 and state['c5bwrites']==1 and fault=='c5b-high-read':value^=0x80
   if i==5 and state['c5bwrites']==2 and state['c3writes']==1 and fault=='c5b-undo-read':value^=1
   if i in [0,2,3,4] and state['c5bwrites']==1 and fault=='c'+str(i)+'-after-c5b-read':value^=1
   if i==3 and state['c3writes']==1 and fault=='c3-read':value^=1''')
rep('addr+size<=op+572','addr+size<=op+612');rep("'<143I'","'<153I'");rep('0x533c,0x6000','0x5364,0x6000')
rep("    assert struct.unpack('<I',uc.mem_read(op+552,4))[0]==0", "    assert struct.unpack('<I',uc.mem_read(op+592,4))[0]==0\n    assert struct.unpack('<I',uc.mem_read(op+552,4))[0]==0")
rep("([(3,0x80),(3,0x8c)] if state['c3writes'] else [])", "([(3,0x80)]+([(5,0xbe),(5,0x3e)] if state['c5bwrites'] else [])+[(3,0x8c)] if state['c3writes'] else [])")
rep('  else:assert v[100:102]==[0,1]', "  elif fault in ['c5b-undo-read','c5b-drop-undo']:assert sw==[0x21] and outs==[5] and v[148]==1 and v[101]==0\n  else:assert v[100:102]==[0,1]")
rep('(v[1] in [0x757,0x757d,0x757e,0x75710,0x75712])','(v[1] in [0x757,0x757d,0x757e,0x75710,0x75712,0x75714])')
rep(' for lo,hi in [(0,0x880)', ''' if state['c5bwrites']:
  assert state['c5bwrites']==2 and v[143:146]==[0x3e,0xbe,1]
  assert v[146]==(0x3e if fault in ['c5b-drop-write','c5b-high-read'] else 0xbf if fault in ['c5b-read','c5b-wrong-write'] else 0xbe)
  assert v[147]==(0xbe if fault=='c5b-drop-undo' else 0x3f if fault=='c5b-undo-read' else 0x3e)
  assert v[148]==int(v[147]!=v[143])
  for idx,n,target in [(0,149,0x5c),(2,150,0x59),(3,151,0x80),(4,152,93)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c5b-read','c5b-c'+str(idx)+'-coupling'] else target)
 for lo,hi in [(0,0x880)''')
rep('v[138],v[133],v[136],v[137],v[28]', 'v[138],v[148],v[143],v[146],v[147]')
faults="['c5b-read','c5b-high-read','c5b-drop-write','c5b-wrong-write']+['c'+str(i)+'-after-c5b-read' for i in [0,2,3,4]]+['c5b-c'+str(i)+'-coupling' for i in [0,2,3,4]]+['c5b-undo-read','c5b-drop-undo']"
rep(" for n in range(7):\n  run('horizontal", " for fault in "+faults+":run(fault,want=0x75715 if fault in ['c5b-undo-read','c5b-drop-undo'] else 0x75714,fault=fault)\n for n in range(7):\n  run('horizontal")
p.write_text(s,newline='\n')

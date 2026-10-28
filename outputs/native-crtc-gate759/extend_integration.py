"""Fresh relocated native CR17 access and recovery contracts."""
from pathlib import Path
p=Path(__file__).resolve().parent/'integration004.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep("state={'c5bwrites':0,","state={'c17writes':0,'c5bwrites':0,")
rep("    if i==5 and struct.unpack",'''    if i==0x17 and struct.unpack('<I',uc.mem_read(op+620,4))[0]:
     state['c17writes']+=1;n=state['c17writes'];assert n<=2 and value==(0x63 if n==1 else 0xe3)
     assert state['seq']==0x21 and state['gate']==5 and not hrestore and state['c5bwrites']==1
     assert all(state['c'+str(i2)+'writes']==1 for i2 in [0,2,3,4,5])
     assert struct.unpack('<3I',uc.mem_read(op+612,12))==(0xe3,0x63,1)
     if fault==('c17-drop-write' if n==1 else 'c17-drop-undo'):return
     cr[0x17]=value
     if n==1 and fault=='c17-wrong-write':cr[0x17]^=1
     for idx2 in [0,2,3,4,5]:
      if n==1 and fault=='c17-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==5 and struct.unpack''')
rep("state['c5bwrites']+=1;n=state['c5bwrites'];assert", "state['c5bwrites']+=1;n=state['c5bwrites'];assert state['c17writes']==2*struct.unpack('<I',uc.mem_read(op+620,4))[0]\n     assert")
rep("   if i==5 and state['c5bwrites']==1 and fault=='c5b-read':value^=1",'''   if i==0x17 and not state['recovering'] and struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x75916 and not struct.unpack('<I',uc.mem_read(op+620,4))[0] and fault=='c17-before-read':value^=1
   if i==0x17 and state['c17writes']==1 and fault=='c17-read':value^=1
   if i==0x17 and state['c17writes']==1 and fault=='c17-high-read':value^=0x80
   if i==0x17 and state['c17writes']==2 and state['c5bwrites']==1 and fault=='c17-undo-read':value^=1
   if i in [0,2,3,4,5] and state['c17writes']==1 and fault=='c'+str(i)+'-after-c17-read':value^=1
   if i==5 and state['c5bwrites']==1 and fault=='c5b-read':value^=1''')
rep('addr+size<=op+612','addr+size<=op+656');rep("'<153I'","'<164I'");rep('0x5364,0x6000','0x5390,0x6000')
rep("    assert struct.unpack('<I',uc.mem_read(op+592,4))[0]==0", "    assert struct.unpack('<I',uc.mem_read(op+632,4))[0]==0 and cr[0x17]==0xe3\n    assert struct.unpack('<I',uc.mem_read(op+592,4))[0]==0")
rep("([(5,0xbe),(5,0x3e)] if state['c5bwrites'] else [])", "([(5,0xbe)]+([(0x17,0x63),(0x17,0xe3)] if state['c17writes'] else [])+[(5,0x3e)] if state['c5bwrites'] else [])")
rep('  else:assert v[100:102]==[0,1]',"  elif fault in ['c17-undo-read','c17-drop-undo']:assert sw==[0x21] and outs==[5] and v[158]==1 and v[101]==0\n  else:assert v[100:102]==[0,1]")
rep('0x75912,0x75914])','0x75912,0x75914,0x75916])')
rep(' for lo,hi in [(0,0x880)', ''' if v[1] in [0x759,0x75916] and not refusal and want!=5:
  assert v[153]==(0xe2 if fault=='c17-before-read' else 0xe3)
  assert v[155]==int(fault!='c17-before-read') and state['c17writes']==2*v[155]
  if v[155]:
   assert v[154]==0x63
   assert v[156]==(0xe3 if fault in ['c17-drop-write','c17-high-read'] else 0x62 if fault in ['c17-read','c17-wrong-write'] else 0x63)
   assert v[157]==(0x63 if fault=='c17-drop-undo' else 0xe2 if fault=='c17-undo-read' else 0xe3)
   assert v[158]==int(v[157]!=v[153])
   for idx,n,target in [(0,159,0x5c),(2,160,0x59),(3,161,0x80),(4,162,93),(5,163,0xbe)]:
    assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c17-read','c17-c'+str(idx)+'-coupling'] else target)
 for lo,hi in [(0,0x880)''')
rep('0 if refusal else want,v[1],v[30],v[100],v[108],v[121],v[129],v[138],v[148],v[143],v[146],v[147]', '0 if refusal else want,v[30],v[100],v[108],v[121],v[129],v[138],v[148],v[158],v[153],v[156],v[157]')
faults="['c17-before-read','c17-read','c17-high-read','c17-drop-write','c17-wrong-write']+['c'+str(i)+'-after-c17-read' for i in [0,2,3,4,5]]+['c17-c'+str(i)+'-coupling' for i in [0,2,3,4,5]]+['c17-undo-read','c17-drop-undo']"
rep(" for n in range(7):\n  run('horizontal", " for fault in "+faults+":run(fault,want=0x75917 if fault in ['c17-undo-read','c17-drop-undo'] else 0x75916,fault=fault)\n for n in range(7):\n  run('horizontal")
p.write_text(s,newline='\n')

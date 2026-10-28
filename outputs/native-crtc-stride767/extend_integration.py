"""Independent relocated CR19 high-stride faults and pre-enable recovery checks."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration004.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
rep("state={'c17bwrites':0","state={'c19bwrites':0,'c17bwrites':0")
rep('    if i==0x17 and struct.unpack', '''    if i==0x19 and struct.unpack('<I',uc.mem_read(op+808,4))[0] and state['c19bwrites']<2:
     state['c19bwrites']+=1;n=state['c19bwrites'];assert n<=2 and value==(0x30 if n==1 else 0x10)
     assert state['seq']==0x21 and state['gate']==5 and not hrestore and state['c17bwrites']==1
     assert struct.unpack('<3I',uc.mem_read(op+800,12))==(0x10,0x30,1)
     assert struct.unpack('<I',uc.mem_read(op+824,4))[0]==0x80
     if fault==('c19b-drop-write' if n==1 else 'c19b-drop-undo'):return
     cr[0x19]=value
     if n==1 and fault=='c19b-wrong-write':cr[0x19]^=1
     for idx2 in [0,1,2,3,4,5,0x13,0x17]:
      if n==1 and fault=='c19b-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==0x17 and struct.unpack''')
rep("state['c17bwrites']+=1;n=state['c17bwrites'];assert", "state['c17bwrites']+=1;n=state['c17bwrites'];assert state['c19bwrites']==2*struct.unpack('<I',uc.mem_read(op+808,4))[0];assert")
rep('   i=sels[0x6013d4]\n', '''   i=sels[0x6013d4]
   if struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x7671e and not struct.unpack('<I',uc.mem_read(op+808,4))[0] and state['c17bwrites']==1:
    if i==0x19 and fault=='c19b-before-read':value^=1
    if i==0x13 and fault=='c13-before-c19b-read':value^=1
   if i==0x19 and state['c19bwrites']==1 and fault=='c19b-read':value^=1
   if i==0x19 and state['c19bwrites']==1 and fault=='c19b-high-read':value^=0x20
   if i==0x19 and state['c19bwrites']==2 and state['c17bwrites']==1 and fault=='c19b-undo-read':value^=1
   if i==0x13 and state['c19bwrites']==2 and state['c17bwrites']==1 and fault=='c13-undo-c19b-read':value^=1
   if i in [0,1,2,3,4,5,0x13,0x17] and state['c19bwrites']==1 and fault=='c'+str(i)+'-after-c19b-read':value^=1
''')
rep('   if value==4:\n', "   if value==4:\n    assert struct.unpack('<I',uc.mem_read(op+820,4))[0]==0\n")
rep('addr+size<=op+800','addr+size<=op+864');rep("'<200I'","'<216I'")
rep('[(0x17,0xe3),(0x17,0x63)] if state', "[(0x17,0xe3)]+([(0x19,0x30),(0x19,0x10)] if state['c19bwrites'] else [])+[(0x17,0x63)] if state")
rep('  else:assert v[100:102]==[0,1]', "  elif fault in ['c19b-undo-read','c19b-drop-undo','c19b-c19-coupling','c13-undo-c19b-read']:assert sw==[0x21] and outs==[5] and v[205]!=0 and v[101]==0\n  else:assert v[100:102]==[0,1]")
rep('0x7671c]','0x7671c,0x7671e]')
rep(' for lo,hi in [(0,0x880)', ''' if state['c19bwrites']:
  assert state['c19bwrites']==2 and v[200:203]==[0x10,0x30,1]
  assert v[203]==(0x10 if fault in ['c19b-drop-write','c19b-high-read'] else 0x31 if fault in ['c19b-read','c19b-wrong-write'] else 0x30)
  assert v[204]==(0x30 if fault=='c19b-drop-undo' else 0x11 if fault=='c19b-undo-read' else 0x10)
  assert v[206]==128 and v[215]==(129 if fault in ['c19b-c19-coupling','c13-undo-c19b-read'] else 128)
  assert v[205]==int(v[204]!=v[200])+2*int(v[215]!=v[206])
  for idx,n,target in [(0x13,207,128),(0x17,208,227),(0,209,92),(1,210,89),(2,211,89),(3,212,128),(4,213,93),(5,214,190)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c19b-read','c19b-c'+str(idx)+'-coupling'] else target)
 elif fault in ['c19b-before-read','c13-before-c19b-read']:
  assert v[200]==(17 if fault=='c19b-before-read' else 16) and v[206]==(129 if fault=='c13-before-c19b-read' else 128)
  assert v[201:206]==[0,0,0xffffffff,0xffffffff,0] and v[207:216]==[0xffffffff]*9
 else:assert v[200:216]==([0]*16 if refusal or want<0x767 else [0,0,0,0xffffffff,0xffffffff,0,0]+[0xffffffff]*9)
 for lo,hi in [(0,0x880)''')
rep('(0x5420,0x6000)','(0x5460,0x6000)')
rep('v[169],v[181],v[193],v[188],v[191],v[192]','v[169],v[193],v[205],v[200],v[203],v[204]')
rep(' for n in range(7):', ''' for fault in ['c19b-before-read','c13-before-c19b-read','c19b-read','c19b-high-read','c19b-drop-write','c19b-wrong-write']+['c'+str(i)+'-after-c19b-read' for i in [0,1,2,3,4,5,0x13,0x17]]+['c19b-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5,0x13,0x17]]+['c19b-undo-read','c19b-drop-undo','c13-undo-c19b-read']:
  run(fault,want=0x7671f if fault in ['c19b-undo-read','c19b-drop-undo','c19b-c19-coupling','c13-undo-c19b-read'] else 0x7671e,fault=fault)
 for n in range(7):''')
p.write_text(s,newline='\n')

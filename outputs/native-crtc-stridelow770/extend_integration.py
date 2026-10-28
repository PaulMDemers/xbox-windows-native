"""Add independent relocated CR13 faults, ordering, recovery, and optical checks."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration004.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
rep("state={'c19bwrites':0","state={'c13writes':0,'c19bwrites':0")
rep('    if i==0x19 and struct.unpack', '''    if i==0x13:
     state['c13writes']+=1;n=state['c13writes'];assert n<=2 and value==(0x68 if n==1 else 0x80)
     assert state['seq']==0x21 and state['gate']==5 and not hrestore and state['c19bwrites']==1
     assert struct.unpack('<3I',uc.mem_read(op+864,12))==(0x80,0x68,1)
     assert struct.unpack('<I',uc.mem_read(op+888,4))[0]==0x30
     if fault==('c13-drop-write' if n==1 else 'c13-drop-undo'):return
     cr[0x13]=value
     if n==1 and fault=='c13-wrong-write':cr[0x13]^=1
     for idx2 in [0,1,2,3,4,5,0x19,0x17]:
      if n==1 and fault=='c13-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==0x19 and struct.unpack''')
rep("state['c19bwrites']+=1;n=state['c19bwrites'];assert", "state['c19bwrites']+=1;n=state['c19bwrites'];assert state['c13writes']==2*struct.unpack('<I',uc.mem_read(op+872,4))[0];assert")
rep('   i=sels[0x6013d4]\n', '''   i=sels[0x6013d4]
   if struct.unpack('<I',uc.mem_read(op+4,4))[0]==0x77020 and not struct.unpack('<I',uc.mem_read(op+872,4))[0] and state['c19bwrites']==1:
    if i==0x13 and fault=='c13-before-read':value^=1
    if i==0x19 and fault=='c19-before-c13-read':value^=1
   if i==0x13 and state['c13writes']==1 and fault=='c13-read':value^=1
   if i==0x13 and state['c13writes']==1 and fault=='c13-high-read':value^=0x80
   if i==0x13 and state['c13writes']==2 and state['c19bwrites']==1 and fault=='c13-undo-read':value^=1
   if i==0x19 and state['c13writes']==2 and state['c19bwrites']==1 and fault=='c19-undo-c13-read':value^=1
   if i in [0,1,2,3,4,5,0x19,0x17] and state['c13writes']==1 and fault=='c'+str(i)+'-after-c13-read':value^=1
''')
rep('   if value==4:\n', "   if value==4:\n    assert struct.unpack('<I',uc.mem_read(op+884,4))[0]==0\n")
rep('addr+size<=op+864','addr+size<=op+928');rep("'<216I'","'<232I'")
rep("[(0x19,0x30),(0x19,0x10)] if state", "[(0x19,0x30)]+([(0x13,0x68),(0x13,0x80)] if state['c13writes'] else [])+[(0x19,0x10)] if state")
rep('  elif fault in [\'c19b-undo-read\'', "  elif fault in ['c13-undo-read','c13-drop-undo','c13-c25-coupling','c19-undo-c13-read']:assert sw==[0x21] and outs==[5] and v[221]!=0 and v[101]==0\n  elif fault in ['c19b-undo-read'")
rep('0x7701e]','0x7701e,0x77020]')
rep("v[215]==(129 if fault in", "v[215]==(104 if fault=='c13-drop-undo' else 129 if fault in")
rep(' for lo,hi in [(0,0x880)', ''' if state['c13writes']:
  assert state['c13writes']==2 and v[216:219]==[0x80,0x68,1]
  assert v[219]==(0x80 if fault=='c13-drop-write' else 0xe8 if fault=='c13-high-read' else 0x69 if fault in ['c13-read','c13-wrong-write'] else 0x68)
  assert v[220]==(0x68 if fault=='c13-drop-undo' else 0x81 if fault=='c13-undo-read' else 0x80)
  assert v[222]==48 and v[231]==(49 if fault in ['c13-c25-coupling','c19-undo-c13-read'] else 48)
  assert v[221]==int(v[220]!=v[216])+2*int(v[231]!=v[222])
  for idx,n,target in [(0x19,223,48),(0x17,224,227),(0,225,92),(1,226,89),(2,227,89),(3,228,128),(4,229,93),(5,230,190)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c13-read','c13-c'+str(idx)+'-coupling'] else target)
 elif fault in ['c13-before-read','c19-before-c13-read']:
  assert v[216]==(129 if fault=='c13-before-read' else 128) and v[222]==(49 if fault=='c19-before-c13-read' else 48)
  assert v[217:222]==[0,0,0xffffffff,0xffffffff,0] and v[223:232]==[0xffffffff]*9
 else:assert v[216:232]==([0]*16 if refusal or want<0x770 else [0,0,0,0xffffffff,0xffffffff,0,0]+[0xffffffff]*9)
 for lo,hi in [(0,0x880)''')
rep('(0x5460,0x6000)','(0x54a0,0x6000)')
rep('v[169],v[193],v[205],v[200],v[203],v[204]','v[169],v[205],v[221],v[216],v[219],v[220]')
rep(' for n in range(7):', ''' for fault in ['c13-before-read','c19-before-c13-read','c13-read','c13-high-read','c13-drop-write','c13-wrong-write']+['c'+str(i)+'-after-c13-read' for i in [0,1,2,3,4,5,0x19,0x17]]+['c13-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5,0x19,0x17]]+['c13-undo-read','c13-drop-undo','c19-undo-c13-read']:
  run(fault,want=0x77021 if fault in ['c13-undo-read','c13-drop-undo','c13-c25-coupling','c19-undo-c13-read'] else 0x77020,fault=fault)
 for n in range(7):''')
rep('json.dumps(R,indent=2)',"json.dumps(R,separators=(',',':'))")
p.write_text(s,newline='\n')

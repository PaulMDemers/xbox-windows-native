"""Add independent CR01 execution, recovery, neighbor and optical checks to761."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration004.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
rep('flags=2,cpu4=0):','flags=2,cpu4=0,c1_original=0x9f):')
rep("state={'c17writes':0", "state={'c1writes':0,'c17writes':0")
rep('cr={3:0x8c','cr={1:c1_original,3:0x8c')
rep("    if i==0x17 and struct.unpack('<I',uc.mem_read(op+620,4))[0]:", """    if i==1:
     state['c1writes']+=1;n=state['c1writes'];assert n<=2 and value==(0x59 if n==1 else c1_original)
     assert state['seq']==0x21 and state['gate']==5 and not hrestore and state['c17writes']==1
     assert state['c5bwrites']==1 and all(state['c'+str(i2)+'writes']==1 for i2 in [0,2,3,4,5])
     assert struct.unpack('<3I',uc.mem_read(op+656,12))==(c1_original,0x59,1)
     if fault==('c1-drop-write' if n==1 else 'c1-drop-undo'):return
     cr[1]=value
     if n==1 and fault=='c1-wrong-write':cr[1]^=1
     for idx2 in [0,2,3,4,5,0x17]:
      if n==1 and fault=='c1-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==0x17 and struct.unpack('<I',uc.mem_read(op+620,4))[0]:""")
rep("state['c17writes']+=1;n=state['c17writes'];assert n<=2", "state['c17writes']+=1;n=state['c17writes'];assert state['c1writes']==2*struct.unpack('<I',uc.mem_read(op+664,4))[0];assert n<=2")
rep("   i=sels[0x6013d4]\n", """   i=sels[0x6013d4]
   if i==1 and state['c1writes']==1 and fault=='c1-read':value^=1
   if i==1 and state['c1writes']==1 and fault=='c1-high-read':value^=0x80
   if i==1 and state['c1writes']==2 and state['c17writes']==1 and fault=='c1-undo-read':value^=1
   if i in [0,2,3,4,5,0x17] and state['c1writes']==1 and fault=='c'+str(i)+'-after-c1-read':value^=1
""")
rep('   if value==4:\n', "   if value==4:\n    assert struct.unpack('<I',uc.mem_read(op+676,4))[0]==0 and cr[1]==c1_original\n")
rep('addr+size<=op+656','addr+size<=op+704')
rep("'<164I'","'<176I'")
rep("([(0x17,0x63),(0x17,0xe3)] if state['c17writes'] else [])", "([(0x17,0x63)]+([(1,0x59),(1,c1_original)] if state['c1writes'] else [])+[(0x17,0xe3)] if state['c17writes'] else [])")
rep("  else:assert v[100:102]==[0,1]", "  elif fault in ['c1-undo-read','c1-drop-undo']:assert sw==[0x21] and outs==[5] and v[169]==1 and v[101]==0\n  else:assert v[100:102]==[0,1]")
rep('0x76114,0x76116]','0x76114,0x76116,0x76118]')
rep('[0x761,0x76116]','[0x761,0x76116,0x76118]')
rep(' for lo,hi in [(0,0x880)', """ if state['c1writes']:
  assert state['c1writes']==2 and v[164:167]==[c1_original,0x59,1]
  assert v[167]==(c1_original if fault=='c1-drop-write' else 0xd9 if fault=='c1-high-read' else 0x58 if fault in ['c1-read','c1-wrong-write'] else 0x59)
  assert v[168]==(0x59 if fault=='c1-drop-undo' else c1_original^1 if fault=='c1-undo-read' else c1_original)
  assert v[169]==int(v[168]!=v[164])
  for idx,n,target in [(0,170,0x5c),(2,171,0x59),(3,172,0x80),(4,173,93),(5,174,0xbe),(0x17,175,0x63)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c1-read','c1-c'+str(idx)+'-coupling'] else target)
 for lo,hi in [(0,0x880)""")
rep('(0x5390,0x6000)','(0x53c0,0x6000)')
rep('v[148],v[158],v[153],v[156],v[157]','v[158],v[169],v[164],v[167],v[168]')
rep(' for n in range(7):\n', """ for fault in ['c1-read','c1-high-read','c1-drop-write','c1-wrong-write']+['c'+str(i)+'-after-c1-read' for i in [0,2,3,4,5,0x17]]+['c1-c'+str(i)+'-coupling' for i in [0,2,3,4,5,0x17]]+['c1-undo-read','c1-drop-undo']:run(fault,want=0x76119 if fault in ['c1-undo-read','c1-drop-undo'] else 0x76118,fault=fault)
 for value in [0,255]:run('CR01-own-value-'+str(value),c1_original=value)
 for n in range(7):
""")
p.write_text(s,newline='\n')

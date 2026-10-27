"""Extend actual-COFF744 contracts with CR05 write and interaction cases."""
from pathlib import Path
p=Path(__file__).resolve().parent/'model.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep("state={'c4writes':0,", "state={'c5writes':0,'c4writes':0,")
rep('assert idx in [4,0x1f,0x14,0x17,0x19]', 'assert idx in [4,5,0x1f,0x14,0x17,0x19]')
rep('    if idx==4:', '''    if idx==5:
     state['c5writes']+=1;assert state['c5writes']<=2
     assert value==(0x3e if state['c5writes']==1 else 0x31)
     assert state['sq']==0x21 and ports==[5] and state['c4writes']==1 and not hr
     assert word(105)==93 and word(110)==0x31 and word(113)==1
     writes.append(['cr',5,value])
     if fault==('c5-drop-write' if state['c5writes']==1 else 'c5-drop-restore'):return
     cr[5]=value
     if state['c5writes']==1 and fault=='c4-coupling':cr[4]^=1
     return
    if idx==4:''')
rep("     state['c4writes']+=1;assert state['c4writes']<=2", "     state['c4writes']+=1;assert state['c4writes']<=2\n     if state['c4writes']==2:assert state['c5writes']==2*word(113)")
rep("   if idx==4 and state['c4writes']==1 and fault=='c4-read':val^=1", """   if idx==4 and state['c4writes']==1 and fault=='c4-read':val^=1
   if idx==4 and state['c5writes']==1 and fault=='c4-after-read':val^=1
   if idx==5 and state['c5writes']==1 and fault=='c5-low-read':val^=1
   if idx==5 and state['c5writes']==1 and fault=='c5-high-read':val^=0x80""")
rep('0x2011c0','0x2011d0');rep('0x5e40','0x5e30')
rep("'<112I',c.mem_read(0x201000,448)","'<116I',c.mem_read(0x201000,464)")
rep("'c5-restore-read','c5-coupling']", "'c5-restore-read','c5-coupling','c5-drop-restore']")
# Previous replacement also extends the existing case list with dropped CR05 restoration.
rep("else 0x746\n  assert v[1]", "else 0x746d if fault in ['c5-drop-write','c5-low-read','c5-high-read','c4-after-read','c4-coupling'] else 0x746\n  assert v[1]")
rep('[0x746,0x7468,0x7469,0x746b]', '[0x746,0x7468,0x7469,0x746b,0x746d]')
rep('[0x746,0x7469,0x746b]', '[0x746,0x7469,0x746b,0x746d]')
rep("if forward!=0x7469:expectedwrites += [['cr',4,93],['cr',4,0xa7]]", "if forward!=0x7469:\n    expectedwrites += [['cr',4,93]]\n    if forward!=0x746b:expectedwrites += [['cr',5,0x3e],['cr',5,0x31]]\n    expectedwrites += [['cr',4,0xa7]]")
rep("  assert v[111]==(0x30 if fault in ['c5-restore-read','c5-coupling','c5-drop-restore'] else 0x31)", "  assert v[111]==(0x3e if fault=='c5-drop-restore' else 0x30 if fault in ['c5-restore-read','c5-coupling'] else 0x31)")
rep("  else:assert v[105]==v[110]==0xffffffff", """  else:assert v[105]==v[110]==0xffffffff
  c5ran=cran and forward!=0x746b
  assert state['c5writes']==2*int(c5ran) and v[113]==int(c5ran)
  if c5ran:
   assert v[112]==0x3e
   assert v[114]==(0x31 if fault=='c5-drop-write' else 0x3f if fault=='c5-low-read' else 0xbe if fault=='c5-high-read' else 0x3e)
   assert v[115]==(92 if fault in ['c4-after-read','c4-coupling'] else 93)
  else:assert v[112:116]==[0,0,0xffffffff,0xffffffff]""")
rep(" for n in range(7):\n  run('horizontal", " for fault in ['c5-drop-write','c5-low-read','c5-high-read','c4-after-read','c4-coupling']:run(fault,fault=fault)\n for n in range(7):\n  run('horizontal")
p.write_text(s,newline='\n')
print('Extended746 model; retained prefix/CR04 faults and CR05 forward/restoration/interaction faults')

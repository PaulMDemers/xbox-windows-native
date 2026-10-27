"""Extend relocated integration for native747 CR05 and reverse recovery."""
from pathlib import Path
p=Path(__file__).resolve().parent/'integration004.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep("state={'c4writes':0,", "state={'c5writes':0,'c4writes':0,")
rep('    if i==4:', """    if i==5:
     state['c5writes']+=1;assert state['c5writes']<=2
     assert value==(0x3e if state['c5writes']==1 else 0x31)
     assert state['seq']==0x21 and state['gate']==5 and state['c4writes']==1 and not hrestore
     assert struct.unpack('<I',uc.mem_read(op+452,4))[0]==1
     if fault==('c5-drop-write' if state['c5writes']==1 else 'c5-drop-restore'):return
     cr[5]=value
     if state['c5writes']==1 and fault=='c4-coupling':cr[4]^=1
    elif i==4:""")
rep("     state['c4writes']+=1;assert state['c4writes']<=2", "     state['c4writes']+=1;assert state['c4writes']<=2\n     if state['c4writes']==2:assert state['c5writes']==2*struct.unpack('<I',uc.mem_read(op+452,4))[0]")
rep("   if i==4 and state['c4writes']==1 and fault=='c4-read':value^=1", """   if i==4 and state['c4writes']==1 and fault=='c4-read':value^=1
   if i==4 and state['c5writes']==1 and fault=='c4-after-read':value^=1
   if i==5 and state['c5writes']==1 and fault=='c5-low-read':value^=1
   if i==5 and state['c5writes']==1 and fault=='c5-high-read':value^=0x80""")
rep('addr+size<=op+448','addr+size<=op+464');rep("'<112I'","'<116I'");rep('0x52c0,0x6000','0x52d0,0x6000')
rep("([(4,93),(4,0xa7)] if state['c4writes'] else [])", "([(4,93)]+([(5,0x3e),(5,0x31)] if state['c5writes'] else [])+[(4,0xa7)] if state['c4writes'] else [])")
rep("'c5-restore-read','c5-coupling']", "'c5-restore-read','c5-coupling','c5-drop-restore']")
rep("  assert v[111]==(0x30 if fault in ['c5-restore-read','c5-coupling','c5-drop-restore'] else 0x31)", "  assert v[111]==(0x3e if fault=='c5-drop-restore' else 0x30 if fault in ['c5-restore-read','c5-coupling'] else 0x31)")
rep("(v[1]==0x747)","(v[1] in [0x747,0x747d])")
rep(" for lo,hi in [(0,0x880)", """ if state['c5writes']:
  assert state['c5writes']==2 and v[112:114]==[0x3e,1]
  assert v[114]==(0x31 if fault=='c5-drop-write' else 0x3f if fault=='c5-low-read' else 0xbe if fault=='c5-high-read' else 0x3e)
  assert v[115]==(92 if fault in ['c4-after-read','c4-coupling'] else 93)
 elif v[107]:assert v[112:116]==[0,0,0xffffffff,0xffffffff]
 for lo,hi in [(0,0x880)""")
rep('v[104],v[105],v[106],v[28],v[11],v[12],v[13]', 'v[109],v[112],v[114],v[111],v[115],v[28],v[11]')
rep(" for n in range(7):\n  run('horizontal", " for fault in ['c5-drop-write','c5-low-read','c5-high-read','c4-after-read','c4-coupling']:run(fault,want=0x747d,fault=fault)\n for n in range(7):\n  run('horizontal")
p.write_text(s,newline='\n')
print('Extended747 integration; CR05 faults and optical values')

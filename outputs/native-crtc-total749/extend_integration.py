"""Extend relocated749 integration with CR00/neighbor/restore contracts."""
from pathlib import Path
p=Path(__file__).resolve().parent/'integration004.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep("state={'c5writes':0,", "state={'c0writes':0,'c5writes':0,")
rep('cr={4:0xa7','cr={0:0xc8,4:0xa7')
rep('    if i==5:', """    if i==0:
     state['c0writes']+=1;assert state['c0writes']<=2
     assert value==(0x5c if state['c0writes']==1 else 0xc8)
     assert state['seq']==0x21 and state['gate']==5 and state['c4writes']==1 and state['c5writes']==1 and not hrestore
     assert struct.unpack('<I',uc.mem_read(op+472,4))[0]==1 and not cr[0x11]&0x80
     if fault==('c0-drop-write' if state['c0writes']==1 else 'c0-drop-restore'):return
     cr[0]=value
     if state['c0writes']==1 and fault=='c0-c4-coupling':cr[4]^=1
     if state['c0writes']==1 and fault=='c0-c5-coupling':cr[5]^=1
    elif i==5:""")
rep("     state['c5writes']+=1;assert state['c5writes']<=2", "     state['c5writes']+=1;assert state['c5writes']<=2\n     if state['c5writes']==2:assert state['c0writes']==2*struct.unpack('<I',uc.mem_read(op+472,4))[0]")
rep("   if i==4 and state['c4writes']==1 and fault=='c4-read':value^=1", """   if i==0 and state['c0writes']==1 and fault=='c0-read':value^=1
   if i==0 and state['c0writes']==2 and fault=='c0-restore-read':value^=1
   if i==4 and state['c0writes']==1 and fault=='c4-after-c0-read':value^=1
   if i==5 and state['c0writes']==1 and fault=='c5-after-c0-read':value^=1
   if i==4 and state['c4writes']==1 and fault=='c4-read':value^=1""")
rep('addr+size<=op+464','addr+size<=op+496');rep("'<116I'","'<124I'");rep('0x52d0,0x6000','0x52f0,0x6000')
rep("    assert struct.unpack('<I',uc.mem_read(op+432,4))[0]==0", "    assert struct.unpack('<I',uc.mem_read(op+484,4))[0]==0 and cr[0]==0xc8\n    assert struct.unpack('<I',uc.mem_read(op+432,4))[0]==0")
rep("([(5,0x3e),(5,0x31)] if state['c5writes'] else [])", "([(5,0x3e)]+([(0,0x5c),(0,0xc8)] if state['c0writes'] else [])+[(5,0x31)] if state['c5writes'] else [])")
rep("  else:assert v[100:102]==[0,1]", "  elif fault in ['c0-restore-read','c0-drop-restore']:assert sw==[0x21] and outs==[5] and v[121]==1 and v[101]==0\n  else:assert v[100:102]==[0,1]")
rep('(v[1] in [0x749,0x749d])','(v[1] in [0x749,0x749d,0x749e])')
rep(' for lo,hi in [(0,0x880)', """ if state['c0writes']:
  assert state['c0writes']==2 and v[116:119]==[0xc8,92,1]
  assert v[119]==(0xc8 if fault=='c0-drop-write' else 0x5d if fault=='c0-read' else 0x5c)
  assert v[120]==(0xc9 if fault=='c0-restore-read' else 0x5c if fault=='c0-drop-restore' else 0xc8)
  assert v[121]==int(v[120]!=v[116])
  assert v[122]==(92 if fault in ['c4-after-c0-read','c0-c4-coupling'] else 93)
  assert v[123]==(0x3f if fault in ['c5-after-c0-read','c0-c5-coupling'] else 0x3e)
 for lo,hi in [(0,0x880)""")
rep('v[109],v[112],v[114],v[111],v[115],v[28],v[11]', 'v[121],v[116],v[119],v[120],v[28],v[11],v[123]')
rep(" for n in range(7):\n  run('horizontal", " run('CRTC-baseline-0',want=0x7492,nmm=0,ncr=0,cr_bad=(0,0))\n for fault in ['c0-read','c0-drop-write','c0-restore-read','c0-drop-restore','c4-after-c0-read','c5-after-c0-read','c0-c4-coupling','c0-c5-coupling']:run(fault,want=0x749f if fault in ['c0-restore-read','c0-drop-restore'] else 0x749e,fault=fault)\n for n in range(7):\n  run('horizontal")
p.write_text(s,newline='\n')
print('Extended749 integration with CR00')

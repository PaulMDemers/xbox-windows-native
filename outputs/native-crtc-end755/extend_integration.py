"""Extend relocated native integration with isolated CR03 and report bounds."""
from pathlib import Path
p=Path(__file__).resolve().parent/'integration004.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep("state={'c2writes':0,", "state={'c3writes':0,'c2writes':0,")
rep('cr={2:0x9f','cr={3:0x8c,2:0x9f')
rep('    if i==2:', '''    if i==3:
     state['c3writes']+=1;assert state['c3writes']<=2
     assert value==(0x80 if state['c3writes']==1 else 0x8c)
     assert state['seq']==0x21 and state['gate']==5 and all(state['c'+str(i2)+'writes']==1 for i2 in [0,2,4,5]) and not hrestore
     assert struct.unpack('<I',uc.mem_read(op+540,4))[0]==1 and not cr[0x11]&0x80
     if fault==('c3-drop-write' if state['c3writes']==1 else 'c3-drop-restore'):return
     cr[3]=value
     for idx2 in [0,2,4,5]:
      if state['c3writes']==1 and fault=='c3-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==2:''')
rep("     state['c2writes']+=1;assert state['c2writes']<=2", "     state['c2writes']+=1;assert state['c2writes']<=2\n     if state['c2writes']==2:assert state['c3writes']==2*struct.unpack('<I',uc.mem_read(op+540,4))[0]")
rep("   if i==2 and state['c2writes']==1 and fault=='c2-read':value^=1", '''   if i==3 and state['c3writes']==1 and fault=='c3-read':value^=1
   if i==3 and state['c3writes']==1 and fault=='c3-high-read':value^=0x80
   if i==3 and state['c3writes']==2 and fault=='c3-restore-read':value^=1
   if i in [0,2,4,5] and state['c3writes']==1 and fault=='c'+str(i)+'-after-c3-read':value^=1
   if i==2 and state['c2writes']==1 and fault=='c2-read':value^=1''')
rep('addr+size<=op+532','addr+size<=op+572');rep("'<133I'","'<143I'");rep('0x5314,0x6000','0x533c,0x6000')
rep("    assert struct.unpack('<I',uc.mem_read(op+516,4))[0]==0", "    assert struct.unpack('<I',uc.mem_read(op+552,4))[0]==0 and cr[3]==0x8c\n    assert struct.unpack('<I',uc.mem_read(op+516,4))[0]==0")
rep("([(2,0x59),(2,0x9f)] if state['c2writes'] else [])", "([(2,0x59)]+([(3,0x80),(3,0x8c)] if state['c3writes'] else [])+[(2,0x9f)] if state['c2writes'] else [])")
rep('  else:assert v[100:102]==[0,1]', "  elif fault in ['c3-restore-read','c3-drop-restore']:assert sw==[0x21] and outs==[5] and v[138]==1 and v[101]==0\n  else:assert v[100:102]==[0,1]")
rep('(v[1] in [0x755,0x755d,0x755e,0x75510])','(v[1] in [0x755,0x755d,0x755e,0x75510,0x75512])')
rep(' for lo,hi in [(0,0x880)', ''' if state['c3writes']:
  assert state['c3writes']==2 and v[133:136]==[0x8c,0x80,1]
  assert v[136]==(0x8c if fault=='c3-drop-write' else 0x81 if fault=='c3-read' else 0 if fault=='c3-high-read' else 0x80)
  assert v[137]==(0x8d if fault=='c3-restore-read' else 0x80 if fault=='c3-drop-restore' else 0x8c)
  assert v[138]==int(v[137]!=v[133])
  for idx,n,target in [(0,139,0x5c),(2,140,0x59),(4,141,93),(5,142,0x3e)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c3-read','c3-c'+str(idx)+'-coupling'] else target)
 for lo,hi in [(0,0x880)''')
rep('v[129],v[124],v[127],v[128],v[28],v[11]', 'v[129],v[138],v[133],v[136],v[137],v[28]')
rep(" for n in range(7):\n  run('horizontal", " run('CRTC-baseline-3',want=0x7552,nmm=0,ncr=0,cr_bad=(3,0))\n for fault in ['c3-read','c3-high-read','c3-drop-write','c3-restore-read','c3-drop-restore']+['c'+str(i)+'-after-c3-read' for i in [0,2,4,5]]+['c3-c'+str(i)+'-coupling' for i in [0,2,4,5]]:run(fault,want=0x75513 if fault in ['c3-restore-read','c3-drop-restore'] else 0x75512,fault=fault)\n for n in range(7):\n  run('horizontal")
p.write_text(s,newline='\n')

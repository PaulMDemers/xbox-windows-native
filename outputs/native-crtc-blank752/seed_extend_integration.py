"""Extend752 relocated integration with CR02 and expanded guarded result extent."""
from pathlib import Path
p=Path(__file__).resolve().parent/'integration004.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep("state={'c0writes':0,", "state={'c2writes':0,'c0writes':0,")
rep('cr={0:0xc8','cr={2:0x9f,0:0xc8')
rep('    if i==0:', '''    if i==2:
     state['c2writes']+=1;assert state['c2writes']<=2
     assert value==(0x59 if state['c2writes']==1 else 0x9f)
     assert state['seq']==0x21 and state['gate']==5 and state['c4writes']==1 and state['c5writes']==1 and state['c0writes']==1 and not hrestore
     assert struct.unpack('<I',uc.mem_read(op+504,4))[0]==1 and not cr[0x11]&0x80
     if fault==('c2-drop-write' if state['c2writes']==1 else 'c2-drop-restore'):return
     cr[2]=value
     for idx2 in [0,4,5]:
      if state['c2writes']==1 and fault=='c2-c'+str(idx2)+'-coupling':cr[idx2]^=1
    elif i==0:''')
rep("     state['c0writes']+=1;assert state['c0writes']<=2", "     state['c0writes']+=1;assert state['c0writes']<=2\n     if state['c0writes']==2:assert state['c2writes']==2*struct.unpack('<I',uc.mem_read(op+504,4))[0]")
rep("   if i==0 and state['c0writes']==1 and fault=='c0-read':value^=1", '''   if i==2 and state['c2writes']==1 and fault=='c2-read':value^=1
   if i==2 and state['c2writes']==2 and fault=='c2-restore-read':value^=1
   if i in [0,4,5] and state['c2writes']==1 and fault=='c'+str(i)+'-after-c2-read':value^=1
   if i==0 and state['c0writes']==1 and fault=='c0-read':value^=1''')
rep('addr+size<=op+496','addr+size<=op+532');rep("'<124I'","'<133I'");rep('0x52f0,0x6000','0x5314,0x6000')
rep("    assert struct.unpack('<I',uc.mem_read(op+484,4))[0]==0", "    assert struct.unpack('<I',uc.mem_read(op+516,4))[0]==0 and cr[2]==0x9f\n    assert struct.unpack('<I',uc.mem_read(op+484,4))[0]==0")
rep("([(0,0x5c),(0,0xc8)] if state['c0writes'] else [])", "([(0,0x5c)]+([(2,0x59),(2,0x9f)] if state['c2writes'] else [])+[(0,0xc8)] if state['c0writes'] else [])")
rep('  else:assert v[100:102]==[0,1]', "  elif fault in ['c2-restore-read','c2-drop-restore']:assert sw==[0x21] and outs==[5] and v[129]==1 and v[101]==0\n  else:assert v[100:102]==[0,1]")
rep('(v[1] in [0x752,0x752d,0x752e])','(v[1] in [0x752,0x752d,0x752e,0x75210])')
rep(' for lo,hi in [(0,0x880)', ''' if state['c2writes']:
  assert state['c2writes']==2 and v[124:127]==[0x9f,89,1]
  assert v[127]==(0x9f if fault=='c2-drop-write' else 0x58 if fault=='c2-read' else 0x59)
  assert v[128]==(0x9e if fault=='c2-restore-read' else 0x59 if fault=='c2-drop-restore' else 0x9f)
  assert v[129]==int(v[128]!=v[124])
  for idx,n,target in [(0,130,0x5c),(4,131,93),(5,132,0x3e)]:
   assert v[n]==(target^1 if fault in ['c'+str(idx)+'-after-c2-read','c2-c'+str(idx)+'-coupling'] else target)
 for lo,hi in [(0,0x880)''')
rep('v[121],v[116],v[119],v[120],v[28],v[11],v[123]', 'v[121],v[129],v[124],v[127],v[128],v[28],v[11]')
rep(" for n in range(7):\n  run('horizontal", " run('CRTC-baseline-2',want=0x7522,nmm=0,ncr=0,cr_bad=(2,0))\n for fault in ['c2-read','c2-drop-write','c2-restore-read','c2-drop-restore','c0-after-c2-read','c4-after-c2-read','c5-after-c2-read','c2-c0-coupling','c2-c4-coupling','c2-c5-coupling']:run(fault,want=0x75211 if fault in ['c2-restore-read','c2-drop-restore'] else 0x75210,fault=fault)\n for n in range(7):\n  run('horizontal")
p.write_text(s,newline='\n')
print('Extended752 integration and guarded result extent')

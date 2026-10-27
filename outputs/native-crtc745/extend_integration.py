"""Add independent CR04 contracts to relocated745 image tests."""
from pathlib import Path
p=Path(__file__).resolve().parent/'integration004.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep("state={'selector':", "state={'c4writes':0,'selector':")
rep(' cr={9:0x25,', ' cr={4:0xa7,5:0x31,9:0x25,')
rep("    if i==0x1f:", """    if i==4:
     state['c4writes']+=1;assert state['c4writes']<=2
     assert value==(93 if state['c4writes']==1 else 0xa7)
     assert state['seq']==0x21 and state['gate']==5 and state['ncr']==3 and not hrestore
     assert list(struct.unpack('<3I',uc.mem_read(op+388,12)))==[7,7,0xffffffff]
     if fault==('c4-write' if state['c4writes']==1 else 'c4-restore-write'):return
     cr[4]=value
     if state['c4writes']==1 and fault=='c5-coupling':cr[5]^=1
    elif i==0x1f:""")
rep("   if fault=='unlock11'", """   i=sels[0x6013d4]
   if i==4 and state['c4writes']==1 and fault=='c4-read':value^=1
   if i==4 and state['c4writes']==2 and fault=='c4-restore-read':value^=1
   if i==5 and state['c4writes']==1 and fault=='c5-read':value^=1
   if i==5 and state['c4writes']==2 and fault=='c5-restore-read':value^=1
   if fault=='unlock11'""")
rep("    assert struct.unpack('<I',uc.mem_read(op+400,4))[0]==0", "    assert struct.unpack('<I',uc.mem_read(op+432,4))[0]==0 and cr[4]==0xa7 and cr[5]==0x31\n    assert struct.unpack('<I',uc.mem_read(op+400,4))[0]==0")
rep('op+416','op+448');rep("'<104I'","'<112I'");rep('0x52a0,0x6000','0x52c0,0x6000')
rep("+CS[:ncr]+([(0x19,0x51)]", "+CS[:ncr]+([(4,93),(4,0xa7)] if state['c4writes'] else [])+([(0x19,0x51)]")
rep("  else:assert v[100:102]==[0,1]", "  elif fault in ['c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling']:assert sw==[0x21] and outs==[5] and v[108]!=0 and v[101]==0\n  else:assert v[100:102]==[0,1]")
rep(" for lo,hi in [(0,0x880)", """ if state['c4writes']:
  assert state['c4writes']==2 and v[104]==0xa7 and v[107]==1 and v[109]==0x31
  assert v[105]==(92 if fault=='c4-read' else 0xa7 if fault=='c4-write' else 93)
  assert v[106]==(0xa6 if fault=='c4-restore-read' else 93 if fault=='c4-restore-write' else 0xa7)
  assert v[110]==(0x30 if fault in ['c5-read','c5-coupling'] else 0x31)
  assert v[111]==(0x30 if fault in ['c5-restore-read','c5-coupling'] else 0x31)
  assert v[108]==int(v[104]!=v[106])+2*int(v[109]!=v[111])
  assert (v[105]==93 and v[110]==0x31)==(v[1]==0x745)
 for lo,hi in [(0,0x880)""")
rep('words=[0x7450000d,phase,0 if refusal else want,v[1],v[4],v[99],v[30],v[100],v[28],v[11],v[12],v[13],v[98]]', 'words=[0x7450000d,0 if refusal else want,v[1],v[30],v[100],v[108],v[104],v[105],v[106],v[28],v[11],v[12],v[13]]')
rep(" for n in range(7):\n  run('horizontal", " for a in [4,5]:run('CRTC-baseline-'+str(a),want=0x7452,nmm=0,ncr=0,cr_bad=(a,0))\n for fault in ['c4-read','c4-write','c5-read','c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling']:\n  want=0x745b if fault in ['c4-read','c4-write','c5-read'] else 0x745c\n  run(fault,want=want,fault=fault)\n for n in range(7):\n  run('horizontal")
p.write_text(s,newline='\n')
print('Updated745 relocated integration expectations and nine CR04/CR05 cases')

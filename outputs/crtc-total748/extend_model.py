"""Extend748 model with CR00 and independent neighbor/recovery faults."""
from pathlib import Path
p=Path(__file__).resolve().parent/'model.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep('cr={4:0xa7','cr={0:0xc8,4:0xa7')
rep(" if baseline=='c4':", " if baseline=='c0':cr[0]^=1\n if baseline=='c4':")
rep("state={'c5writes':0,", "state={'c0writes':0,'c5writes':0,")
rep('assert idx in [4,5,','assert idx in [0,4,5,')
rep('    if idx==5:', """    if idx==0:
     state['c0writes']+=1;assert state['c0writes']<=2
     assert value==(0x5c if state['c0writes']==1 else 0xc8)
     assert state['sq']==0x21 and ports==[5] and state['c4writes']==1 and state['c5writes']==1 and not hr
     assert word(114)==0x3e and word(115)==93 and word(118)==1 and not cr[0x11]&0x80
     writes.append(['cr',0,value])
     if fault==('c0-drop-write' if state['c0writes']==1 else 'c0-drop-restore'):return
     cr[0]=value
     if state['c0writes']==1 and fault=='c0-c4-coupling':cr[4]^=1
     if state['c0writes']==1 and fault=='c0-c5-coupling':cr[5]^=1
     return
    if idx==5:""")
rep("     state['c5writes']+=1;assert state['c5writes']<=2", "     state['c5writes']+=1;assert state['c5writes']<=2\n     if state['c5writes']==2:assert state['c0writes']==2*word(118)")
rep("   if idx==4 and state['c4writes']==1 and fault=='c4-read':val^=1", """   if idx==0 and state['c0writes']==1 and fault=='c0-read':val^=1
   if idx==0 and state['c0writes']==2 and fault=='c0-restore-read':val^=1
   if idx==4 and state['c0writes']==1 and fault=='c4-after-c0-read':val^=1
   if idx==5 and state['c0writes']==1 and fault=='c5-after-c0-read':val^=1
   if idx==4 and state['c4writes']==1 and fault=='c4-read':val^=1""")
rep('0x2011d0','0x2011f0');rep('0x5e30','0x5e10')
rep("'<116I',c.mem_read(0x201000,464)","'<124I',c.mem_read(0x201000,496)")
rep('   assert word(108)==0', '   assert word(121)==0 and cr[0]==0xc8 and word(120)==0xc8\n   assert word(108)==0')
rep("  cbad=fault in", "  zbad=fault in ['c0-restore-read','c0-drop-restore']\n  cbad=fault in")
rep('hbad or cbad','hbad or cbad or zbad')
rep("else 0x748\n  assert v[1]", "else 0x748e if fault in ['c0-read','c0-drop-write','c4-after-c0-read','c5-after-c0-read','c0-c4-coupling','c0-c5-coupling'] else 0x748\n  assert v[1]")
rep('[0x748,0x7488,0x7489,0x748b,0x748d]', '[0x748,0x7488,0x7489,0x748b,0x748d,0x748e]')
rep('[0x748,0x7489,0x748b,0x748d]', '[0x748,0x7489,0x748b,0x748d,0x748e]')
rep("    if forward!=0x748b:expectedwrites += [['cr',5,0x3e],['cr',5,0x31]]", "    if forward!=0x748b:\n     expectedwrites += [['cr',5,0x3e]]\n     if forward!=0x748d:expectedwrites += [['cr',0,0x5c],['cr',0,0xc8]]\n     expectedwrites += [['cr',5,0x31]]")
rep("else 0x748c if cbad", "else 0x748f if zbad else 0x748c if cbad")
rep("  else:assert v[112:116]==[0,0,0xffffffff,0xffffffff]", """  else:assert v[112:116]==[0,0,0xffffffff,0xffffffff]
  c0ran=c5ran and forward!=0x748d
  assert v[116]==0xc8 and state['c0writes']==2*int(c0ran) and v[118]==int(c0ran)
  assert v[120]==(0xc9 if fault=='c0-restore-read' else 0x5c if fault=='c0-drop-restore' else 0xc8)
  assert v[121]==int(zbad)
  if c0ran:
   assert v[117]==0x5c
   assert v[119]==(0xc8 if fault=='c0-drop-write' else 0x5d if fault=='c0-read' else 0x5c)
   assert v[122]==(92 if fault in ['c4-after-c0-read','c0-c4-coupling'] else 93)
   assert v[123]==(0x3f if fault in ['c5-after-c0-read','c0-c5-coupling'] else 0x3e)
  else:assert v[117:120]==[0,0,0xffffffff] and v[122:124]==[0xffffffff]*2""")
rep(" for n in range(7):\n  run('horizontal", " run('crtc-baseline-c0',baseline='c0')\n for fault in ['c0-read','c0-drop-write','c0-restore-read','c0-drop-restore','c4-after-c0-read','c5-after-c0-read','c0-c4-coupling','c0-c5-coupling']:run(fault,fault=fault)\n for n in range(7):\n  run('horizontal")
p.write_text(s,newline='\n')
print('Extended748 CR00 model')

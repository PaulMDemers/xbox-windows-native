"""Extend source-only754 harness with separate second-write access/order fault checks."""
from pathlib import Path
k=Path(__file__).resolve().parent;p=k/'model.py';s=p.read_text()
s=s.replace("'c3writes':0","'c5bwrites':0,'c3writes':0")
at='''    if idx==3:
'''
new='''    if idx==5 and word(145) and state['c5bwrites']<2:
     state['c5bwrites']+=1;n=state['c5bwrites'];assert value==(0xbe if n==1 else 0x3e)
     assert state['sq']==0x21 and ports==[5] and not hr
     assert all(state['c'+str(i)+'writes']==1 for i in [0,2,3,4,5])
     assert word(136)==0x80 and word(142)==0x3e and word(143)==0x3e and word(144)==0xbe
     writes.append(['cr',5,value])
     if fault==('c5b-drop-write' if n==1 else 'c5b-drop-undo'):return
     cr[5]=value
     if n==1 and fault=='c5b-wrong-write':cr[5]^=1
     for idx2 in [0,2,3,4]:
      if n==1 and fault=='c5b-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
'''
assert at in s;s=s.replace(at,new+at)
s=s.replace("state['c3writes']+=1;assert state['c3writes']<=2","state['c3writes']+=1;assert state['c3writes']<=2\n     if state['c3writes']==2:assert state['c5bwrites']==2*word(145)")
at='''   val=cr[idx]
'''
s=s.replace(at,at+'''   if idx==5 and state['c5bwrites']==1 and fault=='c5b-read':val^=1
   if idx==5 and state['c5bwrites']==1 and fault=='c5b-high-read':val^=0x80
   if idx==5 and state['c5bwrites']==2 and state['c3writes']==1 and fault=='c5b-undo-read':val^=1
   if idx in [0,2,3,4] and state['c5bwrites']==1 and fault=='c'+str(idx)+'-after-c5b-read':val^=1
''')
s=s.replace('0x20123c','0x201264').replace('0x5dc4','0x5d9c').replace("'<143I'","'<153I'").replace('0x201000,572','0x201000,612')
s=s.replace("   assert word(138)==0", "   assert word(148)==0 and (not word(145) or word(147)==0x3e)\n   assert word(138)==0")
s=s.replace("  hbad=fault.startswith", "  nbad=fault in ['c5b-undo-read','c5b-drop-undo']\n  hbad=fault.startswith")
s=s.replace('hbad or cbad or zbad or bbad or ebad','hbad or cbad or zbad or bbad or ebad or nbad')
faults="['c5b-read','c5b-high-read','c5b-drop-write','c5b-wrong-write']+['c'+str(i)+'-after-c5b-read' for i in [0,2,3,4]]+['c5b-c'+str(i)+'-coupling' for i in [0,2,3,4]]"
s=s.replace('else 0x756\n  assert v[1]==forward', 'else 0x75614 if fault in '+faults+' else 0x756\n  assert v[1]==forward')
s=s.replace('0x75612]','0x75612,0x75614]')
s=s.replace("       if forward!=0x75610:expectedwrites += [['cr',3,0x80],['cr',3,0x8c]]", "       if forward!=0x75610:\n        expectedwrites += [['cr',3,0x80]]\n        if forward!=0x75612:expectedwrites += [['cr',5,0xbe],['cr',5,0x3e]]\n        expectedwrites += [['cr',3,0x8c]]")
s=s.replace('else 0x75613 if ebad','else 0x75615 if nbad else 0x75613 if ebad')
at=" R['cases'].append"
new='''  c5bran=c3ran and forward!=0x75612
  assert v[145]==int(c5bran) and state['c5bwrites']==2*int(c5bran)
  assert v[148]==int(nbad)
  if c5bran:
   assert v[143:146]==[0x3e,0xbe,1]
   assert v[146]==(0x3e if fault in ['c5b-drop-write','c5b-high-read'] else 0xbf if fault in ['c5b-read','c5b-wrong-write'] else 0xbe)
   assert v[147]==(0xbe if fault=='c5b-drop-undo' else 0x3f if fault=='c5b-undo-read' else 0x3e)
   for idx,n,expected in [(0,149,0x5c),(2,150,0x59),(3,151,0x80),(4,152,93)]:
    assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c5b-read','c5b-c'+str(idx)+'-coupling'] else expected)
  else:assert v[143:153]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
'''
assert at in s;s=s.replace(at,new+at)
s=s.replace(' for n in range(7):\n  run(', ' for fault in '+faults+"+['c5b-undo-read','c5b-drop-undo']:run(fault,fault=fault)\n for n in range(7):\n  run(")
p.write_text(s,newline='\n')
# Extend independent schema without importing probe/harness constants.
p=k/'audit_logic.py';s=p.read_text().replace('143-word','153-word').replace('len(v)==143','len(v)==153')
s=s.replace(' assert c3attempt in', ' c5bbefore,c5btarget,c5battempt,c5bafter,c5bundo,nm,c0afterb,c2afterb,c3afterb,c4afterb=v[143:153]\n assert c5battempt in [0,1] and nm in [0,1]\n assert c3attempt in')
s=s.replace('0x75612]','0x75612,0x75614]')
s=s.replace('and em==0','and em==0 and nm==0').replace('or bm or em:','or bm or em or nm:')
s=s.replace('else 0x75613 if em','else 0x75615 if nm else 0x75613 if em')
s=s.replace('(forward==0x756)','(forward in [0x756,0x75614])')
at=" return {'cr03':"
new=''' assert c5battempt==int(forward in [0x756,0x75614])
 if c5battempt:
  assert c5bbefore==c5after3==62 and c5btarget==((c5bbefore&127)|128)
  assert all(n<=255 for n in [c5bafter,c5bundo,c0afterb,c2afterb,c3afterb,c4afterb])
  assert nm==int(c5bundo!=c5bbefore)
  assert (c5bafter==190 and [c0afterb,c2afterb,c3afterb,c4afterb]==[92,89,128,93])==(forward==0x756)
 else:assert v[143:153]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
'''
s=s.replace(at,new+" return {'cr05_second':{'before':c5bbefore,'target':c5btarget,'attempted':c5battempt,'after':c5bafter,'intermediate_restored':c5bundo,'cleanup_mask':nm,'CR00_after':c0afterb,'CR02_after':c2afterb,'CR03_after':c3afterb,'CR04_after':c4afterb},'cr03':")
p.write_text(s,newline='\n')

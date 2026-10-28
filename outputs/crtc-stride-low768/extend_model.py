"""Independent access-order and fault oracle for CR13 after CR19."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
rep("state={'c19bwrites':0","state={'c13writes':0,'c19bwrites':0")
rep('assert idx in [1,3,2,0,4,5,0x1f,0x14,0x17,0x19]','assert idx in [1,3,2,0,4,5,0x13,0x1f,0x14,0x17,0x19]')
rep('    if idx==0x19 and word(202)', '''    if idx==0x13:
     state['c13writes']+=1;n=state['c13writes'];assert n<=2 and value==(0x68 if n==1 else 0x80)
     assert state['sq']==0x21 and ports==[5] and not hr and state['c19bwrites']==1 and state['c17bwrites']==1
     assert [word(216),word(217),word(218),word(222)]==[0x80,0x68,1,0x30]
     writes.append(['cr',idx,value])
     if fault==('c13-drop-write' if n==1 else 'c13-drop-undo'):return
     cr[idx]=value
     if n==1 and fault=='c13-wrong-write':cr[idx]^=1
     for idx2 in [0,1,2,3,4,5,0x19,0x17]:
      if n==1 and fault=='c13-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==0x19 and word(202)''')
rep("state['c19bwrites']+=1;n=state['c19bwrites'];assert", "state['c19bwrites']+=1;n=state['c19bwrites'];assert state['c13writes']==2*word(218)\n     assert")
rep('   val=cr[idx]\n', '''   val=cr[idx]
   if word(1)==0x76820 and not word(218) and state['c19bwrites']==1:
    if idx==0x13 and fault=='c13-before-read':val^=1
    if idx==0x19 and fault=='c19-before-c13-read':val^=1
   if idx==0x13 and state['c13writes']==1 and fault=='c13-read':val^=1
   if idx==0x13 and state['c13writes']==1 and fault=='c13-high-read':val^=0x80
   if idx==0x13 and state['c13writes']==2 and state['c19bwrites']==1 and fault=='c13-undo-read':val^=1
   if idx==0x19 and state['c13writes']==2 and state['c19bwrites']==1 and fault=='c19-undo-c13-read':val^=1
   if idx in [0,1,2,3,4,5,0x19,0x17] and state['c13writes']==1 and fault=='c'+str(idx)+'-after-c13-read':val^=1
''')
rep('0x201360','0x2013a0');rep('0x5ca0','0x5c60');rep("'<216I'","'<232I'");rep('0x201000,864','0x201000,928')
rep('   assert word(205)==0','   assert word(221)==0 and (not word(218) or (word(220)==word(216) and word(231)==word(222)))\n   assert word(205)==0')
rep('  tmask=',"  umask=(1 if fault in ['c13-undo-read','c13-drop-undo'] else 0)|(2 if fault in ['c13-c25-coupling','c19-undo-c13-read'] else 0)\n  ubad=bool(umask)\n  tmask=")
rep("['c19b-c19-coupling','c13-undo-c19b-read'] else 0)","['c19b-c19-coupling','c13-undo-c19b-read','c13-drop-undo'] else 0)")
rep('or sbad or tbad','or sbad or tbad or ubad')
faults="['c13-before-read','c19-before-c13-read','c13-read','c13-high-read','c13-drop-write','c13-wrong-write']+['c'+str(i)+'-after-c13-read' for i in [0,1,2,3,4,5,0x19,0x17]]+['c13-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5,0x19,0x17]]"
rep('else 0x768\n  assert v[1]==forward','else 0x76820 if fault in '+faults+' else 0x768\n  assert v[1]==forward')
rep('0x7681e]','0x7681e,0x76820]')
rep("             if forward!=0x7681c and fault not in ['c19b-before-read','c13-before-c19b-read']:expectedwrites += [['cr',0x19,0x30],['cr',0x19,0x10]]", "             if forward!=0x7681c and fault not in ['c19b-before-read','c13-before-c19b-read']:\n              expectedwrites += [['cr',0x19,0x30]]\n              if forward!=0x7681e and fault not in ['c13-before-read','c19-before-c13-read']:expectedwrites += [['cr',0x13,0x68],['cr',0x13,0x80]]\n              expectedwrites += [['cr',0x19,0x10]]")
rep('else 0x7681f if tbad','else 0x76821 if ubad else 0x7681f if tbad')
rep("assert v[215]==(0x81 if fault", "assert v[215]==(0x68 if fault=='c13-drop-undo' else 0x81 if fault")
new='''  c13ran=c19bran and forward!=0x7681e
  assert v[218]==int(c13ran and fault not in ['c13-before-read','c19-before-c13-read']) and state['c13writes']==2*v[218] and v[221]==umask
  if c13ran:
   assert v[216]==(0x81 if fault=='c13-before-read' else 0x80)
   assert v[222]==(0x31 if fault=='c19-before-c13-read' else 0x30)
   if v[218]:
    assert v[217]==0x68
    assert v[219]==(0x80 if fault=='c13-drop-write' else 0xe8 if fault=='c13-high-read' else 0x69 if fault in ['c13-read','c13-wrong-write'] else 0x68)
    assert v[220]==(0x68 if fault=='c13-drop-undo' else 0x81 if fault=='c13-undo-read' else 0x80)
    assert v[231]==(0x31 if fault in ['c13-c25-coupling','c19-undo-c13-read'] else 0x30)
    for idx,n,expected in [(0x19,223,0x30),(0x17,224,0xe3),(0,225,0x5c),(1,226,0x59),(2,227,0x59),(3,228,0x80),(4,229,93),(5,230,0xbe)]:
     assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c13-read','c13-c'+str(idx)+'-coupling'] else expected)
   else:assert v[217:222]==[0,0,0xffffffff,0xffffffff,0] and v[223:232]==[0xffffffff]*9
  else:assert v[216:232]==[0,0,0,0xffffffff,0xffffffff,0,0]+[0xffffffff]*9
'''
rep(" R['cases'].append",new+" R['cases'].append")
rep(' for n in range(7):\n  run(', ' for fault in '+faults+"+['c13-undo-read','c13-drop-undo','c19-undo-c13-read']:run(fault,fault=fault)\n for n in range(7):\n  run(")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('216-word','232-word').replace('len(v)==216','len(v)==232')
s=s.replace(' assert c19ba in',' c13before,c13target,c13attempt,c13after,c13undo,um,c19before13,c19after13,c17after13,c0after13,c1after13,c2after13,c3after13,c4after13,c5after13,c19undo13=v[216:232]\n assert c13attempt in [0,1] and um in [0,1,2,3]\n assert c19ba in')
s=s.replace('0x7681e]','0x7681e,0x76820]').replace('and tm==0','and tm==0 and um==0').replace('or sm or tm:','or sm or tm or um:').replace('else 0x7681f if tm','else 0x76821 if um else 0x7681f if tm')
s=s.replace('==(forward==0x768)','==(forward in [0x768,0x76820])')
new=''' if forward in [0x768,0x76820]:
  assert c13before<=255 and c19before13<=255 and c13attempt==int(c13before==c13v and c19before13==c19bv)
  if c13attempt:
   assert c13before==128 and c19before13==48 and c13target==104
   assert all(n<=255 for n in [c13after,c13undo,c19after13,c17after13,c0after13,c1after13,c2after13,c3after13,c4after13,c5after13,c19undo13])
   assert um==int(c13undo!=c13before)+2*int(c19undo13!=c19before13)
   assert (c13after==104 and [c19after13,c17after13,c0after13,c1after13,c2after13,c3after13,c4after13,c5after13]==[48,227,92,89,89,128,93,190])==(forward==0x768)
  else:assert v[217:222]==[0,0,0xffffffff,0xffffffff,0] and v[223:232]==[0xffffffff]*9
 else:assert v[216:232]==[0,0,0,0xffffffff,0xffffffff,0,0]+[0xffffffff]*9
'''
s=s.replace(" return {'cr19_second':",new+" return {'cr13':{'before':c13before,'target':c13target,'attempted':c13attempt,'after':c13after,'restored':c13undo,'cleanup_mask':um,'CR19_before_after_recovered':[c19before13,c19after13,c19undo13],'neighbors_after':[c17after13,c0after13,c1after13,c2after13,c3after13,c4after13,c5after13]},'cr19_second':")
p.write_text(s,newline='\n')

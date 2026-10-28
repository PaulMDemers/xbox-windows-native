"""Independent CR19 transaction access oracle, fault cases, and raw-result schema."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
rep('cr={1:c1_original','cr={0x13:0x80,1:c1_original')
rep("state={'c17bwrites':0","state={'c19bwrites':0,'c17bwrites':0")
rep('    if idx==0x17 and word(190)', '''    if idx==0x19 and word(202) and state['c19bwrites']<2:
     state['c19bwrites']+=1;n=state['c19bwrites'];assert n<=2 and value==(0x30 if n==1 else 0x10)
     assert state['sq']==0x21 and ports==[5] and not hr and state['c17bwrites']==1
     assert [word(200),word(201),word(202),word(206)]==[0x10,0x30,1,0x80]
     writes.append(['cr',idx,value])
     if fault==('c19b-drop-write' if n==1 else 'c19b-drop-undo'):return
     cr[idx]=value
     if n==1 and fault=='c19b-wrong-write':cr[idx]^=1
     for idx2 in [0,1,2,3,4,5,0x13,0x17]:
      if n==1 and fault=='c19b-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==0x17 and word(190)''')
rep("state['c17bwrites']+=1;n=state['c17bwrites'];assert", "state['c17bwrites']+=1;n=state['c17bwrites'];assert state['c19bwrites']==2*word(202)\n     assert")
rep('   val=cr[idx]\n', '''   val=cr[idx]
   if word(1)==0x7661e and not word(202):
    if idx==0x19 and fault=='c19b-before-read':val^=1
    if idx==0x13 and fault=='c13-before-c19b-read':val^=1
   if idx==0x19 and state['c19bwrites']==1 and fault=='c19b-read':val^=1
   if idx==0x19 and state['c19bwrites']==1 and fault=='c19b-high-read':val^=0x20
   if idx==0x19 and state['c19bwrites']==2 and state['c17bwrites']==1 and fault=='c19b-undo-read':val^=1
   if idx==0x13 and state['c19bwrites']==2 and state['c17bwrites']==1 and fault=='c13-undo-c19b-read':val^=1
   if idx in [0,1,2,3,4,5,0x13,0x17] and state['c19bwrites']==1 and fault=='c'+str(idx)+'-after-c19b-read':val^=1
''')
rep('0x201320','0x201360');rep('0x5ce0','0x5ca0');rep("'<200I'","'<216I'");rep('0x201000,800','0x201000,864')
rep('   assert word(193)==0','   assert word(205)==0 and (not word(202) or (word(204)==word(200) and word(215)==word(206)))\n   assert word(193)==0')
rep('  sbad=fault in',"  tmask=(1 if fault in ['c19b-undo-read','c19b-drop-undo'] else 0)|(2 if fault in ['c19b-c19-coupling','c13-undo-c19b-read'] else 0)\n  tbad=bool(tmask)\n  sbad=fault in")
rep('or rbad or sbad','or rbad or sbad or tbad')
faults="['c19b-before-read','c13-before-c19b-read','c19b-read','c19b-high-read','c19b-drop-write','c19b-wrong-write']+['c'+str(i)+'-after-c19b-read' for i in [0,1,2,3,4,5,0x13,0x17]]+['c19b-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5,0x13,0x17]]"
rep('else 0x766\n  assert v[1]==forward','else 0x7661e if fault in '+faults+' else 0x766\n  assert v[1]==forward')
rep('0x7661c]','0x7661c,0x7661e]')
rep("            if forward!=0x7661a and fault!='c17b-before-read':expectedwrites += [['cr',0x17,0xe3],['cr',0x17,0x63]]", "            if forward!=0x7661a and fault!='c17b-before-read':\n             expectedwrites += [['cr',0x17,0xe3]]\n             if forward!=0x7661c and fault not in ['c19b-before-read','c13-before-c19b-read']:expectedwrites += [['cr',0x19,0x30],['cr',0x19,0x10]]\n             expectedwrites += [['cr',0x17,0x63]]")
rep('else 0x7661d if sbad','else 0x7661f if tbad else 0x7661d if sbad')
new='''  c19bran=c17bran and forward!=0x7661c
  assert v[202]==int(c19bran and fault not in ['c19b-before-read','c13-before-c19b-read']) and state['c19bwrites']==2*v[202] and v[205]==tmask
  if c19bran:
   assert v[200]==(0x11 if fault=='c19b-before-read' else 0x10)
   assert v[206]==(0x81 if fault=='c13-before-c19b-read' else 0x80)
   if v[202]:
    assert v[201]==0x30
    assert v[203]==(0x10 if fault in ['c19b-high-read','c19b-drop-write'] else 0x31 if fault in ['c19b-read','c19b-wrong-write'] else 0x30)
    assert v[204]==(0x30 if fault=='c19b-drop-undo' else 0x11 if fault=='c19b-undo-read' else 0x10)
    assert v[215]==(0x81 if fault in ['c19b-c19-coupling','c13-undo-c19b-read'] else 0x80)
    for idx,n,expected in [(0x13,207,0x80),(0x17,208,0xe3),(0,209,0x5c),(1,210,0x59),(2,211,0x59),(3,212,0x80),(4,213,93),(5,214,0xbe)]:
     assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c19b-read','c19b-c'+str(idx)+'-coupling'] else expected)
   else:assert v[201:206]==[0,0,0xffffffff,0xffffffff,0] and v[207:216]==[0xffffffff]*9
  else:assert v[200:216]==[0,0,0,0xffffffff,0xffffffff,0,0]+[0xffffffff]*9
'''
rep(" R['cases'].append",new+" R['cases'].append")
rep(' for n in range(7):\n  run(', ' for fault in '+faults+"+['c19b-undo-read','c19b-drop-undo','c13-undo-c19b-read']:run(fault,fault=fault)\n for n in range(7):\n  run(")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('200-word','216-word').replace('len(v)==200','len(v)==216')
s=s.replace(' assert c17ba in',' c19bb,c19bt,c19ba,c19bv,c19bu,tm,c13b,c13v,c17v,c0v,c1v,c2v,c3v,c4v,c5v,c13u=v[200:216]\n assert c19ba in [0,1] and tm in [0,1,2,3]\n assert c17ba in')
s=s.replace('0x7661c]','0x7661c,0x7661e]').replace('and sm==0','and sm==0 and tm==0').replace('or rm or sm:','or rm or sm or tm:').replace('else 0x7661d if sm','else 0x7661f if tm else 0x7661d if sm')
s=s.replace('==(forward==0x766)','==(forward in [0x766,0x7661e])')
new=''' if forward in [0x766,0x7661e]:
  assert c19bb<=255 and c13b<=255 and c19ba==int(c19bb==v[70] and c13b==128)
  if c19ba:
   assert c19bb==16 and c19bt==((c19bb&31)|32) and all(n<=255 for n in [c19bv,c19bu,c13v,c17v,c0v,c1v,c2v,c3v,c4v,c5v,c13u])
   assert tm==int(c19bu!=c19bb)+2*int(c13u!=c13b)
   assert (c19bv==48 and [c13v,c17v,c0v,c1v,c2v,c3v,c4v,c5v]==[128,227,92,89,89,128,93,190])==(forward==0x766)
  else:assert v[201:206]==[0,0,0xffffffff,0xffffffff,0] and v[207:216]==[0xffffffff]*9
 else:assert v[200:216]==[0,0,0,0xffffffff,0xffffffff,0,0]+[0xffffffff]*9
'''
s=s.replace(" return {'cr17_second':",new+" return {'cr19_second':{'before':c19bb,'target':c19bt,'attempted':c19ba,'after':c19bv,'intermediate_restored':c19bu,'cleanup_mask':tm,'CR13_before_after_recovered':[c13b,c13v,c13u],'neighbors_after':[c17v,c0v,c1v,c2v,c3v,c4v,c5v]},'cr17_second':")
p.write_text(s,newline='\n')

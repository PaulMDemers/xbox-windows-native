"""Fresh CR01 model and independent result-schema extension."""
from pathlib import Path
k=Path(__file__).resolve().parent;p=k/'model.py';s=p.read_text()
s=s.replace("out=K/'model002.json'","out=K/'model001.json'")
s=s.replace('fault="",baseline="")','fault="",baseline="",c1_original=0x9f)')
s=s.replace('cr={3:','cr={1:c1_original,3:').replace("state={'c17writes':0","state={'c1writes':0,'c17writes':0")
s=s.replace('assert idx in [3,2,0,4,5,','assert idx in [1,3,2,0,4,5,')
s=s.replace('    if idx==0x17 and word(155):','''    if idx==1:
     state['c1writes']+=1;n=state['c1writes'];assert n<=2 and value==(0x59 if n==1 else c1_original)
     assert state['sq']==0x21 and ports==[5] and not hr and state['c17writes']==1
     assert state['c5bwrites']==1 and all(state['c'+str(i)+'writes']==1 for i in [0,2,3,4,5])
     assert word(164)==c1_original and word(165)==0x59 and word(166)==1
     writes.append(['cr',idx,value])
     if fault==('c1-drop-write' if n==1 else 'c1-drop-undo'):return
     cr[idx]=value
     if n==1 and fault=='c1-wrong-write':cr[idx]^=1
     for idx2 in [0,2,3,4,5,17]:
      if n==1 and fault=='c1-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==0x17 and word(155):''')
s=s.replace("state['c17writes']+=1;n=state['c17writes'];assert", "state['c17writes']+=1;n=state['c17writes'];assert state['c1writes']==2*word(166)\n     assert")
s=s.replace('   val=cr[idx]\n','''   val=cr[idx]
   if idx==1 and state['c1writes']==1 and fault=='c1-read':val^=1
   if idx==1 and state['c1writes']==1 and fault=='c1-high-read':val^=0x80
   if idx==1 and state['c1writes']==2 and state['c17writes']==1 and fault=='c1-undo-read':val^=1
   if idx in [0,2,3,4,5,17] and state['c1writes']==1 and fault=='c'+str(idx)+'-after-c1-read':val^=1
''')
s=s.replace('0x201290','0x2012c0').replace('0x5d70','0x5d40').replace("'<164I'","'<176I'").replace('0x201000,656','0x201000,704')
s=s.replace('   assert word(158)==0',"   assert word(169)==0 and cr[1]==c1_original and (not word(166) or word(168)==c1_original)\n   assert word(158)==0")
s=s.replace('  dbad=fault in',"  fbad=fault in ['c1-undo-read','c1-drop-undo']\n  dbad=fault in")
s=s.replace('or nbad or dbad','or nbad or dbad or fbad')
faults="['c1-read','c1-high-read','c1-drop-write','c1-wrong-write']+['c'+str(i)+'-after-c1-read' for i in [0,2,3,4,5,17]]+['c1-c'+str(i)+'-coupling' for i in [0,2,3,4,5,17]]"
s=s.replace('else 0x760\n  assert v[1]==forward','else 0x76018 if fault in '+faults+' else 0x760\n  assert v[1]==forward')
s=s.replace('0x76016]','0x76016,0x76018]')
s=s.replace("         if forward!=0x76014 and fault!='c17-before-read':expectedwrites += [['cr',0x17,0x63],['cr',0x17,0xe3]]", "         if forward!=0x76014 and fault!='c17-before-read':\n          expectedwrites += [['cr',0x17,0x63]]\n          if forward!=0x76016:expectedwrites += [['cr',1,0x59],['cr',1,c1_original]]\n          expectedwrites += [['cr',0x17,0xe3]]")
s=s.replace('else 0x76017 if dbad','else 0x76019 if fbad else 0x76017 if dbad')
at=" R['cases'].append"
new='''  c1ran=c17ran and forward!=0x76016
  assert v[166]==int(c1ran) and state['c1writes']==2*v[166] and v[169]==int(fbad)
  if c1ran:
   assert v[164:167]==[c1_original,0x59,1]
   assert v[167]==(c1_original if fault=='c1-drop-write' else 0xd9 if fault=='c1-high-read' else 0x58 if fault in ['c1-read','c1-wrong-write'] else 0x59)
   assert v[168]==(0x59 if fault=='c1-drop-undo' else c1_original^1 if fault=='c1-undo-read' else c1_original)
   for idx,n,expected in [(0,170,0x5c),(2,171,0x59),(3,172,0x80),(4,173,93),(5,174,0xbe),(17,175,0x63)]:
    assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c1-read','c1-c'+str(idx)+'-coupling'] else expected)
  else:assert v[164:176]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
'''
assert at in s;s=s.replace(at,new+at)
s=s.replace(' for n in range(7):\n  run(', ' for fault in '+faults+"+['c1-undo-read','c1-drop-undo']:run(fault,fault=fault)\n for value in [0,255]:run('CR01-own-value-'+str(value),c1_original=value)\n for n in range(7):\n  run(")
p.write_text(s,newline='\n')
p=k/'audit_logic.py';s=p.read_text().replace('164-word','176-word').replace('len(v)==164','len(v)==176')
s=s.replace(' assert c17attempt in',' c1,c1target,c1attempt,c1after,c1undo,fm,c0after1,c2after1,c3after1,c4after1,c5after1,c17after1=v[164:176]\n assert c1attempt in [0,1] and fm in [0,1]\n assert c17attempt in')
s=s.replace('0x76016]','0x76016,0x76018]').replace('and dm==0','and dm==0 and fm==0').replace('or nm or dm:','or nm or dm or fm:').replace('else 0x76017 if dm','else 0x76019 if fm else 0x76017 if dm')
s=s.replace('==(forward==0x760)','==(forward in [0x760,0x76018])')
at=" return {'cr17':"
new=''' assert c1attempt==int(forward in [0x760,0x76018])
 if c1attempt:
  assert c1<=255 and c1target==89 and all(n<=255 for n in [c1after,c1undo,c0after1,c2after1,c3after1,c4after1,c5after1,c17after1])
  assert fm==int(c1undo!=c1)
  assert (c1after==89 and [c0after1,c2after1,c3after1,c4after1,c5after1,c17after1]==[92,89,128,93,190,99])==(forward==0x760)
 else:assert v[164:176]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
'''
assert at in s;s=s.replace(at,new+" return {'cr01':{'before':c1,'target':c1target,'attempted':c1attempt,'after':c1after,'restored':c1undo,'cleanup_mask':fm,'neighbors_after':[c0after1,c2after1,c3after1,c4after1,c5after1,c17after1]},'cr17':")
p.write_text(s,newline='\n')

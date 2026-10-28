"""Extend756 contracts for new CR17 phase; exact access order and recovery faults."""
from pathlib import Path
k=Path(__file__).resolve().parent;p=k/'model.py';s=p.read_text()
s=s.replace("'c5bwrites':0","'c17writes':0,'c5bwrites':0")
s=s.replace("    if idx==5 and word(145)",'''    if idx==0x17 and word(155):
     state['c17writes']+=1;n=state['c17writes'];assert n<=2 and value==(0x63 if n==1 else 0xe3)
     assert state['sq']==0x21 and ports==[5] and not hr and state['c5bwrites']==1
     assert all(state['c'+str(i)+'writes']==1 for i in [0,2,3,4,5])
     assert word(146)==0xbe and word(153)==0xe3 and word(154)==0x63
     writes.append(['cr',idx,value])
     if fault==('c17-drop-write' if n==1 else 'c17-drop-undo'):return
     cr[idx]=value
     if n==1 and fault=='c17-wrong-write':cr[idx]^=1
     for idx2 in [0,2,3,4,5]:
      if n==1 and fault=='c17-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==5 and word(145)''')
s=s.replace("state['c5bwrites']+=1;n=state['c5bwrites'];assert", "state['c5bwrites']+=1;n=state['c5bwrites'];assert state['c17writes']==2*word(155)\n     assert")
s=s.replace('   val=cr[idx]\n', '''   val=cr[idx]
   if idx==0x17 and word(1)==0x75816 and not word(155) and fault=='c17-before-read':val^=1
   if idx==0x17 and state['c17writes']==1 and fault=='c17-read':val^=1
   if idx==0x17 and state['c17writes']==1 and fault=='c17-high-read':val^=0x80
   if idx==0x17 and state['c17writes']==2 and state['c5bwrites']==1 and fault=='c17-undo-read':val^=1
   if idx in [0,2,3,4,5] and state['c17writes']==1 and fault=='c'+str(idx)+'-after-c17-read':val^=1
''')
s=s.replace('0x201264','0x201290').replace('0x5d9c','0x5d70').replace("'<153I'","'<164I'").replace('0x201000,612','0x201000,656')
s=s.replace('   assert word(148)==0','   assert word(158)==0 and cr[0x17]==0xe3 and (not word(155) or word(157)==0xe3)\n   assert word(148)==0')
s=s.replace("  nbad=fault in", "  dbad=fault in ['c17-undo-read','c17-drop-undo']\n  nbad=fault in")
s=s.replace('hbad or cbad or zbad or bbad or ebad or nbad','hbad or cbad or zbad or bbad or ebad or nbad or dbad')
faults="['c17-before-read','c17-read','c17-high-read','c17-drop-write','c17-wrong-write']+['c'+str(i)+'-after-c17-read' for i in [0,2,3,4,5]]+['c17-c'+str(i)+'-coupling' for i in [0,2,3,4,5]]"
s=s.replace('else 0x758\n  assert v[1]==forward','else 0x75816 if fault in '+faults+' else 0x758\n  assert v[1]==forward')
s=s.replace('0x75814]','0x75814,0x75816]')
s=s.replace("        if forward!=0x75812:expectedwrites += [['cr',5,0xbe],['cr',5,0x3e]]", "        if forward!=0x75812:\n         expectedwrites += [['cr',5,0xbe]]\n         if forward!=0x75814 and fault!='c17-before-read':expectedwrites += [['cr',0x17,0x63],['cr',0x17,0xe3]]\n         expectedwrites += [['cr',5,0x3e]]")
s=s.replace('  assert v[30]==mask',"  if fault=='c17-drop-undo':mask|=1<<12\n  assert v[30]==mask")
s=s.replace('else 0x75815 if nbad','else 0x75817 if dbad else 0x75815 if nbad')
at=" R['cases'].append"
new='''  c17ran=c5bran and forward!=0x75814
  assert v[155]==int(c17ran and fault!='c17-before-read') and state['c17writes']==2*v[155]
  assert v[158]==int(dbad)
  if c17ran:
   assert v[153]==(0xe2 if fault=='c17-before-read' else 0xe3)
   if v[155]:
    assert v[154]==0x63
    assert v[156]==(0xe3 if fault in ['c17-drop-write','c17-high-read'] else 0x62 if fault in ['c17-read','c17-wrong-write'] else 0x63)
    assert v[157]==(0x63 if fault=='c17-drop-undo' else 0xe2 if fault=='c17-undo-read' else 0xe3)
    for idx,n,expected in [(0,159,0x5c),(2,160,0x59),(3,161,0x80),(4,162,93),(5,163,0xbe)]:
     assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c17-read','c17-c'+str(idx)+'-coupling'] else expected)
   else:assert v[154:164]==[0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
  else:assert v[153:164]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
'''
assert at in s;s=s.replace(at,new+at)
s=s.replace(' for n in range(7):\n  run(', ' for fault in '+faults+"+['c17-undo-read','c17-drop-undo']:run(fault,fault=fault)\n for n in range(7):\n  run(")
p.write_text(s,newline='\n')
# Independent schema expansion without importing implementation/harness constants.
p=k/'audit_logic.py';s=p.read_text().replace('153-word','164-word').replace('len(v)==153','len(v)==164')
s=s.replace(' assert c5battempt in',' c17,c17target,c17attempt,c17after,c17undo,dm,c0after17,c2after17,c3after17,c4after17,c5after17=v[153:164]\n assert c17attempt in [0,1] and dm in [0,1]\n assert c5battempt in')
s=s.replace('0x75814]','0x75814,0x75816]')
s=s.replace('and nm==0','and nm==0 and dm==0').replace('or em or nm:','or em or nm or dm:')
s=s.replace('else 0x75815 if nm','else 0x75817 if dm else 0x75815 if nm')
s=s.replace('(forward==0x758)','(forward in [0x758,0x75816])')
at=" return {'cr05_second':"
new=''' if forward in [0x758,0x75816]:
  assert c17<=255
  assert c17attempt==int(c17==v[69])
  if c17attempt:
   assert c17target==(c17&127) and all(n<=255 for n in [c17after,c17undo,c0after17,c2after17,c3after17,c4after17,c5after17])
   assert dm==int(c17undo!=c17)
   assert (c17after==c17target and [c0after17,c2after17,c3after17,c4after17,c5after17]==[92,89,128,93,190])==(forward==0x758)
  else:assert v[154:164]==[0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 else:assert v[153:164]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
'''
assert at in s;s=s.replace(at,new+" return {'cr17':{'before':c17,'target':c17target,'attempted':c17attempt,'after':c17after,'restored':c17undo,'cleanup_mask':dm,'CR00_after':c0after17,'CR02_after':c2after17,'CR03_after':c3after17,'CR04_after':c4after17,'CR05_after':c5after17},'cr05_second':")
p.write_text(s,newline='\n')

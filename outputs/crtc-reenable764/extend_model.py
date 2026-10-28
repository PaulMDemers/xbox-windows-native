"""Independent764 access sequence, read/write faults and result validator extension."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
rep("state={'c2bwrites':0","state={'c17bwrites':0,'c2bwrites':0")
rep('    if idx==2 and word(178)', '''    if idx==0x17 and word(190) and state['c17bwrites']<2:
     state['c17bwrites']+=1;n=state['c17bwrites'];assert n<=2 and value==(0xe3 if n==1 else 0x63)
     assert state['sq']==0x21 and ports==[5] and not hr and state['c2bwrites']==state['c1writes']==state['c17writes']==1
     assert state['c5bwrites']==1 and all(state['c'+str(i)+'writes']==1 for i in [0,2,3,4,5])
     assert [word(188),word(189),word(190)]==[0x63,0xe3,1]
     writes.append(['cr',idx,value])
     if fault==('c17b-drop-write' if n==1 else 'c17b-drop-undo'):return
     cr[idx]=value
     if n==1 and fault=='c17b-wrong-write':cr[idx]^=1
     for idx2 in [0,1,2,3,4,5]:
      if n==1 and fault=='c17b-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==2 and word(178)''')
rep("state['c2bwrites']+=1;n=state['c2bwrites'];assert", "state['c2bwrites']+=1;n=state['c2bwrites'];assert state['c17bwrites']==2*word(190)\n     assert")
rep('   val=cr[idx]\n', '''   val=cr[idx]
   if idx==0x17 and word(1)==0x7641c and not word(190) and state['c2bwrites']==1 and fault=='c17b-before-read':val^=1
   if idx==0x17 and state['c17bwrites']==1 and fault=='c17b-read':val^=1
   if idx==0x17 and state['c17bwrites']==1 and fault=='c17b-low-read':val^=0x80
   if idx==0x17 and state['c17bwrites']==2 and state['c2bwrites']==1 and fault=='c17b-undo-read':val^=1
   if idx in [0,1,2,3,4,5] and state['c17bwrites']==1 and fault=='c'+str(idx)+'-after-c17b-read':val^=1
''')
rep('0x2012f0','0x201320');rep('0x5d10','0x5ce0');rep("'<188I'","'<200I'");rep('0x201000,752','0x201000,800')
rep('   assert word(181)==0', '   assert word(193)==0 and (not word(190) or word(192)==word(188))\n   assert word(181)==0')
rep('  rbad=fault in', "  sbad=fault in ['c17b-undo-read','c17b-drop-undo']\n  rbad=fault in")
rep('or fbad or rbad','or fbad or rbad or sbad')
faults="['c17b-before-read','c17b-read','c17b-low-read','c17b-drop-write','c17b-wrong-write']+['c'+str(i)+'-after-c17b-read' for i in [0,1,2,3,4,5]]+['c17b-c'+str(i)+'-coupling' for i in [0,1,2,3,4,5]]"
rep('else 0x764\n  assert v[1]==forward','else 0x7641c if fault in '+faults+' else 0x764\n  assert v[1]==forward')
rep('0x7641a]','0x7641a,0x7641c]')
rep("           if forward!=0x76418 and fault!='c2b-before-read':expectedwrites += [['cr',2,0x59],['cr',2,0x59]]", "           if forward!=0x76418 and fault!='c2b-before-read':\n            expectedwrites += [['cr',2,0x59]]\n            if forward!=0x7641a and fault!='c17b-before-read':expectedwrites += [['cr',0x17,0xe3],['cr',0x17,0x63]]\n            expectedwrites += [['cr',2,0x59]]")
rep('else 0x7641b if rbad','else 0x7641d if sbad else 0x7641b if rbad')
new='''  c17bran=c2bran and forward!=0x7641a
  assert v[190]==int(c17bran and fault!='c17b-before-read') and state['c17bwrites']==2*v[190] and v[193]==int(sbad)
  if c17bran:
   assert v[188]==(0x62 if fault=='c17b-before-read' else 0x63)
   if v[190]:
    assert v[189]==0xe3
    assert v[191]==(0x63 if fault in ['c17b-low-read','c17b-drop-write'] else 0xe2 if fault in ['c17b-read','c17b-wrong-write'] else 0xe3)
    assert v[192]==(0xe3 if fault=='c17b-drop-undo' else 0x62 if fault=='c17b-undo-read' else 0x63)
    for idx,n,expected in [(0,194,0x5c),(1,195,0x59),(2,196,0x59),(3,197,0x80),(4,198,93),(5,199,0xbe)]:
     assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c17b-read','c17b-c'+str(idx)+'-coupling'] else expected)
   else:assert v[189:200]==[0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
  else:assert v[188:200]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
'''
rep(" R['cases'].append",new+" R['cases'].append")
rep(' for n in range(7):\n  run(', ' for fault in '+faults+"+['c17b-undo-read','c17b-drop-undo']:run(fault,fault=fault)\n for n in range(7):\n  run(")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('188-word','200-word').replace('len(v)==188','len(v)==200')
s=s.replace(' assert c2ba in', ' c17bb,c17bt,c17ba,c17bv,c17bu,sm,c0after17b,c1after17b,c2after17b,c3after17b,c4after17b,c5after17b=v[188:200]\n assert c17ba in [0,1] and sm in [0,1]\n assert c2ba in')
s=s.replace('0x7641a]','0x7641a,0x7641c]').replace('and rm==0','and rm==0 and sm==0').replace('or fm or rm:','or fm or rm or sm:').replace('else 0x7641b if rm','else 0x7641d if sm else 0x7641b if rm')
s=s.replace('==(forward==0x764)','==(forward in [0x764,0x7641c])')
new=''' if forward in [0x764,0x7641c]:
  assert c17bb<=255 and c17ba==int(c17bb==c17after2b)
  if c17ba:
   assert c17bb==99 and c17bt==((c17bb&127)|128) and all(n<=255 for n in [c17bv,c17bu,c0after17b,c1after17b,c2after17b,c3after17b,c4after17b,c5after17b])
   assert sm==int(c17bu!=c17bb)
   assert (c17bv==227 and [c0after17b,c1after17b,c2after17b,c3after17b,c4after17b,c5after17b]==[92,89,89,128,93,190])==(forward==0x764)
  else:assert v[189:200]==[0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 else:assert v[188:200]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
'''
assert " return {'cr02_second':" in s
s=s.replace(" return {'cr02_second':",new+" return {'cr17_second':{'before':c17bb,'target':c17bt,'attempted':c17ba,'after':c17bv,'intermediate_restored':c17bu,'cleanup_mask':sm,'neighbors_after':[c0after17b,c1after17b,c2after17b,c3after17b,c4after17b,c5after17b]},'cr02_second':")
p.write_text(s,newline='\n')

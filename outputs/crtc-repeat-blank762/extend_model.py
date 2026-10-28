"""Independent later-CR02 access/failure model and result schema extension."""
from pathlib import Path
k=Path(__file__).resolve().parent;p=k/'model.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
rep("state={'c1writes':0", "state={'c2bwrites':0,'c1writes':0")
rep('    if idx==1:', '''    if idx==2 and word(178) and state['c2bwrites']<2:
     state['c2bwrites']+=1;n=state['c2bwrites'];assert n<=2 and value==0x59
     assert state['sq']==0x21 and ports==[5] and not hr and state['c1writes']==state['c17writes']==1
     assert state['c5bwrites']==1 and all(state['c'+str(i)+'writes']==1 for i in [0,2,3,4,5])
     assert word(176)==word(177)==0x59 and word(178)==1
     writes.append(['cr',idx,value])
     if fault==('c2b-drop-write' if n==1 else 'c2b-drop-undo') or (n==2 and fault=='c2b-wrong-write-drop-undo'):return
     cr[idx]=value
     if n==1 and fault in ['c2b-wrong-write','c2b-wrong-write-drop-undo']:cr[idx]^=1
     for idx2 in [0,1,3,4,5,0x17]:
      if n==1 and fault=='c2b-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==1:''')
rep("state['c1writes']+=1;n=state['c1writes'];assert", "state['c1writes']+=1;n=state['c1writes'];assert state['c2bwrites']==2*word(178)\n     assert")
rep('   val=cr[idx]\n','''   val=cr[idx]
   if idx==2 and word(1)==0x7621a and not word(178) and state['c1writes']==1 and fault=='c2b-before-read':val^=1
   if idx==2 and state['c2bwrites']==1 and fault=='c2b-read':val^=1
   if idx==2 and state['c2bwrites']==1 and fault=='c2b-high-read':val^=0x80
   if idx==2 and state['c2bwrites']==2 and state['c1writes']==1 and fault=='c2b-undo-read':val^=1
   if idx in [0,1,3,4,5,0x17] and state['c2bwrites']==1 and fault=='c'+str(idx)+'-after-c2b-read':val^=1
''')
rep('0x2012c0','0x2012f0');rep('0x5d40','0x5d10');rep("'<176I'","'<188I'");rep('0x201000,704','0x201000,752')
rep('   assert word(169)==0',"   assert word(181)==0 and (not word(178) or word(180)==word(176))\n   assert word(169)==0")
rep('  fbad=fault in',"  rbad=fault in ['c2b-undo-read','c2b-wrong-write-drop-undo']\n  fbad=fault in")
rep('or dbad or fbad','or dbad or fbad or rbad')
faults="['c2b-before-read','c2b-read','c2b-high-read','c2b-wrong-write','c2b-wrong-write-drop-undo']+['c'+str(i)+'-after-c2b-read' for i in [0,1,3,4,5,0x17]]+['c2b-c'+str(i)+'-coupling' for i in [0,1,3,4,5,0x17]]"
rep('else 0x762\n  assert v[1]==forward','else 0x7621a if fault in '+faults+' else 0x762\n  assert v[1]==forward')
rep('0x76218]','0x76218,0x7621a]')
rep("          if forward!=0x76216:expectedwrites += [['cr',1,0x59],['cr',1,c1_original]]", "          if forward!=0x76216:\n           expectedwrites += [['cr',1,0x59]]\n           if forward!=0x76218 and fault!='c2b-before-read':expectedwrites += [['cr',2,0x59],['cr',2,0x59]]\n           expectedwrites += [['cr',1,c1_original]]")
rep('else 0x76219 if fbad','else 0x7621b if rbad else 0x76219 if fbad')
new='''  c2bran=c1ran and forward!=0x76218
  assert v[178]==int(c2bran and fault!='c2b-before-read') and state['c2bwrites']==2*v[178] and v[181]==int(rbad)
  if c2bran:
   assert v[176]==(0x58 if fault=='c2b-before-read' else 0x59)
   if v[178]:
    assert v[177]==0x59
    assert v[179]==(0xd9 if fault=='c2b-high-read' else 0x58 if fault in ['c2b-read','c2b-wrong-write','c2b-wrong-write-drop-undo'] else 0x59)
    assert v[180]==(0x58 if fault in ['c2b-undo-read','c2b-wrong-write-drop-undo'] else 0x59)
    for idx,n,expected in [(0,182,0x5c),(1,183,0x59),(3,184,0x80),(4,185,93),(5,186,0xbe),(0x17,187,0x63)]:
     assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c2b-read','c2b-c'+str(idx)+'-coupling'] else expected)
   else:assert v[177:188]==[0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
  else:assert v[176:188]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
'''
rep(" R['cases'].append",new+" R['cases'].append")
rep(' for n in range(7):\n  run(', ' for fault in '+faults+"+['c2b-undo-read','c2b-drop-write','c2b-drop-undo']:run(fault,fault=fault)\n for n in range(7):\n  run(")
p.write_text(s,newline='\n')
p=k/'audit_logic.py';s=p.read_text().replace('176-word','188-word').replace('len(v)==176','len(v)==188')
s=s.replace(' assert c1attempt in', ' c2bb,c2bt,c2ba,c2bv,c2bu,rm,c0after2b,c1after2b,c3after2b,c4after2b,c5after2b,c17after2b=v[176:188]\n assert c2ba in [0,1] and rm in [0,1]\n assert c1attempt in')
s=s.replace('0x76218]','0x76218,0x7621a]').replace('and fm==0','and fm==0 and rm==0').replace('or dm or fm:','or dm or fm or rm:').replace('else 0x76219 if fm','else 0x7621b if rm else 0x76219 if fm')
s=s.replace('==(forward==0x762)','==(forward in [0x762,0x7621a])')
new=''' if forward in [0x762,0x7621a]:
  assert c2bb<=255 and c2ba==int(c2bb==c2after1)
  if c2ba:
   assert c2bb==c2bt==89 and all(n<=255 for n in [c2bv,c2bu,c0after2b,c1after2b,c3after2b,c4after2b,c5after2b,c17after2b])
   assert rm==int(c2bu!=c2bb)
   assert (c2bv==89 and [c0after2b,c1after2b,c3after2b,c4after2b,c5after2b,c17after2b]==[92,89,128,93,190,99])==(forward==0x762)
  else:assert v[177:188]==[0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 else:assert v[176:188]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
'''
assert " return {'cr01':" in s;s=s.replace(" return {'cr01':",new+" return {'cr02_second':{'before':c2bb,'target':c2bt,'attempted':c2ba,'after':c2bv,'intermediate_restored':c2bu,'cleanup_mask':rm,'neighbors_after':[c0after2b,c1after2b,c3after2b,c4after2b,c5after2b,c17after2b],'same_value_write_observability':'dropped same-value write/undo cannot be distinguished by unchanged readback'},'cr01':")
p.write_text(s,newline='\n')

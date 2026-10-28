"""Extend actual-instruction model and independent result contract for CR03."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'model.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep('cr={2:0x9f,','cr={3:0x8c,2:0x9f,')
rep(" if baseline=='c2':", " if baseline=='c3':cr[3]^=1\n if baseline=='c2':")
rep("state={'c2writes':0,", "state={'c3writes':0,'c2writes':0,")
rep('assert idx in [2,0,4,5,','assert idx in [3,2,0,4,5,')
rep('    if idx==2:', '''    if idx==3:
     state['c3writes']+=1;assert state['c3writes']<=2
     assert value==(0x80 if state['c3writes']==1 else 0x8c)
     assert state['sq']==0x21 and ports==[5] and all(state['c'+str(i)+'writes']==1 for i in [0,2,4,5]) and not hr
     assert word(127)==0x59 and word(130)==0x5c and word(131)==93 and word(132)==0x3e and word(135)==1 and not cr[0x11]&0x80
     writes.append(['cr',3,value])
     if fault==('c3-drop-write' if state['c3writes']==1 else 'c3-drop-restore'):return
     cr[3]=value
     for idx2 in [0,2,4,5]:
      if state['c3writes']==1 and fault=='c3-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==2:''')
rep("     state['c2writes']+=1;assert state['c2writes']<=2", "     state['c2writes']+=1;assert state['c2writes']<=2\n     if state['c2writes']==2:assert state['c3writes']==2*word(135)")
rep("   if idx==2 and state['c2writes']==1 and fault=='c2-read':val^=1", '''   if idx==3 and state['c3writes']==1 and fault=='c3-read':val^=1
   if idx==3 and state['c3writes']==1 and fault=='c3-high-read':val^=0x80
   if idx==3 and state['c3writes']==2 and fault=='c3-restore-read':val^=1
   if idx in [0,2,4,5] and state['c3writes']==1 and fault=='c'+str(idx)+'-after-c3-read':val^=1
   if idx==2 and state['c2writes']==1 and fault=='c2-read':val^=1''')
rep('0x201214','0x20123c');rep('0x5dec','0x5dc4')
rep("'<133I',c.mem_read(0x201000,532)","'<143I',c.mem_read(0x201000,572)")
rep('   assert word(129)==0', '   assert word(138)==0 and cr[3]==0x8c and word(137)==0x8c\n   assert word(129)==0')
rep('  bbad=fault in', "  ebad=fault in ['c3-restore-read','c3-drop-restore']\n  bbad=fault in")
rep('hbad or cbad or zbad or bbad','hbad or cbad or zbad or bbad or ebad')
rep('else 0x753\n  assert v[1]', "else 0x75312 if fault in ['c3-read','c3-high-read','c3-drop-write']+['c'+str(i)+'-after-c3-read' for i in [0,2,4,5]]+['c3-c'+str(i)+'-coupling' for i in [0,2,4,5]] else 0x753\n  assert v[1]")
rep('0x75310]', '0x75310,0x75312]')
rep("      if forward!=0x753e:expectedwrites += [['cr',2,0x59],['cr',2,0x9f]]", "      if forward!=0x753e:\n       expectedwrites += [['cr',2,0x59]]\n       if forward!=0x75310:expectedwrites += [['cr',3,0x80],['cr',3,0x8c]]\n       expectedwrites += [['cr',2,0x9f]]")
rep('else 0x75311 if bbad','else 0x75313 if ebad else 0x75311 if bbad')
rep('  else:assert v[125:128]==[0,0,0xffffffff] and v[130:133]==[0xffffffff]*3', '''  else:assert v[125:128]==[0,0,0xffffffff] and v[130:133]==[0xffffffff]*3
  c3ran=c2ran and forward!=0x75310
  assert v[133]==0x8c and state['c3writes']==2*int(c3ran) and v[135]==int(c3ran)
  assert v[137]==(0x8d if fault=='c3-restore-read' else 0x80 if fault=='c3-drop-restore' else 0x8c)
  assert v[138]==int(ebad)
  if c3ran:
   assert v[134]==0x80
   assert v[136]==(0x8c if fault=='c3-drop-write' else 0x81 if fault=='c3-read' else 0 if fault=='c3-high-read' else 0x80)
   for idx,n,expected in [(0,139,0x5c),(2,140,0x59),(4,141,93),(5,142,0x3e)]:
    assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c3-read','c3-c'+str(idx)+'-coupling'] else expected)
  else:assert v[134:137]==[0,0,0xffffffff] and v[139:143]==[0xffffffff]*4''')
rep(" for n in range(7):\n  run('horizontal", " run('crtc-baseline-c3',baseline='c3')\n for fault in ['c3-read','c3-high-read','c3-drop-write','c3-restore-read','c3-drop-restore']+['c'+str(i)+'-after-c3-read' for i in [0,2,4,5]]+['c3-c'+str(i)+'-coupling' for i in [0,2,4,5]]:run(fault,fault=fault)\n for n in range(7):\n  run('horizontal")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text()
rep('133-word','143-word');rep('len(v)==133','len(v)==143')
rep(' assert c2attempt in', ' c3,c3target,c3attempt,c3after,c3restore,em,c0after3,c2after3,c4after3,c5after3=v[133:143]\n assert c3attempt in [0,1] and em in [0,1]\n assert c2attempt in')
rep('0x75310]','0x75310,0x75312]')
rep('and bm==0)','and bm==0 and em==0)')
rep('else 0x75311 if bm','else 0x75313 if em else 0x75311 if bm')
rep('if mask or cm or zm or bm:','if mask or cm or zm or bm or em:')
rep('(forward==0x753)','(forward in [0x753,0x75312])')
rep(" return {'cr02':", ''' assert c3attempt==int(forward in [0x753,0x75312])
 if forward in [0x7531,0x7532]:
  assert em==0 and c3restore==0xffffffff
  if forward==0x7531:assert c3==0
 else:assert c3==0x8c and em==int(c3restore!=c3)
 if c3attempt:
  assert c3target==((c3&0xe0)|((779//8-1)&31)) and all(n<=255 for n in [c3after,c0after3,c2after3,c4after3,c5after3])
  assert (c3after==c3target and c0after3==92 and c2after3==89 and c4after3==93 and c5after3==62)==(forward==0x753)
 else:assert c3target==0 and [c3after,c0after3,c2after3,c4after3,c5after3]==[0xffffffff]*5
 return {'cr03':{'before':c3,'target':c3target,'attempted':c3attempt,'after':c3after,'restored':c3restore,'cleanup_mask':em,'CR00_after':c0after3,'CR02_after':c2after3,'CR04_after':c4after3,'CR05_after':c5after3},'cr02':''')
p.write_text(s,newline='\n')

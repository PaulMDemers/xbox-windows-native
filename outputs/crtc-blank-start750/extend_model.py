"""Add CR02 actual-instruction fault and independent audit contracts."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'model.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep('cr={0:0xc8,','cr={2:0x9f,0:0xc8,')
rep(" if baseline=='c0':", " if baseline=='c2':cr[2]^=1\n if baseline=='c0':")
rep("state={'c0writes':0,", "state={'c2writes':0,'c0writes':0,")
rep('assert idx in [0,4,5,','assert idx in [2,0,4,5,')
rep('    if idx==0:', '''    if idx==2:
     state['c2writes']+=1;assert state['c2writes']<=2
     assert value==(0x59 if state['c2writes']==1 else 0x9f)
     assert state['sq']==0x21 and ports==[5] and state['c4writes']==1 and state['c5writes']==1 and state['c0writes']==1 and not hr
     assert word(119)==0x5c and word(122)==93 and word(123)==0x3e and word(126)==1 and not cr[0x11]&0x80
     writes.append(['cr',2,value])
     if fault==('c2-drop-write' if state['c2writes']==1 else 'c2-drop-restore'):return
     cr[2]=value
     for idx2 in [0,4,5]:
      if state['c2writes']==1 and fault=='c2-c'+str(idx2)+'-coupling':cr[idx2]^=1
     return
    if idx==0:''')
rep("     state['c0writes']+=1;assert state['c0writes']<=2", "     state['c0writes']+=1;assert state['c0writes']<=2\n     if state['c0writes']==2:assert state['c2writes']==2*word(126)")
rep("   if idx==0 and state['c0writes']==1 and fault=='c0-read':val^=1", '''   if idx==2 and state['c2writes']==1 and fault=='c2-read':val^=1
   if idx==2 and state['c2writes']==2 and fault=='c2-restore-read':val^=1
   if idx in [0,4,5] and state['c2writes']==1 and fault=='c'+str(idx)+'-after-c2-read':val^=1
   if idx==0 and state['c0writes']==1 and fault=='c0-read':val^=1''')
rep('0x2011f0','0x201214');rep('0x5e10','0x5dec')
rep("'<124I',c.mem_read(0x201000,496)","'<133I',c.mem_read(0x201000,532)")
rep('   assert word(121)==0', '   assert word(129)==0 and cr[2]==0x9f and word(128)==0x9f\n   assert word(121)==0')
rep('  zbad=fault in', "  bbad=fault in ['c2-restore-read','c2-drop-restore']\n  zbad=fault in")
rep('hbad or cbad or zbad','hbad or cbad or zbad or bbad')
rep('else 0x750\n  assert v[1]', "else 0x75010 if fault in ['c2-read','c2-drop-write','c0-after-c2-read','c4-after-c2-read','c5-after-c2-read','c2-c0-coupling','c2-c4-coupling','c2-c5-coupling'] else 0x750\n  assert v[1]")
rep('[0x750,0x7508,0x7509,0x750b,0x750d,0x750e]', '[0x750,0x7508,0x7509,0x750b,0x750d,0x750e,0x75010]')
rep('[0x750,0x7509,0x750b,0x750d,0x750e]', '[0x750,0x7509,0x750b,0x750d,0x750e,0x75010]')
rep("     if forward!=0x750d:expectedwrites += [['cr',0,0x5c],['cr',0,0xc8]]", "     if forward!=0x750d:\n      expectedwrites += [['cr',0,0x5c]]\n      if forward!=0x750e:expectedwrites += [['cr',2,0x59],['cr',2,0x9f]]\n      expectedwrites += [['cr',0,0xc8]]")
rep('else 0x750f if zbad','else 0x75011 if bbad else 0x750f if zbad')
rep('  else:assert v[117:120]==[0,0,0xffffffff] and v[122:124]==[0xffffffff]*2', '''  else:assert v[117:120]==[0,0,0xffffffff] and v[122:124]==[0xffffffff]*2
  c2ran=c0ran and forward!=0x750e
  assert v[124]==0x9f and state['c2writes']==2*int(c2ran) and v[126]==int(c2ran)
  assert v[128]==(0x9e if fault=='c2-restore-read' else 0x59 if fault=='c2-drop-restore' else 0x9f)
  assert v[129]==int(bbad)
  if c2ran:
   assert v[125]==0x59
   assert v[127]==(0x9f if fault=='c2-drop-write' else 0x58 if fault=='c2-read' else 0x59)
   for idx,n,expected in [(0,130,0x5c),(4,131,93),(5,132,0x3e)]:
    assert v[n]==(expected^1 if fault in ['c'+str(idx)+'-after-c2-read','c2-c'+str(idx)+'-coupling'] else expected)
  else:assert v[125:128]==[0,0,0xffffffff] and v[130:133]==[0xffffffff]*3''')
rep(" for n in range(7):\n  run('horizontal", " run('crtc-baseline-c2',baseline='c2')\n for fault in ['c2-read','c2-drop-write','c2-restore-read','c2-drop-restore','c0-after-c2-read','c4-after-c2-read','c5-after-c2-read','c2-c0-coupling','c2-c4-coupling','c2-c5-coupling']:run(fault,fault=fault)\n for n in range(7):\n  run('horizontal")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text()
rep('124-word','133-word');rep('len(v)==124','len(v)==133')
rep(' assert c0attempt in', ' c2,c2target,c2attempt,c2after,c2restore,bm,c0after2,c4after2,c5after2=v[124:133]\n assert c2attempt in [0,1] and bm in [0,1]\n assert c0attempt in')
rep('0x750e]','0x750e,0x75010]')
rep('mask==0 and cm==0 and zm==0','mask==0 and cm==0 and zm==0 and bm==0')
rep('else 0x750f if zm','else 0x75011 if bm else 0x750f if zm')
rep('if mask or cm or zm:','if mask or cm or zm or bm:')
rep('(forward==0x750)','(forward in [0x750,0x75010])')
rep(" return {'cr00':", ''' assert c2attempt==int(forward in [0x750,0x75010])
 if forward in [0x7501,0x7502]:
  assert bm==0 and c2restore==0xffffffff
  if forward==0x7501:assert c2==0
 else:assert c2==0x9f and bm==int(c2restore!=c2)
 if c2attempt:
  assert c2target==89 and all(n<=255 for n in [c2after,c0after2,c4after2,c5after2])
  assert (c2after==89 and c0after2==92 and c4after2==93 and c5after2==62)==(forward==0x750)
 else:assert c2target==0 and [c2after,c0after2,c4after2,c5after2]==[0xffffffff]*4
 return {'cr02':{'before':c2,'target':c2target,'attempted':c2attempt,'after':c2after,'restored':c2restore,'cleanup_mask':bm,'CR00_after':c0after2,'CR04_after':c4after2,'CR05_after':c5after2},'cr00':''')
p.write_text(s,newline='\n')
print('Extended750 model and independent schema')

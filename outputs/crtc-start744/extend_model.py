"""Author744's new actual-COFF checks without touching prior evidence."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model.py';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep('cr={0x11:9,','cr={4:0xa7,5:0x31,0x11:9,')
rep(" if baseline=='gr':gr=1", " if baseline=='c4':cr[4]^=1\n if baseline=='c5':cr[5]^=1\n if baseline=='gr':gr=1")
rep("state={'sq':sq,", "state={'c4writes':0,'sq':sq,")
rep('assert idx in [0x1f,0x14,0x17,0x19]', '''assert idx in [4,0x1f,0x14,0x17,0x19]
    if idx==4:
     state['c4writes']+=1;assert state['c4writes']<=2
     assert value==(93 if state['c4writes']==1 else 0xa7)
     assert state['sq']==0x21 and ports==[5] and not (cr[0x11]&0x80)
     assert word(98)==7 and word(99)==0xffffffff and not hr
     writes.append(['cr',4,value])
     if fault==('c4-write' if state['c4writes']==1 else 'c4-restore-write'):return
     cr[4]=value
     if state['c4writes']==1 and fault=='c5-coupling':cr[5]^=1
     return''')
rep('   val=cr[idx]\n', '''   val=cr[idx]
   if idx==4 and state['c4writes']==1 and fault=='c4-read':val^=1
   if idx==4 and state['c4writes']==2 and fault=='c4-restore-read':val^=1
   if idx==5 and state['c4writes']==1 and fault=='c5-read':val^=1
   if idx==5 and state['c4writes']==2 and fault=='c5-restore-read':val^=1
''')
rep('0x2011a0','0x2011c0');rep('0x5e60','0x5e40')
rep("'<104I',c.mem_read(0x201000,416)","'<112I',c.mem_read(0x201000,448)")
rep('assert word(100)==0 and word(97)', 'assert word(108)==0 and cr[4]==0xa7 and cr[5]==0x31\n   assert word(106)==0xa7 and word(111)==0x31\n   assert word(100)==0 and word(97)')
rep("  assert ports==([5] if hbad else [5,4]),(name,ports)", "  cbad=fault in ['c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling']\n  assert ports==([5] if hbad or cbad else [5,4]),(name,ports)")
rep("else 0x744\n  assert v[1]", "else 0x744b if fault in ['c4-read','c4-write','c5-read','c5-coupling'] else 0x744\n  assert v[1]")
rep('forward in [0x744,0x7448,0x7449]', 'forward in [0x744,0x7448,0x7449,0x744b]')
rep('forward in [0x744,0x7449]', 'forward in [0x744,0x7449,0x744b]')
rep("expectedwrites += [['h',a,b] for a,b in H]+[['h',H[i][0],HB[i]] for i in range(6,-1,-1)]", "expectedwrites += [['h',a,b] for a,b in H]\n   if forward!=0x7449:expectedwrites += [['cr',4,93],['cr',4,0xa7]]\n   expectedwrites += [['h',H[i][0],HB[i]] for i in range(6,-1,-1)]")
rep("  if not hbad:expectedwrites", "  if not (hbad or cbad):expectedwrites")
rep('(1<<15 if hbad else 0)', '(1<<15 if hbad or cbad else 0)')
rep('[hm,int(not hbad)]','[hm,int(not (hbad or cbad))]')
rep("0x7446 if fault=='selector' else 0x744a", "0x7446 if fault=='selector' else 0x744c if cbad else 0x744a")
rep("  assert v[28]==(fault!='selector')", """  assert v[28]==(fault!='selector')
  assert v[104]==0xa7 and v[109]==0x31
  cran=horizontal_ran and forward!=0x7449
  assert v[107]==int(cran) and state['c4writes']==(2 if cran else 0)
  assert v[108]==(1 if fault in ['c4-restore-read','c4-restore-write'] else 2 if fault in ['c5-restore-read','c5-coupling'] else 0)
  assert v[106]==(0xa6 if fault=='c4-restore-read' else 93 if fault=='c4-restore-write' else 0xa7)
  assert v[111]==(0x30 if fault in ['c5-restore-read','c5-coupling'] else 0x31)
  if cran:
   assert v[105]==(92 if fault=='c4-read' else 0xa7 if fault=='c4-write' else 93)
   assert v[110]==(0x30 if fault in ['c5-read','c5-coupling'] else 0x31)
  else:assert v[105]==v[110]==0xffffffff""")
rep(" for n in range(7):\n  run('horizontal", " for bline in ['c4','c5']:run('crtc-baseline-'+bline,baseline=bline)\n for fault in ['c4-read','c4-write','c4-restore-read','c4-restore-write','c5-read','c5-restore-read','c5-coupling']:run(fault,fault=fault)\n for n in range(7):\n  run('horizontal")
p.write_text(s,newline='\n')
print('Extended744 model with CR04/CR05, recovery-order and output-enable fault checks')

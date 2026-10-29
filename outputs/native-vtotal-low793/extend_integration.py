"""Extend independent full-bridge oracle for CR06 total low byte."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration007.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'ct7writes'","state={'ct6writes':0,'ct7writes'")
s=s.replace('0x79334]','0x79334,0x79336]').replace('0x79334,0x793]','0x79334,0x79336,0x793]')
rep("    if i==7 and state['c10writes']==1:", '''    if i==6:
     state['ct6writes']+=1;n=state['ct6writes'];assert n<=2 and value==[12,236][n-1]
     assert state['ct7writes']==1 and state['c10writes']==1 and word(1) in [0x79336,0x793]
     assert [word(520),word(521),word(522)]==[236,12,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('ct6-drop-write' if n==1 else 'ct6-drop-undo') or (n==2 and fault=='ct6-wrong-write-drop-undo'):return
     cr[6]=value
     if fault==('ct6-wrong-write' if n==1 else 'ct6-wrong-undo') or (n==1 and fault=='ct6-wrong-write-drop-undo'):cr[6]^=1
     if n==1 and fault.startswith('ct6-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[7,9,0x10,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
    elif i==7 and state['c10writes']==1:''')
rep("state['ct7writes']+=1;n=state['ct7writes'];assert n<=2", "state['ct7writes']+=1;n=state['ct7writes'];assert n==1 or state['ct6writes']==2*word(522);assert n<=2")
rep("   i=sels[0x6013d4]\n", """   i=sels[0x6013d4]
   if i in [6,7,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['ct7writes']==1 and word(1) in [0x79336,0x793]:
    j=[6,7,9,0x10,0x12,0x15,0x16,0x18,0x25].index(i);phase=['before','after','undo'][state['ct6writes']]
    if fault=='ct6-'+phase+'-'+str(j):value^=1
""")
rep('    assert word(495)==0','    assert word(525)==0 and (not word(522) or word(524)==word(520))\n    assert word(495)==0')
rep('[(7,116),(7,116)]',"[(7,116)]+([(6,12),(6,236)] if state['ct6writes'] else [])+[(7,116)]")
rep("  if fault.startswith(('ct7-undo-'", "  if fault.startswith(('ct6-undo-','ct6-coupling-')) or fault in ['ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[525]!=0 and v[101]==0\n  elif fault.startswith(('ct7-undo-'")
model=(K/'model.py').read_text();a=model.index(' reached_c7=');block=model[a:model.index(" R['cases'].append",a)]
block=block.replace('not cpu_bad and not baseline and forward',"state['c13writes'] and v[1]")
for m in ['c7mask','c10mask','ct7mask','ct6mask']:block=block.replace('=='+m,'')
for start,end in [(430,460),(460,490),(490,520),(520,550)]:
 tail='' if end==550 else str(end)
 before=f' else:assert v[{start}:{start+6}]==[0,0,0,0xffffffff,0xffffffff,0] and v[{start+6}:{tail}]==[0,0xffffffff,0xffffffff]*8'
 after=f' else:assert v[{start}:{end}]==([0]*30 if refusal or want<0x793 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)'
 assert before in block,before;block=block.replace(before,after)
a=s.index(' reached_c7=');z=s.index(' for lo,hi in [(0,0x880)',a);s=s[:a]+block+s[z:]
rep('v[237],v[261],v[435],v[465],v[495],v[490],v[493],v[494]','v[261],v[435],v[465],v[495],v[525],v[520],v[523],v[524]')
rep("try:\n for phase", """try:
 for phase in ['before','after','undo']:
  for j in range(9):run('ct6-'+phase+'-'+str(j),want=0x79337 if phase=='undo' else 0x79336,fault='ct6-'+phase+'-'+str(j))
 for j in range(1,9):run('ct6-coupling-'+str(j),want=0x79337,fault='ct6-coupling-'+str(j))
 for f in ['ct6-drop-write','ct6-wrong-write','ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo']:
  run(f,want=0x79336 if f in ['ct6-drop-write','ct6-wrong-write'] else 0x79337,fault=f)
 for phase""")
p.write_text(s,newline='\n')
print('Extended793 full-path oracle; no hardware access')

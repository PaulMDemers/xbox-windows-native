"""Extend independent full-bridge device oracle for CR16 blank-end."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration008.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'ct6writes'","state={'ct16writes':0,'ct6writes'")
s=s.replace('0x79536]','0x79536,0x79538]').replace('0x79536,0x795]','0x79536,0x79538,0x795]')
rep('    if i==6:', '''    if i==0x16:
     state['ct16writes']+=1;n=state['ct16writes'];assert n<=2 and value==[140,237][n-1]
     assert state['ct6writes']==1 and state['ct7writes']==1 and word(1) in [0x79538,0x795]
     assert [word(550),word(551),word(552)]==[237,140,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('ct16-drop-write' if n==1 else 'ct16-drop-undo') or (n==2 and fault=='ct16-wrong-write-drop-undo'):return
     cr[0x16]=value
     if fault==('ct16-wrong-write' if n==1 else 'ct16-wrong-undo') or (n==1 and fault=='ct16-wrong-write-drop-undo'):cr[0x16]^=1
     if n==1 and fault.startswith('ct16-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,0x10,0x12,0x15,0x18,0x25][j-1]]^=1
    elif i==6:''')
rep("state['ct6writes']+=1;n=state['ct6writes'];assert n<=2", "state['ct6writes']+=1;n=state['ct6writes'];assert n==1 or state['ct16writes']==2*word(552);assert n<=2")
rep("   i=sels[0x6013d4]\n", """   i=sels[0x6013d4]
   if i in [0x16,6,7,9,0x10,0x12,0x15,0x18,0x25] and state['ct6writes']==1 and word(1) in [0x79538,0x795]:
    j=[0x16,6,7,9,0x10,0x12,0x15,0x18,0x25].index(i);phase=['before','after','undo'][state['ct16writes']]
    if fault=='ct16-'+phase+'-'+str(j):value^=1
""")
rep('    assert word(525)==0','    assert word(555)==0 and (not word(552) or word(554)==word(550))\n    assert word(525)==0')
rep('[(6,12),(6,236)]',"[(6,12)]+([(22,140),(22,237)] if state['ct16writes'] else [])+[(6,236)]")
rep("  if fault.startswith(('ct6-undo-'", "  if fault.startswith(('ct16-undo-','ct16-coupling-')) or fault in ['ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[555]!=0 and v[101]==0\n  elif fault.startswith(('ct6-undo-'")
model=(K/'model.py').read_text();a=model.index(' reached_c7=');block=model[a:model.index(" R['cases'].append",a)]
block=block.replace('not cpu_bad and not baseline and forward',"state['c13writes'] and v[1]")
for m in ['c7mask','c10mask','ct7mask','ct6mask','ct16mask']:block=block.replace('=='+m,'')
for start,end in [(430,460),(460,490),(490,520),(520,550),(550,580)]:
 tail='' if end==580 else str(end)
 before=f' else:assert v[{start}:{start+6}]==[0,0,0,0xffffffff,0xffffffff,0] and v[{start+6}:{tail}]==[0,0xffffffff,0xffffffff]*8'
 after=f' else:assert v[{start}:{end}]==([0]*30 if refusal or want<0x795 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)'
 assert before in block,before;block=block.replace(before,after)
a=s.index(' reached_c7=');z=s.index(' for lo,hi in [(0,0x880)',a);s=s[:a]+block+s[z:]
rep('v[261],v[435],v[465],v[495],v[525],v[520],v[523],v[524]','v[435],v[465],v[495],v[525],v[555],v[550],v[553],v[554]')
rep("try:\n for phase", """try:
 for phase in ['before','after','undo']:
  for j in range(9):run('ct16-'+phase+'-'+str(j),want=0x79539 if phase=='undo' else 0x79538,fault='ct16-'+phase+'-'+str(j))
 for j in range(1,9):run('ct16-coupling-'+str(j),want=0x79539,fault='ct16-coupling-'+str(j))
 for f in ['ct16-drop-write','ct16-wrong-write','ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo']:
  run(f,want=0x79538 if f in ['ct16-drop-write','ct16-wrong-write'] else 0x79539,fault=f)
 for phase""")
p.write_text(s,newline='\n')
print('Extended795 full bridge oracle; no hardware access')

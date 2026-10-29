"""Add independent CR07 display-end device behavior and fault cases to full bridge."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration009.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'ct16writes'","state={'cd7writes':0,'ct16writes'")
s=s.replace('0x79738]','0x79738,0x7973a]').replace('0x79738,0x797]','0x79738,0x7973a,0x797]')
rep('    if i==0x16:', '''    if i==7 and state['ct16writes']==1:
     state['cd7writes']+=1;n=state['cd7writes'];assert n<=2 and value==[54,116][n-1]
     assert state['ct6writes']==1 and state['ct7writes']==1 and word(1) in [0x7973a,0x797]
     assert [word(580),word(581),word(582)]==[116,54,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cd7-drop-write' if n==1 else 'cd7-drop-undo') or (n==2 and fault=='cd7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('cd7-wrong-write' if n==1 else 'cd7-wrong-undo') or (n==1 and fault=='cd7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('cd7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,16,18,21,22,24,37][j-1]]^=1
    elif i==0x16:''')
rep("state['ct16writes']+=1;n=state['ct16writes'];assert n<=2", "state['ct16writes']+=1;n=state['ct16writes'];assert n==1 or state['cd7writes']==2*word(582);assert n<=2")
rep("   i=sels[0x6013d4]\n", """   i=sels[0x6013d4]
   if i in [7,6,9,16,18,21,22,24,37] and state['ct16writes']==1 and word(1) in [0x7973a,0x797]:
    j=[7,6,9,16,18,21,22,24,37].index(i);phase=['before','after','undo'][state['cd7writes']]
    if fault=='cd7-'+phase+'-'+str(j):value^=1
""")
rep('    assert word(555)==0','    assert word(585)==0 and (not word(582) or word(584)==word(580))\n    assert word(555)==0')
rep('[(22,140),(22,237)]',"[(22,140)]+([(7,54),(7,116)] if state['cd7writes'] else [])+[(22,237)]")
rep("  if fault.startswith(('ct16-undo-'", "  if fault.startswith(('cd7-undo-','cd7-coupling-')) or fault in ['cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[585]!=0 and v[101]==0\n  elif fault.startswith(('ct16-undo-'")
model=(K/'model.py').read_text();a=model.index(' reached_c7=');block=model[a:model.index(" R['cases'].append",a)]
block=block.replace('not cpu_bad and not baseline and forward',"state['c13writes'] and v[1]")
for m in ['c7mask','c10mask','ct7mask','ct6mask','ct16mask','cd7mask']:block=block.replace('=='+m,'')
for start,end in [(430,460),(460,490),(490,520),(520,550),(550,580),(580,610)]:
 tail='' if end==610 else str(end)
 before=f' else:assert v[{start}:{start+6}]==[0,0,0,0xffffffff,0xffffffff,0] and v[{start+6}:{tail}]==[0,0xffffffff,0xffffffff]*8'
 after=f' else:assert v[{start}:{end}]==([0]*30 if refusal or want<0x797 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)'
 assert before in block,before;block=block.replace(before,after)
a=s.index(' reached_c7=');z=s.index(' for lo,hi in [(0,0x880)',a);s=s[:a]+block+s[z:]
rep('v[435],v[465],v[495],v[525],v[555],v[550],v[553],v[554]','v[465],v[495],v[525],v[555],v[585],v[580],v[583],v[584]')
rep("try:\n for phase", """try:
 for phase in ['before','after','undo']:
  for j in range(9):run('cd7-'+phase+'-'+str(j),want=0x7973b if phase=='undo' else 0x7973a,fault='cd7-'+phase+'-'+str(j))
 for j in range(1,9):run('cd7-coupling-'+str(j),want=0x7973b,fault='cd7-coupling-'+str(j))
 for f in ['cd7-drop-write','cd7-wrong-write','cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo']:
  run(f,want=0x7973a if f in ['cd7-drop-write','cd7-wrong-write'] else 0x7973b,fault=f)
 for phase""")
p.write_bytes(s.encode());print('Extended797 bridge oracle; no hardware access')

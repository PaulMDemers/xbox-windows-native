"""Add independently specified CR12 device behavior to native full-bridge tests."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration010.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
rep("state={'cd7writes'","state={'cd12writes':0,'cd7writes'")
s=s.replace('0x7993a]','0x7993a,0x7993c]').replace('0x7993a,0x799]','0x7993a,0x7993c,0x799]')
rep("    if i==7 and state['ct16writes']==1:","""    if i==0x12:
     state['cd12writes']+=1;n=state['cd12writes'];assert n<=2 and value==[223,207][n-1]
     assert state['cd7writes']==1 and state['ct16writes']==1 and word(1) in [0x7993c,0x799]
     assert [word(610),word(611),word(612)]==[207,223,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cd12-drop-write' if n==1 else 'cd12-drop-undo') or (n==2 and fault=='cd12-wrong-write-drop-undo'):return
     cr[18]=value
     if fault==('cd12-wrong-write' if n==1 else 'cd12-wrong-undo') or (n==1 and fault=='cd12-wrong-write-drop-undo'):cr[18]^=1
     if n==1 and fault.startswith('cd12-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,16,21,22,24,37][j-1]]^=1
    elif i==7 and state['ct16writes']==1:""")
rep("state['cd7writes']+=1;n=state['cd7writes'];assert n<=2", "state['cd7writes']+=1;n=state['cd7writes'];assert n==1 or state['cd12writes']==2*word(612);assert n<=2")
rep("   i=sels[0x6013d4]\n", """   i=sels[0x6013d4]
   if i in [18,6,7,9,16,21,22,24,37] and state['cd7writes']==1 and word(1) in [0x7993c,0x799]:
    j=[18,6,7,9,16,21,22,24,37].index(i);phase=['before','after','undo'][state['cd12writes']]
    if fault=='cd12-'+phase+'-'+str(j):value^=1
""")
rep('    assert word(585)==0','    assert word(615)==0 and (not word(612) or word(614)==word(610))\n    assert word(585)==0')
rep('[(7,54),(7,116)]',"[(7,54)]+([(18,223),(18,207)] if state['cd12writes'] else [])+[(7,116)]")
rep("  if fault.startswith(('cd7-undo-'", "  if fault.startswith(('cd12-undo-','cd12-coupling-')) or fault in ['cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[615]!=0 and v[101]==0\n  elif fault.startswith(('cd7-undo-'")
model=(K/'model.py').read_text();a=model.index(' reached_c7=');block=model[a:model.index(" R['cases'].append",a)]
block=block.replace('not cpu_bad and not baseline and forward',"state['c13writes'] and v[1]")
for m in ['c7mask','c10mask','ct7mask','ct6mask','ct16mask','cd7mask','cd12mask']:block=block.replace('=='+m,'')
for start,end in [(430,460),(460,490),(490,520),(520,550),(550,580),(580,610),(610,640)]:
 tail='' if end==640 else str(end)
 before=f' else:assert v[{start}:{start+6}]==[0,0,0,0xffffffff,0xffffffff,0] and v[{start+6}:{tail}]==[0,0xffffffff,0xffffffff]*8'
 after=f' else:assert v[{start}:{end}]==([0]*30 if refusal or want<0x799 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)'
 assert before in block,before;block=block.replace(before,after)
a=s.index(' reached_c7=');z=s.index(' for lo,hi in [(0,0x880)',a);s=s[:a]+block+s[z:]
rep('v[465],v[495],v[525],v[555],v[585],v[580],v[583],v[584]','v[495],v[525],v[555],v[585],v[615],v[610],v[613],v[614]')
rep("try:\n for phase", """try:
 for phase in ['before','after','undo']:
  for j in range(9):run('cd12-'+phase+'-'+str(j),want=0x7993d if phase=='undo' else 0x7993c,fault='cd12-'+phase+'-'+str(j))
 for j in range(1,9):run('cd12-coupling-'+str(j),want=0x7993d,fault='cd12-coupling-'+str(j))
 for f in ['cd12-drop-write','cd12-wrong-write','cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo']:
  run(f,want=0x7993c if f in ['cd12-drop-write','cd12-wrong-write'] else 0x7993d,fault=f)
 for phase""")
assert s.count('op+580')==2
p.write_bytes(s.encode());print('Extended799 bridge oracle; no hardware access')

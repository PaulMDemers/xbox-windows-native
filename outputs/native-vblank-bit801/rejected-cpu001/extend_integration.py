"""Add independent CR09 behavior/faults to fresh801 complete bridge execution."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration010.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
rep("state={'cd12writes'","state={'cb9writes':0,'cd12writes'")
s=s.replace('0x8013c]','0x8013c,0x8013e]').replace('0x8013c,0x801]','0x8013c,0x8013e,0x801]')
rep('    if i==0x12:',"""    if i==9:
     state['cb9writes']+=1;n=state['cb9writes'];assert n<=2 and value==[64,96][n-1]
     assert state['cd12writes']==1 and word(1) in [0x8013e,0x801]
     assert [word(640),word(641),word(642)]==[96,64,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cb9-drop-write' if n==1 else 'cb9-drop-undo') or (n==2 and fault=='cb9-wrong-write-drop-undo'):return
     cr[9]=value
     if fault==('cb9-wrong-write' if n==1 else 'cb9-wrong-undo') or (n==1 and fault=='cb9-wrong-write-drop-undo'):cr[9]^=1
     if n==1 and fault.startswith('cb9-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,16,18,21,22,24,37][j-1]]^=1
    elif i==0x12:""")
rep("state['cd12writes']+=1;n=state['cd12writes'];assert n<=2", "state['cd12writes']+=1;n=state['cd12writes'];assert n==1 or state['cb9writes']==2*word(642);assert n<=2")
rep('   i=sels[0x6013d4]\n',"""   i=sels[0x6013d4]
   if i in [9,6,7,16,18,21,22,24,37] and state['cd12writes']==1 and word(1) in [0x8013e,0x801]:
    j=[9,6,7,16,18,21,22,24,37].index(i);phase=['before','after','undo'][state['cb9writes']]
    if fault=='cb9-'+phase+'-'+str(j):value^=1
""")
rep('    assert word(615)==0','    assert word(645)==0 and (not word(642) or word(644)==word(640))\n    assert word(615)==0')
rep('[(18,223),(18,207)]','[(18,223)]+([(9,64),(9,96)] if state[\'cb9writes\'] else [])+[(18,207)]')
rep("  if fault.startswith(('cd12-undo-'", "  if fault.startswith(('cb9-undo-','cb9-coupling-')) or fault in ['cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[645]!=0 and v[101]==0\n  elif fault.startswith(('cd12-undo-'")
model=(K/'model002.py').read_text();a=model.index(' reached_c7=');block=model[a:model.index(" R['cases'].append",a)]
block=block.replace('not cpu_bad and not baseline and forward',"state['c13writes'] and v[1]")
for m in ['c7mask','c10mask','ct7mask','ct6mask','ct16mask','cd7mask','cd12mask','cb9mask']:block=block.replace('=='+m,'')
for start,end in [(430,460),(460,490),(490,520),(520,550),(550,580),(580,610),(610,640),(640,670)]:
 tail='' if end==670 else str(end)
 before=f' else:assert v[{start}:{start+6}]==[0,0,0,0xffffffff,0xffffffff,0] and v[{start+6}:{tail}]==[0,0xffffffff,0xffffffff]*8'
 after=f' else:assert v[{start}:{end}]==([0]*30 if refusal or want<0x801 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)'
 assert before in block,before;block=block.replace(before,after)
a=s.index(' reached_c7=');z=s.index(' for lo,hi in [(0,0x880)',a);s=s[:a]+block+s[z:]
rep('v[495],v[525],v[555],v[585],v[615],v[610],v[613],v[614]','v[525],v[555],v[585],v[615],v[645],v[640],v[643],v[644]')
rep('try:\n for phase',"""try:
 for phase in ['before','after','undo']:
  for j in range(9):run('cb9-'+phase+'-'+str(j),want=0x8013f if phase=='undo' else 0x8013e,fault='cb9-'+phase+'-'+str(j))
 for j in range(1,9):run('cb9-coupling-'+str(j),want=0x8013f,fault='cb9-coupling-'+str(j))
 for f in ['cb9-drop-write','cb9-wrong-write','cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:
  run(f,want=0x8013e if f in ['cb9-drop-write','cb9-wrong-write'] else 0x8013f,fault=f)
 for phase""")
p.write_bytes(s.encode());print('Extended801 full bridge oracle')

"""Extend806 full bridge oracle with explicit CR15 faults and reverse recovery."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration012.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
rep("state={'cb7writes'","state={'cb15writes':0,'cb7writes'")
s=s.replace('0x80640]','0x80640,0x80642]').replace('0x80640,0x806]','0x80640,0x80642,0x806]')
rep("    if i==7 and state['cb9writes']==1:","""    if i==0x15:
     state['cb15writes']+=1;n=state['cb15writes'];assert n<=2 and value==[223,207][n-1]
     assert state['cb7writes']==1 and word(1) in [0x80642,0x806]
     assert [word(700),word(701),word(702)]==[207,223,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cb15-drop-write' if n==1 else 'cb15-drop-undo') or (n==2 and fault=='cb15-wrong-write-drop-undo'):return
     cr[21]=value
     if fault==('cb15-wrong-write' if n==1 else 'cb15-wrong-undo') or (n==1 and fault=='cb15-wrong-write-drop-undo'):cr[21]^=1
     if n==1 and fault.startswith('cb15-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,16,18,22,24,37][j-1]]^=1
    elif i==7 and state['cb9writes']==1:""")
rep("state['cb7writes']+=1;n=state['cb7writes'];assert n<=2", "state['cb7writes']+=1;n=state['cb7writes'];assert n==1 or state['cb15writes']==2*word(702);assert n<=2")
rep('   i=sels[0x6013d4]\n',"""   i=sels[0x6013d4]
   if i in [21,6,7,9,16,18,22,24,37] and state['cb7writes']==1 and word(1) in [0x80642,0x806]:
    j=[21,6,7,9,16,18,22,24,37].index(i);phase=['before','after','undo'][state['cb15writes']]
    if fault=='cb15-'+phase+'-'+str(j):value^=1
""")
rep('    assert word(675)==0','    assert word(705)==0 and (not word(702) or word(704)==word(700))\n    assert word(675)==0')
rep('[(7,62),(7,54)]',"[(7,62)]+([(21,223),(21,207)] if state['cb15writes'] else [])+[(7,54)]")
rep("  if fault.startswith(('cb7-undo-'", "  if fault.startswith(('cb15-undo-','cb15-coupling-')) or fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[705]!=0 and v[101]==0\n  elif fault.startswith(('cb7-undo-'")
model=(K/'model002.py').read_text();a=model.index(' reached_c7=');block=model[a:model.index(" R['cases'].append",a)]
block=block.replace('not cpu_bad and not baseline and forward',"state['c13writes'] and v[1]")
for m in ['c7mask','c10mask','ct7mask','ct6mask','ct16mask','cd7mask','cd12mask','cb9mask','cb7mask','cb15mask']:block=block.replace('=='+m,'')
for start in range(430,730,30):
 end=start+30;tail='' if end==730 else str(end)
 before=f' else:assert v[{start}:{start+6}]==[0,0,0,0xffffffff,0xffffffff,0] and v[{start+6}:{tail}]==[0,0xffffffff,0xffffffff]*8'
 after=f' else:assert v[{start}:{end}]==([0]*30 if refusal or want<0x806 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)'
 assert before in block,before;block=block.replace(before,after)
a=s.index(' reached_c7=');z=s.index(' for lo,hi in [(0,0x880)',a);s=s[:a]+block+s[z:]
rep('v[555],v[585],v[615],v[645],v[675],v[670],v[673],v[674]','v[585],v[615],v[645],v[675],v[705],v[700],v[703],v[704]')
rep('try:\n for phase',"""try:
 for phase in ['before','after','undo']:
  for j in range(9):run('cb15-'+phase+'-'+str(j),want=0x80643 if phase=='undo' else 0x80642,fault='cb15-'+phase+'-'+str(j))
 for j in range(1,9):run('cb15-coupling-'+str(j),want=0x80643,fault='cb15-coupling-'+str(j))
 for f in ['cb15-drop-write','cb15-wrong-write','cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:
  run(f,want=0x80642 if f in ['cb15-drop-write','cb15-wrong-write'] else 0x80643,fault=f)
 for phase""")
p.write_bytes(s.encode())
print('806 full-bridge CR15 fault coverage added')

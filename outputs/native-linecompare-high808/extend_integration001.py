"""Add independent CR07 high-linecompare faults to relocated808 bridge checks."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration012.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
rep("state={'cb15writes'","state={'cl7writes':0,'cb15writes'")
s=s.replace('0x80842]','0x80842,0x80844]').replace('0x80842,0x808]','0x80842,0x80844,0x808]')
rep('    if i==0x15:',"""    if i==7 and state['cb15writes']==1 and word(1) in [0x80844,0x808]:
     state['cl7writes']+=1;n=state['cl7writes'];assert n<=2 and value==62
     assert [word(730),word(731),word(732)]==[62,62,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cl7-drop-write' if n==1 else 'cl7-drop-undo') or (n==2 and fault=='cl7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('cl7-wrong-write' if n==1 else 'cl7-wrong-undo') or (n==1 and fault=='cl7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('cl7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,16,18,21,22,24,37][j-1]]^=1
    elif i==0x15:""")
rep("state['cb15writes']+=1;n=state['cb15writes'];assert n<=2", "state['cb15writes']+=1;n=state['cb15writes'];assert n==1 or state['cl7writes']==2*word(732);assert n<=2")
rep('   i=sels[0x6013d4]\n',"""   i=sels[0x6013d4]
   if i in [7,6,9,16,18,21,22,24,37] and state['cb15writes']==1 and word(1) in [0x80844,0x808]:
    j=[7,6,9,16,18,21,22,24,37].index(i);phase=['before','after','undo'][state['cl7writes']]
    if fault=='cl7-'+phase+'-'+str(j):value^=1
""")
rep('    assert word(705)==0','    assert word(735)==0 and (not word(732) or word(734)==word(730))\n    assert word(705)==0')
rep('[(21,223),(21,207)]',"[(21,223)]+([(7,62),(7,62)] if state['cl7writes'] else [])+[(21,207)]")
rep("  if fault.startswith(('cb15-undo-'", "  if fault.startswith(('cl7-undo-','cl7-coupling-')) or fault in ['cl7-wrong-undo','cl7-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[735]!=0 and v[101]==0\n  elif fault.startswith(('cb15-undo-'")
model=(K/'model002.py').read_text();a=model.index(' reached_c7=');block=model[a:model.index(" R['cases'].append",a)]
block=block.replace('not cpu_bad and not baseline and forward',"state['c13writes'] and v[1]")
for m in ['c7mask','c10mask','ct7mask','ct6mask','ct16mask','cd7mask','cd12mask','cb9mask','cb7mask','cb15mask','cl7mask']:block=block.replace('=='+m,'')
for start in range(430,760,30):
 end=start+30;tail='' if end==760 else str(end)
 before=f' else:assert v[{start}:{start+6}]==[0,0,0,0xffffffff,0xffffffff,0] and v[{start+6}:{tail}]==[0,0xffffffff,0xffffffff]*8'
 after=f' else:assert v[{start}:{end}]==([0]*30 if refusal or want<0x808 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)'
 assert before in block,before;block=block.replace(before,after)
a=s.index(' reached_c7=');z=s.index(' for lo,hi in [(0,0x880)',a);s=s[:a]+block+s[z:]
rep('v[585],v[615],v[645],v[675],v[705],v[700],v[703],v[704]','v[615],v[645],v[675],v[705],v[735],v[730],v[733],v[734]')
rep('try:\n for phase',"""try:
 for phase in ['before','after','undo']:
  for j in range(9):run('cl7-'+phase+'-'+str(j),want=0x80845 if phase=='undo' else 0x80844,fault='cl7-'+phase+'-'+str(j))
 for j in range(1,9):run('cl7-coupling-'+str(j),want=0x80845,fault='cl7-coupling-'+str(j))
 for f in ['cl7-drop-write','cl7-wrong-write','cl7-drop-undo','cl7-wrong-undo','cl7-wrong-write-drop-undo']:
  run(f,want=0x808 if f in ['cl7-drop-write','cl7-drop-undo'] else 0x80844 if f=='cl7-wrong-write' else 0x80845,fault=f)
 for phase""")
p.write_bytes(s.encode())
print('808 bridge CR07 high-linecompare fault coverage added')

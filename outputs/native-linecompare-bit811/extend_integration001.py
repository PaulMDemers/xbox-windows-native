"""Append CR09 bit6 cases to the relocated bridge's independent device oracle."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration012.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
rep("state={'cl7writes'","state={'cl9writes':0,'cl7writes'")
s=s.replace('0x81144]','0x81144,0x81146]').replace('0x81144,0x811]','0x81144,0x81146,0x811]')
rep("    if i==7 and state['cb15writes']==1", """    if i==9 and state['cl7writes']==1 and word(1) in [0x81146,0x811]:
     state['cl9writes']+=1;n=state['cl9writes'];assert n<=2 and value==64
     assert [word(760),word(761),word(762)]==[64,64,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cl9-drop-write' if n==1 else 'cl9-drop-undo') or (n==2 and fault=='cl9-wrong-write-drop-undo'):return
     cr[9]=value
     if fault==('cl9-wrong-write' if n==1 else 'cl9-wrong-undo') or (n==1 and fault=='cl9-wrong-write-drop-undo'):cr[9]^=1
     if n==1 and fault.startswith('cl9-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,16,18,21,22,24,37][j-1]]^=1
    elif i==7 and state['cb15writes']==1""")
rep("state['cl7writes']+=1;n=state['cl7writes'];assert n<=2", "state['cl7writes']+=1;n=state['cl7writes'];assert n==1 or state['cl9writes']==2*word(762);assert n<=2")
rep('   i=sels[0x6013d4]\n',"""   i=sels[0x6013d4]
   if i in [9,6,7,16,18,21,22,24,37] and state['cl7writes']==1 and word(1) in [0x81146,0x811]:
    j=[9,6,7,16,18,21,22,24,37].index(i);phase=['before','after','undo'][state['cl9writes']]
    if fault=='cl9-'+phase+'-'+str(j):value^=1
""")
rep('    assert word(735)==0','    assert word(765)==0 and (not word(762) or word(764)==word(760))\n    assert word(735)==0')
rep('[(7,62),(7,62)]',"[(7,62)]+([(9,64),(9,64)] if state['cl9writes'] else [])+[(7,62)]")
rep("  if fault.startswith(('cl7-undo-'", "  if fault.startswith(('cl9-undo-','cl9-coupling-')) or fault in ['cl9-wrong-undo','cl9-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[765]!=0 and v[101]==0\n  elif fault.startswith(('cl7-undo-'")
model=(K/'model002.py').read_text();a=model.index(' reached_c7=');block=model[a:model.index(" R['cases'].append",a)]
block=block.replace('not cpu_bad and not baseline and forward',"state['c13writes'] and v[1]")
for m in ['c7mask','c10mask','ct7mask','ct6mask','ct16mask','cd7mask','cd12mask','cb9mask','cb7mask','cb15mask','cl7mask','cl9mask']:block=block.replace('=='+m,'')
for start in range(430,790,30):
 end=start+30;tail='' if end==790 else str(end)
 before=f' else:assert v[{start}:{start+6}]==[0,0,0,0xffffffff,0xffffffff,0] and v[{start+6}:{tail}]==[0,0xffffffff,0xffffffff]*8'
 after=f' else:assert v[{start}:{end}]==([0]*30 if refusal or want<0x811 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)'
 assert before in block,before;block=block.replace(before,after)
a=s.index(' reached_c7=');z=s.index(' for lo,hi in [(0,0x880)',a);s=s[:a]+block+s[z:]
rep('v[615],v[645],v[675],v[705],v[735],v[730],v[733],v[734]','v[645],v[675],v[705],v[735],v[765],v[760],v[763],v[764]')
rep('try:\n for phase',"""try:
 for phase in ['before','after','undo']:
  for j in range(9):run('cl9-'+phase+'-'+str(j),want=0x81147 if phase=='undo' else 0x81146,fault='cl9-'+phase+'-'+str(j))
 for j in range(1,9):run('cl9-coupling-'+str(j),want=0x81147,fault='cl9-coupling-'+str(j))
 for f in ['cl9-drop-write','cl9-wrong-write','cl9-drop-undo','cl9-wrong-undo','cl9-wrong-write-drop-undo']:
  run(f,want=0x811 if f in ['cl9-drop-write','cl9-drop-undo'] else 0x81146 if f=='cl9-wrong-write' else 0x81147,fault=f)
 for phase""")
p.write_bytes(s.encode())
print('811 relocated bridge adds40 CR09 cases; all earlier assertions retained')

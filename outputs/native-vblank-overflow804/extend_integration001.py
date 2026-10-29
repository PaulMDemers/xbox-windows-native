"""Extend804 full bridge oracle with independent CR07 blank-start fault outcomes."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration012.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
rep("state={'cb9writes'","state={'cb7writes':0,'cb9writes'")
s=s.replace('0x8043e]','0x8043e,0x80440]').replace('0x8043e,0x804]','0x8043e,0x80440,0x804]')
rep('    if i==9:',"""    if i==7 and state['cb9writes']==1:
     state['cb7writes']+=1;n=state['cb7writes'];assert n<=2 and value==[62,54][n-1]
     assert state['cd12writes']==1 and word(1) in [0x80440,0x804]
     assert [word(670),word(671),word(672)]==[54,62,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('cb7-drop-write' if n==1 else 'cb7-drop-undo') or (n==2 and fault=='cb7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('cb7-wrong-write' if n==1 else 'cb7-wrong-undo') or (n==1 and fault=='cb7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('cb7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,16,18,21,22,24,37][j-1]]^=1
    elif i==9:""")
rep("state['cb9writes']+=1;n=state['cb9writes'];assert n<=2", "state['cb9writes']+=1;n=state['cb9writes'];assert n==1 or state['cb7writes']==2*word(672);assert n<=2")
rep('   i=sels[0x6013d4]\n',"""   i=sels[0x6013d4]
   if i in [7,6,9,16,18,21,22,24,37] and state['cb9writes']==1 and word(1) in [0x80440,0x804]:
    j=[7,6,9,16,18,21,22,24,37].index(i);phase=['before','after','undo'][state['cb7writes']]
    if fault=='cb7-'+phase+'-'+str(j):value^=1
""")
rep('    assert word(645)==0','    assert word(675)==0 and (not word(672) or word(674)==word(670))\n    assert word(645)==0')
rep('[(9,64),(9,96)]',"[(9,64)]+([(7,62),(7,54)] if state['cb7writes'] else [])+[(9,96)]")
rep("  if fault.startswith(('cb9-undo-'", "  if fault.startswith(('cb7-undo-','cb7-coupling-')) or fault in ['cb7-drop-undo','cb7-wrong-undo','cb7-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[675]!=0 and v[101]==0\n  elif fault.startswith(('cb9-undo-'")
model=(K/'model002.py').read_text();a=model.index(' reached_c7=');block=model[a:model.index(" R['cases'].append",a)]
block=block.replace('not cpu_bad and not baseline and forward',"state['c13writes'] and v[1]")
for m in ['c7mask','c10mask','ct7mask','ct6mask','ct16mask','cd7mask','cd12mask','cb9mask','cb7mask']:block=block.replace('=='+m,'')
for start in range(430,700,30):
 end=start+30;tail='' if end==700 else str(end)
 before=f' else:assert v[{start}:{start+6}]==[0,0,0,0xffffffff,0xffffffff,0] and v[{start+6}:{tail}]==[0,0xffffffff,0xffffffff]*8'
 after=f' else:assert v[{start}:{end}]==([0]*30 if refusal or want<0x804 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)'
 assert before in block,before;block=block.replace(before,after)
a=s.index(' reached_c7=');z=s.index(' for lo,hi in [(0,0x880)',a);s=s[:a]+block+s[z:]
rep('v[525],v[555],v[585],v[615],v[645],v[640],v[643],v[644]','v[555],v[585],v[615],v[645],v[675],v[670],v[673],v[674]')
rep('try:\n for phase',"""try:
 for phase in ['before','after','undo']:
  for j in range(9):run('cb7-'+phase+'-'+str(j),want=0x80441 if phase=='undo' else 0x80440,fault='cb7-'+phase+'-'+str(j))
 for j in range(1,9):run('cb7-coupling-'+str(j),want=0x80441,fault='cb7-coupling-'+str(j))
 for f in ['cb7-drop-write','cb7-wrong-write','cb7-drop-undo','cb7-wrong-undo','cb7-wrong-write-drop-undo']:
  run(f,want=0x80440 if f in ['cb7-drop-write','cb7-wrong-write'] else 0x80441,fault=f)
 for phase""")
p.write_bytes(s.encode())
# Explicit independent report offsets and full relocation mutation coverage.
p=K/'optical_review005.py';s=p.read_text();a=s.index('offsets = (');z=s.index('\nr =',a)
s=s[:a]+'offsets = '+repr(tuple([0x8d4]+[0x68c0+4*j for j in [30,100,108,555,585,615,645,675,670,673,674]]))+s[z:];p.write_bytes(s.encode())
for n in ['page_review008.py','page_boundary009.py']:
 p=K/n;s=p.read_text().replace('range(14)','range(15)');p.write_bytes(s.encode())
print('Extended804 integration and report bounds, before any host build')

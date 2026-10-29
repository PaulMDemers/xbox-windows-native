"""Extend independent full-bridge oracle for shared CR07 total operation."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration007.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'c10writes'","state={'ct7writes':0,'c10writes'")
s=s.replace('0x79132]','0x79132,0x79134]').replace('0x79132,0x791]','0x79132,0x79134,0x791]')
rep('    if i==0x10:', '''    if i==7 and state['c10writes']==1:
     state['ct7writes']+=1;n=state['ct7writes'];assert n<=2 and value==116
     assert state['c7writes']==1 and word(1) in [0x79134,0x791]
     assert [word(490),word(491),word(492)]==[116,116,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('ct7-drop-write' if n==1 else 'ct7-drop-undo') or (n==2 and fault=='ct7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('ct7-wrong-write' if n==1 else 'ct7-wrong-undo') or (n==1 and fault=='ct7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('ct7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,0x10,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
    elif i==0x10:''')
rep("state['c10writes']+=1;n=state['c10writes'];assert n<=2", "state['c10writes']+=1;n=state['c10writes'];assert n==1 or state['ct7writes']==2*word(492);assert n<=2")
rep("   i=sels[0x6013d4]\n", """   i=sels[0x6013d4]
   if i in [7,6,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['c10writes']==1 and word(1) in [0x79134,0x791]:
    j=[7,6,9,0x10,0x12,0x15,0x16,0x18,0x25].index(i);phase=['before','after','undo'][state['ct7writes']]
    if fault=='ct7-'+phase+'-'+str(j):value^=1
""")
rep('    assert word(465)==0','    assert word(495)==0 and (not word(492) or word(494)==word(490))\n    assert word(465)==0')
rep('[(16,233),(16,212)]',"[(16,233)]+([(7,116),(7,116)] if state['ct7writes'] else [])+[(16,212)]")
rep("  if fault.startswith(('c10-undo-'", "  if fault.startswith(('ct7-undo-','ct7-coupling-')) or fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[495]!=0 and v[101]==0\n  elif fault.startswith(('c10-undo-'")
model=(K/'model.py').read_text();a=model.index(' reached_c7=');block=model[a:model.index(" R['cases'].append",a)]
block=block.replace('not cpu_bad and not baseline and forward',"state['c13writes'] and v[1]").replace('==c7mask','').replace('==c10mask','').replace('==ct7mask','')
for start,end in [(430,460),(460,490),(490,520)]:
 tail='' if end==520 else str(end)
 before=f' else:assert v[{start}:{start+6}]==[0,0,0,0xffffffff,0xffffffff,0] and v[{start+6}:{tail}]==[0,0xffffffff,0xffffffff]*8'
 after=f' else:assert v[{start}:{end}]==([0]*30 if refusal or want<0x791 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)'
 assert before in block,before;block=block.replace(before,after)
a=s.index(' reached_c7=');z=s.index(' for lo,hi in [(0,0x880)',a);s=s[:a]+block+s[z:]
rep('v[261],v[285],v[435],v[465],v[460],v[463],v[464]','v[261],v[435],v[465],v[495],v[490],v[493],v[494]')
rep("try:\n for phase", """try:
 for phase in ['before','after','undo']:
  for j in range(9):run('ct7-'+phase+'-'+str(j),want=0x79135 if phase=='undo' else 0x79134,fault='ct7-'+phase+'-'+str(j))
 for j in range(1,9):run('ct7-coupling-'+str(j),want=0x79135,fault='ct7-coupling-'+str(j))
 for f in ['ct7-drop-write','ct7-wrong-write','ct7-drop-undo','ct7-wrong-undo','ct7-wrong-write-drop-undo']:
  run(f,want=0x791 if f in ['ct7-drop-write','ct7-drop-undo'] else 0x79134 if f=='ct7-wrong-write' else 0x79135,fault=f)
 for phase""")
p.write_text(s,newline='\n')
print('Extended791 full-path oracle; no hardware access')

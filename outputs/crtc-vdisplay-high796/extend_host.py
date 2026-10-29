"""Extend the actual compiled-code oracle and independent schema for CR07 display end."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model.py';s=p.read_text()
def replace(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'ct16writes'","state={'cd7writes':0,'ct16writes'")
s=s.replace('0x201910','0x201988').replace('0x56f0','0x5678').replace("'<580I',c.mem_read(0x201000,2320)","'<610I',c.mem_read(0x201000,2440)")
s=s.replace('0x79638]','0x79638,0x7963a]').replace('0x79638,0x796]','0x79638,0x7963a,0x796]').replace('v[556:]==','v[556:580]==')
replace('    if idx==0x16:', '''    if idx==7 and state['ct16writes']==1:
     assert state['ct6writes']==1 and state['ct7writes']==1 and word(1) in [0x7963a,0x796]
     state['cd7writes']+=1;n=state['cd7writes'];assert n<=2
     assert [word(580),word(581),word(582)]==[116,54,1] and value==[54,116][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',7,value])
     if fault==('cd7-drop-write' if n==1 else 'cd7-drop-undo') or (n==2 and fault=='cd7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('cd7-wrong-write' if n==1 else 'cd7-wrong-undo') or (n==1 and fault=='cd7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('cd7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,16,18,21,22,24,37][j-1]]^=1
     return
    if idx==0x16:''')
replace("state['ct16writes']+=1;n=state['ct16writes'];assert n<=2","state['ct16writes']+=1;n=state['ct16writes'];assert n<=2\n     if n==2:assert state['cd7writes']==2*word(582)")
replace('   val=cr[idx]', '''   val=cr[idx]
   if idx in [7,6,9,16,18,21,22,24,37] and state['ct16writes']==1 and word(1) in [0x7963a,0x796]:
    j=[7,6,9,16,18,21,22,24,37].index(idx);phase=['before','after','undo'][state['cd7writes']]
    if fault=='cd7-'+phase+'-'+str(j):val^=1
''')
replace('  if val==4:\n','  if val==4:\n   assert word(585)==0 and (not word(582) or word(584)==word(580))\n')
for label,mapping,own in [('ct16',{1:2,2:8,3:16,4:32,5:64,6:0,7:128,8:256},4),('ct6',{1:0,2:4,3:8,4:16,5:32,6:0,7:128,8:256},2),('ct7',{1:0,2:4,3:8,4:16,5:32,6:0,7:128,8:256},0),('c10',{1:0,2:8,3:0,4:16,5:32,6:0,7:128,8:256},0),('c7',{1:0,2:4,3:0,4:16,5:32,6:0,7:128,8:256},0)]:
 token='  '+label+'bad=bool('+label+'mask)'
 replace(token,"  if fault in ['cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo']:"+label+'mask|='+str(own)+"\n  if fault.startswith('cd7-coupling-'):\n   j=int(fault.rsplit('-',1)[1]);"+label+'mask|='+repr(mapping)+'[j]\n'+token)
replace('  ct16bad=bool(ct16mask)', '''  ct16bad=bool(ct16mask)
  cd7mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('cd7-undo-','cd7-coupling-')) else 1 if fault in ['cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo'] else 0
  cd7bad=bool(cd7mask)''')
s=s.replace('or ct16bad','or ct16bad or cd7bad')
replace('else 0x796\n  assert v[1]==forward',"else 0x7963a if fault.startswith(('cd7-before-','cd7-after-','cd7-coupling-')) or fault in ['cd7-drop-write','cd7-wrong-write','cd7-wrong-write-drop-undo'] else 0x796\n  assert v[1]==forward")
replace("[['cr',22,140],['cr',22,237]]","[['cr',22,140]]+([['cr',7,54],['cr',7,116]] if forward in [0x796,0x7963a] and not fault.startswith('cd7-before-') else [])+[['cr',22,237]]")
s=s.replace('else 0x79639 if ct16bad','else 0x7963b if cd7bad else 0x79639 if ct16bad')
for token,mapping,own in [("   if fault=='c7-wrong-undo':undo[0]^=1",{2:2,4:4,5:5,7:7,8:8},None),("   if fault=='c10-wrong-undo':undo[0]^=1",{2:3,4:4,5:5,7:7,8:8},None),("   if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:undo[0]^=1",{2:2,3:3,4:4,5:5,7:7,8:8},None),("   if fault=='ct6-wrong-undo':undo[0]=237",{2:2,3:3,4:4,5:5,7:7,8:8},1),("   if fault=='ct16-wrong-undo':undo[0]=236",{1:1,2:3,3:4,4:5,5:6,7:7,8:8},2)]:
 extra=''
 if own is not None:
  extra="\n   if fault=='cd7-drop-undo':undo["+str(own)+"]=54\n   if fault=='cd7-wrong-undo':undo["+str(own)+"]=117\n   if fault=='cd7-wrong-write-drop-undo':undo["+str(own)+"]=55"
 replace(token,token+extra+"\n   if fault.startswith('cd7-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n    if j in mapping:undo[mapping[j]]^=1")
replace(" R['cases'].append(",''' # Independently specified CR07 display-end target and complete neighboring tuple.
 reached_cd7=not cpu_bad and not baseline and forward in [0x796,0x7963a]
 if reached_cd7:
  ref=[116,12,96,233,207,207,140,255,16];before=ref.copy()
  attempted_cd7=not fault.startswith('cd7-before-')
  if not attempted_cd7:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[580]]+[v[586+3*i] for i in range(8)]==before
  assert v[581:583]==([54,1] if attempted_cd7 else [0,0]) and state['cd7writes']==2*int(attempted_cd7)
  if attempted_cd7:
   after=ref.copy();after[0]=54;undo=ref.copy()
   if fault=='cd7-drop-write':after[0]=116
   if fault in ['cd7-wrong-write','cd7-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cd7-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cd7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cd7-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='cd7-drop-undo':undo[0]=54
   if fault=='cd7-wrong-undo':undo[0]=117
   if fault=='cd7-wrong-write-drop-undo':undo[0]=55
   assert [v[583]]+[v[587+3*i] for i in range(8)]==after
   assert [v[584]]+[v[588+3*i] for i in range(8)]==undo
   assert v[585]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==cd7mask
  else:assert v[583:586]==[0xffffffff,0xffffffff,0] and all(v[587+3*i:589+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[580:586]==[0,0,0,0xffffffff,0xffffffff,0] and v[586:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('cd7-'+phase+'-'+str(j),fault='cd7-'+phase+'-'+str(j))\n for j in range(1,9):run('cd7-coupling-'+str(j),fault='cd7-coupling-'+str(j))\n for f in ['cd7-drop-write','cd7-wrong-write','cd7-drop-undo','cd7-wrong-undo','cd7-wrong-write-drop-undo']:run(f,fault=f)")
p.write_bytes(s.encode())
p=K/'audit_logic.py';s=p.read_text().replace('580-word','610-word').replace('len(v)==580','len(v)==610').replace('0x79638]','0x79638,0x7963a]').replace('(forward==0x796)','(forward in [0x796,0x7963a])').replace('v[556:]==','v[556:580]==')
code=''' cb7d,ct7d,ca7d,cf7d,cu7d,cm7d=v[580:586]
 cn7d=[v[586+3*i] for i in range(8)];cfns7d=[v[587+3*i] for i in range(8)];cuns7d=[v[588+3*i] for i in range(8)]
 assert ca7d in [0,1] and 0<=cm7d<512
 if forward in [0x796,0x7963a]:
  assert ca7d==int([cb7d]+cn7d==[116,12,96,233,207,207,140,255,16])
  if ca7d:
   assert ct7d==54
   assert cm7d==sum(1<<i for i,(a,b) in enumerate(zip([cu7d]+cuns7d,[cb7d]+cn7d)) if a!=b)
   assert (cf7d==54 and cfns7d==cn7d)==(forward==0x796)
  else:assert ct7d==cm7d==0 and cf7d==cu7d==0xffffffff and cfns7d==cuns7d==[0xffffffff]*8 and forward==0x7963a
 else:assert v[580:586]==[0,0,0,0xffffffff,0xffffffff,0] and v[586:]==[0,0xffffffff,0xffffffff]*8
'''
replace(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and cm16==0)','and cm16==0 and cm7d==0)').replace('or cm16:','or cm16 or cm7d:').replace('else 0x79639 if cm16','else 0x7963b if cm7d else 0x79639 if cm16')
s=s.replace("return {'crtc_vblank_end':", "return {'crtc_vdisplay_high':{'before':cb7d,'target':ct7d,'attempted':ca7d,'after':cf7d,'restored':cu7d,'cleanup_mask':cm7d,'neighbors_before':cn7d,'neighbors_after':cfns7d,'neighbors_restored':cuns7d},'crtc_vblank_end':")
p.write_bytes(s.encode())
print('Extended796 compiled-code oracle and separate schema')

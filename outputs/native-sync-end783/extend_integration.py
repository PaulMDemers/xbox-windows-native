"""Fresh783 full-path oracle extension; independent sync-end expectations."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration005.py';s=p.read_text()
s=s.replace("state={'sywrites'","state={'sewrites':0,'sywrites'").replace('sytrace=[]','sytrace=[];setrace=[]')
s=s.replace('0x7832a]','0x7832a,0x7832c]').replace('0x7832a,0x783]','0x7832a,0x7832c,0x783]')
s=s.replace('op+1480','op+1600').replace("'<370I'","'<400I'").replace('(0x56c8,0x6000)','(0x5740,0x6000)').replace('v[340:]==','v[340:370]==')
s=s.replace('time.monotonic()+480','time.monotonic()+540')
anchor='   elif off==0x68080c:';assert s.count(anchor)==1
s=s.replace(anchor,'''   elif off==0x680810:
    assert width==4 and state['seq']==0x21 and state['gate']==5 and state['sywrites']==1 and not hrestore
    assert word(1) in [0x7832c,0x783]
    state['sewrites']+=1;n=state['sewrites'];assert n<=2 and value==(492 if n==1 else 729)
    assert [word(i) for i in [370,371,372]]==[729,492,1]
    setrace.append((off,value))
    if fault==('se-drop-write' if n==1 else 'se-drop-undo'):return
    mm[off]=value
    if fault==('se-wrong-write' if n==1 else 'se-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('se-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x680814,0x68080c,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
'''+anchor)
s=s.replace("state['sywrites']+=1;n=state['sywrites'];", "state['sywrites']+=1;n=state['sywrites'];assert n==1 or state['sewrites']==2*word(372); ")
anchor='   i=sels[0x6013d4]\n';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''   if i in [0x13,0x19] and state['sywrites']==1 and word(1) in [0x7832c,0x783]:
    j=7+[0x13,0x19].index(i);phase=['before','after','undo'][state['sewrites']]
    if fault=='se-'+phase+'-'+str(j):value^=1
''')
anchor='   assert width==4 and off in mm;value=mm[off]';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if off in [0x680810,0x680800,0x680804,0x680808,0x680814,0x68080c,0x680818] and state['sywrites']==1 and word(1) in [0x7832c,0x783]:
    j=[0x680810,0x680800,0x680804,0x680808,0x680814,0x68080c,0x680818].index(off);phase=['before','after','undo'][state['sewrites']]
    if fault=='se-'+phase+'-'+str(j):value^=1''')
s=s.replace('   if value==4:\n','   if value==4:\n    assert word(375)==0 and (not word(372) or word(374)==word(370))\n    assert mm[0x680810]==729\n')
anchor="  if fault.startswith(('sy-undo-','sy-coupling-'))";assert s.count(anchor)==1
s=s.replace(anchor,"  if fault.startswith(('se-undo-','se-coupling-')) or fault in ['se-drop-undo','se-wrong-undo']:assert sw==[0x21] and outs==[5] and v[375]!=0 and v[101]==0\n"+anchor.replace('  if','  elif',1))
s=s.replace("'sy-coupling-8']","'sy-coupling-8','se-coupling-8']")
for offset,mapping,slot in [(235,'{6:4,7:5,8:6}',3),(259,'{1:1,6:4,7:5,8:6}',3),(283,'{1:1,2:2,6:6,7:7,8:8}',4),(313,'{1:1,2:2,3:3,6:6,7:7,8:8}',5),(343,'{1:1,2:2,3:3,4:4,6:6,7:7,8:8}',5)]:
 anchor=f'   assert [v[{offset}]]';assert s.count(anchor)==1
 s=s.replace(anchor,"   if fault.startswith('se-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);k="+mapping+".get(j)\n    if k is not None:undo[k]^=1\n"+f"   if fault=='se-drop-undo':undo[{slot}]=492\n   if fault=='se-wrong-undo':undo[{slot}]^=1\n"+anchor)
at=s.index(' for lo,hi in ')
s=s[:at]+''' reached_se=state['c13writes'] and v[1] in [0x783,0x7832c]
 if reached_se:
  ref=[729,479,524,479,0,489,719,104,48];before=ref.copy();attempted_se=not fault.startswith('se-before-')
  if not attempted_se:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[370]]+[v[376+3*i] for i in range(8)]==before
  assert v[371:373]==([492,1] if attempted_se else [0,0])
  assert setrace==([(0x680810,492),(0x680810,729)] if attempted_se else [])
  if attempted_se:
   after=[492]+ref[1:];undo=ref.copy()
   if fault=='se-drop-write':after[0]=729
   if fault=='se-wrong-write':after[0]^=1
   if fault.startswith('se-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('se-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('se-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='se-drop-undo':undo[0]=492
   if fault=='se-wrong-undo':undo[0]^=1
   assert [v[373]]+[v[377+3*i] for i in range(8)]==after
   assert [v[374]]+[v[378+3*i] for i in range(8)]==undo
   assert v[375]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[373:376]==[0xffffffff,0xffffffff,0] and all(v[377+3*i:379+3*i]==[0xffffffff]*2 for i in range(8))
 else:
  assert not setrace
  assert v[370:]==([0]*30 if refusal or want<0x783 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
'''+s[at:]
s=s.replace('v[237],v[261],v[285],v[315],v[345],v[340],v[343],v[344]','v[237],v[261],v[285],v[345],v[375],v[370],v[373],v[374]')
s=s.replace("'vertical_sync_start_writes':sytrace", "'vertical_sync_end_writes':setrace,'vertical_sync_start_writes':sytrace")
s=s.replace(" for layout in ('dual','relocated'):", " for phase in ['before','after','undo']:\n  for j in range(9):run('se-'+phase+'-'+str(j),want=0x7832d if phase=='undo' else 0x7832c,fault='se-'+phase+'-'+str(j))\n for j in range(1,9):run('se-coupling-'+str(j),want=0x7832d,fault='se-coupling-'+str(j))\n for f in ['se-drop-write','se-wrong-write','se-drop-undo','se-wrong-undo']:run(f,want=0x7832d if f.endswith('undo') else 0x7832c,fault=f)\n for layout in ('dual','relocated'):")
p.write_text(s,newline='\n');print('Extended783 full-path oracle; no hardware access')

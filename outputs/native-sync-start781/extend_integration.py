"""Extend fresh781 full-path oracle for the independent sync-start transaction."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration005.py';s=p.read_text()
s=s.replace("state={'vswrites'","state={'sywrites':0,'vswrites'").replace('vstrace=[]','vstrace=[];sytrace=[]')
s=s.replace('0x78128]','0x78128,0x7812a]').replace('0x78128,0x781]','0x78128,0x7812a,0x781]')
s=s.replace('op+1360','op+1480').replace("'<340I'","'<370I'").replace('(0x5650,0x6000)','(0x56c8,0x6000)').replace('v[310:]==','v[310:340]==')
s=s.replace('time.monotonic()+420','time.monotonic()+480') #39 extra full framebuffer cases
anchor='   elif off==0x680814:';assert s.count(anchor)==1
s=s.replace(anchor,'''   elif off==0x68080c:
    assert width==4 and state['seq']==0x21 and state['gate']==5 and state['vswrites']==1 and not hrestore
    assert word(1) in [0x7812a,0x781]
    state['sywrites']+=1;n=state['sywrites'];assert n<=2 and value==(489 if n==1 else 724)
    assert [word(i) for i in [340,341,342]]==[724,489,1]
    sytrace.append((off,value))
    if fault==('sy-drop-write' if n==1 else 'sy-drop-undo'):return
    mm[off]=value
    if fault==('sy-wrong-write' if n==1 else 'sy-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('sy-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x680814,0x680810,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
'''+anchor)
s=s.replace("state['vswrites']+=1;n=state['vswrites'];", "state['vswrites']+=1;n=state['vswrites'];assert n==1 or state['sywrites']==2*word(342); ")
anchor='   i=sels[0x6013d4]\n';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''   if i in [0x13,0x19] and state['vswrites']==1 and word(1) in [0x7812a,0x781]:
    j=7+[0x13,0x19].index(i);phase=['before','after','undo'][state['sywrites']]
    if fault=='sy-'+phase+'-'+str(j):value^=1
''')
anchor='   assert width==4 and off in mm;value=mm[off]';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if off in [0x68080c,0x680800,0x680804,0x680808,0x680814,0x680810,0x680818] and state['vswrites']==1 and word(1) in [0x7812a,0x781]:
    j=[0x68080c,0x680800,0x680804,0x680808,0x680814,0x680810,0x680818].index(off);phase=['before','after','undo'][state['sywrites']]
    if fault=='sy-'+phase+'-'+str(j):value^=1''')
s=s.replace('   if value==4:\n','   if value==4:\n    assert word(345)==0 and (not word(342) or word(344)==word(340))\n    assert mm[0x68080c]==724\n')
anchor="  if fault.startswith(('vs-undo-','vs-coupling-'))";assert s.count(anchor)==1
s=s.replace(anchor,"  if fault.startswith(('sy-undo-','sy-coupling-')) or fault in ['sy-drop-undo','sy-wrong-undo']:assert sw==[0x21] and outs==[5] and v[345]!=0 and v[101]==0\n"+anchor.replace('  if','  elif',1))
s=s.replace("'vs-coupling-8']","'vs-coupling-8','sy-coupling-8']")
for offset,mapping,slot in [(235,'{5:3,6:4,7:5,8:6}',2),(259,'{1:1,5:3,6:4,7:5,8:6}',2),(283,'{1:1,2:2,5:4,6:6,7:7,8:8}',3),(313,'{1:1,2:2,3:3,5:5,6:6,7:7,8:8}',4)]:
 anchor=f'   assert [v[{offset}]]';assert s.count(anchor)==1
 s=s.replace(anchor,"   if fault.startswith('sy-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);k="+mapping+".get(j)\n    if k is not None:undo[k]^=1\n"+f"   if fault=='sy-drop-undo':undo[{slot}]=489\n   if fault=='sy-wrong-undo':undo[{slot}]^=1\n"+anchor)
anchor=' for lo,hi in ';at=s.index(anchor)
s=s[:at]+''' reached_sy=state['c13writes'] and v[1] in [0x781,0x7812a]
 if reached_sy:
  ref=[724,479,524,479,0,729,719,104,48];before=ref.copy();attempted_sy=not fault.startswith('sy-before-')
  if not attempted_sy:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[340]]+[v[346+3*i] for i in range(8)]==before
  assert v[341:343]==([489,1] if attempted_sy else [0,0])
  assert sytrace==([(0x68080c,489),(0x68080c,724)] if attempted_sy else [])
  if attempted_sy:
   after=[489]+ref[1:];undo=ref.copy()
   if fault=='sy-drop-write':after[0]=724
   if fault=='sy-wrong-write':after[0]^=1
   if fault.startswith('sy-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('sy-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('sy-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='sy-drop-undo':undo[0]=489
   if fault=='sy-wrong-undo':undo[0]^=1
   assert [v[343]]+[v[347+3*i] for i in range(8)]==after
   assert [v[344]]+[v[348+3*i] for i in range(8)]==undo
   assert v[345]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[343:346]==[0xffffffff,0xffffffff,0] and all(v[347+3*i:349+3*i]==[0xffffffff]*2 for i in range(8))
 else:
  assert not sytrace
  assert v[340:]==([0]*30 if refusal or want<0x781 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
'''+s[at:]
s=s.replace('v[237],v[261],v[285],v[315],v[311],v[310],v[313],v[314]','v[237],v[261],v[285],v[315],v[345],v[340],v[343],v[344]')
s=s.replace("'vertical_valid_start_writes':vstrace", "'vertical_sync_start_writes':sytrace,'vertical_valid_start_writes':vstrace")
s=s.replace(" for layout in ('dual','relocated'):", " for phase in ['before','after','undo']:\n  for j in range(9):run('sy-'+phase+'-'+str(j),want=0x7812b if phase=='undo' else 0x7812a,fault='sy-'+phase+'-'+str(j))\n for j in range(1,9):run('sy-coupling-'+str(j),want=0x7812b,fault='sy-coupling-'+str(j))\n for f in ['sy-drop-write','sy-wrong-write','sy-drop-undo','sy-wrong-undo']:run(f,want=0x7812b if f.endswith('undo') else 0x7812a,fault=f)\n for layout in ('dual','relocated'):")
p.write_text(s,newline='\n');print('Extended781 integration, no physical access')

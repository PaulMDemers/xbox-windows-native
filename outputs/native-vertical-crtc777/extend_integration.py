"""Independent relocated777 nine-value stage and restoration fault oracle."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration005.py';s=p.read_text()
s=s.replace("state={'vtwrites'","state={'vcwrites':0,'vtwrites'").replace('vttrace=[]','vttrace=[];vctrace=[]').replace('mm.update(dict(V));','mm.update(dict(V));mm.update({0x680808:719,0x680814:0});')
s=s.replace('0x77724]','0x77724,0x77726]').replace('0x77724,0x777]','0x77724,0x77726,0x777]')
s=s.replace('op+1120','op+1240').replace("'<280I'","'<310I'").replace('(0x5560,0x6000)','(0x55d8,0x6000)').replace('v[256:]==','v[256:280]==')
anchor='   elif off==0x680804:';assert s.count(anchor)==1
s=s.replace(anchor,'''   elif off==0x680808:
    assert width==4 and state['seq']==0x21 and state['gate']==5 and state['vtwrites']==1 and not hrestore
    assert word(1) in [0x77726,0x777]
    state['vcwrites']+=1;n=state['vcwrites'];assert n<=2 and value==(479 if n==1 else 719)
    assert [word(i) for i in [280,281,282]]==[719,479,1]
    vctrace.append((off,value))
    if fault==('vc-drop-write' if n==1 else 'vc-drop-undo'):return
    mm[off]=value
    if fault==('vc-wrong-write' if n==1 else 'vc-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('vc-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x68080c,0x680810,0x680814,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
'''+anchor)
s=s.replace("state['vtwrites']+=1;n=state['vtwrites'];", "state['vtwrites']+=1;n=state['vtwrites'];assert n==1 or state['vcwrites']==2*word(282); ")
anchor='   i=sels[0x6013d4]\n';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''   if i in [0x13,0x19] and state['vtwrites']==1 and word(1) in [0x77726,0x777]:
    j=7+[0x13,0x19].index(i);phase=['before','after','undo'][state['vcwrites']]
    if fault=='vc-'+phase+'-'+str(j):value^=1
''')
anchor='   assert width==4 and off in mm;value=mm[off]';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if off in [0x680808,0x680800,0x680804,0x68080c,0x680810,0x680814,0x680818] and state['vtwrites']==1 and word(1) in [0x77726,0x777]:
    j=[0x680808,0x680800,0x680804,0x68080c,0x680810,0x680814,0x680818].index(off);phase=['before','after','undo'][state['vcwrites']]
    if fault=='vc-'+phase+'-'+str(j):value^=1''')
s=s.replace('   if value==4:\n','   if value==4:\n    assert word(285)==0 and (not word(282) or word(284)==word(280))\n    assert mm[0x680808]==719 and mm[0x680814]==0\n')
anchor="  if fault.startswith(('vt-undo-','vt-coupling-')) or fault in ['vt-drop-undo','vt-wrong-undo']:";assert s.count(anchor)==1
s=s.replace(anchor,"  if fault.startswith(('vc-undo-','vc-coupling-')) or fault in ['vc-drop-undo','vc-wrong-undo']:assert sw==[0x21] and outs==[5] and v[285]!=0 and v[101]==0\n"+anchor.replace('  if','  elif',1))
s=s.replace("'vt-coupling-6']","'vt-coupling-6','vc-coupling-8']")
for offset,maskmap in [(235,'{3:2,4:3,6:4,7:5,8:6}'),(259,'{1:1,3:2,4:3,6:4,7:5,8:6}')]:
 anchor=f"   assert [v[{offset}]]+[v[{offset+4}+3*i] for i in range(6)]==after";assert s.count(anchor)==1
 s=s.replace(anchor,f'''   if fault.startswith('vc-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={maskmap}.get(j)
    if k is not None:undo[k]^=1
'''+anchor)
anchor=' for lo,hi in ';at=s.index(anchor)
s=s[:at]+''' reached_vc=state['c13writes'] and v[1] in [0x777,0x77726]
 if reached_vc:
  ref=[719,479,524,724,729,0,719,104,48];before=ref.copy();attempted_vc=not fault.startswith('vc-before-')
  if not attempted_vc:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[280]]+[v[286+3*i] for i in range(8)]==before
  assert v[281:283]==([479,1] if attempted_vc else [0,0])
  assert vctrace==([(0x680808,479),(0x680808,719)] if attempted_vc else [])
  if attempted_vc:
   after=[479]+ref[1:];undo=ref.copy()
   if fault=='vc-drop-write':after[0]=719
   if fault=='vc-wrong-write':after[0]^=1
   if fault.startswith('vc-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('vc-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('vc-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='vc-drop-undo':undo[0]=479
   if fault=='vc-wrong-undo':undo[0]^=1
   assert [v[283]]+[v[287+3*i] for i in range(8)]==after
   assert [v[284]]+[v[288+3*i] for i in range(8)]==undo
   assert v[285]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[283:286]==[0xffffffff,0xffffffff,0] and all(v[287+3*i:289+3*i]==[0xffffffff]*2 for i in range(8))
 else:
  assert not vctrace
  assert v[280:]==([0]*30 if refusal or want<0x777 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
'''+s[at:]
s=s.replace('v[169],v[237],v[261],v[256],v[259],v[260]','v[237],v[261],v[285],v[280],v[283],v[284]')
s=s.replace("'vertical_total_writes':vttrace", "'vertical_crtc_writes':vctrace,'vertical_total_writes':vttrace")
s=s.replace(" for layout in ('dual','relocated'):", " for phase in ['before','after','undo']:\n  for j in range(9):run('vc-'+phase+'-'+str(j),want=0x77727 if phase=='undo' else 0x77726,fault='vc-'+phase+'-'+str(j))\n for j in range(1,9):run('vc-coupling-'+str(j),want=0x77727,fault='vc-coupling-'+str(j))\n for f in ['vc-drop-write','vc-wrong-write','vc-drop-undo','vc-wrong-undo']:run(f,want=0x77727 if f.endswith('undo') else 0x77726,fault=f)\n for layout in ('dual','relocated'):")
p.write_text(s,newline='\n');print('Extended777 relocated integration; no physical access')

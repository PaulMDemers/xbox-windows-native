"""Independent779 relocated integration extension; same-value stores stay ambiguous."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration005.py';s=p.read_text()
s=s.replace("state={'vcwrites'","state={'vswrites':0,'vcwrites'").replace('vctrace=[]','vctrace=[];vstrace=[]')
s=s.replace('0x77926]','0x77926,0x77928]').replace('0x77926,0x779]','0x77926,0x77928,0x779]')
s=s.replace('op+1240','op+1360').replace("'<310I'","'<340I'").replace('(0x55d8,0x6000)','(0x5650,0x6000)').replace('v[280:]==','v[280:310]==')
anchor='   elif off==0x680808:';assert s.count(anchor)==1
s=s.replace(anchor,'''   elif off==0x680814:
    assert width==4 and state['seq']==0x21 and state['gate']==5 and state['vcwrites']==1 and not hrestore
    assert word(1) in [0x77928,0x779]
    state['vswrites']+=1;n=state['vswrites'];assert n<=2 and value==0
    assert [word(i) for i in [310,311,312]]==[0,0,1]
    vstrace.append((off,value))
    if fault==('vs-drop-write' if n==1 else 'vs-drop-undo') or (n==2 and fault=='vs-wrong-write-drop-undo'):return
    mm[off]=value
    if fault==('vs-wrong-write' if n==1 else 'vs-wrong-undo') or (n==1 and fault=='vs-wrong-write-drop-undo'):mm[off]^=1
    if n==1 and fault.startswith('vs-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x68080c,0x680810,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
'''+anchor)
s=s.replace("state['vcwrites']+=1;n=state['vcwrites'];", "state['vcwrites']+=1;n=state['vcwrites'];assert n==1 or state['vswrites']==2*word(312); ")
anchor='   i=sels[0x6013d4]\n';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''   if i in [0x13,0x19] and state['vcwrites']==1 and word(1) in [0x77928,0x779]:
    j=7+[0x13,0x19].index(i);phase=['before','after','undo'][state['vswrites']]
    if fault=='vs-'+phase+'-'+str(j):value^=1
''')
anchor='   assert width==4 and off in mm;value=mm[off]';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if off in [0x680814,0x680800,0x680804,0x680808,0x68080c,0x680810,0x680818] and state['vcwrites']==1 and word(1) in [0x77928,0x779]:
    j=[0x680814,0x680800,0x680804,0x680808,0x68080c,0x680810,0x680818].index(off);phase=['before','after','undo'][state['vswrites']]
    if fault=='vs-'+phase+'-'+str(j):value^=1''')
s=s.replace('   if value==4:\n','   if value==4:\n    assert word(315)==0 and (not word(312) or word(314)==word(310))\n    assert mm[0x680814]==0\n')
anchor="  if fault.startswith(('vc-undo-','vc-coupling-')) or fault in ['vc-drop-undo','vc-wrong-undo']:";assert s.count(anchor)==1
s=s.replace(anchor,"  if fault.startswith(('vs-undo-','vs-coupling-')) or fault in ['vs-wrong-undo','vs-wrong-write-drop-undo']:assert sw==[0x21] and outs==[5] and v[315]!=0 and v[101]==0\n"+anchor.replace('  if','  elif',1))
s=s.replace("'vc-coupling-8']","'vc-coupling-8','vs-coupling-8']")
for offset,mapping in [(235,'{4:2,5:3,6:4,7:5,8:6}'),(259,'{1:1,4:2,5:3,6:4,7:5,8:6}')]:
 anchor=f'   assert [v[{offset}]]';assert s.count(anchor)==1
 s=s.replace(anchor,"   if fault.startswith('vs-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);k="+mapping+".get(j)\n    if k is not None:undo[k]^=1\n"+anchor)
anchor='   assert [v[283]]';assert s.count(anchor)==1
s=s.replace(anchor,'''   if fault.startswith('vs-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,4:3,5:4,6:6,7:7,8:8}.get(j)
    if k is not None:undo[k]^=1
   if fault in ['vs-wrong-undo','vs-wrong-write-drop-undo']:undo[5]^=1
'''+anchor)
anchor=' for lo,hi in ';at=s.index(anchor)
s=s[:at]+''' reached_vs=state['c13writes'] and v[1] in [0x779,0x77928]
 if reached_vs:
  ref=[0,479,524,479,724,729,719,104,48];before=ref.copy();attempted_vs=not fault.startswith('vs-before-')
  if not attempted_vs:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[310]]+[v[316+3*i] for i in range(8)]==before
  assert v[311:313]==([0,1] if attempted_vs else [0,0])
  assert vstrace==([(0x680814,0),(0x680814,0)] if attempted_vs else [])
  if attempted_vs:
   after=ref.copy();undo=ref.copy()
   if fault in ['vs-wrong-write','vs-wrong-write-drop-undo']:after[0]=1
   if fault.startswith('vs-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('vs-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('vs-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault in ['vs-wrong-undo','vs-wrong-write-drop-undo']:undo[0]=1
   assert [v[313]]+[v[317+3*i] for i in range(8)]==after
   assert [v[314]]+[v[318+3*i] for i in range(8)]==undo
   assert v[315]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[313:316]==[0xffffffff,0xffffffff,0] and all(v[317+3*i:319+3*i]==[0xffffffff]*2 for i in range(8))
 else:
  assert not vstrace
  assert v[310:]==([0]*30 if refusal or want<0x779 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
'''+s[at:]
s=s.replace('v[121],v[129],v[237],v[261],v[285],v[280],v[283],v[284]','v[237],v[261],v[285],v[315],v[311],v[310],v[313],v[314]')
s=s.replace("'vertical_crtc_writes':vctrace", "'vertical_valid_start_writes':vstrace,'vertical_crtc_writes':vctrace")
s=s.replace(" for layout in ('dual','relocated'):", " for phase in ['before','after','undo']:\n  for j in range(9):run('vs-'+phase+'-'+str(j),want=0x77929 if phase=='undo' else 0x77928,fault='vs-'+phase+'-'+str(j))\n for j in range(1,9):run('vs-coupling-'+str(j),want=0x77929,fault='vs-coupling-'+str(j))\n for f in ['vs-drop-write','vs-wrong-write','vs-drop-undo','vs-wrong-undo','vs-wrong-write-drop-undo']:run(f,want=0x779 if f in ['vs-drop-write','vs-drop-undo'] else 0x77929 if f.endswith('undo') else 0x77928,fault=f)\n for layout in ('dual','relocated'):")
p.write_text(s,newline='\n');print('Extended779 relocated integration; no physical access')

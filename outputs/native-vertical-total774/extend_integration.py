"""Independent relocated774 seven-value stage and restoration fault oracle."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration004.py';s=p.read_text()
s=s.replace("state={'vwrites'","state={'vtwrites':0,'vwrites'").replace('vtrace=[]','vtrace=[];vttrace=[]')
s=s.replace('0x77422]','0x77422,0x77424]').replace('0x77422,0x774]','0x77422,0x77424,0x774]')
s=s.replace('op+1024','op+1120').replace("'<256I'","'<280I'").replace('(0x5500,0x6000)','(0x5560,0x6000)').replace('v[232:]==','v[232:256]==')
anchor='   elif off in dict(V):';assert s.count(anchor)==1
s=s.replace(anchor,'''   elif off==0x680804:
    assert width==4 and state['seq']==0x21 and state['gate']==5 and state['vwrites']==1 and not hrestore
    assert word(1) in [0x77424,0x774]
    state['vtwrites']+=1;n=state['vtwrites'];assert n<=2 and value==(524 if n==1 else 749)
    assert [word(i) for i in [256,257,258]]==[749,524,1]
    vttrace.append((off,value))
    if fault==('vt-drop-write' if n==1 else 'vt-drop-undo'):return
    mm[off]=value
    if fault==('vt-wrong-write' if n==1 else 'vt-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('vt-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=6
     if j<=4:mm[[0x680800,0x68080c,0x680810,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-5]]^=1
'''+anchor)
s=s.replace("state['vwrites']+=1;n=state['vwrites'];", "state['vwrites']+=1;n=state['vwrites'];assert n==1 or state['vtwrites']==2*word(258); ")
anchor='   i=sels[0x6013d4]\n';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''   if i in [0x13,0x19] and state['vwrites']==1 and word(1) in [0x77424,0x774]:
    j=5+[0x13,0x19].index(i);phase=['before','after','undo'][state['vtwrites']]
    if fault=='vt-'+phase+'-'+str(j):value^=1
''')
anchor='   assert width==4 and off in mm;value=mm[off]';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if off in dict(V) and state['vwrites']==1 and word(1) in [0x77424,0x774]:
    j=[0x680804,0x680800,0x68080c,0x680810,0x680818].index(off);phase=['before','after','undo'][state['vtwrites']]
    if fault=='vt-'+phase+'-'+str(j):value^=1''')
s=s.replace('   if value==4:\n','   if value==4:\n    assert word(261)==0 and (not word(258) or word(260)==word(256))\n')
anchor="  if fault.startswith(('v-undo-','v-coupling-')):"
# Existing branch includes four named undo variants.
anchor="  if fault.startswith(('v-undo-','v-coupling-')) or fault in ['v-drop-undo','v-wrong-undo']:"
assert s.count(anchor)==1
s=s.replace(anchor,"  if fault.startswith(('vt-undo-','vt-coupling-')) or fault in ['vt-drop-undo','vt-wrong-undo']:assert sw==[0x21] and outs==[5] and v[261]!=0 and v[101]==0\n"+anchor.replace('  if','  elif',1))
s=s.replace("'v-coupling-6']","'v-coupling-6','vt-coupling-6']")
anchor="   assert [v[235]]+[v[239+3*i] for i in range(6)]==after";assert s.count(anchor)==1
s=s.replace(anchor,'''   if fault.startswith('vt-coupling-') and int(fault.rsplit('-',1)[1])>=2:undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='vt-drop-undo':undo[1]=524
   if fault=='vt-wrong-undo':undo[1]^=1
'''+anchor)
anchor=' for lo,hi in ';at=s.index(anchor)
s=s[:at]+''' reached_vt=state['c13writes'] and v[1] in [0x774,0x77424]
 if reached_vt:
  ref=[749,479,724,729,719,104,48];before=ref.copy();attempted_vt=not fault.startswith('vt-before-')
  if not attempted_vt:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[256]]+[v[262+3*i] for i in range(6)]==before
  assert v[257:259]==([524,1] if attempted_vt else [0,0])
  assert vttrace==([(0x680804,524),(0x680804,749)] if attempted_vt else [])
  if attempted_vt:
   after=[524]+ref[1:];undo=ref.copy()
   if fault=='vt-drop-write':after[0]=749
   if fault=='vt-wrong-write':after[0]^=1
   if fault.startswith('vt-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('vt-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('vt-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='vt-drop-undo':undo[0]=524
   if fault=='vt-wrong-undo':undo[0]^=1
   assert [v[259]]+[v[263+3*i] for i in range(6)]==after
   assert [v[260]]+[v[264+3*i] for i in range(6)]==undo
   assert v[261]==sum(1<<i for i in range(7) if undo[i]!=ref[i])
  else:assert v[259:262]==[0xffffffff,0xffffffff,0] and all(v[i]==0xffffffff for i in [263,264,266,267,269,270,272,273,275,276,278,279])
 else:
  assert not vttrace
  assert v[256:]==([0]*24 if refusal or want<0x774 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*6)
'''+s[at:]
s=s.replace('v[221],v[237],v[232],v[235],v[236]','v[237],v[261],v[256],v[259],v[260]')
s=s.replace("'vertical_writes':vtrace", "'vertical_total_writes':vttrace,'vertical_writes':vtrace")
s=s.replace(" for layout in ('dual','relocated'):", " for phase in ['before','after','undo']:\n  for j in range(7):run('vt-'+phase+'-'+str(j),want=0x77425 if phase=='undo' else 0x77424,fault='vt-'+phase+'-'+str(j))\n for j in range(1,7):run('vt-coupling-'+str(j),want=0x77425,fault='vt-coupling-'+str(j))\n for f in ['vt-drop-write','vt-wrong-write','vt-drop-undo','vt-wrong-undo']:run(f,want=0x77425 if f.endswith('undo') else 0x77424,fault=f)\n for layout in ('dual','relocated'):")
p.write_text(s,newline='\n');print('Extended774 integration; no physical access')

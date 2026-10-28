"""Fresh785 full-path oracle extension, valid-end values and relocated owned IDT."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration005.py';s=p.read_text()
s=s.replace("state={'sewrites'","state={'vewrites':0,'sewrites'").replace('setrace=[]','setrace=[];vetrace=[]')
s=s.replace('0x7852c]','0x7852c,0x7852e]').replace('0x7852c,0x785]','0x7852c,0x7852e,0x785]')
s=s.replace('op+1600','op+1720').replace("'<400I'","'<430I'").replace('(0x5740,0x6000)','(0x57b8,0x6004)').replace('v[370:]==','v[370:400]==')
s=s.replace('time.monotonic()+540','time.monotonic()+600')
anchor='   elif off==0x680810:';assert s.count(anchor)==1
s=s.replace(anchor,'''   elif off==0x680818:
    assert width==4 and state['seq']==0x21 and state['gate']==5 and state['sewrites']==1 and not hrestore
    assert word(1) in [0x7852e,0x785]
    state['vewrites']+=1;n=state['vewrites'];assert n<=2 and value==(479 if n==1 else 719)
    assert [word(i) for i in [400,401,402]]==[719,479,1]
    vetrace.append((off,value))
    if fault==('ve-drop-write' if n==1 else 've-drop-undo'):return
    mm[off]=value
    if fault==('ve-wrong-write' if n==1 else 've-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('ve-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x680814,0x68080c,0x680810][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
'''+anchor)
s=s.replace("state['sewrites']+=1;n=state['sewrites'];", "state['sewrites']+=1;n=state['sewrites'];assert n==1 or state['vewrites']==2*word(402); ")
anchor='   i=sels[0x6013d4]\n';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''   if i in [0x13,0x19] and state['sewrites']==1 and word(1) in [0x7852e,0x785]:
    j=7+[0x13,0x19].index(i);phase=['before','after','undo'][state['vewrites']]
    if fault=='ve-'+phase+'-'+str(j):value^=1
''')
anchor='   assert width==4 and off in mm;value=mm[off]';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if off in [0x680818,0x680800,0x680804,0x680808,0x680814,0x68080c,0x680810] and state['sewrites']==1 and word(1) in [0x7852e,0x785]:
    j=[0x680818,0x680800,0x680804,0x680808,0x680814,0x68080c,0x680810].index(off);phase=['before','after','undo'][state['vewrites']]
    if fault=='ve-'+phase+'-'+str(j):value^=1''')
s=s.replace('   if value==4:\n','   if value==4:\n    assert word(405)==0 and (not word(402) or word(404)==word(400))\n    assert mm[0x680818]==719\n')
anchor="  if fault.startswith(('se-undo-','se-coupling-'))";assert s.count(anchor)==1
s=s.replace(anchor,"  if fault.startswith(('ve-undo-','ve-coupling-')) or fault in ['ve-drop-undo','ve-wrong-undo']:assert sw==[0x21] and outs==[5] and v[405]!=0 and v[101]==0\n"+anchor.replace('  if','  elif',1))
s=s.replace("'se-coupling-8']","'se-coupling-8','ve-coupling-8']")
for offset,mapping,slot in [(235,'{7:5,8:6}',4),(259,'{1:1,7:5,8:6}',4),(283,'{1:1,2:2,7:7,8:8}',6),(313,'{1:1,2:2,3:3,7:7,8:8}',6),(343,'{1:1,2:2,3:3,4:4,7:7,8:8}',6),(374,'{1:1,2:2,3:3,4:4,5:5,7:7,8:8}',6)]:
 anchor=f'   assert [v[{offset}]]';assert s.count(anchor)==1
 s=s.replace(anchor,"   if fault.startswith('ve-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);k="+mapping+".get(j)\n    if k is not None:undo[k]^=1\n"+f"   if fault=='ve-drop-undo':undo[{slot}]=479\n   if fault=='ve-wrong-undo':undo[{slot}]^=1\n"+anchor)
at=s.index(' for lo,hi in ')
s=s[:at]+''' reached_ve=state['c13writes'] and v[1] in [0x785,0x7852e]
 if reached_ve:
  ref=[719,479,524,479,0,489,492,104,48];before=ref.copy();attempted_ve=not fault.startswith('ve-before-')
  if not attempted_ve:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[400]]+[v[406+3*i] for i in range(8)]==before
  assert v[401:403]==([479,1] if attempted_ve else [0,0])
  assert vetrace==([(0x680818,479),(0x680818,719)] if attempted_ve else [])
  if attempted_ve:
   after=[479]+ref[1:];undo=ref.copy()
   if fault=='ve-drop-write':after[0]=719
   if fault=='ve-wrong-write':after[0]^=1
   if fault.startswith('ve-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('ve-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('ve-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='ve-drop-undo':undo[0]=479
   if fault=='ve-wrong-undo':undo[0]^=1
   assert [v[403]]+[v[407+3*i] for i in range(8)]==after
   assert [v[404]]+[v[408+3*i] for i in range(8)]==undo
   assert v[405]==sum(1<<i for i in range(9) if undo[i]!=ref[i])
  else:assert v[403:406]==[0xffffffff,0xffffffff,0] and all(v[407+3*i:409+3*i]==[0xffffffff]*2 for i in range(8))
 else:
  assert not vetrace
  assert v[400:]==([0]*30 if refusal or want<0x785 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)
'''+s[at:]
s=s.replace('v[237],v[261],v[285],v[345],v[375],v[370],v[373],v[374]','v[237],v[261],v[285],v[375],v[405],v[400],v[403],v[404]')
s=s.replace("'vertical_sync_end_writes':setrace", "'vertical_valid_end_writes':vetrace,'vertical_sync_end_writes':setrace")
s=s.replace(" for layout in ('dual','relocated'):", " for phase in ['before','after','undo']:\n  for j in range(9):run('ve-'+phase+'-'+str(j),want=0x7852f if phase=='undo' else 0x7852e,fault='ve-'+phase+'-'+str(j))\n for j in range(1,9):run('ve-coupling-'+str(j),want=0x7852f,fault='ve-coupling-'+str(j))\n for f in ['ve-drop-write','ve-wrong-write','ve-drop-undo','ve-wrong-undo']:run(f,want=0x7852f if f.endswith('undo') else 0x7852e,fault=f)\n for layout in ('dual','relocated'):")
p.write_text(s,newline='\n');print('Extended785 full-path oracle; no hardware access')

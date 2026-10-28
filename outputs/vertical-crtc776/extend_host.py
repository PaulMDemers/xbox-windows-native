"""Extend independently specified actual COFF oracle, including coupling propagation."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'model.py';s=p.read_text()
s=s.replace("state={'vtwrites'","state={'vcwrites':0,'vtwrites'").replace('mm.update(dict(V));','mm.update(dict(V));mm.update({0x680808:719,0x680814:0});')
s=s.replace('0x201460','0x2014d8').replace('0x5ba0','0x5b28').replace("'<280I',c.mem_read(0x201000,1120)","'<310I',c.mem_read(0x201000,1240)")
s=s.replace('0x77624]', '0x77624,0x77626]').replace('0x77624,0x776]', '0x77624,0x77626,0x776]')
s=s.replace('v[262:]==','v[262:280]==')
anchor='   val=cr[idx]';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if idx in [0x13,0x19] and state['vtwrites']==1 and word(1) in [0x77626,0x776]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vcwrites']]
    if fault=='vc-'+phase+'-'+str(j):val^=1
''')
anchor='  elif off in dict(V):';assert s.count(anchor)==1
s=s.replace(anchor,'''  elif off in [0x680808,0x680814]:
   assert width==4 and state['sq']==0x21 and ports==[5] and not hr and state['vtwrites']==1
   assert word(1) in [0x77626,0x776]
   if kind==u.UC_MEM_WRITE:
    assert off==0x680808
    state['vcwrites']+=1;n=state['vcwrites'];assert n<=2
    assert [word(280),word(281),word(282)]==[719,479,1] and value==(479 if n==1 else 719)
    writes.append(['vc',off,value])
    if fault==('vc-drop-write' if n==1 else 'vc-drop-undo'):return
    mm[off]=value
    if fault==('vc-wrong-write' if n==1 else 'vc-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('vc-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x68080c,0x680810,0x680814,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
    return
   val=mm[off];j=0 if off==0x680808 else 5;phase=['before','after','undo'][state['vcwrites']]
   if fault=='vc-'+phase+'-'+str(j):val^=1
'''+anchor)
s=s.replace("state['vtwrites']+=1;n=state['vtwrites'];assert n<=2", "state['vtwrites']+=1;n=state['vtwrites'];assert n<=2\n    if n==2:assert state['vcwrites']==2*word(282)")
anchor="   val=mm[off];phase=['before','after','undo'][state['vwrites']]";assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if state['vtwrites']==1 and word(1) in [0x77626,0x776]:
    cj={0x680800:1,0x680804:2,0x68080c:3,0x680810:4,0x680818:6}[off]
    cp=['before','after','undo'][state['vcwrites']]
    if fault=='vc-'+cp+'-'+str(cj):val^=1
''')
s=s.replace('  if val==4:\n','  if val==4:\n   assert word(285)==0 and (not word(282) or word(284)==word(280))\n   assert mm[0x680808]==719 and mm[0x680814]==0\n')
s=s.replace("'vt-coupling-6']","'vt-coupling-6','vc-coupling-8']")
s=s.replace('  vbad=bool(vmask)', '''  if fault.startswith('vc-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={3:2,4:3,6:4,7:5,8:6}.get(j)
   if k is not None:vmask|=1<<k
  vbad=bool(vmask)''')
s=s.replace('  qbad=bool(qmask)', '''  if fault.startswith('vc-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1:1,3:2,4:3,6:4,7:5,8:6}.get(j)
   if k is not None:qmask|=1<<k
  qbad=bool(qmask)
  wmask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('vc-undo-','vc-coupling-')) else 1 if fault in ['vc-drop-undo','vc-wrong-undo'] else 0
  wbad=bool(wmask)''')
s=s.replace('or qbad','or qbad or wbad')
s=s.replace('else 0x776\n  assert v[1]==forward',"else 0x77626 if fault.startswith(('vc-before-','vc-after-','vc-coupling-')) or fault in ['vc-drop-write','vc-wrong-write'] else 0x776\n  assert v[1]==forward")
s=s.replace("[['vt',0x680804,524],['vt',0x680804,749]]", "[['vt',0x680804,524]]+([['vc',0x680808,479],['vc',0x680808,719]] if forward in [0x776,0x77626] and not fault.startswith('vc-before-') else [])+[['vt',0x680804,749]]")
s=s.replace('else 0x77625 if qbad','else 0x77627 if wbad else 0x77625 if qbad')
anchor="   assert [v[235]]+[v[239+3*i] for i in range(6)]==after";assert s.count(anchor)==1
s=s.replace(anchor,'''   if fault.startswith('vc-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={3:2,4:3,6:4,7:5,8:6}.get(j)
    if k is not None:undo[k]^=1
'''+anchor)
anchor="   assert [v[259]]+[v[263+3*i] for i in range(6)]==after";assert s.count(anchor)==1
s=s.replace(anchor,'''   if fault.startswith('vc-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,3:2,4:3,6:4,7:5,8:6}.get(j)
    if k is not None:undo[k]^=1
'''+anchor)
anchor=" R['cases'].append(";assert s.count(anchor)==1
s=s.replace(anchor,''' # Independently specified NVVCRTC baseline, mutation, recovery and neighbors.
 reached_vc=not cpu_bad and not baseline and forward in [0x776,0x77626]
 if reached_vc:
  ref=[719,479,524,724,729,0,719,104,48];before=ref.copy()
  attempted_vc=not fault.startswith('vc-before-')
  if not attempted_vc:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[280]]+[v[286+3*i] for i in range(8)]==before
  assert v[281:283]==([479,1] if attempted_vc else [0,0]) and state['vcwrites']==2*int(attempted_vc)
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
   assert v[285]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==wmask
  else:assert v[283:286]==[0xffffffff,0xffffffff,0] and all(v[287+3*i:289+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[280:286]==[0,0,0,0xffffffff,0xffffffff,0] and v[286:]==[0,0xffffffff,0xffffffff]*8
'''+anchor)
s=s.replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('vc-'+phase+'-'+str(j),fault='vc-'+phase+'-'+str(j))\n for j in range(1,9):run('vc-coupling-'+str(j),fault='vc-coupling-'+str(j))\n for f in ['vc-drop-write','vc-wrong-write','vc-drop-undo','vc-wrong-undo']:run(f,fault=f)")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('280-word','310-word').replace('len(v)==280','len(v)==310').replace('0x77624]','0x77624,0x77626]').replace('(forward==0x776)','(forward in [0x776,0x77626])').replace('v[262:]==','v[262:280]==')
anchor=' assert c13attempt in [0,1]'
code=''' wb,wt,wa,wf,wu,wm=v[280:286]
 wnb=[v[286+3*i] for i in range(8)];wna=[v[287+3*i] for i in range(8)];wnu=[v[288+3*i] for i in range(8)]
 assert wa in [0,1] and 0<=wm<512
 if forward in [0x776,0x77626]:
  assert wa==int([wb]+wnb==[719,479,524,724,729,0,719,104,48])
  if wa:
   assert wt==479 and wm==sum(1<<i for i,(a,b) in enumerate(zip([wu]+wnu,[wb]+wnb)) if a!=b)
   assert (wf==479 and wna==wnb)==(forward==0x776)
  else:assert wt==wm==0 and wf==wu==0xffffffff and wna==wnu==[0xffffffff]*8 and forward==0x77626
 else:assert v[280:286]==[0,0,0,0xffffffff,0xffffffff,0] and v[286:]==[0,0xffffffff,0xffffffff]*8
'''
s=s.replace(anchor,code+anchor).replace('and qm==0)','and qm==0 and wm==0)').replace('or qm:','or qm or wm:').replace('else 0x77625 if qm','else 0x77627 if wm else 0x77625 if qm')
s=s.replace("return {'vertical_total':", "return {'vertical_crtc':{'before':wb,'target':wt,'attempted':wa,'after':wf,'restored':wu,'cleanup_mask':wm,'neighbors_before':wnb,'neighbors_after':wna,'neighbors_restored':wnu},'vertical_total':")
s=s.replace('plus two vertical words','plus three vertical words');p.write_text(s,newline='\n')
p=K/'audit_collection.py';s=p.read_text().replace('len(v)==280','len(v)==310').replace('0x77624]','0x77624,0x77626]').replace('two_vertical_words','three_vertical_words');p.write_text(s,newline='\n')
print('Extended776 actual COFF oracle and strict schema; no hardware access')

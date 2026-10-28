"""Extend the independently specified actual-COFF oracle and strict schema."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'model.py';s=p.read_text()
s=s.replace("state={'vwrites'","state={'vtwrites':0,'vwrites'")
s=s.replace('0x201400','0x201460').replace('0x5c00','0x5ba0').replace("'<256I',c.mem_read(0x201000,1024)","'<280I',c.mem_read(0x201000,1120)")
s=s.replace('0x77322]', '0x77322,0x77324]').replace('0x77322,0x773]', '0x77322,0x77324,0x773]')
s=s.replace('v[238:]==','v[238:256]==')
anchor='   val=cr[idx]';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if idx in [0x13,0x19] and state['vwrites']==1 and word(1) in [0x77324,0x773]:
    j=5+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vtwrites']]
    if fault=='vt-'+phase+'-'+str(j):val^=1
''')
anchor='   if kind==u.UC_MEM_WRITE:\n    assert off==0x680800';assert s.count(anchor)==1
s=s.replace(anchor,'''   if kind==u.UC_MEM_WRITE and off==0x680804:
    assert state['vwrites']==1 and word(1) in [0x77324,0x773]
    state['vtwrites']+=1;n=state['vtwrites'];assert n<=2
    assert [word(256),word(257),word(258)]==[749,524,1] and value==(524 if n==1 else 749)
    writes.append(['vt',off,value])
    if fault==('vt-drop-write' if n==1 else 'vt-drop-undo'):return
    mm[off]=value
    if fault==('vt-wrong-write' if n==1 else 'vt-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('vt-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=6
     if j<=4:mm[[0x680800,0x68080c,0x680810,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-5]]^=1
    return
'''+anchor)
s=s.replace("state['vwrites']+=1;n=state['vwrites'];assert n<=2", "state['vwrites']+=1;n=state['vwrites'];assert n<=2\n    if n==2:assert state['vtwrites']==2*word(258)")
anchor="   val=mm[off];phase=['before','after','undo'][state['vwrites']]";assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if state['vwrites']==1 and word(1) in [0x77324,0x773]:
    tj=[0x680804,0x680800,0x68080c,0x680810,0x680818].index(off)
    tp=['before','after','undo'][state['vtwrites']]
    if fault=='vt-'+tp+'-'+str(tj):val^=1
''')
s=s.replace('  if val==4:\n','  if val==4:\n   assert word(261)==0 and (not word(258) or word(260)==word(256))\n')
s=s.replace("'v-coupling-6']","'v-coupling-6','vt-coupling-6']")
s=s.replace('  vbad=bool(vmask)', '''  if fault.startswith('vt-coupling-') and int(fault.rsplit('-',1)[1])>=2:vmask|=1<<int(fault.rsplit('-',1)[1])
  if fault in ['vt-drop-undo','vt-wrong-undo']:vmask|=2
  vbad=bool(vmask)
  qmask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('vt-undo-','vt-coupling-')) else 1 if fault in ['vt-drop-undo','vt-wrong-undo'] else 0
  qbad=bool(qmask)''')
s=s.replace('or vbad','or vbad or qbad')
s=s.replace('else 0x773\n  assert v[1]==forward',"else 0x77324 if fault.startswith(('vt-before-','vt-after-','vt-coupling-')) or fault in ['vt-drop-write','vt-wrong-write'] else 0x773\n  assert v[1]==forward")
s=s.replace("[['v',0x680800,479],['v',0x680800,719]]", "[['v',0x680800,479]]+([['vt',0x680804,524],['vt',0x680804,749]] if forward in [0x773,0x77324] and not fault.startswith('vt-before-') else [])+[['v',0x680800,719]]")
s=s.replace('else 0x77323 if vbad','else 0x77325 if qbad else 0x77323 if vbad')
anchor="   assert [v[235]]+[v[239+3*i] for i in range(6)]==after";assert s.count(anchor)==1
s=s.replace(anchor,'''   if fault.startswith('vt-coupling-') and int(fault.rsplit('-',1)[1])>=2:undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='vt-drop-undo':undo[1]=524
   if fault=='vt-wrong-undo':undo[1]^=1
'''+anchor)
anchor=" R['cases'].append(";assert s.count(anchor)==1
s=s.replace(anchor,''' # New stage expected values and order are specified independently of code/result status.
 reached_vt=not cpu_bad and not baseline and forward in [0x773,0x77324]
 if reached_vt:
  ref=[749,479,724,729,719,104,48];before=ref.copy()
  attempted_vt=not fault.startswith('vt-before-')
  if not attempted_vt:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[256]]+[v[262+3*i] for i in range(6)]==before
  assert v[257:259]==([524,1] if attempted_vt else [0,0]) and state['vtwrites']==2*int(attempted_vt)
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
   assert v[261]==sum(1<<i for i in range(7) if undo[i]!=ref[i])==qmask
  else:assert v[259:262]==[0xffffffff,0xffffffff,0] and all(v[i]==0xffffffff for i in [263,264,266,267,269,270,272,273,275,276,278,279])
 else:assert v[256:262]==[0,0,0,0xffffffff,0xffffffff,0] and v[262:]==[0,0xffffffff,0xffffffff]*6
'''+anchor)
s=s.replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(7):run('vt-'+phase+'-'+str(j),fault='vt-'+phase+'-'+str(j))\n for j in range(1,7):run('vt-coupling-'+str(j),fault='vt-coupling-'+str(j))\n for f in ['vt-drop-write','vt-wrong-write','vt-drop-undo','vt-wrong-undo']:run(f,fault=f)")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('256-word','280-word').replace('len(v)==256','len(v)==280').replace('0x77322]','0x77322,0x77324]').replace('(forward==0x773)','(forward in [0x773,0x77324])').replace('v[238:]==','v[238:256]==')
anchor=' assert c13attempt in [0,1]'
code=''' qb,qt,qa,qf,qu,qm=v[256:262]
 qnb=[v[262+3*i] for i in range(6)];qna=[v[263+3*i] for i in range(6)];qnu=[v[264+3*i] for i in range(6)]
 assert qa in [0,1] and 0<=qm<128
 if forward in [0x773,0x77324]:
  assert qa==int([qb]+qnb==[749,479,724,729,719,104,48])
  if qa:
   assert qt==524 and qm==sum(1<<i for i,(a,b) in enumerate(zip([qu]+qnu,[qb]+qnb)) if a!=b)
   assert (qf==524 and qna==qnb)==(forward==0x773)
  else:assert qt==qm==0 and qf==qu==0xffffffff and qna==qnu==[0xffffffff]*6 and forward==0x77324
 else:assert v[256:262]==[0,0,0,0xffffffff,0xffffffff,0] and v[262:]==[0,0xffffffff,0xffffffff]*6
'''
s=s.replace(anchor,code+anchor).replace('and vm==0)','and vm==0 and qm==0)').replace('or vm:','or vm or qm:').replace('else 0x77323 if vm','else 0x77325 if qm else 0x77323 if vm')
s=s.replace("return {'vertical_display_end':", "return {'vertical_total':{'before':qb,'target':qt,'attempted':qa,'after':qf,'restored':qu,'cleanup_mask':qm,'neighbors_before':qnb,'neighbors_after':qna,'neighbors_restored':qnu},'vertical_display_end':")
s=s.replace('plus one vertical word','plus two vertical words');p.write_text(s,newline='\n')
print('Extended773 host fault oracle and schema; no hardware access')

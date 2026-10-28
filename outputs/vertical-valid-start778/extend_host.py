"""Independent778 COFF oracle extension; same-value drop ambiguity retained."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'model.py';s=p.read_text()
s=s.replace("state={'vcwrites'","state={'vswrites':0,'vcwrites'")
s=s.replace('0x2014d8','0x201550').replace('0x5b28','0x5ab0').replace("'<310I',c.mem_read(0x201000,1240)","'<340I',c.mem_read(0x201000,1360)")
s=s.replace('0x77826]','0x77826,0x77828]').replace('0x77826,0x778]','0x77826,0x77828,0x778]')
s=s.replace('v[286:]==','v[286:310]==')
anchor='   val=cr[idx]';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if idx in [0x13,0x19] and state['vcwrites']==1 and word(1) in [0x77828,0x778]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vswrites']]
    if fault=='vs-'+phase+'-'+str(j):val^=1
''')
anchor='   if kind==u.UC_MEM_WRITE:\n    assert off==0x680808';assert s.count(anchor)==1
s=s.replace(anchor,'''   if kind==u.UC_MEM_WRITE and off==0x680814:
    assert state['vcwrites']==1 and word(1) in [0x77828,0x778]
    state['vswrites']+=1;n=state['vswrites'];assert n<=2
    assert [word(310),word(311),word(312)]==[0,0,1] and value==0
    writes.append(['vs',off,value])
    if fault==('vs-drop-write' if n==1 else 'vs-drop-undo') or (n==2 and fault=='vs-wrong-write-drop-undo'):return
    mm[off]=value
    if fault==('vs-wrong-write' if n==1 else 'vs-wrong-undo') or (n==1 and fault=='vs-wrong-write-drop-undo'):mm[off]^=1
    if n==1 and fault.startswith('vs-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x68080c,0x680810,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
    return
'''+anchor)
s=s.replace("state['vcwrites']+=1;n=state['vcwrites'];assert n<=2", "state['vcwrites']+=1;n=state['vcwrites'];assert n<=2\n    if n==2:assert state['vswrites']==2*word(312)")
anchor="   if fault=='vc-'+phase+'-'+str(j):val^=1";assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if state['vcwrites']==1 and word(1) in [0x77828,0x778]:
    sj=0 if off==0x680814 else 3;sp=['before','after','undo'][state['vswrites']]
    if fault=='vs-'+sp+'-'+str(sj):val^=1
''')
anchor="   val=mm[off];phase=['before','after','undo'][state['vwrites']]";assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if state['vcwrites']==1 and word(1) in [0x77828,0x778]:
    sj={0x680800:1,0x680804:2,0x68080c:4,0x680810:5,0x680818:6}[off]
    sp=['before','after','undo'][state['vswrites']]
    if fault=='vs-'+sp+'-'+str(sj):val^=1
''')
s=s.replace('  if val==4:\n','  if val==4:\n   assert word(315)==0 and (not word(312) or word(314)==word(310))\n')
s=s.replace("'vc-coupling-8']","'vc-coupling-8','vs-coupling-8']")
s=s.replace('  vbad=bool(vmask)', '''  if fault.startswith('vs-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={4:2,5:3,6:4,7:5,8:6}.get(j)
   if k is not None:vmask|=1<<k
  vbad=bool(vmask)''')
s=s.replace('  qbad=bool(qmask)', '''  if fault.startswith('vs-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1:1,4:2,5:3,6:4,7:5,8:6}.get(j)
   if k is not None:qmask|=1<<k
  qbad=bool(qmask)''')
s=s.replace('  wbad=bool(wmask)', '''  if fault.startswith('vs-coupling-'):
   j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,4:3,5:4,6:6,7:7,8:8}.get(j)
   if k is not None:wmask|=1<<k
  if fault in ['vs-wrong-undo','vs-wrong-write-drop-undo']:wmask|=32
  wbad=bool(wmask)
  xmask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('vs-undo-','vs-coupling-')) else 1 if fault in ['vs-wrong-undo','vs-wrong-write-drop-undo'] else 0
  xbad=bool(xmask)''')
s=s.replace('or wbad','or wbad or xbad')
s=s.replace('else 0x778\n  assert v[1]==forward',"else 0x77828 if fault.startswith(('vs-before-','vs-after-','vs-coupling-')) or fault in ['vs-wrong-write','vs-wrong-write-drop-undo'] else 0x778\n  assert v[1]==forward")
s=s.replace("[['vc',0x680808,479],['vc',0x680808,719]]", "[['vc',0x680808,479]]+([['vs',0x680814,0],['vs',0x680814,0]] if forward in [0x778,0x77828] and not fault.startswith('vs-before-') else [])+[['vc',0x680808,719]]")
s=s.replace('else 0x77827 if wbad','else 0x77829 if xbad else 0x77827 if wbad')
for offset,mapping in [(235,'{4:2,5:3,6:4,7:5,8:6}'),(259,'{1:1,4:2,5:3,6:4,7:5,8:6}')]:
 anchor='   assert [v['+str(offset)+']]';assert s.count(anchor)==1
 addition="   if fault.startswith('vs-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);k="+mapping+".get(j)\n    if k is not None:undo[k]^=1\n"
 s=s.replace(anchor,addition+anchor)
anchor='   assert [v[283]]';assert s.count(anchor)==1
s=s.replace(anchor,'''   if fault.startswith('vs-coupling-'):
    j=int(fault.rsplit('-',1)[1]);k={1:1,2:2,4:3,5:4,6:6,7:7,8:8}.get(j)
    if k is not None:undo[k]^=1
   if fault in ['vs-wrong-undo','vs-wrong-write-drop-undo']:undo[5]^=1
'''+anchor)
anchor=" R['cases'].append(";assert s.count(anchor)==1
s=s.replace(anchor,''' # Independently specified NVVVALIDSTART same-value attempt and recovery.
 reached_vs=not cpu_bad and not baseline and forward in [0x778,0x77828]
 if reached_vs:
  ref=[0,479,524,479,724,729,719,104,48];before=ref.copy()
  attempted_vs=not fault.startswith('vs-before-')
  if not attempted_vs:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[310]]+[v[316+3*i] for i in range(8)]==before
  assert v[311:313]==([0,1] if attempted_vs else [0,0]) and state['vswrites']==2*int(attempted_vs)
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
   assert v[315]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==xmask
  else:assert v[313:316]==[0xffffffff,0xffffffff,0] and all(v[317+3*i:319+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[310:316]==[0,0,0,0xffffffff,0xffffffff,0] and v[316:]==[0,0xffffffff,0xffffffff]*8
'''+anchor)
s=s.replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('vs-'+phase+'-'+str(j),fault='vs-'+phase+'-'+str(j))\n for j in range(1,9):run('vs-coupling-'+str(j),fault='vs-coupling-'+str(j))\n for f in ['vs-drop-write','vs-wrong-write','vs-drop-undo','vs-wrong-undo','vs-wrong-write-drop-undo']:run(f,fault=f)")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('310-word','340-word').replace('len(v)==310','len(v)==340').replace('0x77826]','0x77826,0x77828]').replace('(forward==0x778)','(forward in [0x778,0x77828])').replace('v[286:]==','v[286:310]==')
anchor=' assert c13attempt in [0,1]'
code=''' xb,xt,xa,xf,xu,xm=v[310:316]
 xnb=[v[316+3*i] for i in range(8)];xna=[v[317+3*i] for i in range(8)];xnu=[v[318+3*i] for i in range(8)]
 assert xa in [0,1] and 0<=xm<512
 if forward in [0x778,0x77828]:
  assert xa==int([xb]+xnb==[0,479,524,479,724,729,719,104,48])
  if xa:
   assert xt==0 and xm==sum(1<<i for i,(a,b) in enumerate(zip([xu]+xnu,[xb]+xnb)) if a!=b)
   assert (xf==0 and xna==xnb)==(forward==0x778)
  else:assert xt==xm==0 and xf==xu==0xffffffff and xna==xnu==[0xffffffff]*8 and forward==0x77828
 else:assert v[310:316]==[0,0,0,0xffffffff,0xffffffff,0] and v[316:]==[0,0xffffffff,0xffffffff]*8
'''
s=s.replace(anchor,code+anchor).replace('and wm==0)','and wm==0 and xm==0)').replace('or wm:','or wm or xm:').replace('else 0x77827 if wm','else 0x77829 if xm else 0x77827 if wm')
s=s.replace("return {'vertical_crtc':", "return {'vertical_valid_start':{'before':xb,'target':xt,'attempted':xa,'after':xf,'restored':xu,'cleanup_mask':xm,'neighbors_before':xnb,'neighbors_after':xna,'neighbors_restored':xnu,'same_value_drop_indistinguishable':True},'vertical_crtc':")
s=s.replace('plus three vertical words','plus four vertical words');p.write_text(s,newline='\n')
print('Extended778 actual COFF oracle and strict schema; no physical access')

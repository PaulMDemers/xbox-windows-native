"""Extend inherited actual-code oracle and strict independent result schema."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'model.py';s=p.read_text()
s=s.replace("state={'vswrites'","state={'sywrites':0,'vswrites'")
s=s.replace('0x201550','0x2015c8').replace('0x5ab0','0x5a38').replace("'<340I',c.mem_read(0x201000,1360)","'<370I',c.mem_read(0x201000,1480)")
s=s.replace('0x78028]','0x78028,0x7802a]').replace('0x78028,0x780]','0x78028,0x7802a,0x780]')
s=s.replace('v[316:]==','v[316:340]==')
anchor='   val=cr[idx]';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if idx in [0x13,0x19] and state['vswrites']==1 and word(1) in [0x7802a,0x780]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['sywrites']]
    if fault=='sy-'+phase+'-'+str(j):val^=1
''')
anchor='   if kind==u.UC_MEM_WRITE and off==0x680804:';assert s.count(anchor)==1
s=s.replace(anchor,'''   if kind==u.UC_MEM_WRITE and off==0x68080c:
    assert state['vswrites']==1 and word(1) in [0x7802a,0x780]
    state['sywrites']+=1;n=state['sywrites'];assert n<=2
    assert [word(340),word(341),word(342)]==[724,489,1] and value==(489 if n==1 else 724)
    writes.append(['sy',off,value])
    if fault==('sy-drop-write' if n==1 else 'sy-drop-undo'):return
    mm[off]=value
    if fault==('sy-wrong-write' if n==1 else 'sy-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('sy-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x680814,0x680810,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
    return
'''+anchor)
s=s.replace("state['vswrites']+=1;n=state['vswrites'];assert n<=2", "state['vswrites']+=1;n=state['vswrites'];assert n<=2\n    if n==2:assert state['sywrites']==2*word(342)")
anchor="   val=mm[off];j=0 if off==0x680808 else 5;phase=['before','after','undo'][state['vcwrites']]";assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if state['vswrites']==1 and word(1) in [0x7802a,0x780]:
    sj=4 if off==0x680814 else 3;sp=['before','after','undo'][state['sywrites']]
    if fault=='sy-'+sp+'-'+str(sj):val^=1
''')
anchor="   val=mm[off];phase=['before','after','undo'][state['vwrites']]";assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if state['vswrites']==1 and word(1) in [0x7802a,0x780]:
    sj={0x680800:1,0x680804:2,0x68080c:0,0x680810:5,0x680818:6}[off]
    sp=['before','after','undo'][state['sywrites']]
    if fault=='sy-'+sp+'-'+str(sj):val^=1
''')
s=s.replace('  if val==4:\n','  if val==4:\n   assert word(345)==0 and (not word(342) or word(344)==word(340))\n')
s=s.replace("'vs-coupling-8']","'vs-coupling-8','sy-coupling-8']")
maps={'v':{5:3,6:4,7:5,8:6},'q':{1:1,5:3,6:4,7:5,8:6},'w':{1:1,2:2,5:4,6:6,7:7,8:8},'x':{1:1,2:2,3:3,5:5,6:6,7:7,8:8}}
for key,mapping in maps.items():
 anchor='  '+key+'bad=bool('+key+'mask)';assert s.count(anchor)==1
 syncbit={'v':2,'q':2,'w':3,'x':4}[key]
 s=s.replace(anchor,"  if fault.startswith('sy-coupling-'):\n   j=int(fault.rsplit('-',1)[1]);k="+repr(mapping)+".get(j)\n   if k is not None:"+key+"mask|=1<<k\n  if fault in ['sy-drop-undo','sy-wrong-undo']:"+key+"mask|="+str(1<<syncbit)+'\n'+anchor)
s=s.replace('  xbad=bool(xmask)','''  xbad=bool(xmask)
  ymask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('sy-undo-','sy-coupling-')) else 1 if fault in ['sy-drop-undo','sy-wrong-undo'] else 0
  ybad=bool(ymask)''')
s=s.replace('or xbad','or xbad or ybad')
s=s.replace('else 0x780\n  assert v[1]==forward',"else 0x7802a if fault.startswith(('sy-before-','sy-after-','sy-coupling-')) or fault in ['sy-drop-write','sy-wrong-write'] else 0x780\n  assert v[1]==forward")
s=s.replace("[['vs',0x680814,0],['vs',0x680814,0]]", "[['vs',0x680814,0]]+([['sy',0x68080c,489],['sy',0x68080c,724]] if forward in [0x780,0x7802a] and not fault.startswith('sy-before-') else [])+[['vs',0x680814,0]]")
s=s.replace('else 0x78029 if xbad','else 0x7802b if ybad else 0x78029 if xbad')
for offset,key,syncbit in [(235,'v',2),(259,'q',2),(283,'w',3),(313,'x',4)]:
 anchor='   assert [v['+str(offset)+']]';assert s.count(anchor)==1
 addition="   if fault.startswith('sy-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);k="+repr(maps[key])+".get(j)\n    if k is not None:undo[k]^=1\n"
 addition+="   if fault=='sy-drop-undo':undo["+str(syncbit)+"]=489\n   if fault=='sy-wrong-undo':undo["+str(syncbit)+"]^=1\n"
 s=s.replace(anchor,addition+anchor)
anchor=" R['cases'].append(";assert s.count(anchor)==1
s=s.replace(anchor,''' # Independently specified NVVSYNCSTART transition and neighbor recovery.
 reached_sy=not cpu_bad and not baseline and forward in [0x780,0x7802a]
 if reached_sy:
  ref=[724,479,524,479,0,729,719,104,48];before=ref.copy()
  attempted_sy=not fault.startswith('sy-before-')
  if not attempted_sy:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[340]]+[v[346+3*i] for i in range(8)]==before
  assert v[341:343]==([489,1] if attempted_sy else [0,0]) and state['sywrites']==2*int(attempted_sy)
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
   assert v[345]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==ymask
  else:assert v[343:346]==[0xffffffff,0xffffffff,0] and all(v[347+3*i:349+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[340:346]==[0,0,0,0xffffffff,0xffffffff,0] and v[346:]==[0,0xffffffff,0xffffffff]*8
'''+anchor)
s=s.replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('sy-'+phase+'-'+str(j),fault='sy-'+phase+'-'+str(j))\n for j in range(1,9):run('sy-coupling-'+str(j),fault='sy-coupling-'+str(j))\n for f in ['sy-drop-write','sy-wrong-write','sy-drop-undo','sy-wrong-undo']:run(f,fault=f)")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('340-word','370-word').replace('len(v)==340','len(v)==370').replace('0x78028]','0x78028,0x7802a]').replace('(forward==0x780)','(forward in [0x780,0x7802a])').replace('v[316:]==','v[316:340]==')
anchor=' assert c13attempt in [0,1]'
code=''' yb,yt,ya,yf,yu,ym=v[340:346]
 ynb=[v[346+3*i] for i in range(8)];yna=[v[347+3*i] for i in range(8)];ynu=[v[348+3*i] for i in range(8)]
 assert ya in [0,1] and 0<=ym<512
 if forward in [0x780,0x7802a]:
  assert ya==int([yb]+ynb==[724,479,524,479,0,729,719,104,48])
  if ya:
   assert yt==489 and ym==sum(1<<i for i,(a,b) in enumerate(zip([yu]+ynu,[yb]+ynb)) if a!=b)
   assert (yf==489 and yna==ynb)==(forward==0x780)
  else:assert yt==ym==0 and yf==yu==0xffffffff and yna==ynu==[0xffffffff]*8 and forward==0x7802a
 else:assert v[340:346]==[0,0,0,0xffffffff,0xffffffff,0] and v[346:]==[0,0xffffffff,0xffffffff]*8
'''
s=s.replace(anchor,code+anchor).replace('and xm==0)','and xm==0 and ym==0)').replace('or xm:','or xm or ym:').replace('else 0x78029 if xm','else 0x7802b if ym else 0x78029 if xm')
s=s.replace("return {'vertical_valid_start':", "return {'vertical_sync_start':{'before':yb,'target':yt,'attempted':ya,'after':yf,'restored':yu,'cleanup_mask':ym,'neighbors_before':ynb,'neighbors_after':yna,'neighbors_restored':ynu},'vertical_valid_start':")
s=s.replace('plus four vertical words','plus five vertical words');p.write_text(s,newline='\n')
print('Extended780 actual COFF oracle and strict result schema; no hardware access')

"""Extend actual COFF execution oracle and independent physical schema for valid-end."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'model.py';s=p.read_text()
def replace(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'sewrites'","state={'vewrites':0,'sewrites'")
s=s.replace('0x201640','0x2016b8').replace('0x59c0','0x5948').replace("'<400I',c.mem_read(0x201000,1600)","'<430I',c.mem_read(0x201000,1720)")
s=s.replace('0x7842c]','0x7842c,0x7842e]').replace('0x7842c,0x784]','0x7842c,0x7842e,0x784]').replace('v[376:]==','v[376:400]==')
replace('   val=cr[idx]', '''   val=cr[idx]
   if idx in [0x13,0x19] and state['sewrites']==1 and word(1) in [0x7842e,0x784]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vewrites']]
    if fault=='ve-'+phase+'-'+str(j):val^=1
''')
replace('   if kind==u.UC_MEM_WRITE and off==0x680804:', '''   if kind==u.UC_MEM_WRITE and off==0x680818:
    assert state['sewrites']==1 and word(1) in [0x7842e,0x784]
    state['vewrites']+=1;n=state['vewrites'];assert n<=2
    assert [word(400),word(401),word(402)]==[719,479,1] and value==(479 if n==1 else 719)
    writes.append(['ve',off,value])
    if fault==('ve-drop-write' if n==1 else 've-drop-undo'):return
    mm[off]=value
    if fault==('ve-wrong-write' if n==1 else 've-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('ve-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x680814,0x68080c,0x680810][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
    return
   if kind==u.UC_MEM_WRITE and off==0x680804:''')
replace("state['sewrites']+=1;n=state['sewrites'];assert n<=2", "state['sewrites']+=1;n=state['sewrites'];assert n<=2\n    if n==2:assert state['vewrites']==2*word(402)")
anchor="   val=mm[off];j=0 if off==0x680808 else 5;phase=['before','after','undo'][state['vcwrites']]"
replace(anchor,anchor+'''
   if state['sewrites']==1 and word(1) in [0x7842e,0x784]:
    sj=4 if off==0x680814 else 3;sp=['before','after','undo'][state['vewrites']]
    if fault=='ve-'+sp+'-'+str(sj):val^=1
''')
anchor="   val=mm[off];phase=['before','after','undo'][state['vwrites']]"
replace(anchor,anchor+'''
   if state['sewrites']==1 and word(1) in [0x7842e,0x784]:
    sj={0x680800:1,0x680804:2,0x68080c:5,0x680810:6,0x680818:0}[off]
    sp=['before','after','undo'][state['vewrites']]
    if fault=='ve-'+sp+'-'+str(sj):val^=1
''')
replace('  if val==4:\n','  if val==4:\n   assert word(405)==0 and (not word(402) or word(404)==word(400))\n')
s=s.replace("'se-coupling-8']","'se-coupling-8','ve-coupling-8']")
# Only faults still present after each intervening own-register undo survive.
maps={'v':{7:5,8:6},'q':{1:1,7:5,8:6},'w':{1:1,2:2,7:7,8:8},'x':{1:1,2:2,3:3,7:7,8:8},'y':{1:1,2:2,3:3,4:4,7:7,8:8},'end':{1:1,2:2,3:3,4:4,5:5,7:7,8:8}}
slots={'v':4,'q':4,'w':6,'x':6,'y':6,'end':6}
for key,mapping in maps.items():
 anchor='  '+key+'bad=bool('+key+'mask)'
 replace(anchor,"  if fault.startswith('ve-coupling-'):\n   j=int(fault.rsplit('-',1)[1]);k="+repr(mapping)+".get(j)\n   if k is not None:"+key+"mask|=1<<k\n  if fault in ['ve-drop-undo','ve-wrong-undo']:"+key+"mask|="+str(1<<slots[key])+'\n'+anchor)
replace('  endbad=bool(endmask)', '''  endbad=bool(endmask)
  vemask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('ve-undo-','ve-coupling-')) else 1 if fault in ['ve-drop-undo','ve-wrong-undo'] else 0
  vebad=bool(vemask)''')
s=s.replace('or endbad','or endbad or vebad')
replace('else 0x784\n  assert v[1]==forward',"else 0x7842e if fault.startswith(('ve-before-','ve-after-','ve-coupling-')) or fault in ['ve-drop-write','ve-wrong-write'] else 0x784\n  assert v[1]==forward")
replace("[['se',0x680810,492],['se',0x680810,729]]", "[['se',0x680810,492]]+([['ve',0x680818,479],['ve',0x680818,719]] if forward in [0x784,0x7842e] and not fault.startswith('ve-before-') else [])+[['se',0x680810,729]]")
s=s.replace('else 0x7842d if endbad','else 0x7842f if vebad else 0x7842d if endbad')
for offset,key in [(235,'v'),(259,'q'),(283,'w'),(313,'x'),(343,'y'),(374,'end')]:
 anchor='   assert [v['+str(offset)+']]'
 addition="   if fault.startswith('ve-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);k="+repr(maps[key])+".get(j)\n    if k is not None:undo[k]^=1\n"
 addition+="   if fault=='ve-drop-undo':undo["+str(slots[key])+"]=479\n   if fault=='ve-wrong-undo':undo["+str(slots[key])+"]^=1\n"
 replace(anchor,addition+anchor)
replace(" R['cases'].append(",''' # Independent NVVVALIDEND constants, neighbors, and reverse recovery.
 reached_ve=not cpu_bad and not baseline and forward in [0x784,0x7842e]
 if reached_ve:
  ref=[719,479,524,479,0,489,492,104,48];before=ref.copy()
  attempted_ve=not fault.startswith('ve-before-')
  if not attempted_ve:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[400]]+[v[406+3*i] for i in range(8)]==before
  assert v[401:403]==([479,1] if attempted_ve else [0,0]) and state['vewrites']==2*int(attempted_ve)
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
   assert v[405]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==vemask
  else:assert v[403:406]==[0xffffffff,0xffffffff,0] and all(v[407+3*i:409+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[400:406]==[0,0,0,0xffffffff,0xffffffff,0] and v[406:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('ve-'+phase+'-'+str(j),fault='ve-'+phase+'-'+str(j))\n for j in range(1,9):run('ve-coupling-'+str(j),fault='ve-coupling-'+str(j))\n for f in ['ve-drop-write','ve-wrong-write','ve-drop-undo','ve-wrong-undo']:run(f,fault=f)")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('400-word','430-word').replace('len(v)==400','len(v)==430').replace('0x7842c]','0x7842c,0x7842e]').replace('(forward==0x784)','(forward in [0x784,0x7842e])').replace('v[376:]==','v[376:400]==')
code=''' vb2,vt2,va2,vf2,vu2,vm2=v[400:406]
 vn2=[v[406+3*i] for i in range(8)];vfns=[v[407+3*i] for i in range(8)];vuns=[v[408+3*i] for i in range(8)]
 assert va2 in [0,1] and 0<=vm2<512
 if forward in [0x784,0x7842e]:
  assert va2==int([vb2]+vn2==[719,479,524,479,0,489,492,104,48])
  if va2:
   assert vt2==479 and vm2==sum(1<<i for i,(a,b) in enumerate(zip([vu2]+vuns,[vb2]+vn2)) if a!=b)
   assert (vf2==479 and vfns==vn2)==(forward==0x784)
  else:assert vt2==vm2==0 and vf2==vu2==0xffffffff and vfns==vuns==[0xffffffff]*8 and forward==0x7842e
 else:assert v[400:406]==[0,0,0,0xffffffff,0xffffffff,0] and v[406:]==[0,0xffffffff,0xffffffff]*8
'''
replace(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and emsk==0)','and emsk==0 and vm2==0)').replace('or emsk:','or emsk or vm2:').replace('else 0x7842d if emsk','else 0x7842f if vm2 else 0x7842d if emsk')
s=s.replace("return {'vertical_sync_end':", "return {'vertical_valid_end':{'before':vb2,'target':vt2,'attempted':va2,'after':vf2,'restored':vu2,'cleanup_mask':vm2,'neighbors_before':vn2,'neighbors_after':vfns,'neighbors_restored':vuns},'vertical_sync_end':")
s=s.replace('plus six vertical words','plus seven vertical words');p.write_text(s,newline='\n')
print('Extended784 actual COFF oracle and strict schema; no hardware access')

"""Extend actual-code oracle and independent physical schema for sync-end."""
from pathlib import Path
import re
K=Path(__file__).resolve().parent
p=K/'model.py';s=p.read_text()
def replace(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'sywrites'","state={'sewrites':0,'sywrites'")
s=s.replace('0x2015c8','0x201640').replace('0x5a38','0x59c0').replace("'<370I',c.mem_read(0x201000,1480)","'<400I',c.mem_read(0x201000,1600)")
s=s.replace('0x7822a]','0x7822a,0x7822c]').replace('0x7822a,0x782]','0x7822a,0x7822c,0x782]').replace('v[346:]==','v[346:370]==')
replace('   val=cr[idx]', '''   val=cr[idx]
   if idx in [0x13,0x19] and state['sywrites']==1 and word(1) in [0x7822c,0x782]:
    j=7+[0x13,0x19].index(idx);phase=['before','after','undo'][state['sewrites']]
    if fault=='se-'+phase+'-'+str(j):val^=1
''')
replace('   if kind==u.UC_MEM_WRITE and off==0x680804:', '''   if kind==u.UC_MEM_WRITE and off==0x680810:
    assert state['sywrites']==1 and word(1) in [0x7822c,0x782]
    state['sewrites']+=1;n=state['sewrites'];assert n<=2
    assert [word(370),word(371),word(372)]==[729,492,1] and value==(492 if n==1 else 729)
    writes.append(['se',off,value])
    if fault==('se-drop-write' if n==1 else 'se-drop-undo'):return
    mm[off]=value
    if fault==('se-wrong-write' if n==1 else 'se-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('se-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8
     if j<=6:mm[[0x680800,0x680804,0x680808,0x680814,0x68080c,0x680818][j-1]]^=1
     else:cr[[0x13,0x19][j-7]]^=1
    return
   if kind==u.UC_MEM_WRITE and off==0x680804:''')
replace("state['sywrites']+=1;n=state['sywrites'];assert n<=2", "state['sywrites']+=1;n=state['sywrites'];assert n<=2\n    if n==2:assert state['sewrites']==2*word(372)")
anchor="   val=mm[off];j=0 if off==0x680808 else 5;phase=['before','after','undo'][state['vcwrites']]"
replace(anchor,anchor+'''
   if state['sywrites']==1 and word(1) in [0x7822c,0x782]:
    sj=4 if off==0x680814 else 3;sp=['before','after','undo'][state['sewrites']]
    if fault=='se-'+sp+'-'+str(sj):val^=1
''')
anchor="   val=mm[off];phase=['before','after','undo'][state['vwrites']]"
replace(anchor,anchor+'''
   if state['sywrites']==1 and word(1) in [0x7822c,0x782]:
    sj={0x680800:1,0x680804:2,0x68080c:5,0x680810:0,0x680818:6}[off]
    sp=['before','after','undo'][state['sewrites']]
    if fault=='se-'+sp+'-'+str(sj):val^=1
''')
replace('  if val==4:\n','  if val==4:\n   assert word(375)==0 and (not word(372) or word(374)==word(370))\n')
s=s.replace("'sy-coupling-8']","'sy-coupling-8','se-coupling-8']")
# Earlier recovery snapshots see only faults that remain after intervening undo.
# Own previous-stage writes restore their own register before taking snapshots.
maps={'v':{6:4,7:5,8:6},'q':{1:1,6:4,7:5,8:6},'w':{1:1,2:2,6:6,7:7,8:8},'x':{1:1,2:2,3:3,6:6,7:7,8:8},'y':{1:1,2:2,3:3,4:4,6:6,7:7,8:8}}
bits={'v':3,'q':3,'w':4,'x':5,'y':5}
for key,mapping in maps.items():
 anchor='  '+key+'bad=bool('+key+'mask)'
 replace(anchor,"  if fault.startswith('se-coupling-'):\n   j=int(fault.rsplit('-',1)[1]);k="+repr(mapping)+".get(j)\n   if k is not None:"+key+"mask|=1<<k\n  if fault in ['se-drop-undo','se-wrong-undo']:"+key+"mask|="+str(1<<bits[key])+'\n'+anchor)
replace('  ybad=bool(ymask)', '''  ybad=bool(ymask)
  endmask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('se-undo-','se-coupling-')) else 1 if fault in ['se-drop-undo','se-wrong-undo'] else 0
  endbad=bool(endmask)''')
s=s.replace('or ybad','or ybad or endbad')
replace('else 0x782\n  assert v[1]==forward',"else 0x7822c if fault.startswith(('se-before-','se-after-','se-coupling-')) or fault in ['se-drop-write','se-wrong-write'] else 0x782\n  assert v[1]==forward")
replace("[['sy',0x68080c,489],['sy',0x68080c,724]]", "[['sy',0x68080c,489]]+([['se',0x680810,492],['se',0x680810,729]] if forward in [0x782,0x7822c] and not fault.startswith('se-before-') else [])+[['sy',0x68080c,724]]")
s=s.replace('else 0x7822b if ybad','else 0x7822d if endbad else 0x7822b if ybad')
for offset,key in [(235,'v'),(259,'q'),(283,'w'),(313,'x'),(343,'y')]:
 anchor='   assert [v['+str(offset)+']]'
 addition="   if fault.startswith('se-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);k="+repr(maps[key])+".get(j)\n    if k is not None:undo[k]^=1\n"
 addition+="   if fault=='se-drop-undo':undo["+str(bits[key])+"]=492\n   if fault=='se-wrong-undo':undo["+str(bits[key])+"]^=1\n"
 replace(anchor,addition+anchor)
replace(" R['cases'].append(",''' # Independently specified NVVSYNCEND values and neighbor recovery.
 reached_se=not cpu_bad and not baseline and forward in [0x782,0x7822c]
 if reached_se:
  ref=[729,479,524,479,0,489,719,104,48];before=ref.copy()
  attempted_se=not fault.startswith('se-before-')
  if not attempted_se:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[370]]+[v[376+3*i] for i in range(8)]==before
  assert v[371:373]==([492,1] if attempted_se else [0,0]) and state['sewrites']==2*int(attempted_se)
  if attempted_se:
   after=[492]+ref[1:];undo=ref.copy()
   if fault=='se-drop-write':after[0]=729
   if fault=='se-wrong-write':after[0]^=1
   if fault.startswith('se-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('se-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('se-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='se-drop-undo':undo[0]=492
   if fault=='se-wrong-undo':undo[0]^=1
   assert [v[373]]+[v[377+3*i] for i in range(8)]==after
   assert [v[374]]+[v[378+3*i] for i in range(8)]==undo
   assert v[375]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==endmask
  else:assert v[373:376]==[0xffffffff,0xffffffff,0] and all(v[377+3*i:379+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[370:376]==[0,0,0,0xffffffff,0xffffffff,0] and v[376:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('se-'+phase+'-'+str(j),fault='se-'+phase+'-'+str(j))\n for j in range(1,9):run('se-coupling-'+str(j),fault='se-coupling-'+str(j))\n for f in ['se-drop-write','se-wrong-write','se-drop-undo','se-wrong-undo']:run(f,fault=f)")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('370-word','400-word').replace('len(v)==370','len(v)==400').replace('0x7822a]','0x7822a,0x7822c]').replace('(forward==0x782)','(forward in [0x782,0x7822c])').replace('v[346:]==','v[346:370]==')
code=''' eb,et,ea,ef,eu,emsk=v[370:376]
 enb=[v[376+3*i] for i in range(8)];ena=[v[377+3*i] for i in range(8)];enu=[v[378+3*i] for i in range(8)]
 assert ea in [0,1] and 0<=emsk<512
 if forward in [0x782,0x7822c]:
  assert ea==int([eb]+enb==[729,479,524,479,0,489,719,104,48])
  if ea:
   assert et==492 and emsk==sum(1<<i for i,(a,b) in enumerate(zip([eu]+enu,[eb]+enb)) if a!=b)
   assert (ef==492 and ena==enb)==(forward==0x782)
  else:assert et==emsk==0 and ef==eu==0xffffffff and ena==enu==[0xffffffff]*8 and forward==0x7822c
 else:assert v[370:376]==[0,0,0,0xffffffff,0xffffffff,0] and v[376:]==[0,0xffffffff,0xffffffff]*8
'''
replace(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and ym==0)','and ym==0 and emsk==0)').replace('or ym:','or ym or emsk:').replace('else 0x7822b if ym','else 0x7822d if emsk else 0x7822b if ym')
s=s.replace("return {'vertical_sync_start':", "return {'vertical_sync_end':{'before':eb,'target':et,'attempted':ea,'after':ef,'restored':eu,'cleanup_mask':emsk,'neighbors_before':enb,'neighbors_after':ena,'neighbors_restored':enu},'vertical_sync_start':")
s=s.replace('plus five vertical words','plus six vertical words');p.write_text(s,newline='\n')
print('Extended782 actual COFF oracle and strict result schema; no hardware access')

"""Actual-COFF oracle for CR10 including propagation into earlier CR07 cleanup."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model.py';s=p.read_text()
def replace(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'c7writes'","state={'c10writes':0,'c7writes'")
s=s.replace('0x201730','0x2017a8').replace('0x58d0','0x5858').replace("'<460I',c.mem_read(0x201000,1840)","'<490I',c.mem_read(0x201000,1960)")
s=s.replace('0x78830]','0x78830,0x78832]').replace('0x78830,0x788]','0x78830,0x78832,0x788]').replace('v[436:]==','v[436:460]==')
replace('assert idx in [7,','assert idx in [0x10,7,')
replace('    if idx==7:', '''    if idx==0x10:
     assert state['c7writes']==1 and state['vewrites']==1 and word(1) in [0x78832,0x788]
     state['c10writes']+=1;n=state['c10writes'];assert n<=2
     assert [word(460),word(461),word(462)]==[212,233,1] and value==(233 if n==1 else 212)
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',0x10,value])
     if fault==('c10-drop-write' if n==1 else 'c10-drop-undo'):return
     cr[0x10]=value
     if fault==('c10-wrong-write' if n==1 else 'c10-wrong-undo'):cr[0x10]^=1
     if n==1 and fault.startswith('c10-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
     return
    if idx==7:''')
replace("state['c7writes']+=1;n=state['c7writes'];assert n<=2","state['c7writes']+=1;n=state['c7writes'];assert n<=2\n     if n==2:assert state['c10writes']==2*word(462)")
replace('   val=cr[idx]', '''   val=cr[idx]
   if idx in [0x10,6,7,9,0x12,0x15,0x16,0x18,0x25] and state['c7writes']==1 and word(1) in [0x78832,0x788]:
    j=[0x10,6,7,9,0x12,0x15,0x16,0x18,0x25].index(idx);phase=['before','after','undo'][state['c10writes']]
    if fault=='c10-'+phase+'-'+str(j):val^=1
''')
replace('  if val==4:\n','  if val==4:\n   assert word(465)==0 and (not word(462) or word(464)==word(460))\n')
replace('  c7bad=bool(c7mask)', '''  # Persistent CR10 corruption is visible in CR07's later neighbor recovery.
  if fault in ['c10-drop-undo','c10-wrong-undo']:c7mask|=8
  if fault.startswith('c10-coupling-'):c7mask|=[0,2,0,4,16,32,64,128,256][int(fault.rsplit('-',1)[1])]
  c7bad=bool(c7mask)
  c10mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('c10-undo-','c10-coupling-')) else 1 if fault in ['c10-drop-undo','c10-wrong-undo'] else 0
  c10bad=bool(c10mask)''')
s=s.replace('or c7bad','or c7bad or c10bad')
replace('else 0x788\n  assert v[1]==forward',"else 0x78832 if fault.startswith(('c10-before-','c10-after-','c10-coupling-')) or fault in ['c10-drop-write','c10-wrong-write'] else 0x788\n  assert v[1]==forward")
replace("[['cr',7,116],['cr',7,240]]","[['cr',7,116]]+([['cr',0x10,233],['cr',0x10,212]] if forward in [0x788,0x78832] and not fault.startswith('c10-before-') else [])+[['cr',7,240]]")
s=s.replace('else 0x78831 if c7bad','else 0x78833 if c10bad else 0x78831 if c7bad')
replace("   if fault=='c7-wrong-undo':undo[0]^=1", """   if fault=='c7-wrong-undo':undo[0]^=1
   if fault=='c10-drop-undo':undo[3]=233
   if fault=='c10-wrong-undo':undo[3]^=1
   if fault.startswith('c10-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1:1,3:2,4:4,5:5,6:6,7:7,8:8}
    if j in mapping:undo[mapping[j]]^=1""")
replace(" R['cases'].append(",''' # New CR10 fields and complete neighbor tuple, independent constants.
 reached_c10=not cpu_bad and not baseline and forward in [0x788,0x78832]
 if reached_c10:
  ref=[212,236,116,96,207,207,237,255,16];before=ref.copy()
  attempted_c10=not fault.startswith('c10-before-')
  if not attempted_c10:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[460]]+[v[466+3*i] for i in range(8)]==before
  assert v[461:463]==([233,1] if attempted_c10 else [0,0]) and state['c10writes']==2*int(attempted_c10)
  if attempted_c10:
   after=[233]+ref[1:];undo=ref.copy()
   if fault=='c10-drop-write':after[0]=212
   if fault=='c10-wrong-write':after[0]^=1
   if fault.startswith('c10-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('c10-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('c10-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='c10-drop-undo':undo[0]=233
   if fault=='c10-wrong-undo':undo[0]^=1
   assert [v[463]]+[v[467+3*i] for i in range(8)]==after
   assert [v[464]]+[v[468+3*i] for i in range(8)]==undo
   assert v[465]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==c10mask
  else:assert v[463:466]==[0xffffffff,0xffffffff,0] and all(v[467+3*i:469+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[460:466]==[0,0,0,0xffffffff,0xffffffff,0] and v[466:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('c10-'+phase+'-'+str(j),fault='c10-'+phase+'-'+str(j))\n for j in range(1,9):run('c10-coupling-'+str(j),fault='c10-coupling-'+str(j))\n for f in ['c10-drop-write','c10-wrong-write','c10-drop-undo','c10-wrong-undo']:run(f,fault=f)")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('460-word','490-word').replace('len(v)==460','len(v)==490').replace('0x78830]','0x78830,0x78832]').replace('(forward==0x788)','(forward in [0x788,0x78832])').replace('v[436:]==','v[436:460]==')
code=''' cb10,ct10,ca10,cf10,cu10,cm10=v[460:466]
 cn10=[v[466+3*i] for i in range(8)];cfns10=[v[467+3*i] for i in range(8)];cuns10=[v[468+3*i] for i in range(8)]
 assert ca10 in [0,1] and 0<=cm10<512
 if forward in [0x788,0x78832]:
  assert ca10==int([cb10]+cn10==[212,236,116,96,207,207,237,255,16])
  if ca10:
   assert ct10==233
   assert cm10==sum(1<<i for i,(a,b) in enumerate(zip([cu10]+cuns10,[cb10]+cn10)) if a!=b)
   assert (cf10==233 and cfns10==cn10)==(forward==0x788)
  else:assert ct10==cm10==0 and cf10==cu10==0xffffffff and cfns10==cuns10==[0xffffffff]*8 and forward==0x78832
 else:assert v[460:466]==[0,0,0,0xffffffff,0xffffffff,0] and v[466:]==[0,0xffffffff,0xffffffff]*8
'''
replace(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and cm7==0)','and cm7==0 and cm10==0)').replace('or cm7:','or cm7 or cm10:').replace('else 0x78831 if cm7','else 0x78833 if cm10 else 0x78831 if cm7')
s=s.replace("return {'crtc_vsync_high':", "return {'crtc_vsync_low':{'before':cb10,'target':ct10,'attempted':ca10,'after':cf10,'restored':cu10,'cleanup_mask':cm10,'neighbors_before':cn10,'neighbors_after':cfns10,'neighbors_restored':cuns10},'crtc_vsync_high':")
p.write_text(s,newline='\n')
print('Extended788 COFF oracle and physical schema; no hardware access')

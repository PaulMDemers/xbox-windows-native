"""Extend actual COFF oracle and independent schema for shared CR07 transaction."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model.py';s=p.read_text()
def replace(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'c10writes'","state={'ct7writes':0,'c10writes'")
s=s.replace('0x2017a8','0x201820').replace('0x5858','0x57e0').replace("'<490I',c.mem_read(0x201000,1960)","'<520I',c.mem_read(0x201000,2080)")
s=s.replace('0x79032]','0x79032,0x79034]').replace('0x79032,0x790]','0x79032,0x79034,0x790]').replace('v[466:]==','v[466:490]==')
replace('    if idx==7:', '''    if idx==7 and state['c10writes']==1:
     assert state['c7writes']==1 and word(1) in [0x79034,0x790]
     state['ct7writes']+=1;n=state['ct7writes'];assert n<=2
     assert [word(490),word(491),word(492)]==[116,116,1] and value==116
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',7,value])
     if fault==('ct7-drop-write' if n==1 else 'ct7-drop-undo') or (n==2 and fault=='ct7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('ct7-wrong-write' if n==1 else 'ct7-wrong-undo') or (n==1 and fault=='ct7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('ct7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,0x10,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
     return
    if idx==7:''')
replace("state['c10writes']+=1;n=state['c10writes'];assert n<=2","state['c10writes']+=1;n=state['c10writes'];assert n<=2\n     if n==2:assert state['ct7writes']==2*word(492)")
replace('   val=cr[idx]', '''   val=cr[idx]
   if idx in [7,6,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['c10writes']==1 and word(1) in [0x79034,0x790]:
    j=[7,6,9,0x10,0x12,0x15,0x16,0x18,0x25].index(idx);phase=['before','after','undo'][state['ct7writes']]
    if fault=='ct7-'+phase+'-'+str(j):val^=1
''')
replace('  if val==4:\n','  if val==4:\n   assert word(495)==0 and (not word(492) or word(494)==word(490))\n')
replace('  c7bad=bool(c7mask)', '''  if fault.startswith('ct7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);c7mask|={1:2,2:4,3:0,4:16,5:32,6:64,7:128,8:256}[j]
  c7bad=bool(c7mask)''')
replace('  c10bad=bool(c10mask)', '''  if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:c10mask|=4
  if fault.startswith('ct7-coupling-'):
   j=int(fault.rsplit('-',1)[1]);c10mask|={1:2,2:8,3:0,4:16,5:32,6:64,7:128,8:256}[j]
  c10bad=bool(c10mask)
  ct7mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('ct7-undo-','ct7-coupling-')) else 1 if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo'] else 0
  ct7bad=bool(ct7mask)''')
s=s.replace('or c10bad','or c10bad or ct7bad')
replace('else 0x790\n  assert v[1]==forward',"else 0x79034 if fault.startswith(('ct7-before-','ct7-after-','ct7-coupling-')) or fault in ['ct7-wrong-write','ct7-wrong-write-drop-undo'] else 0x790\n  assert v[1]==forward")
replace("[['cr',0x10,233],['cr',0x10,212]]","[['cr',0x10,233]]+([['cr',7,116],['cr',7,116]] if forward in [0x790,0x79034] and not fault.startswith('ct7-before-') else [])+[['cr',0x10,212]]")
s=s.replace('else 0x79033 if c10bad','else 0x79035 if ct7bad else 0x79033 if c10bad')
replace("   if fault=='c7-wrong-undo':undo[0]^=1", """   if fault=='c7-wrong-undo':undo[0]^=1
   if fault.startswith('ct7-coupling-'):
    j=int(fault.rsplit('-',1)[1])
    if j!=3:undo[j]^=1""")
replace("   if fault=='c10-wrong-undo':undo[0]^=1", """   if fault=='c10-wrong-undo':undo[0]^=1
   if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:undo[2]^=1
   if fault.startswith('ct7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);mapping={1:1,2:3,4:4,5:5,6:6,7:7,8:8}
    if j in mapping:undo[mapping[j]]^=1""")
replace(" R['cases'].append(",''' # Exact new shared-CR07 tuple with independently specified constants.
 reached_ct7=not cpu_bad and not baseline and forward in [0x790,0x79034]
 if reached_ct7:
  ref=[116,236,96,233,207,207,237,255,16];before=ref.copy()
  attempted_ct7=not fault.startswith('ct7-before-')
  if not attempted_ct7:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[490]]+[v[496+3*i] for i in range(8)]==before
  assert v[491:493]==([116,1] if attempted_ct7 else [0,0]) and state['ct7writes']==2*int(attempted_ct7)
  if attempted_ct7:
   after=ref.copy();undo=ref.copy()
   if fault in ['ct7-wrong-write','ct7-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('ct7-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('ct7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('ct7-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:undo[0]^=1
   assert [v[493]]+[v[497+3*i] for i in range(8)]==after
   assert [v[494]]+[v[498+3*i] for i in range(8)]==undo
   assert v[495]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==ct7mask
  else:assert v[493:496]==[0xffffffff,0xffffffff,0] and all(v[497+3*i:499+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[490:496]==[0,0,0,0xffffffff,0xffffffff,0] and v[496:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('ct7-'+phase+'-'+str(j),fault='ct7-'+phase+'-'+str(j))\n for j in range(1,9):run('ct7-coupling-'+str(j),fault='ct7-coupling-'+str(j))\n for f in ['ct7-drop-write','ct7-wrong-write','ct7-drop-undo','ct7-wrong-undo','ct7-wrong-write-drop-undo']:run(f,fault=f)")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('490-word','520-word').replace('len(v)==490','len(v)==520').replace('0x79032]','0x79032,0x79034]').replace('(forward==0x790)','(forward in [0x790,0x79034])').replace('v[466:]==','v[466:490]==')
code=''' cb7t,ct7t,ca7t,cf7t,cu7t,cm7t=v[490:496]
 cn7t=[v[496+3*i] for i in range(8)];cfns7t=[v[497+3*i] for i in range(8)];cuns7t=[v[498+3*i] for i in range(8)]
 assert ca7t in [0,1] and 0<=cm7t<512
 if forward in [0x790,0x79034]:
  assert ca7t==int([cb7t]+cn7t==[116,236,96,233,207,207,237,255,16])
  if ca7t:
   assert ct7t==116
   assert cm7t==sum(1<<i for i,(a,b) in enumerate(zip([cu7t]+cuns7t,[cb7t]+cn7t)) if a!=b)
   assert (cf7t==116 and cfns7t==cn7t)==(forward==0x790)
  else:assert ct7t==cm7t==0 and cf7t==cu7t==0xffffffff and cfns7t==cuns7t==[0xffffffff]*8 and forward==0x79034
 else:assert v[490:496]==[0,0,0,0xffffffff,0xffffffff,0] and v[496:]==[0,0xffffffff,0xffffffff]*8
'''
replace(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and cm10==0)','and cm10==0 and cm7t==0)').replace('or cm10:','or cm10 or cm7t:').replace('else 0x79033 if cm10','else 0x79035 if cm7t else 0x79033 if cm10')
s=s.replace("return {'crtc_vsync_low':", "return {'crtc_vtotal_high':{'before':cb7t,'target':ct7t,'attempted':ca7t,'after':cf7t,'restored':cu7t,'cleanup_mask':cm7t,'neighbors_before':cn7t,'neighbors_after':cfns7t,'neighbors_restored':cuns7t},'crtc_vsync_low':")
p.write_text(s,newline='\n')
print('Extended790 host oracle/schema; no hardware access')

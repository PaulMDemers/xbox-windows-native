"""Extend the real-COFF oracle and separate schema for CR06; no hardware access."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model.py';s=p.read_text()
def replace(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'ct7writes'","state={'ct6writes':0,'ct7writes'")
s=s.replace('0x201820','0x201898').replace('0x57e0','0x5768').replace("'<520I',c.mem_read(0x201000,2080)","'<550I',c.mem_read(0x201000,2200)")
s=s.replace('0x79234]','0x79234,0x79236]').replace('0x79234,0x792]','0x79234,0x79236,0x792]').replace('v[496:]==','v[496:520]==')
replace('assert idx in [0x10,7,1,3,2,0,4,5,0x13,0x1f,0x14,0x17,0x19]','assert idx in [6,0x10,7,1,3,2,0,4,5,0x13,0x1f,0x14,0x17,0x19]')
replace('    if idx==0x10:', '''    if idx==6:
     assert state['ct7writes']==1 and state['c10writes']==1 and word(1) in [0x79236,0x792]
     state['ct6writes']+=1;n=state['ct6writes'];assert n<=2
     assert [word(520),word(521),word(522)]==[236,12,1] and value==[12,236][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',6,value])
     if fault==('ct6-drop-write' if n==1 else 'ct6-drop-undo') or (n==2 and fault=='ct6-wrong-write-drop-undo'):return
     cr[6]=value
     if fault==('ct6-wrong-write' if n==1 else 'ct6-wrong-undo') or (n==1 and fault=='ct6-wrong-write-drop-undo'):cr[6]^=1
     if n==1 and fault.startswith('ct6-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[7,9,0x10,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
     return
    if idx==0x10:''')
replace("state['ct7writes']+=1;n=state['ct7writes'];assert n<=2","state['ct7writes']+=1;n=state['ct7writes'];assert n<=2\n     if n==2:assert state['ct6writes']==2*word(522)")
replace('   val=cr[idx]', '''   val=cr[idx]
   if idx in [6,7,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['ct7writes']==1 and word(1) in [0x79236,0x792]:
    j=[6,7,9,0x10,0x12,0x15,0x16,0x18,0x25].index(idx);phase=['before','after','undo'][state['ct6writes']]
    if fault=='ct6-'+phase+'-'+str(j):val^=1
''')
replace('  if val==4:\n','  if val==4:\n   assert word(525)==0 and (not word(522) or word(524)==word(520))\n')
# Explicit propagation in actual reverse order: CR06, second CR07, CR10, first CR07.
replace('  c7bad=bool(c7mask)', '''  if fault in ['ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo']:c7mask|=2
  if fault.startswith('ct6-coupling-'):
   j=int(fault.rsplit('-',1)[1]);c7mask|={1:0,2:4,3:0,4:16,5:32,6:64,7:128,8:256}[j]
  c7bad=bool(c7mask)''')
replace('  c10bad=bool(c10mask)', '''  if fault in ['ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo']:c10mask|=2
  if fault.startswith('ct6-coupling-'):
   j=int(fault.rsplit('-',1)[1]);c10mask|={1:0,2:8,3:0,4:16,5:32,6:64,7:128,8:256}[j]
  c10bad=bool(c10mask)''')
replace('  ct7bad=bool(ct7mask)', '''  if fault in ['ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo']:ct7mask|=2
  if fault.startswith('ct6-coupling-'):
   j=int(fault.rsplit('-',1)[1]);ct7mask|={1:0,2:4,3:8,4:16,5:32,6:64,7:128,8:256}[j]
  ct7bad=bool(ct7mask)
  ct6mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('ct6-undo-','ct6-coupling-')) else 1 if fault in ['ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo'] else 0
  ct6bad=bool(ct6mask)''')
s=s.replace('or ct7bad','or ct7bad or ct6bad')
replace('else 0x792\n  assert v[1]==forward',"else 0x79236 if fault.startswith(('ct6-before-','ct6-after-','ct6-coupling-')) or fault in ['ct6-drop-write','ct6-wrong-write','ct6-wrong-write-drop-undo'] else 0x792\n  assert v[1]==forward")
replace("[['cr',7,116],['cr',7,116]]","[['cr',7,116]]+([['cr',6,12],['cr',6,236]] if forward in [0x792,0x79236] and not fault.startswith('ct6-before-') else [])+[['cr',7,116]]")
s=s.replace('else 0x79235 if ct7bad','else 0x79237 if ct6bad else 0x79235 if ct7bad')
for token,neighbor_map in [("   if fault=='c7-wrong-undo':undo[0]^=1",{2:2,4:4,5:5,6:6,7:7,8:8}),("   if fault=='c10-wrong-undo':undo[0]^=1",{2:3,4:4,5:5,6:6,7:7,8:8}),("   if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:undo[0]^=1",{2:2,3:3,4:4,5:5,6:6,7:7,8:8})]:
 replace(token,token+"\n   if fault=='ct6-drop-undo':undo[1]=12\n   if fault=='ct6-wrong-undo':undo[1]=237\n   if fault=='ct6-wrong-write-drop-undo':undo[1]=13\n   if fault.startswith('ct6-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);mapping="+repr(neighbor_map)+"\n    if j in mapping:undo[mapping[j]]^=1")
replace(" R['cases'].append(",''' # Independent CR06 tuple: total 524 -> low byte 12, saved byte 236.
 reached_ct6=not cpu_bad and not baseline and forward in [0x792,0x79236]
 if reached_ct6:
  ref=[236,116,96,233,207,207,237,255,16];before=ref.copy()
  attempted_ct6=not fault.startswith('ct6-before-')
  if not attempted_ct6:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[520]]+[v[526+3*i] for i in range(8)]==before
  assert v[521:523]==([12,1] if attempted_ct6 else [0,0]) and state['ct6writes']==2*int(attempted_ct6)
  if attempted_ct6:
   after=ref.copy();after[0]=12;undo=ref.copy()
   if fault=='ct6-drop-write':after[0]=236
   if fault in ['ct6-wrong-write','ct6-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('ct6-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('ct6-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('ct6-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='ct6-drop-undo':undo[0]=12
   if fault=='ct6-wrong-undo':undo[0]=237
   if fault=='ct6-wrong-write-drop-undo':undo[0]=13
   assert [v[523]]+[v[527+3*i] for i in range(8)]==after
   assert [v[524]]+[v[528+3*i] for i in range(8)]==undo
   assert v[525]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==ct6mask
  else:assert v[523:526]==[0xffffffff,0xffffffff,0] and all(v[527+3*i:529+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[520:526]==[0,0,0,0xffffffff,0xffffffff,0] and v[526:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('ct6-'+phase+'-'+str(j),fault='ct6-'+phase+'-'+str(j))\n for j in range(1,9):run('ct6-coupling-'+str(j),fault='ct6-coupling-'+str(j))\n for f in ['ct6-drop-write','ct6-wrong-write','ct6-drop-undo','ct6-wrong-undo','ct6-wrong-write-drop-undo']:run(f,fault=f)")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('520-word','550-word').replace('len(v)==520','len(v)==550').replace('0x79234]','0x79234,0x79236]').replace('(forward==0x792)','(forward in [0x792,0x79236])').replace('v[496:]==','v[496:520]==')
code=''' cb6,ct6,ca6,cf6,cu6,cm6=v[520:526]
 cn6=[v[526+3*i] for i in range(8)];cfns6=[v[527+3*i] for i in range(8)];cuns6=[v[528+3*i] for i in range(8)]
 assert ca6 in [0,1] and 0<=cm6<512
 if forward in [0x792,0x79236]:
  assert ca6==int([cb6]+cn6==[236,116,96,233,207,207,237,255,16])
  if ca6:
   assert ct6==12
   assert cm6==sum(1<<i for i,(a,b) in enumerate(zip([cu6]+cuns6,[cb6]+cn6)) if a!=b)
   assert (cf6==12 and cfns6==cn6)==(forward==0x792)
  else:assert ct6==cm6==0 and cf6==cu6==0xffffffff and cfns6==cuns6==[0xffffffff]*8 and forward==0x79236
 else:assert v[520:526]==[0,0,0,0xffffffff,0xffffffff,0] and v[526:]==[0,0xffffffff,0xffffffff]*8
'''
replace(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and cm7t==0)','and cm7t==0 and cm6==0)').replace('or cm7t:','or cm7t or cm6:').replace('else 0x79235 if cm7t','else 0x79237 if cm6 else 0x79235 if cm7t')
s=s.replace("return {'crtc_vtotal_high':", "return {'crtc_vtotal_low':{'before':cb6,'target':ct6,'attempted':ca6,'after':cf6,'restored':cu6,'cleanup_mask':cm6,'neighbors_before':cn6,'neighbors_after':cfns6,'neighbors_restored':cuns6},'crtc_vtotal_high':")
p.write_text(s,newline='\n')
print('Extended792 actual-COFF oracle and independent schema')

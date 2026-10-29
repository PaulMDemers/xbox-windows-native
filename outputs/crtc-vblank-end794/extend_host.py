"""Extend actual COFF oracle and separate result validator for CR16."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model.py';s=p.read_text()
def replace(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'ct6writes'","state={'ct16writes':0,'ct6writes'")
s=s.replace('0x201898','0x201910').replace('0x5768','0x56f0').replace("'<550I',c.mem_read(0x201000,2200)","'<580I',c.mem_read(0x201000,2320)")
s=s.replace('0x79436]','0x79436,0x79438]').replace('0x79436,0x794]','0x79436,0x79438,0x794]').replace('v[526:]==','v[526:550]==')
replace('assert idx in [6,0x10,7,1,3,2,0,4,5,0x13,0x1f,0x14,0x17,0x19]','assert idx in [0x16,6,0x10,7,1,3,2,0,4,5,0x13,0x1f,0x14,0x17,0x19]')
replace('    if idx==6:', '''    if idx==0x16:
     assert state['ct6writes']==1 and state['ct7writes']==1 and word(1) in [0x79438,0x794]
     state['ct16writes']+=1;n=state['ct16writes'];assert n<=2
     assert [word(550),word(551),word(552)]==[237,140,1] and value==[140,237][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',0x16,value])
     if fault==('ct16-drop-write' if n==1 else 'ct16-drop-undo') or (n==2 and fault=='ct16-wrong-write-drop-undo'):return
     cr[0x16]=value
     if fault==('ct16-wrong-write' if n==1 else 'ct16-wrong-undo') or (n==1 and fault=='ct16-wrong-write-drop-undo'):cr[0x16]^=1
     if n==1 and fault.startswith('ct16-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,0x10,0x12,0x15,0x18,0x25][j-1]]^=1
     return
    if idx==6:''')
replace("state['ct6writes']+=1;n=state['ct6writes'];assert n<=2","state['ct6writes']+=1;n=state['ct6writes'];assert n<=2\n     if n==2:assert state['ct16writes']==2*word(552)")
replace('   val=cr[idx]', '''   val=cr[idx]
   if idx in [0x16,6,7,9,0x10,0x12,0x15,0x18,0x25] and state['ct6writes']==1 and word(1) in [0x79438,0x794]:
    j=[0x16,6,7,9,0x10,0x12,0x15,0x18,0x25].index(idx);phase=['before','after','undo'][state['ct16writes']]
    if fault=='ct16-'+phase+'-'+str(j):val^=1
''')
replace('  if val==4:\n','  if val==4:\n   assert word(555)==0 and (not word(552) or word(554)==word(550))\n')
for label,mapping in [('c7',{1:0,2:0,3:4,4:0,5:16,6:32,7:128,8:256}),('c10',{1:0,2:0,3:8,4:0,5:16,6:32,7:128,8:256}),('ct7',{1:0,2:0,3:4,4:8,5:16,6:32,7:128,8:256}),('ct6',{1:0,2:2,3:4,4:8,5:16,6:32,7:128,8:256})]:
 token='  '+label+'bad=bool('+label+'mask)'
 replace(token,"  if fault in ['ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo']:"+label+"mask|=64\n  if fault.startswith('ct16-coupling-'):\n   j=int(fault.rsplit('-',1)[1]);"+label+'mask|='+repr(mapping)+'[j]\n'+token)
replace('  ct6bad=bool(ct6mask)', '''  ct6bad=bool(ct6mask)
  ct16mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('ct16-undo-','ct16-coupling-')) else 1 if fault in ['ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo'] else 0
  ct16bad=bool(ct16mask)''')
s=s.replace('or ct6bad','or ct6bad or ct16bad')
replace('else 0x794\n  assert v[1]==forward',"else 0x79438 if fault.startswith(('ct16-before-','ct16-after-','ct16-coupling-')) or fault in ['ct16-drop-write','ct16-wrong-write','ct16-wrong-write-drop-undo'] else 0x794\n  assert v[1]==forward")
replace("[['cr',6,12],['cr',6,236]]","[['cr',6,12]]+([['cr',22,140],['cr',22,237]] if forward in [0x794,0x79438] and not fault.startswith('ct16-before-') else [])+[['cr',6,236]]")
s=s.replace('else 0x79437 if ct6bad','else 0x79439 if ct16bad else 0x79437 if ct6bad')
for token,mapping in [("   if fault=='c7-wrong-undo':undo[0]^=1",{3:2,5:4,6:5,7:7,8:8}),("   if fault=='c10-wrong-undo':undo[0]^=1",{3:3,5:4,6:5,7:7,8:8}),("   if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:undo[0]^=1",{3:2,4:3,5:4,6:5,7:7,8:8}),("   if fault=='ct6-wrong-undo':undo[0]=237",{2:1,3:2,4:3,5:4,6:5,7:7,8:8})]:
 replace(token,token+"\n   if fault=='ct16-drop-undo':undo[6]=140\n   if fault=='ct16-wrong-undo':undo[6]=236\n   if fault=='ct16-wrong-write-drop-undo':undo[6]=141\n   if fault.startswith('ct16-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n    if j in mapping:undo[mapping[j]]^=1")
replace(" R['cases'].append(",''' # Independent CR16 tuple: saved ED, preserve bit7, total524 low7 =>8C.
 reached_ct16=not cpu_bad and not baseline and forward in [0x794,0x79438]
 if reached_ct16:
  ref=[237,12,116,96,233,207,207,255,16];before=ref.copy()
  attempted_ct16=not fault.startswith('ct16-before-')
  if not attempted_ct16:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[550]]+[v[556+3*i] for i in range(8)]==before
  assert v[551:553]==([140,1] if attempted_ct16 else [0,0]) and state['ct16writes']==2*int(attempted_ct16)
  if attempted_ct16:
   after=ref.copy();after[0]=140;undo=ref.copy()
   if fault=='ct16-drop-write':after[0]=237
   if fault in ['ct16-wrong-write','ct16-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('ct16-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('ct16-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('ct16-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='ct16-drop-undo':undo[0]=140
   if fault=='ct16-wrong-undo':undo[0]=236
   if fault=='ct16-wrong-write-drop-undo':undo[0]=141
   assert [v[553]]+[v[557+3*i] for i in range(8)]==after
   assert [v[554]]+[v[558+3*i] for i in range(8)]==undo
   assert v[555]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==ct16mask
  else:assert v[553:556]==[0xffffffff,0xffffffff,0] and all(v[557+3*i:559+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[550:556]==[0,0,0,0xffffffff,0xffffffff,0] and v[556:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('ct16-'+phase+'-'+str(j),fault='ct16-'+phase+'-'+str(j))\n for j in range(1,9):run('ct16-coupling-'+str(j),fault='ct16-coupling-'+str(j))\n for f in ['ct16-drop-write','ct16-wrong-write','ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo']:run(f,fault=f)")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('550-word','580-word').replace('len(v)==550','len(v)==580').replace('0x79436]','0x79436,0x79438]').replace('(forward==0x794)','(forward in [0x794,0x79438])').replace('v[526:]==','v[526:550]==')
code=''' cb16,ct16,ca16,cf16,cu16,cm16=v[550:556]
 cn16=[v[556+3*i] for i in range(8)];cfns16=[v[557+3*i] for i in range(8)];cuns16=[v[558+3*i] for i in range(8)]
 assert ca16 in [0,1] and 0<=cm16<512
 if forward in [0x794,0x79438]:
  assert ca16==int([cb16]+cn16==[237,12,116,96,233,207,207,255,16])
  if ca16:
   assert ct16==140
   assert cm16==sum(1<<i for i,(a,b) in enumerate(zip([cu16]+cuns16,[cb16]+cn16)) if a!=b)
   assert (cf16==140 and cfns16==cn16)==(forward==0x794)
  else:assert ct16==cm16==0 and cf16==cu16==0xffffffff and cfns16==cuns16==[0xffffffff]*8 and forward==0x79438
 else:assert v[550:556]==[0,0,0,0xffffffff,0xffffffff,0] and v[556:]==[0,0xffffffff,0xffffffff]*8
'''
replace(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and cm6==0)','and cm6==0 and cm16==0)').replace('or cm6:','or cm6 or cm16:').replace('else 0x79437 if cm6','else 0x79439 if cm16 else 0x79437 if cm6')
s=s.replace("return {'crtc_vtotal_low':", "return {'crtc_vblank_end':{'before':cb16,'target':ct16,'attempted':ca16,'after':cf16,'restored':cu16,'cleanup_mask':cm16,'neighbors_before':cn16,'neighbors_after':cfns16,'neighbors_restored':cuns16},'crtc_vtotal_low':")
p.write_text(s,newline='\n')
print('Extended794 actual COFF oracle and independent schema')

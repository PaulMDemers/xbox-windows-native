"""Extend actual COFF execution oracle and independent result schema for CR12."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model.py';s=p.read_text()
def replace(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'cd7writes'","state={'cd12writes':0,'cd7writes'")
s=s.replace('0x201988','0x201a00').replace('0x5678','0x5600').replace("'<610I',c.mem_read(0x201000,2440)","'<640I',c.mem_read(0x201000,2560)")
s=s.replace('0x7983a]','0x7983a,0x7983c]').replace('0x7983a,0x798]','0x7983a,0x7983c,0x798]').replace('v[586:]==','v[586:610]==')
replace("    if idx==7 and state['ct16writes']==1:",'''    if idx==0x12:
     assert state['cd7writes']==1 and state['ct16writes']==1 and word(1) in [0x7983c,0x798]
     state['cd12writes']+=1;n=state['cd12writes'];assert n<=2
     assert [word(610),word(611),word(612)]==[207,223,1] and value==[223,207][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',18,value])
     if fault==('cd12-drop-write' if n==1 else 'cd12-drop-undo') or (n==2 and fault=='cd12-wrong-write-drop-undo'):return
     cr[18]=value
     if fault==('cd12-wrong-write' if n==1 else 'cd12-wrong-undo') or (n==1 and fault=='cd12-wrong-write-drop-undo'):cr[18]^=1
     if n==1 and fault.startswith('cd12-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,16,21,22,24,37][j-1]]^=1
     return
    if idx==7 and state['ct16writes']==1:''')
replace("state['cd7writes']+=1;n=state['cd7writes'];assert n<=2","state['cd7writes']+=1;n=state['cd7writes'];assert n<=2\n     if n==2:assert state['cd12writes']==2*word(612)")
replace('   val=cr[idx]', '''   val=cr[idx]
   if idx in [18,6,7,9,16,21,22,24,37] and state['cd7writes']==1 and word(1) in [0x7983c,0x798]:
    j=[18,6,7,9,16,21,22,24,37].index(idx);phase=['before','after','undo'][state['cd12writes']]
    if fault=='cd12-'+phase+'-'+str(j):val^=1
''')
replace('  if val==4:\n','  if val==4:\n   assert word(615)==0 and (not word(612) or word(614)==word(610))\n')
# Recovery-order map is specified independently of the implementation.
stages=[('cd7',[7,6,9,16,18,21,22,24,37]),('ct16',[22,6,7,9,16,18,21,24,37]),('ct6',[6,7,9,16,18,21,22,24,37]),('ct7',[7,6,9,16,18,21,22,24,37]),('c10',[16,6,7,9,18,21,22,24,37]),('c7',[7,6,9,16,18,21,22,24,37])]
repaired=set();mappings={}
for label,regs in stages:
 repaired.add(regs[0]);mapping={j:regs.index(a) for j,a in enumerate([6,7,9,16,21,22,24,37],1) if a not in repaired and a in regs};own=regs.index(18);mappings[label]=(mapping,own)
 token='  '+label+'bad=bool('+label+'mask)'
 replace(token,"  if fault in ['cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo']:"+label+'mask|='+str(1<<own)+"\n  if fault.startswith('cd12-coupling-'):\n   j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n   if j in mapping:"+label+'mask|=1<<mapping[j]\n'+token)
replace('  cd7bad=bool(cd7mask)', '''  cd7bad=bool(cd7mask)
  cd12mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('cd12-undo-','cd12-coupling-')) else 1 if fault in ['cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo'] else 0
  cd12bad=bool(cd12mask)''')
s=s.replace('or cd7bad','or cd7bad or cd12bad')
replace('else 0x798\n  assert v[1]==forward',"else 0x7983c if fault.startswith(('cd12-before-','cd12-after-','cd12-coupling-')) or fault in ['cd12-drop-write','cd12-wrong-write','cd12-wrong-write-drop-undo'] else 0x798\n  assert v[1]==forward")
replace("[['cr',7,54],['cr',7,116]]","[['cr',7,54]]+([['cr',18,223],['cr',18,207]] if forward in [0x798,0x7983c] and not fault.startswith('cd12-before-') else [])+[['cr',7,116]]")
s=s.replace('else 0x7983b if cd7bad','else 0x7983d if cd12bad else 0x7983b if cd7bad')
tokens={'c7':"   if fault=='c7-wrong-undo':undo[0]^=1",'c10':"   if fault=='c10-wrong-undo':undo[0]^=1",'ct7':"   if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:undo[0]^=1",'ct6':"   if fault=='ct6-wrong-undo':undo[0]=237",'ct16':"   if fault=='ct16-wrong-undo':undo[0]=236",'cd7':"   if fault=='cd7-wrong-undo':undo[0]=117"}
for label,token in tokens.items():
 mapping,own=mappings[label]
 extra="\n   if fault=='cd12-drop-undo':undo["+str(own)+"]=223\n   if fault=='cd12-wrong-undo':undo["+str(own)+"]=206\n   if fault=='cd12-wrong-write-drop-undo':undo["+str(own)+"]=222"
 replace(token,token+extra+"\n   if fault.startswith('cd12-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n    if j in mapping:undo[mapping[j]]^=1")
replace(" R['cases'].append(",''' # Independently specified complete CR12 transaction tuple.
 reached_cd12=not cpu_bad and not baseline and forward in [0x798,0x7983c]
 if reached_cd12:
  ref=[207,12,54,96,233,207,140,255,16];before=ref.copy()
  attempted_cd12=not fault.startswith('cd12-before-')
  if not attempted_cd12:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[610]]+[v[616+3*i] for i in range(8)]==before
  assert v[611:613]==([223,1] if attempted_cd12 else [0,0]) and state['cd12writes']==2*int(attempted_cd12)
  if attempted_cd12:
   after=ref.copy();after[0]=223;undo=ref.copy()
   if fault=='cd12-drop-write':after[0]=207
   if fault in ['cd12-wrong-write','cd12-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cd12-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cd12-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cd12-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='cd12-drop-undo':undo[0]=223
   if fault=='cd12-wrong-undo':undo[0]=206
   if fault=='cd12-wrong-write-drop-undo':undo[0]=222
   assert [v[613]]+[v[617+3*i] for i in range(8)]==after
   assert [v[614]]+[v[618+3*i] for i in range(8)]==undo
   assert v[615]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==cd12mask
  else:assert v[613:616]==[0xffffffff,0xffffffff,0] and all(v[617+3*i:619+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[610:616]==[0,0,0,0xffffffff,0xffffffff,0] and v[616:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('cd12-'+phase+'-'+str(j),fault='cd12-'+phase+'-'+str(j))\n for j in range(1,9):run('cd12-coupling-'+str(j),fault='cd12-coupling-'+str(j))\n for f in ['cd12-drop-write','cd12-wrong-write','cd12-drop-undo','cd12-wrong-undo','cd12-wrong-write-drop-undo']:run(f,fault=f)")
p.write_bytes(s.encode())
p=K/'audit_logic.py';s=p.read_text().replace('610-word','640-word').replace('len(v)==610','len(v)==640').replace('0x7983a]','0x7983a,0x7983c]').replace('(forward==0x798)','(forward in [0x798,0x7983c])').replace('v[586:]==','v[586:610]==')
code=''' cb12,ct12,ca12,cf12,cu12,cm12=v[610:616]
 cn12=[v[616+3*i] for i in range(8)];cfns12=[v[617+3*i] for i in range(8)];cuns12=[v[618+3*i] for i in range(8)]
 assert ca12 in [0,1] and 0<=cm12<512
 if forward in [0x798,0x7983c]:
  assert ca12==int([cb12]+cn12==[207,12,54,96,233,207,140,255,16])
  if ca12:
   assert ct12==223
   assert cm12==sum(1<<i for i,(a,b) in enumerate(zip([cu12]+cuns12,[cb12]+cn12)) if a!=b)
   assert (cf12==223 and cfns12==cn12)==(forward==0x798)
  else:assert ct12==cm12==0 and cf12==cu12==0xffffffff and cfns12==cuns12==[0xffffffff]*8 and forward==0x7983c
 else:assert v[610:616]==[0,0,0,0xffffffff,0xffffffff,0] and v[616:]==[0,0xffffffff,0xffffffff]*8
'''
replace(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and cm7d==0)','and cm7d==0 and cm12==0)').replace('or cm7d:','or cm7d or cm12:').replace('else 0x7983b if cm7d','else 0x7983d if cm12 else 0x7983b if cm7d')
s=s.replace("return {'crtc_vdisplay_high':", "return {'crtc_vdisplay_low':{'before':cb12,'target':ct12,'attempted':ca12,'after':cf12,'restored':cu12,'cleanup_mask':cm12,'neighbors_before':cn12,'neighbors_after':cfns12,'neighbors_restored':cuns12},'crtc_vdisplay_high':")
p.write_bytes(s.encode())
print('Extended798 actual-code oracle and independent schema')

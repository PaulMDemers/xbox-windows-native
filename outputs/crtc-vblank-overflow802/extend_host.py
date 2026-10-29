"""Extend actual COFF fault oracle and independent result schema for CR07 bit3."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'cb9writes'","state={'cb7writes':0,'cb9writes'")
s=s.replace('0x201a78','0x201af0').replace('0x5588','0x5510').replace("'<670I',c.mem_read(0x201000,2680)","'<700I',c.mem_read(0x201000,2800)")
s=s.replace('0x8023e]','0x8023e,0x80240]').replace('0x8023e,0x802]','0x8023e,0x80240,0x802]').replace('v[646:]==','v[646:670]==')
rep('    if idx==9:', '''    if idx==7 and state['cb9writes']==1 and word(1) in [0x80240,0x802]:
     state['cb7writes']+=1;n=state['cb7writes'];assert n<=2
     assert [word(670),word(671),word(672)]==[54,62,1] and value==[62,54][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',7,value])
     if fault==('cb7-drop-write' if n==1 else 'cb7-drop-undo') or (n==2 and fault=='cb7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('cb7-wrong-write' if n==1 else 'cb7-wrong-undo') or (n==1 and fault=='cb7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('cb7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,16,18,21,22,24,37][j-1]]^=1
     return
    if idx==9:''')
rep("state['cb9writes']+=1;n=state['cb9writes'];assert n<=2","state['cb9writes']+=1;n=state['cb9writes'];assert n<=2\n     if n==2:assert state['cb7writes']==2*word(672)")
rep('   val=cr[idx]', '''   val=cr[idx]
   if idx in [7,6,9,16,18,21,22,24,37] and state['cb9writes']==1 and word(1) in [0x80240,0x802]:
    j=[7,6,9,16,18,21,22,24,37].index(idx);phase=['before','after','undo'][state['cb7writes']]
    if fault=='cb7-'+phase+'-'+str(j):val^=1
''')
rep('  if val==4:\n','  if val==4:\n   assert word(675)==0 and (not word(672) or word(674)==word(670))\n')
stages=[('cb9',[9,6,7,16,18,21,22,24,37]),('cd12',[18,6,7,9,16,21,22,24,37]),('cd7',[7,6,9,16,18,21,22,24,37]),('ct16',[22,6,7,9,16,18,21,24,37]),('ct6',[6,7,9,16,18,21,22,24,37]),('ct7',[7,6,9,16,18,21,22,24,37]),('c10',[16,6,7,9,18,21,22,24,37]),('c7',[7,6,9,16,18,21,22,24,37])]
repaired=set();mappings={}
for label,regs in stages:
 repaired.add(regs[0]);mapping={j:regs.index(a) for j,a in enumerate([6,9,16,18,21,22,24,37],1) if a not in repaired and a in regs};own=regs.index(7) if 7 not in repaired else None;mappings[label]=(mapping,own)
 token='  '+label+'bad=bool('+label+'mask)'
 extra=''
 if own is not None:extra="  if fault in ['cb7-drop-undo','cb7-wrong-undo','cb7-wrong-write-drop-undo']:"+label+'mask|='+str(1<<own)+'\n'
 rep(token,extra+"  if fault.startswith('cb7-coupling-'):\n   j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n   if j in mapping:"+label+'mask|=1<<mapping[j]\n'+token)
rep('  cb9bad=bool(cb9mask)', '''  cb9bad=bool(cb9mask)
  cb7mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('cb7-undo-','cb7-coupling-')) else 1 if fault in ['cb7-drop-undo','cb7-wrong-undo','cb7-wrong-write-drop-undo'] else 0
  cb7bad=bool(cb7mask)''')
s=s.replace('or cb9bad','or cb9bad or cb7bad')
rep('else 0x802\n  assert v[1]==forward',"else 0x80240 if fault.startswith(('cb7-before-','cb7-after-','cb7-coupling-')) or fault in ['cb7-drop-write','cb7-wrong-write','cb7-wrong-write-drop-undo'] else 0x802\n  assert v[1]==forward")
rep("[['cr',9,64],['cr',9,96]]","[['cr',9,64]]+([['cr',7,62],['cr',7,54]] if forward in [0x802,0x80240] and not fault.startswith('cb7-before-') else [])+[['cr',9,96]]")
s=s.replace('else 0x8023f if cb9bad','else 0x80241 if cb7bad else 0x8023f if cb9bad')
tokens={'c7':"   if fault=='c7-wrong-undo':undo[0]^=1",'c10':"   if fault=='c10-wrong-undo':undo[0]^=1",'ct7':"   if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:undo[0]^=1",'ct6':"   if fault=='ct6-wrong-undo':undo[0]=237",'ct16':"   if fault=='ct16-wrong-undo':undo[0]=236",'cd7':"   if fault=='cd7-wrong-undo':undo[0]=117",'cd12':"   if fault=='cd12-wrong-undo':undo[0]=206",'cb9':"   if fault=='cb9-wrong-undo':undo[0]=97"}
for label,token in tokens.items():
 mapping,own=mappings[label];extra=''
 if own is not None:
  extra="\n   if fault=='cb7-drop-undo':undo["+str(own)+"]=62\n   if fault=='cb7-wrong-undo':undo["+str(own)+"]=55\n   if fault=='cb7-wrong-write-drop-undo':undo["+str(own)+"]=63"
 rep(token,token+extra+"\n   if fault.startswith('cb7-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n    if j in mapping:undo[mapping[j]]^=1")
rep(" R['cases'].append(",''' # Complete new transaction, independent literals and masks.
 reached_cb7=not cpu_bad and not baseline and forward in [0x802,0x80240]
 if reached_cb7:
  ref=[54,12,64,233,223,207,140,255,16];before=ref.copy()
  attempted_cb7=not fault.startswith('cb7-before-')
  if not attempted_cb7:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[670]]+[v[676+3*i] for i in range(8)]==before
  assert v[671:673]==([62,1] if attempted_cb7 else [0,0]) and state['cb7writes']==2*int(attempted_cb7)
  if attempted_cb7:
   after=ref.copy();after[0]=62;undo=ref.copy()
   if fault=='cb7-drop-write':after[0]=54
   if fault in ['cb7-wrong-write','cb7-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cb7-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cb7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cb7-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='cb7-drop-undo':undo[0]=62
   if fault=='cb7-wrong-undo':undo[0]=55
   if fault=='cb7-wrong-write-drop-undo':undo[0]=63
   assert [v[673]]+[v[677+3*i] for i in range(8)]==after
   assert [v[674]]+[v[678+3*i] for i in range(8)]==undo
   assert v[675]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==cb7mask
  else:assert v[673:676]==[0xffffffff,0xffffffff,0] and all(v[677+3*i:679+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[670:676]==[0,0,0,0xffffffff,0xffffffff,0] and v[676:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
rep(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('cb7-'+phase+'-'+str(j),fault='cb7-'+phase+'-'+str(j))\n for j in range(1,9):run('cb7-coupling-'+str(j),fault='cb7-coupling-'+str(j))\n for f in ['cb7-drop-write','cb7-wrong-write','cb7-drop-undo','cb7-wrong-undo','cb7-wrong-write-drop-undo']:run(f,fault=f)")
p.write_bytes(s.encode())
p=K/'audit_logic.py';s=p.read_text().replace('670-word','700-word').replace('len(v)==670','len(v)==700').replace('0x8023e]','0x8023e,0x80240]').replace('(forward==0x802)','(forward in [0x802,0x80240])').replace('v[646:]==','v[646:670]==')
code=''' cb7b,ct7b,ca7b,cf7b,cu7b,cm7b=v[670:676]
 cn7b=[v[676+3*i] for i in range(8)];cfns7b=[v[677+3*i] for i in range(8)];cuns7b=[v[678+3*i] for i in range(8)]
 assert ca7b in [0,1] and 0<=cm7b<512
 if forward in [0x802,0x80240]:
  assert ca7b==int([cb7b]+cn7b==[54,12,64,233,223,207,140,255,16])
  if ca7b:
   assert ct7b==62 and ct7b==((cb7b&0xf7)|(((480-1)>>5)&8))
   assert cm7b==sum(1<<i for i,(a,b) in enumerate(zip([cu7b]+cuns7b,[cb7b]+cn7b)) if a!=b)
   assert (cf7b==62 and cfns7b==cn7b)==(forward==0x802)
  else:assert ct7b==cm7b==0 and cf7b==cu7b==0xffffffff and cfns7b==cuns7b==[0xffffffff]*8 and forward==0x80240
 else:assert v[670:676]==[0,0,0,0xffffffff,0xffffffff,0] and v[676:]==[0,0xffffffff,0xffffffff]*8
'''
rep(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and cm9==0)','and cm9==0 and cm7b==0)').replace('or cm9:','or cm9 or cm7b:').replace('else 0x8023f if cm9','else 0x80241 if cm7b else 0x8023f if cm9')
s=s.replace("return {'crtc_vblank_bit':", "return {'crtc_vblank_overflow':{'before':cb7b,'target':ct7b,'attempted':ca7b,'after':cf7b,'restored':cu7b,'cleanup_mask':cm7b,'neighbors_before':cn7b,'neighbors_after':cfns7b,'neighbors_restored':cuns7b},'crtc_vblank_bit':")
p.write_bytes(s.encode())
print('Extended802 actual-code oracle and independent schema')

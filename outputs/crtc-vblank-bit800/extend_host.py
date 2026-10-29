"""Extend the actual COFF oracle and independent schema for CR09 bit5."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model.py';s=p.read_text()
def replace(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'cd12writes'","state={'cb9writes':0,'cd12writes'")
s=s.replace('0x201a00','0x201a78').replace('0x5600','0x5588').replace("'<640I',c.mem_read(0x201000,2560)","'<670I',c.mem_read(0x201000,2680)")
s=s.replace('0x8003c]','0x8003c,0x8003e]').replace('0x8003c,0x800]','0x8003c,0x8003e,0x800]').replace('v[616:]==','v[616:640]==')
replace('assert idx in [0x12,','assert idx in [9,0x12,')
replace('    if idx==0x12:', '''    if idx==9:
     assert state['cd12writes']==1 and state['cd7writes']==1 and word(1) in [0x8003e,0x800]
     state['cb9writes']+=1;n=state['cb9writes'];assert n<=2
     assert [word(640),word(641),word(642)]==[96,64,1] and value==[64,96][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',9,value])
     if fault==('cb9-drop-write' if n==1 else 'cb9-drop-undo') or (n==2 and fault=='cb9-wrong-write-drop-undo'):return
     cr[9]=value
     if fault==('cb9-wrong-write' if n==1 else 'cb9-wrong-undo') or (n==1 and fault=='cb9-wrong-write-drop-undo'):cr[9]^=1
     if n==1 and fault.startswith('cb9-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,16,18,21,22,24,37][j-1]]^=1
     return
    if idx==0x12:''')
replace("state['cd12writes']+=1;n=state['cd12writes'];assert n<=2","state['cd12writes']+=1;n=state['cd12writes'];assert n<=2\n     if n==2:assert state['cb9writes']==2*word(642)")
replace('   val=cr[idx]', '''   val=cr[idx]
   if idx in [9,6,7,16,18,21,22,24,37] and state['cd12writes']==1 and word(1) in [0x8003e,0x800]:
    j=[9,6,7,16,18,21,22,24,37].index(idx);phase=['before','after','undo'][state['cb9writes']]
    if fault=='cb9-'+phase+'-'+str(j):val^=1
''')
replace('  if val==4:\n','  if val==4:\n   assert word(645)==0 and (not word(642) or word(644)==word(640))\n')
# Independent reverse order and register-to-mask mappings.
stages=[('cd12',[18,6,7,9,16,21,22,24,37]),('cd7',[7,6,9,16,18,21,22,24,37]),('ct16',[22,6,7,9,16,18,21,24,37]),('ct6',[6,7,9,16,18,21,22,24,37]),('ct7',[7,6,9,16,18,21,22,24,37]),('c10',[16,6,7,9,18,21,22,24,37]),('c7',[7,6,9,16,18,21,22,24,37])]
repaired=set();mappings={}
for label,regs in stages:
 repaired.add(regs[0]);mapping={j:regs.index(a) for j,a in enumerate([6,7,16,18,21,22,24,37],1) if a not in repaired and a in regs};own=regs.index(9);mappings[label]=(mapping,own)
 token='  '+label+'bad=bool('+label+'mask)'
 replace(token,"  if fault in ['cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:"+label+'mask|='+str(1<<own)+"\n  if fault.startswith('cb9-coupling-'):\n   j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n   if j in mapping:"+label+'mask|=1<<mapping[j]\n'+token)
replace('  cd12bad=bool(cd12mask)', '''  cd12bad=bool(cd12mask)
  cb9mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('cb9-undo-','cb9-coupling-')) else 1 if fault in ['cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo'] else 0
  cb9bad=bool(cb9mask)''')
s=s.replace('or cd12bad','or cd12bad or cb9bad')
replace('else 0x800\n  assert v[1]==forward',"else 0x8003e if fault.startswith(('cb9-before-','cb9-after-','cb9-coupling-')) or fault in ['cb9-drop-write','cb9-wrong-write','cb9-wrong-write-drop-undo'] else 0x800\n  assert v[1]==forward")
replace("[['cr',18,223],['cr',18,207]]","[['cr',18,223]]+([['cr',9,64],['cr',9,96]] if forward in [0x800,0x8003e] and not fault.startswith('cb9-before-') else [])+[['cr',18,207]]")
s=s.replace('else 0x8003d if cd12bad','else 0x8003f if cb9bad else 0x8003d if cd12bad')
tokens={'c7':"   if fault=='c7-wrong-undo':undo[0]^=1",'c10':"   if fault=='c10-wrong-undo':undo[0]^=1",'ct7':"   if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:undo[0]^=1",'ct6':"   if fault=='ct6-wrong-undo':undo[0]=237",'ct16':"   if fault=='ct16-wrong-undo':undo[0]=236",'cd7':"   if fault=='cd7-wrong-undo':undo[0]=117",'cd12':"   if fault=='cd12-wrong-undo':undo[0]=206"}
for label,token in tokens.items():
 mapping,own=mappings[label]
 extra="\n   if fault=='cb9-drop-undo':undo["+str(own)+"]=64\n   if fault=='cb9-wrong-undo':undo["+str(own)+"]=97\n   if fault=='cb9-wrong-write-drop-undo':undo["+str(own)+"]=65"
 replace(token,token+extra+"\n   if fault.startswith('cb9-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n    if j in mapping:undo[mapping[j]]^=1")
replace(" R['cases'].append(",''' # Complete CR09 transaction tuple, independently specified.
 reached_cb9=not cpu_bad and not baseline and forward in [0x800,0x8003e]
 if reached_cb9:
  ref=[96,12,54,233,223,207,140,255,16];before=ref.copy()
  attempted_cb9=not fault.startswith('cb9-before-')
  if not attempted_cb9:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[640]]+[v[646+3*i] for i in range(8)]==before
  assert v[641:643]==([64,1] if attempted_cb9 else [0,0]) and state['cb9writes']==2*int(attempted_cb9)
  if attempted_cb9:
   after=ref.copy();after[0]=64;undo=ref.copy()
   if fault=='cb9-drop-write':after[0]=96
   if fault in ['cb9-wrong-write','cb9-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cb9-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cb9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cb9-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='cb9-drop-undo':undo[0]=64
   if fault=='cb9-wrong-undo':undo[0]=97
   if fault=='cb9-wrong-write-drop-undo':undo[0]=65
   assert [v[643]]+[v[647+3*i] for i in range(8)]==after
   assert [v[644]]+[v[648+3*i] for i in range(8)]==undo
   assert v[645]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==cb9mask
  else:assert v[643:646]==[0xffffffff,0xffffffff,0] and all(v[647+3*i:649+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[640:646]==[0,0,0,0xffffffff,0xffffffff,0] and v[646:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('cb9-'+phase+'-'+str(j),fault='cb9-'+phase+'-'+str(j))\n for j in range(1,9):run('cb9-coupling-'+str(j),fault='cb9-coupling-'+str(j))\n for f in ['cb9-drop-write','cb9-wrong-write','cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:run(f,fault=f)")
p.write_bytes(s.encode())
p=K/'audit_logic.py';s=p.read_text().replace('640-word','670-word').replace('len(v)==640','len(v)==670').replace('0x8003c]','0x8003c,0x8003e]').replace('(forward==0x800)','(forward in [0x800,0x8003e])').replace('v[616:]==','v[616:640]==')
code=''' cb9,ct9,ca9,cf9,cu9,cm9=v[640:646]
 cn9=[v[646+3*i] for i in range(8)];cfns9=[v[647+3*i] for i in range(8)];cuns9=[v[648+3*i] for i in range(8)]
 assert ca9 in [0,1] and 0<=cm9<512
 if forward in [0x800,0x8003e]:
  assert ca9==int([cb9]+cn9==[96,12,54,233,223,207,140,255,16])
  if ca9:
   assert ct9==64 and ct9==((cb9&0xdf)|(((480-1)>>4)&0x20))
   assert cm9==sum(1<<i for i,(a,b) in enumerate(zip([cu9]+cuns9,[cb9]+cn9)) if a!=b)
   assert (cf9==64 and cfns9==cn9)==(forward==0x800)
  else:assert ct9==cm9==0 and cf9==cu9==0xffffffff and cfns9==cuns9==[0xffffffff]*8 and forward==0x8003e
 else:assert v[640:646]==[0,0,0,0xffffffff,0xffffffff,0] and v[646:]==[0,0xffffffff,0xffffffff]*8
'''
replace(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and cm12==0)','and cm12==0 and cm9==0)').replace('or cm12:','or cm12 or cm9:').replace('else 0x8003d if cm12','else 0x8003f if cm9 else 0x8003d if cm12')
s=s.replace("return {'crtc_vdisplay_low':", "return {'crtc_vblank_bit':{'before':cb9,'target':ct9,'attempted':ca9,'after':cf9,'restored':cu9,'cleanup_mask':cm9,'neighbors_before':cn9,'neighbors_after':cfns9,'neighbors_restored':cuns9},'crtc_vdisplay_low':")
p.write_bytes(s.encode())
print('Extended800 actual-code oracle and independent schema')

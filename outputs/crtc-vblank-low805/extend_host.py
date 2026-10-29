"""Extend compiled COFF fault oracle and independent schema for CR15 low byte."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model003.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'cb7writes'","state={'cb15writes':0,'cb7writes'")
s=s.replace('0x201af0','0x201b68').replace('0x5510','0x5498').replace("'<700I',c.mem_read(0x201000,2800)","'<730I',c.mem_read(0x201000,2920)")
s=s.replace('0x80540]','0x80540,0x80542]').replace('0x80540,0x805]','0x80540,0x80542,0x805]').replace('v[676:]==','v[676:700]==')
rep("    if idx==7 and state['cb9writes']==1",'''    if idx==0x15 and state['cb7writes']==1 and word(1) in [0x80542,0x805]:
     state['cb15writes']+=1;n=state['cb15writes'];assert n<=2
     assert [word(700),word(701),word(702)]==[207,223,1] and value==[223,207][n-1]
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',21,value])
     if fault==('cb15-drop-write' if n==1 else 'cb15-drop-undo') or (n==2 and fault=='cb15-wrong-write-drop-undo'):return
     cr[21]=value
     if fault==('cb15-wrong-write' if n==1 else 'cb15-wrong-undo') or (n==1 and fault=='cb15-wrong-write-drop-undo'):cr[21]^=1
     if n==1 and fault.startswith('cb15-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,16,18,22,24,37][j-1]]^=1
     return
    if idx==7 and state['cb9writes']==1''')
rep("state['cb7writes']+=1;n=state['cb7writes'];assert n<=2","state['cb7writes']+=1;n=state['cb7writes'];assert n<=2\n     if n==2:assert state['cb15writes']==2*word(702)")
rep('   val=cr[idx]', '''   val=cr[idx]
   if idx in [21,6,7,9,16,18,22,24,37] and state['cb7writes']==1 and word(1) in [0x80542,0x805]:
    j=[21,6,7,9,16,18,22,24,37].index(idx);phase=['before','after','undo'][state['cb15writes']]
    if fault=='cb15-'+phase+'-'+str(j):val^=1
''')
rep('  if val==4:\n','  if val==4:\n   assert word(705)==0 and (not word(702) or word(704)==word(700))\n')
stages=[('cb7',[7,6,9,16,18,21,22,24,37]),('cb9',[9,6,7,16,18,21,22,24,37]),('cd12',[18,6,7,9,16,21,22,24,37]),('cd7',[7,6,9,16,18,21,22,24,37]),('ct16',[22,6,7,9,16,18,21,24,37]),('ct6',[6,7,9,16,18,21,22,24,37]),('ct7',[7,6,9,16,18,21,22,24,37]),('c10',[16,6,7,9,18,21,22,24,37]),('c7',[7,6,9,16,18,21,22,24,37])]
repaired=set();mappings={}
for label,regs in stages:
 repaired.add(regs[0]);mapping={j:regs.index(a) for j,a in enumerate([6,7,9,16,18,22,24,37],1) if a not in repaired and a in regs};own=regs.index(21) if 21 not in repaired else None;mappings[label]=(mapping,own)
 token='  '+label+'bad=bool('+label+'mask)';extra=''
 if own is not None:extra="  if fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:"+label+'mask|='+str(1<<own)+'\n'
 rep(token,extra+"  if fault.startswith('cb15-coupling-'):\n   j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n   if j in mapping:"+label+'mask|=1<<mapping[j]\n'+token)
rep('  cb7bad=bool(cb7mask)', '''  cb7bad=bool(cb7mask)
  cb15mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('cb15-undo-','cb15-coupling-')) else 1 if fault in ['cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo'] else 0
  cb15bad=bool(cb15mask)''')
s=s.replace('or cb7bad','or cb7bad or cb15bad')
rep('else 0x805\n  assert v[1]==forward',"else 0x80542 if fault.startswith(('cb15-before-','cb15-after-','cb15-coupling-')) or fault in ['cb15-drop-write','cb15-wrong-write','cb15-wrong-write-drop-undo'] else 0x805\n  assert v[1]==forward")
rep("[['cr',7,62],['cr',7,54]]","[['cr',7,62]]+([['cr',21,223],['cr',21,207]] if forward in [0x805,0x80542] and not fault.startswith('cb15-before-') else [])+[['cr',7,54]]")
s=s.replace('else 0x80541 if cb7bad','else 0x80543 if cb15bad else 0x80541 if cb7bad')
tokens={'c7':"   if fault=='c7-wrong-undo':undo[0]^=1",'c10':"   if fault=='c10-wrong-undo':undo[0]^=1",'ct7':"   if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:undo[0]^=1",'ct6':"   if fault=='ct6-wrong-undo':undo[0]=237",'ct16':"   if fault=='ct16-wrong-undo':undo[0]=236",'cd7':"   if fault=='cd7-wrong-undo':undo[0]=117",'cd12':"   if fault=='cd12-wrong-undo':undo[0]=206",'cb9':"   if fault=='cb9-wrong-undo':undo[0]=97",'cb7':"   if fault=='cb7-wrong-undo':undo[0]=55"}
for label,token in tokens.items():
 mapping,own=mappings[label];extra=''
 if own is not None:extra="\n   if fault=='cb15-drop-undo':undo["+str(own)+"]=223\n   if fault=='cb15-wrong-undo':undo["+str(own)+"]=206\n   if fault=='cb15-wrong-write-drop-undo':undo["+str(own)+"]=222"
 rep(token,token+extra+"\n   if fault.startswith('cb15-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n    if j in mapping:undo[mapping[j]]^=1")
rep(" R['cases'].append(",''' # Complete CR15 transaction, independently enumerated literals and masks.
 reached_cb15=not cpu_bad and not baseline and forward in [0x805,0x80542]
 if reached_cb15:
  ref=[207,12,62,64,233,223,140,255,16];before=ref.copy()
  attempted_cb15=not fault.startswith('cb15-before-')
  if not attempted_cb15:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[700]]+[v[706+3*i] for i in range(8)]==before
  assert v[701:703]==([223,1] if attempted_cb15 else [0,0]) and state['cb15writes']==2*int(attempted_cb15)
  if attempted_cb15:
   after=ref.copy();after[0]=223;undo=ref.copy()
   if fault=='cb15-drop-write':after[0]=207
   if fault in ['cb15-wrong-write','cb15-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cb15-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cb15-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cb15-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='cb15-drop-undo':undo[0]=223
   if fault=='cb15-wrong-undo':undo[0]=206
   if fault=='cb15-wrong-write-drop-undo':undo[0]=222
   assert [v[703]]+[v[707+3*i] for i in range(8)]==after
   assert [v[704]]+[v[708+3*i] for i in range(8)]==undo
   assert v[705]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==cb15mask
  else:assert v[703:706]==[0xffffffff,0xffffffff,0] and all(v[707+3*i:709+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[700:706]==[0,0,0,0xffffffff,0xffffffff,0] and v[706:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
rep(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('cb15-'+phase+'-'+str(j),fault='cb15-'+phase+'-'+str(j))\n for j in range(1,9):run('cb15-coupling-'+str(j),fault='cb15-coupling-'+str(j))\n for f in ['cb15-drop-write','cb15-wrong-write','cb15-drop-undo','cb15-wrong-undo','cb15-wrong-write-drop-undo']:run(f,fault=f)")
p.write_bytes(s.encode())
p=K/'audit_logic.py';s=p.read_text().replace('700-word','730-word').replace('len(v)==700','len(v)==730').replace('0x80540]','0x80540,0x80542]').replace('(forward==0x805)','(forward in [0x805,0x80542])').replace('v[676:]==','v[676:700]==')
code=''' cb15b,ct15b,ca15b,cf15b,cu15b,cm15b=v[700:706]
 cn15b=[v[706+3*i] for i in range(8)];cfns15b=[v[707+3*i] for i in range(8)];cuns15b=[v[708+3*i] for i in range(8)]
 assert ca15b in [0,1] and 0<=cm15b<512
 if forward in [0x805,0x80542]:
  assert ca15b==int([cb15b]+cn15b==[207,12,62,64,233,223,140,255,16])
  if ca15b:
   assert ct15b==223 and ct15b==((480-1)&255)
   assert cm15b==sum(1<<i for i,(a,b) in enumerate(zip([cu15b]+cuns15b,[cb15b]+cn15b)) if a!=b)
   assert (cf15b==223 and cfns15b==cn15b)==(forward==0x805)
  else:assert ct15b==cm15b==0 and cf15b==cu15b==0xffffffff and cfns15b==cuns15b==[0xffffffff]*8 and forward==0x80542
 else:assert v[700:706]==[0,0,0,0xffffffff,0xffffffff,0] and v[706:]==[0,0xffffffff,0xffffffff]*8
'''
rep(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and cm7b==0)','and cm7b==0 and cm15b==0)').replace('or cm7b:','or cm7b or cm15b:').replace('else 0x80541 if cm7b','else 0x80543 if cm15b else 0x80541 if cm7b')
s=s.replace("return {'crtc_vblank_overflow':", "return {'crtc_vblank_low':{'before':cb15b,'target':ct15b,'attempted':ca15b,'after':cf15b,'restored':cu15b,'cleanup_mask':cm15b,'neighbors_before':cn15b,'neighbors_after':cfns15b,'neighbors_restored':cuns15b},'crtc_vblank_overflow':")
p.write_bytes(s.encode())
print('Extended805 actual-code oracle and independent schema')

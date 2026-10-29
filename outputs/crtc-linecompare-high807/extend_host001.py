"""Extend actual COFF oracle with same-value CR07 line-compare coverage."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'model005.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'cb15writes'","state={'cl7writes':0,'cb15writes'")
s=s.replace('0x201b68','0x201be0').replace('0x5498','0x5420').replace("'<730I',c.mem_read(0x201000,2920)","'<760I',c.mem_read(0x201000,3040)")
s=s.replace('0x80742]','0x80742,0x80744]').replace('0x80742,0x807]','0x80742,0x80744,0x807]').replace('v[706:]==','v[706:730]==')
rep("    if idx==0x15 and state['cb7writes']==1",'''    if idx==7 and state['cb15writes']==1 and word(1) in [0x80744,0x807]:
     state['cl7writes']+=1;n=state['cl7writes'];assert n<=2
     assert [word(730),word(731),word(732)]==[62,62,1] and value==62
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',7,value])
     if fault==('cl7-drop-write' if n==1 else 'cl7-drop-undo') or (n==2 and fault=='cl7-wrong-write-drop-undo'):return
     cr[7]=value
     if fault==('cl7-wrong-write' if n==1 else 'cl7-wrong-undo') or (n==1 and fault=='cl7-wrong-write-drop-undo'):cr[7]^=1
     if n==1 and fault.startswith('cl7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,16,18,21,22,24,37][j-1]]^=1
     return
    if idx==0x15 and state['cb7writes']==1''')
rep("state['cb15writes']+=1;n=state['cb15writes'];assert n<=2","state['cb15writes']+=1;n=state['cb15writes'];assert n<=2\n     if n==2:assert state['cl7writes']==2*word(732)")
rep('   val=cr[idx]', '''   val=cr[idx]
   if idx in [7,6,9,16,18,21,22,24,37] and state['cb15writes']==1 and word(1) in [0x80744,0x807]:
    j=[7,6,9,16,18,21,22,24,37].index(idx);phase=['before','after','undo'][state['cl7writes']]
    if fault=='cl7-'+phase+'-'+str(j):val^=1
''')
rep('  if val==4:\n','  if val==4:\n   assert word(735)==0 and (not word(732) or word(734)==word(730))\n')
stages=[('cb15',[21,6,7,9,16,18,22,24,37]),('cb7',[7,6,9,16,18,21,22,24,37]),('cb9',[9,6,7,16,18,21,22,24,37]),('cd12',[18,6,7,9,16,21,22,24,37]),('cd7',[7,6,9,16,18,21,22,24,37]),('ct16',[22,6,7,9,16,18,21,24,37]),('ct6',[6,7,9,16,18,21,22,24,37]),('ct7',[7,6,9,16,18,21,22,24,37]),('c10',[16,6,7,9,18,21,22,24,37]),('c7',[7,6,9,16,18,21,22,24,37])]
repaired=set();mappings={}
for label,regs in stages:
 repaired.add(regs[0]);mapping={j:regs.index(a) for j,a in enumerate([6,9,16,18,21,22,24,37],1) if a not in repaired and a in regs};own=regs.index(7) if 7 not in repaired else None;mappings[label]=(mapping,own)
 token='  '+label+'bad=bool('+label+'mask)';extra=''
 if own is not None:extra="  if fault in ['cl7-wrong-undo','cl7-wrong-write-drop-undo']:"+label+'mask|='+str(1<<own)+'\n'
 rep(token,extra+"  if fault.startswith('cl7-coupling-'):\n   j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n   if j in mapping:"+label+'mask|=1<<mapping[j]\n'+token)
rep('  cb15bad=bool(cb15mask)', '''  cb15bad=bool(cb15mask)
  cl7mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('cl7-undo-','cl7-coupling-')) else 1 if fault in ['cl7-wrong-undo','cl7-wrong-write-drop-undo'] else 0
  cl7bad=bool(cl7mask)''')
s=s.replace('or cb15bad','or cb15bad or cl7bad')
rep('else 0x807\n  assert v[1]==forward',"else 0x80744 if fault.startswith(('cl7-before-','cl7-after-','cl7-coupling-')) or fault in ['cl7-wrong-write','cl7-wrong-write-drop-undo'] else 0x807\n  assert v[1]==forward")
rep("[['cr',21,223],['cr',21,207]]","[['cr',21,223]]+([['cr',7,62],['cr',7,62]] if forward in [0x807,0x80744] and not fault.startswith('cl7-before-') else [])+[['cr',21,207]]")
s=s.replace('else 0x80743 if cb15bad','else 0x80745 if cl7bad else 0x80743 if cb15bad')
tokens={'c7':"   if fault=='c7-wrong-undo':undo[0]^=1",'c10':"   if fault=='c10-wrong-undo':undo[0]^=1",'ct7':"   if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:undo[0]^=1",'ct6':"   if fault=='ct6-wrong-undo':undo[0]=237",'ct16':"   if fault=='ct16-wrong-undo':undo[0]=236",'cd7':"   if fault=='cd7-wrong-undo':undo[0]=117",'cd12':"   if fault=='cd12-wrong-undo':undo[0]=206",'cb9':"   if fault=='cb9-wrong-undo':undo[0]=97",'cb7':"   if fault=='cb7-wrong-undo':undo[0]=55",'cb15':"   if fault=='cb15-wrong-write-drop-undo':undo[0]=222"}
for label,token in tokens.items():
 mapping,own=mappings[label];extra=''
 if own is not None:extra="\n   if fault in ['cl7-wrong-undo','cl7-wrong-write-drop-undo']:undo["+str(own)+"]=63"
 rep(token,token+extra+"\n   if fault.startswith('cl7-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n    if j in mapping:undo[mapping[j]]^=1")
rep(" R['cases'].append(",''' # Same-value operation: missing write/undo is observably identical here.
 reached_cl7=not cpu_bad and not baseline and forward in [0x807,0x80744]
 if reached_cl7:
  ref=[62,12,64,233,223,223,140,255,16];before=ref.copy()
  attempted_cl7=not fault.startswith('cl7-before-')
  if not attempted_cl7:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[730]]+[v[736+3*i] for i in range(8)]==before
  assert v[731:733]==([62,1] if attempted_cl7 else [0,0]) and state['cl7writes']==2*int(attempted_cl7)
  if attempted_cl7:
   after=ref.copy();undo=ref.copy()
   if fault in ['cl7-wrong-write','cl7-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cl7-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cl7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cl7-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault in ['cl7-wrong-undo','cl7-wrong-write-drop-undo']:undo[0]=63
   assert [v[733]]+[v[737+3*i] for i in range(8)]==after
   assert [v[734]]+[v[738+3*i] for i in range(8)]==undo
   assert v[735]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==cl7mask
  else:assert v[733:736]==[0xffffffff,0xffffffff,0] and all(v[737+3*i:739+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[730:736]==[0,0,0,0xffffffff,0xffffffff,0] and v[736:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
rep(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('cl7-'+phase+'-'+str(j),fault='cl7-'+phase+'-'+str(j))\n for j in range(1,9):run('cl7-coupling-'+str(j),fault='cl7-coupling-'+str(j))\n for f in ['cl7-drop-write','cl7-wrong-write','cl7-drop-undo','cl7-wrong-undo','cl7-wrong-write-drop-undo']:run(f,fault=f)")
p.write_bytes(s.encode())
p=K/'audit_logic.py';s=p.read_text().replace('730-word','760-word').replace('len(v)==730','len(v)==760').replace('0x80742]','0x80742,0x80744]').replace('(forward==0x807)','(forward in [0x807,0x80744])').replace('v[706:]==','v[706:730]==')
code=''' cl7b,cl7t,cl7a,cl7f,cl7u,cl7m=v[730:736]
 cl7nb=[v[736+3*i] for i in range(8)];cl7nf=[v[737+3*i] for i in range(8)];cl7nu=[v[738+3*i] for i in range(8)]
 assert cl7a in [0,1] and 0<=cl7m<512
 if forward in [0x807,0x80744]:
  assert cl7a==int([cl7b]+cl7nb==[62,12,64,233,223,223,140,255,16])
  if cl7a:
   assert cl7t==62 and cl7t==((cl7b&0xef)|((0x3ff>>4)&0x10))
   assert cl7m==sum(1<<i for i,(a,b) in enumerate(zip([cl7u]+cl7nu,[cl7b]+cl7nb)) if a!=b)
   assert (cl7f==62 and cl7nf==cl7nb)==(forward==0x807)
  else:assert cl7t==cl7m==0 and cl7f==cl7u==0xffffffff and cl7nf==cl7nu==[0xffffffff]*8 and forward==0x80744
 else:assert v[730:736]==[0,0,0,0xffffffff,0xffffffff,0] and v[736:]==[0,0xffffffff,0xffffffff]*8
'''
rep(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and cm15b==0)','and cm15b==0 and cl7m==0)').replace('or cm15b:','or cm15b or cl7m:').replace('else 0x80743 if cm15b','else 0x80745 if cl7m else 0x80743 if cm15b')
s=s.replace("return {'crtc_vblank_low':", "return {'crtc_linecompare_high':{'before':cl7b,'target':cl7t,'attempted':cl7a,'after':cl7f,'restored':cl7u,'cleanup_mask':cl7m,'neighbors_before':cl7nb,'neighbors_after':cl7nf,'neighbors_restored':cl7nu},'crtc_vblank_low':")
p.write_bytes(s.encode())
print('Extended807 actual-code oracle and independent schema')

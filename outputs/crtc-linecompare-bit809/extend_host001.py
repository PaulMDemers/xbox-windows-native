"""Extend actual COFF oracle with same-value CR07 line-compare coverage."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'model005.py';s=p.read_text()
def rep(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'cl7writes'","state={'cl9writes':0,'cb15writes'")
s=s.replace('0x201be0','0x201c58').replace('0x5420','0x53a8').replace("'<730I',c.mem_read(0x201000,2920)","'<760I',c.mem_read(0x201000,3040)")
s=s.replace('0x80944]','0x80944,0x80946]').replace('0x80944,0x809]','0x80944,0x80946,0x809]').replace('v[736:]==','v[736:760]==')
rep("    if idx==7 and state['cb15writes']==1",'''    if idx==9 and state['cl7writes']==1 and word(1) in [0x80946,0x809]:
     state['cl9writes']+=1;n=state['cl9writes'];assert n<=2
     assert [word(760),word(761),word(762)]==[64,64,1] and value==64
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',9,value])
     if fault==('cl9-drop-write' if n==1 else 'cl9-drop-undo') or (n==2 and fault=='cl9-wrong-write-drop-undo'):return
     cr[9]=value
     if fault==('cl9-wrong-write' if n==1 else 'cl9-wrong-undo') or (n==1 and fault=='cl9-wrong-write-drop-undo'):cr[9]^=1
     if n==1 and fault.startswith('cl9-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,16,18,21,22,24,37][j-1]]^=1
     return
    if idx==7 and state['cb15writes']==1''')
rep("state['cl7writes']+=1;n=state['cl7writes'];assert n<=2","state['cl7writes']+=1;n=state['cl7writes'];assert n<=2\n     if n==2:assert state['cl9writes']==2*word(762)")
rep('   val=cr[idx]', '''   val=cr[idx]
   if idx in [9,6,7,16,18,21,22,24,37] and state['cl7writes']==1 and word(1) in [0x80946,0x809]:
    j=[9,6,7,16,18,21,22,24,37].index(idx);phase=['before','after','undo'][state['cl9writes']]
    if fault=='cl9-'+phase+'-'+str(j):val^=1
''')
rep('  if val==4:\n','  if val==4:\n   assert word(765)==0 and (not word(762) or word(764)==word(760))\n')
stages=[('cl7',[7,6,9,16,18,21,22,24,37]),('cb15',[21,6,7,9,16,18,22,24,37]),('cb7',[7,6,9,16,18,21,22,24,37]),('cb9',[9,6,7,16,18,21,22,24,37]),('cd12',[18,6,7,9,16,21,22,24,37]),('cd7',[7,6,9,16,18,21,22,24,37]),('ct16',[22,6,7,9,16,18,21,24,37]),('ct6',[6,7,9,16,18,21,22,24,37]),('ct7',[7,6,9,16,18,21,22,24,37]),('c10',[16,6,7,9,18,21,22,24,37]),('c7',[7,6,9,16,18,21,22,24,37])]
repaired=set();mappings={}
for label,regs in stages:
 repaired.add(regs[0]);mapping={j:regs.index(a) for j,a in enumerate([6,7,16,18,21,22,24,37],1) if a not in repaired and a in regs};own=regs.index(9) if 9 not in repaired else None;mappings[label]=(mapping,own)
 token='  '+label+'bad=bool('+label+'mask)';extra=''
 if own is not None:extra="  if fault in ['cl9-wrong-undo','cl9-wrong-write-drop-undo']:"+label+'mask|='+str(1<<own)+'\n'
 rep(token,extra+"  if fault.startswith('cl9-coupling-'):\n   j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n   if j in mapping:"+label+'mask|=1<<mapping[j]\n'+token)
rep('  cl7bad=bool(cl7mask)', '''  cl7bad=bool(cl7mask)
  cl9mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('cl9-undo-','cl9-coupling-')) else 1 if fault in ['cl9-wrong-undo','cl9-wrong-write-drop-undo'] else 0
  cl9bad=bool(cl9mask)''')
s=s.replace('or cl7bad','or cl7bad or cl9bad')
rep('else 0x809\n  assert v[1]==forward',"else 0x80946 if fault.startswith(('cl9-before-','cl9-after-','cl9-coupling-')) or fault in ['cl9-wrong-write','cl9-wrong-write-drop-undo'] else 0x809\n  assert v[1]==forward")
rep("[['cr',7,62],['cr',7,62]]","[['cr',7,62]]+([['cr',9,64],['cr',9,64]] if forward in [0x809,0x80946] and not fault.startswith('cl9-before-') else [])+[['cr',7,62]]")
s=s.replace('else 0x80945 if cl7bad','else 0x80947 if cl9bad else 0x80945 if cl7bad')
tokens={'cl7':"   if fault in ['cl7-wrong-undo','cl7-wrong-write-drop-undo']:undo[0]=63",'c7':"   if fault=='c7-wrong-undo':undo[0]^=1",'c10':"   if fault=='c10-wrong-undo':undo[0]^=1",'ct7':"   if fault in ['ct7-wrong-undo','ct7-wrong-write-drop-undo']:undo[0]^=1",'ct6':"   if fault=='ct6-wrong-undo':undo[0]=237",'ct16':"   if fault=='ct16-wrong-undo':undo[0]=236",'cd7':"   if fault=='cd7-wrong-undo':undo[0]=117",'cd12':"   if fault=='cd12-wrong-undo':undo[0]=206",'cb9':"   if fault=='cb9-wrong-undo':undo[0]=97",'cb7':"   if fault=='cb7-wrong-undo':undo[0]=55",'cb15':"   if fault=='cb15-wrong-write-drop-undo':undo[0]=222"}
for label,token in tokens.items():
 mapping,own=mappings[label];extra=''
 if own is not None:extra="\n   if fault in ['cl9-wrong-undo','cl9-wrong-write-drop-undo']:undo["+str(own)+"]=65"
 rep(token,token+extra+"\n   if fault.startswith('cl9-coupling-'):\n    j=int(fault.rsplit('-',1)[1]);mapping="+repr(mapping)+"\n    if j in mapping:undo[mapping[j]]^=1")
rep(" R['cases'].append(",''' # Same-value operation: missing write/undo is observably identical here.
 reached_cl9=not cpu_bad and not baseline and forward in [0x809,0x80946]
 if reached_cl9:
  ref=[64,12,62,233,223,223,140,255,16];before=ref.copy()
  attempted_cl9=not fault.startswith('cl9-before-')
  if not attempted_cl9:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[760]]+[v[766+3*i] for i in range(8)]==before
  assert v[761:763]==([64,1] if attempted_cl9 else [0,0]) and state['cl9writes']==2*int(attempted_cl9)
  if attempted_cl9:
   after=ref.copy();undo=ref.copy()
   if fault in ['cl9-wrong-write','cl9-wrong-write-drop-undo']:after[0]^=1
   if fault.startswith('cl9-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('cl9-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('cl9-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault in ['cl9-wrong-undo','cl9-wrong-write-drop-undo']:undo[0]=65
   assert [v[763]]+[v[767+3*i] for i in range(8)]==after
   assert [v[764]]+[v[768+3*i] for i in range(8)]==undo
   assert v[765]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==cl9mask
  else:assert v[763:766]==[0xffffffff,0xffffffff,0] and all(v[767+3*i:769+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[760:766]==[0,0,0,0xffffffff,0xffffffff,0] and v[766:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
rep(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('cl9-'+phase+'-'+str(j),fault='cl9-'+phase+'-'+str(j))\n for j in range(1,9):run('cl9-coupling-'+str(j),fault='cl9-coupling-'+str(j))\n for f in ['cl9-drop-write','cl9-wrong-write','cl9-drop-undo','cl9-wrong-undo','cl9-wrong-write-drop-undo']:run(f,fault=f)")
p.write_bytes(s.encode())
p=K/'audit_logic.py';s=p.read_text().replace('760-word','790-word').replace('len(v)==760','len(v)==790').replace('0x80944]','0x80944,0x80946]').replace('(forward==0x809)','(forward in [0x809,0x80946])').replace('v[736:]==','v[736:760]==')
code=''' cl9b,cl9t,cl9a,cl9f,cl9u,cl9m=v[760:766]
 cl9nb=[v[766+3*i] for i in range(8)];cl9nf=[v[767+3*i] for i in range(8)];cl9nu=[v[768+3*i] for i in range(8)]
 assert cl9a in [0,1] and 0<=cl9m<512
 if forward in [0x809,0x80946]:
  assert cl9a==int([cl9b]+cl9nb==[64,12,62,233,223,223,140,255,16])
  if cl9a:
   assert cl9t==64 and cl9t==((cl9b&0xbf)|((0x3ff>>3)&0x40))
   assert cl9m==sum(1<<i for i,(a,b) in enumerate(zip([cl9u]+cl9nu,[cl9b]+cl9nb)) if a!=b)
   assert (cl9f==64 and cl9nf==cl9nb)==(forward==0x809)
  else:assert cl9t==cl9m==0 and cl9f==cl9u==0xffffffff and cl9nf==cl9nu==[0xffffffff]*8 and forward==0x80946
 else:assert v[760:766]==[0,0,0,0xffffffff,0xffffffff,0] and v[766:]==[0,0xffffffff,0xffffffff]*8
'''
rep(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and cl7m==0)','and cl7m==0 and cl9m==0)').replace('or cl7m:','or cl7m or cl9m:').replace('else 0x80945 if cl7m','else 0x80947 if cl9m else 0x80945 if cl7m')
s=s.replace("return {'crtc_linecompare_high':", "return {'crtc_linecompare_bit':{'before':cl9b,'target':cl9t,'attempted':cl9a,'after':cl9f,'restored':cl9u,'cleanup_mask':cl9m,'neighbors_before':cl9nb,'neighbors_after':cl9nf,'neighbors_restored':cl9nu},'crtc_linecompare_high':")
p.write_bytes(s.encode())
print('Extended809 actual-code oracle and independent schema')

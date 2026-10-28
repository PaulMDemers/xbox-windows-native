"""Extend independent COFF fault oracle and strict result schema for771."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'model.py';s=p.read_text()
s=s.replace("CS=[", "V=[(0x680800,719),(0x680804,749),(0x68080c,724),(0x680810,729),(0x680818,719)]\nCS=[")
s=s.replace("mm=dict(SETUP);", "mm=dict(SETUP);mm.update(dict(V));")
s=s.replace("state={'c13writes'", "state={'vwrites':0,'c13writes'")
s=s.replace("state['c13writes']+=1;n=state['c13writes'];", "state['c13writes']+=1;n=state['c13writes'];assert n==1 or state['vwrites']==2*word(234); ")
anchor='   val=cr[idx]';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   if idx in [0x13,0x19] and state['c13writes']==1 and word(1) in [0x77122,0x771]:
    j=5+[0x13,0x19].index(idx);phase=['before','after','undo'][state['vwrites']]
    if fault=='v-'+phase+'-'+str(j):val^=1
''')
anchor='  elif off in dict(H):'
s=s.replace(anchor,'''  elif off in dict(V):
   assert width==4;j=[a for a,_ in V].index(off)
   assert state['sq']==0x21 and ports==[5] and not hr and state['c13writes']==1
   assert word(1) in [0x77122,0x771]
   if kind==u.UC_MEM_WRITE:
    assert off==0x680800
    state['vwrites']+=1;n=state['vwrites'];assert n<=2
    assert word(232)==719 and word(233)==479 and word(234)==1 and value==(479 if n==1 else 719)
    writes.append(['v',off,value])
    if fault==('v-drop-write' if n==1 else 'v-drop-undo'):return
    mm[off]=value
    if fault==('v-wrong-write' if n==1 else 'v-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('v-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=6
     if j<=4:mm[V[j][0]]^=1
     else:cr[[0x13,0x19][j-5]]^=1
    return
   val=mm[off];phase=['before','after','undo'][state['vwrites']]
   if fault=='v-'+phase+'-'+str(j):val^=1
'''+anchor)
s=s.replace('0x2013a0','0x201400').replace('0x5c60','0x5c00').replace("'<232I',c.mem_read(0x201000,928)","'<256I',c.mem_read(0x201000,1024)")
s=s.replace('  if val==4:\n','  if val==4:\n   assert word(237)==0 and (not word(234) or word(236)==word(232))\n   assert [mm[a] for a,_ in V]==[b for _,b in V]\n')
s=s.replace("['c13-c25-coupling','c19-undo-c13-read']","['c13-c25-coupling','c19-undo-c13-read','v-coupling-6']")
# All seven fresh values are guarded, all seven recovery observations independently checked.
s=s.replace('  ubad=bool(umask)','''  ubad=bool(umask)
  vmask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('v-undo-','v-coupling-')) else 1 if fault in ['v-drop-undo','v-wrong-undo'] else 0
  vbad=bool(vmask)''')
s=s.replace('or ubad','or ubad or vbad')
s=s.replace('else 0x771\n  assert v[1]==forward',"else 0x77122 if fault.startswith(('v-before-','v-after-','v-coupling-')) or fault in ['v-drop-write','v-wrong-write'] else 0x771\n  assert v[1]==forward")
s=s.replace('0x77120]', '0x77120,0x77122]')
s=s.replace("[['cr',0x13,0x68],['cr',0x13,0x80]]", "[['cr',0x13,0x68]]+([['v',0x680800,479],['v',0x680800,719]] if forward in [0x771,0x77122] and not fault.startswith('v-before-') else [])+[['cr',0x13,0x80]]")
s=s.replace("else 0x77121 if ubad", "else 0x77123 if vbad else 0x77121 if ubad")
anchor=" R['cases'].append("
assert s.count(anchor)==1
s=s.replace(anchor,''' # Independent expected tail, not a projection inferred from returned status.
 reached=not cpu_bad and not baseline and forward in [0x771,0x77122]
 if reached:
  vb=[719,749,724,729,719,104,48]
  attempted=not fault.startswith('v-before-')
  before=vb.copy()
  if not attempted:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[232]]+[v[238+3*i] for i in range(6)]==before
  assert v[233:235]==([479,1] if attempted else [0,0])
  assert state['vwrites']==2*int(attempted)
  after=[479]+vb[1:];undo=vb.copy()
  if attempted:
   if fault=='v-drop-write':after[0]=719
   if fault=='v-wrong-write':after[0]^=1
   if fault.startswith('v-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('v-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('v-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='v-drop-undo':undo[0]=479
   if fault=='v-wrong-undo':undo[0]^=1
   assert [v[235]]+[v[239+3*i] for i in range(6)]==after
   assert [v[236]]+[v[240+3*i] for i in range(6)]==undo
   assert v[237]==sum(1<<i for i in range(7) if undo[i]!=vb[i])==vmask
  else:assert v[235:238]==[0xffffffff,0xffffffff,0] and all(v[i]==0xffffffff for i in [239,240,242,243,245,246,248,249,251,252,254,255])
 else:
  assert v[232:238]==[0,0,0,0xffffffff,0xffffffff,0] and v[238:]==[0,0xffffffff,0xffffffff]*6
'''+anchor)
s=s.replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(7):run('v-'+phase+'-'+str(j),fault='v-'+phase+'-'+str(j))\n for j in range(1,7):run('v-coupling-'+str(j),fault='v-coupling-'+str(j))\n for f in ['v-drop-write','v-wrong-write','v-drop-undo','v-wrong-undo']:run(f,fault=f)")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('232-word','256-word').replace('len(v)==232','len(v)==256').replace('0x77120]','0x77120,0x77122]').replace('(forward==0x771)','(forward in [0x771,0x77122])')
anchor=' assert c13attempt in [0,1]'
code=''' vb,vt,va,vf,vu,vm=v[232:238]
 nb=[v[238+3*i] for i in range(6)];na=[v[239+3*i] for i in range(6)];nu=[v[240+3*i] for i in range(6)]
 assert va in [0,1] and 0<=vm<128
 if forward in [0x771,0x77122]:
  assert va==int([vb]+nb==[719,749,724,729,719,104,48])
  if va:
   assert vt==479 and vm==sum(1<<i for i,(a,b) in enumerate(zip([vu]+nu,[vb]+nb)) if a!=b)
   assert (vf==479 and na==nb)==(forward==0x771)
  else:assert vt==vm==0 and vf==vu==0xffffffff and na==nu==[0xffffffff]*6 and forward==0x77122
 else:assert v[232:238]==[0,0,0,0xffffffff,0xffffffff,0] and v[238:]==[0,0xffffffff,0xffffffff]*6
'''
s=s.replace(anchor,code+anchor).replace('and um==0)','and um==0 and vm==0)').replace('or um:','or um or vm:').replace('else 0x77121 if um','else 0x77123 if vm else 0x77121 if um')
s=s.replace("return {'cr13':", "return {'vertical_display_end':{'before':vb,'target':vt,'attempted':va,'after':vf,'restored':vu,'cleanup_mask':vm,'neighbors_before':nb,'neighbors_after':na,'neighbors_restored':nu},'cr13':")
s=s.replace('kernel horizontal-only checkpoint; not a visible mode switch','kernel horizontal prefix plus one vertical word; not a visible mode switch')
p.write_text(s,newline='\n')
print('Extended host oracle and schema; no hardware access')

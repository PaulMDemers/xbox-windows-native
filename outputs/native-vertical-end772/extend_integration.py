"""Extend relocated native oracle independently for the new seven-value checkpoint."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'integration004.py';s=p.read_text()
s=s.replace('(0x680830,772)','(0x680830,770)') # Numeric timing is not an attempt namespace.
s=s.replace('CS=[','V=[(0x680800,719),(0x680804,749),(0x68080c,724),(0x680810,729),(0x680818,719)]\nCS=[')
s=s.replace("state={'c13writes'", "state={'vwrites':0,'c13writes'")
s=s.replace("if mm_bad:mm[mm_bad[0]]=mm_bad[1]", "mm.update(dict(V));vtrace=[]\n if mm_bad:mm[mm_bad[0]]=mm_bad[1]\n word=lambda i:struct.unpack('<I',c.mem_read(op+4*i,4))[0]")
s=s.replace("state['c13writes']+=1;n=state['c13writes'];", "state['c13writes']+=1;n=state['c13writes'];assert n==1 or state['vwrites']==2*word(234); ")
s=s.replace('   elif off in dict(H):', '''   elif off in dict(V):
    assert off==0x680800 and width==4 and state['seq']==0x21 and state['gate']==5
    assert state['c13writes']==1 and not hrestore
    state['vwrites']+=1;n=state['vwrites'];assert n<=2 and value==(479 if n==1 else 719)
    assert [word(i) for i in [232,233,234]]==[719,479,1]
    vtrace.append((off,value))
    if fault==('v-drop-write' if n==1 else 'v-drop-undo'):return
    mm[off]=value
    if fault==('v-wrong-write' if n==1 else 'v-wrong-undo'):mm[off]^=1
    if n==1 and fault.startswith('v-coupling-'):
     j=int(fault.rsplit('-',1)[1]);assert 1<=j<=6
     if j<=4:mm[V[j][0]]^=1
     else:cr[[0x13,0x19][j-5]]^=1
   elif off in dict(H):''')
s=s.replace('   i=sels[0x6013d4]\n', '''   i=sels[0x6013d4]
   if i in [0x13,0x19] and state['c13writes']==1 and word(1) in [0x77222,0x772]:
    j=5+[0x13,0x19].index(i);phase=['before','after','undo'][state['vwrites']]
    if fault=='v-'+phase+'-'+str(j):value^=1
''')
s=s.replace('  else:assert width==4 and off in mm;value=mm[off]', '''  else:
   assert width==4 and off in mm;value=mm[off]
   if off in dict(V) and state['c13writes']==1 and word(1) in [0x77222,0x772]:
    assert state['seq']==0x21 and state['gate']==5 and not hrestore
    j=[a for a,_ in V].index(off);phase=['before','after','undo'][state['vwrites']]
    if fault=='v-'+phase+'-'+str(j):value^=1''')
s=s.replace('   if value==4:\n', '   if value==4:\n    assert word(237)==0 and [mm[a] for a,_ in V]==[b for _,b in V]\n')
s=s.replace('op+928','op+1024').replace("'<232I'","'<256I'").replace('(0x54a0,0x6000)','(0x5500,0x6000)')
s=s.replace("  if fault.startswith(('h-restore-','h-cleanup-')):", "  if fault.startswith(('v-undo-','v-coupling-')) or fault in ['v-drop-undo','v-wrong-undo']:assert sw==[0x21] and outs==[5] and v[237]!=0 and v[101]==0\n  elif fault.startswith(('h-restore-','h-cleanup-')):")
s=s.replace('0x77220]', '0x77220,0x77222]')
s=s.replace("['c13-c25-coupling','c19-undo-c13-read']", "['c13-c25-coupling','c19-undo-c13-read','v-coupling-6']")
anchor=' for lo,hi in '
at=s.index(anchor)
s=s[:at]+''' # Expected values depend on the injected fault, not the returned success code.
 reached=state['c13writes'] and v[1] in [0x772,0x77222]
 if reached:
  vb=[719,749,724,729,719,104,48];before=vb.copy();attempted=not fault.startswith('v-before-')
  if not attempted:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[232]]+[v[238+3*i] for i in range(6)]==before
  assert v[233:235]==([479,1] if attempted else [0,0])
  assert vtrace==([(0x680800,479),(0x680800,719)] if attempted else [])
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
   assert v[237]==sum(1<<i for i in range(7) if undo[i]!=vb[i])
  else:assert v[235:238]==[0xffffffff,0xffffffff,0] and all(v[i]==0xffffffff for i in [239,240,242,243,245,246,248,249,251,252,254,255])
 else:
  assert not vtrace
  assert v[232:]==([0]*24 if refusal or want<0x772 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*6)
'''+s[at:]
s=s.replace('v[205],v[221],v[216],v[219],v[220]', 'v[221],v[237],v[232],v[235],v[236]')
s=s.replace("'horizontal_writes':htrace", "'vertical_writes':vtrace,'horizontal_writes':htrace")
s=s.replace(" for layout in ('dual','relocated'):", " for phase in ['before','after','undo']:\n  for j in range(7):run('v-'+phase+'-'+str(j),want=0x77223 if phase=='undo' else 0x77222,fault='v-'+phase+'-'+str(j))\n for j in range(1,7):run('v-coupling-'+str(j),want=0x77223,fault='v-coupling-'+str(j))\n for f in ['v-drop-write','v-wrong-write','v-drop-undo','v-wrong-undo']:run(f,want=0x77223 if f.endswith('undo') else 0x77222,fault=f)\n for layout in ('dual','relocated'):")
p.write_text(s,newline='\n')
print('Extended native integration with31 new faults and unchanged timing770')

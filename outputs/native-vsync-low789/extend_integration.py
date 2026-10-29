"""Construct complete-path CR10 fault oracle, including persistent CR07 neighbor faults."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'integration005.py';s=p.read_text()
assert "'c10writes'" not in s
s=s.replace("state={'c7writes':0","state={'c10writes':0,'c7writes':0")
s=s.replace('0x78930,','0x78930,0x78932,').replace('0x78930]','0x78930,0x78932]')
s=s.replace('    if i==7:', '''    if i==0x10:
     state['c10writes']+=1;n=state['c10writes'];assert n<=2 and value==(233 if n==1 else 212)
     assert state['c7writes']==1 and state['vewrites']==1 and word(1) in [0x78932,0x789]
     assert [word(460),word(461),word(462)]==[212,233,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('c10-drop-write' if n==1 else 'c10-drop-undo'):return
     cr[0x10]=value
     if fault==('c10-wrong-write' if n==1 else 'c10-wrong-undo'):cr[0x10]^=1
     if n==1 and fault.startswith('c10-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
    elif i==7:''',1)
s=s.replace("n=state['c7writes'];assert n<=2", "n=state['c7writes'];assert n==1 or state['c10writes']==2*word(462);assert n<=2")
s=s.replace("   i=sels[0x6013d4]\n", """   i=sels[0x6013d4]
   if i in [0x10,6,7,9,0x12,0x15,0x16,0x18,0x25] and state['c7writes']==1 and word(1) in [0x78932,0x789]:
    j=[0x10,6,7,9,0x12,0x15,0x16,0x18,0x25].index(i);phase=['before','after','undo'][state['c10writes']]
    if fault=='c10-'+phase+'-'+str(j):value^=1
""",1)
s=s.replace('    assert word(435)==0','    assert word(465)==0 and (not word(462) or word(464)==word(460))\n    assert word(435)==0')
s=s.replace('[(7,116),(7,240)]',"[(7,116)]+([(16,233),(16,212)] if state['c10writes'] else [])+[(7,240)]")
s=s.replace("  if fault.startswith(('c7-undo-'", "  if fault.startswith(('c10-undo-','c10-coupling-')) or fault in ['c10-drop-undo','c10-wrong-undo']:assert sw==[0x21] and outs==[5] and v[465]!=0 and v[101]==0\n  elif fault.startswith(('c7-undo-'",1)
model=(K/'model.py').read_text();block=model[model.index(' reached_c7='):model.index(" R['cases'].append",model.index(' reached_c7='))]
block=block.replace('not cpu_bad and not baseline and forward',"state['c13writes'] and v[1]").replace('==c7mask','').replace('==c10mask','')
block=block.replace(" else:assert v[430:436]==[0,0,0,0xffffffff,0xffffffff,0] and v[436:460]==[0,0xffffffff,0xffffffff]*8", " else:assert v[430:460]==([0]*30 if refusal or want<0x789 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)")
block=block.replace(" else:assert v[460:466]==[0,0,0,0xffffffff,0xffffffff,0] and v[466:]==[0,0xffffffff,0xffffffff]*8", " else:assert v[460:]==([0]*30 if refusal or want<0x789 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)")
a=s.index(' reached_c7=');z=s.index(' for lo,hi in [(0,0x880)',a);s=s[:a]+block+s[z:]
s=s.replace('v[405],v[435],v[430],v[433],v[434]','v[435],v[465],v[460],v[463],v[464]')
s=s.replace("try:\n for phase", """try:
 for phase in ['before','after','undo']:
  for j in range(9):run('c10-'+phase+'-'+str(j),want=0x78933 if phase=='undo' else 0x78932,fault='c10-'+phase+'-'+str(j))
 for j in range(1,9):run('c10-coupling-'+str(j),want=0x78933,fault='c10-coupling-'+str(j))
 for f in ['c10-drop-write','c10-wrong-write','c10-drop-undo','c10-wrong-undo']:run(f,want=0x78933 if f.endswith('undo') else 0x78932,fault=f)
 for phase""",1)
s=s.replace("end=base+sy['bridge_hold']","end=base+sy['bridge_hold'];minstack=[sp]")
anchor="  assert (base+0x880<=addr"
assert s.count(anchor)==1
s=s.replace(anchor,"  if base+0x6800<=addr and addr+size<=sp:minstack[0]=min(minstack[0],addr)\n"+anchor)
s=s.replace("'all_pixels_and_guards_exact':True}","'all_pixels_and_guards_exact':True,'stack_bytes_written_from_top':sp-minstack[0],'admitted_stack_bytes':6144}")
p.write_text(s,newline='\n')
print('Prepared789 complete-path CR10 oracle; no hardware access')

"""One-shot source construction of the independently asserted CR07 full path."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'integration005.py';s=p.read_text()
assert "'c7writes'" not in s
s=s.replace("state={'vewrites':0", "state={'c7writes':0,'vewrites':0")
s=s.replace('9:0x25,','6:0xec,7:0xf0,9:0x60,0x10:0xd4,0x12:0xcf,0x15:0xcf,0x16:0xed,0x18:0xff,')
s=s.replace('0x7872e,','0x7872e,0x78730,').replace('0x7872e]','0x7872e,0x78730]')
s=s.replace('    if i==0x13:', '''    if i==7:
     state['c7writes']+=1;n=state['c7writes'];assert n<=2 and value==(116 if n==1 else 240)
     assert state['vewrites']==1 and word(1) in [0x78730,0x787]
     assert [word(430),word(431),word(432)]==[240,116,1]
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     if fault==('c7-drop-write' if n==1 else 'c7-drop-undo'):return
     cr[7]=value
     if fault==('c7-wrong-write' if n==1 else 'c7-wrong-undo'):cr[7]^=1
     if n==1 and fault.startswith('c7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,0x10,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
    elif i==0x13:''',1)
s=s.replace("n=state['vewrites'];assert n<=2", "n=state['vewrites'];assert n==1 or state['c7writes']==2*word(432);assert n<=2")
s=s.replace("   i=sels[0x6013d4]\n", """   i=sels[0x6013d4]
   if i in [7,6,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['vewrites']==1 and word(1) in [0x78730,0x787]:
    j=[7,6,9,0x10,0x12,0x15,0x16,0x18,0x25].index(i);phase=['before','after','undo'][state['c7writes']]
    if fault=='c7-'+phase+'-'+str(j):value^=1
""",1)
s=s.replace('    assert word(405)==0', '    assert word(435)==0 and (not word(432) or word(434)==word(430))\n    assert word(405)==0')
s=s.replace('[(0x13,0x68),(0x13,0x80)]', '[(0x13,0x68)]+([(7,116),(7,240)] if state[\'c7writes\'] else [])+[(0x13,0x80)]')
s=s.replace("  if fault.startswith(('ve-undo-'", "  if fault.startswith(('c7-undo-','c7-coupling-')) or fault in ['c7-drop-undo','c7-wrong-undo']:assert sw==[0x21] and outs==[5] and v[435]!=0 and v[101]==0\n  elif fault.startswith(('ve-undo-'",1)
s=s.replace('assert v[400:]==', 'assert v[400:430]==')
model=(K/'model.py').read_text()
block=model[model.index(' reached_c7='):model.index(" R['cases'].append",model.index(' reached_c7='))]
block=block.replace('not cpu_bad and not baseline and forward', "state['c13writes'] and v[1]").replace('==c7mask','')
block=block.replace(" else:assert v[430:436]==[0,0,0,0xffffffff,0xffffffff,0] and v[436:]==[0,0xffffffff,0xffffffff]*8", " else:assert v[430:]==([0]*30 if refusal or want<0x787 else [0,0,0,0xffffffff,0xffffffff,0]+[0,0xffffffff,0xffffffff]*8)")
s=s.replace(' for lo,hi in [(0,0x880)',block+' for lo,hi in [(0,0x880)')
s=s.replace('v[375],v[405],v[400],v[403],v[404]', 'v[405],v[435],v[430],v[433],v[434]')
s=s.replace("try:\n for phase", """try:
 for phase in ['before','after','undo']:
  for j in range(9):run('c7-'+phase+'-'+str(j),want=0x78731 if phase=='undo' else 0x78730,fault='c7-'+phase+'-'+str(j))
 for j in range(1,9):run('c7-coupling-'+str(j),want=0x78731,fault='c7-coupling-'+str(j))
 for f in ['c7-drop-write','c7-wrong-write','c7-drop-undo','c7-wrong-undo']:run(f,want=0x78731 if f.endswith('undo') else 0x78730,fault=f)
 for phase""",1)
p.write_text(s)
p=K/'link_review007.py';s=p.read_text()
s=s.replace('and exact raw-byte comparison to failed capacity build','and exact raw-section byte checks')
a=s.index("old=json.loads");b=s.index('for n,h in meta',a);s=s[:a]+s[b:]
a=s.index("a=old['compile32']");b=s.index("e=elf",a);s=s[:a]+s[b:]
s=s.replace('14744','15992').replace("assert raw==(P/'payload004/native.bin').read_bytes()\n",'')
s=s.replace("'same_source_as_failed_capacity_build':True,'only_build_change':'larger padding reserve; raw executable bytes identical; owned IDT moved by separate page builder',", "'fresh_ELF_sections_match_raw_bytes':True,")
p.write_text(s)
p=K/'physical003.py';s=p.read_text().replace('Native787 horizontal held checkpoint','Native787 CR07 sync-overflow held checkpoint').replace('native horizontal control and deliberate','native CR07 sync-overflow control and deliberate').replace('and NVVVALIDEND719/479/719 with eight preserved neighbors, own saved-value recovery','and NVVVALIDEND719/479/719 then CR07 F0/74/F0 with eight preserved CRTC neighbors, own saved-value recovery');p.write_text(s)
p=K/'audit_collection006.py';s=p.read_text().replace('NVVVALIDEND','CR07').replace('[719,479,719]','[240,116,240]');p.write_text(s)
print('Prepared787 full-path CR07 assertions and corrected controller/review descriptions')

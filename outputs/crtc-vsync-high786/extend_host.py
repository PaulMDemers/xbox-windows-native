"""Extend independent COFF fault oracle and physical schema for shared CR07 bits."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'model.py';s=p.read_text()
def replace(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
s=s.replace("state={'vewrites'","state={'c7writes':0,'vewrites'")
s=s.replace('0x2016b8','0x201730').replace('0x5948','0x58d0').replace("'<430I',c.mem_read(0x201000,1720)","'<460I',c.mem_read(0x201000,1840)")
s=s.replace('0x7862e]','0x7862e,0x78630]').replace('0x7862e,0x786]','0x7862e,0x78630,0x786]').replace('v[406:]==','v[406:430]==')
replace(' cr={0x13:', ' cr={7:0xf0,6:0xec,9:0x60,0x10:0xd4,0x12:0xcf,0x15:0xcf,0x16:0xed,0x18:0xff,0x25:0x10,0x13:')
replace('assert idx in [1,3,2,0,4,5,0x13,0x1f,0x14,0x17,0x19]','assert idx in [7,1,3,2,0,4,5,0x13,0x1f,0x14,0x17,0x19]')
replace('    if idx==0x13:', '''    if idx==7:
     assert state['vewrites']==1 and word(1) in [0x78630,0x786]
     state['c7writes']+=1;n=state['c7writes'];assert n<=2
     assert [word(430),word(431),word(432)]==[240,116,1] and value==(116 if n==1 else 240)
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',7,value])
     if fault==('c7-drop-write' if n==1 else 'c7-drop-undo'):return
     cr[7]=value
     if fault==('c7-wrong-write' if n==1 else 'c7-wrong-undo'):cr[7]^=1
     if n==1 and fault.startswith('c7-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,9,0x10,0x12,0x15,0x16,0x18,0x25][j-1]]^=1
     return
    if idx==0x13:''')
replace('   val=cr[idx]', '''   val=cr[idx]
   if idx in [7,6,9,0x10,0x12,0x15,0x16,0x18,0x25] and state['vewrites']==1 and word(1) in [0x78630,0x786]:
    j=[7,6,9,0x10,0x12,0x15,0x16,0x18,0x25].index(idx);phase=['before','after','undo'][state['c7writes']]
    if fault=='c7-'+phase+'-'+str(j):val^=1
''')
replace("state['vewrites']+=1;n=state['vewrites'];assert n<=2","state['vewrites']+=1;n=state['vewrites'];assert n<=2\n    if n==2:assert state['c7writes']==2*word(432)")
replace('  if val==4:\n','  if val==4:\n   assert word(435)==0 and (not word(432) or word(434)==word(430))\n')
replace('  vebad=bool(vemask)', '''  vebad=bool(vemask)
  c7mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('c7-undo-','c7-coupling-')) else 1 if fault in ['c7-drop-undo','c7-wrong-undo'] else 0
  c7bad=bool(c7mask)''')
s=s.replace('or vebad','or vebad or c7bad')
replace('else 0x786\n  assert v[1]==forward',"else 0x78630 if fault.startswith(('c7-before-','c7-after-','c7-coupling-')) or fault in ['c7-drop-write','c7-wrong-write'] else 0x786\n  assert v[1]==forward")
replace("[['ve',0x680818,479],['ve',0x680818,719]]","[['ve',0x680818,479]]+([['cr',7,116],['cr',7,240]] if forward in [0x786,0x78630] and not fault.startswith('c7-before-') else [])+[['ve',0x680818,719]]")
s=s.replace('else 0x7862f if vebad','else 0x78631 if c7bad else 0x7862f if vebad')
replace(" R['cases'].append(",''' # Independent shared-overflow bit constants and complete neighboring bytes.
 reached_c7=not cpu_bad and not baseline and forward in [0x786,0x78630]
 if reached_c7:
  ref=[240,236,96,212,207,207,237,255,16];before=ref.copy()
  attempted_c7=not fault.startswith('c7-before-')
  if not attempted_c7:before[int(fault.rsplit('-',1)[1])]^=1
  assert [v[430]]+[v[436+3*i] for i in range(8)]==before
  assert v[431:433]==([116,1] if attempted_c7 else [0,0]) and state['c7writes']==2*int(attempted_c7)
  if attempted_c7:
   after=[116]+ref[1:];undo=ref.copy()
   if fault=='c7-drop-write':after[0]=240
   if fault=='c7-wrong-write':after[0]^=1
   if fault.startswith('c7-after-'):after[int(fault.rsplit('-',1)[1])]^=1
   if fault.startswith('c7-coupling-'):
    j=int(fault.rsplit('-',1)[1]);after[j]^=1;undo[j]^=1
   if fault.startswith('c7-undo-'):undo[int(fault.rsplit('-',1)[1])]^=1
   if fault=='c7-drop-undo':undo[0]=116
   if fault=='c7-wrong-undo':undo[0]^=1
   assert [v[433]]+[v[437+3*i] for i in range(8)]==after
   assert [v[434]]+[v[438+3*i] for i in range(8)]==undo
   assert v[435]==sum(1<<i for i in range(9) if undo[i]!=ref[i])==c7mask
  else:assert v[433:436]==[0xffffffff,0xffffffff,0] and all(v[437+3*i:439+3*i]==[0xffffffff]*2 for i in range(8))
 else:assert v[430:436]==[0,0,0,0xffffffff,0xffffffff,0] and v[436:]==[0,0xffffffff,0xffffffff]*8
 R['cases'].append(''')
replace(" run('baseline-deferred-read-success')", " run('baseline-deferred-read-success')\n for phase in ['before','after','undo']:\n  for j in range(9):run('c7-'+phase+'-'+str(j),fault='c7-'+phase+'-'+str(j))\n for j in range(1,9):run('c7-coupling-'+str(j),fault='c7-coupling-'+str(j))\n for f in ['c7-drop-write','c7-wrong-write','c7-drop-undo','c7-wrong-undo']:run(f,fault=f)")
p.write_text(s,newline='\n')
p=K/'audit_logic.py';s=p.read_text().replace('430-word','460-word').replace('len(v)==430','len(v)==460').replace('0x7862e]','0x7862e,0x78630]').replace('(forward==0x786)','(forward in [0x786,0x78630])').replace('v[406:]==','v[406:430]==')
code=''' cb7,ct7,ca7,cf7,cu7,cm7=v[430:436]
 cn7=[v[436+3*i] for i in range(8)];cfns7=[v[437+3*i] for i in range(8)];cuns7=[v[438+3*i] for i in range(8)]
 assert ca7 in [0,1] and 0<=cm7<512
 if forward in [0x786,0x78630]:
  assert ca7==int([cb7]+cn7==[240,236,96,212,207,207,237,255,16])
  if ca7:
   assert ct7==116 and (cb7^ct7)==0x84
   assert cm7==sum(1<<i for i,(a,b) in enumerate(zip([cu7]+cuns7,[cb7]+cn7)) if a!=b)
   assert (cf7==116 and cfns7==cn7)==(forward==0x786)
  else:assert ct7==cm7==0 and cf7==cu7==0xffffffff and cfns7==cuns7==[0xffffffff]*8 and forward==0x78630
 else:assert v[430:436]==[0,0,0,0xffffffff,0xffffffff,0] and v[436:]==[0,0xffffffff,0xffffffff]*8
'''
replace(' assert c13attempt in [0,1]',code+' assert c13attempt in [0,1]')
s=s.replace('and vm2==0)','and vm2==0 and cm7==0)').replace('or vm2:','or vm2 or cm7:').replace('else 0x7862f if vm2','else 0x78631 if cm7 else 0x7862f if vm2')
s=s.replace("return {'vertical_valid_end':", "return {'crtc_vsync_high':{'before':cb7,'target':ct7,'attempted':ca7,'after':cf7,'restored':cu7,'cleanup_mask':cm7,'neighbors_before':cn7,'neighbors_after':cfns7,'neighbors_restored':cuns7},'vertical_valid_end':")
p.write_text(s,newline='\n')
print('Extended786 COFF oracle and strict physical schema; no hardware access')

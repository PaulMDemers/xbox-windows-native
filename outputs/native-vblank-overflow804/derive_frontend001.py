"""Fresh804 source-only derivation; explicit layout and relocation-count changes."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;A=K.parent/'native-vblank-bit801'
names=['main004.c','layout004.c','layout.h','plan.c','plan.h','page002.c','page.h','page_tool003.c','bridge003.S','fixture.S','link.ld','Makefile','payload_build008.py','host_build009.py','plan_test004.py','relocate003.py','relocate004.py','integration012.py','cpu005.py','optical_oracle.py','optical_review005.py','build012.py','link_review012.py','linked_review007.py','page_review008.py','page_boundary009.py','plan_review003.py','physical007.py']
def rename(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x801(?=[0-9a-f]{0,2}$)','0x804',p) if i%2 else p.replace('801','804') for i,p in enumerate(parts)).replace('0x8010000d','0x8040000d').replace('native-vblank-bit804','native-vblank-overflow804')
r={'source_only':True,'no_parent_runtime':True,'parents':{},'outputs':{}}
for n in names:
 assert not (K/n).exists(),n
 p=A/n;s=rename(p.read_text());r['parents'][n]=hashlib.sha256(p.read_bytes()).hexdigest()
 # Fixed firmware reservation in layout.c is unrelated to payload extent.
 if n!='layout004.c':
  for a,b in [('0x5a00','0x5880'),('0x6a00','0x6880'),('0x6a04','0x6884'),('0x6a3c','0x68bc'),('0x6a40','0x68c0'),('0x74b8','0x73b0'),('0x208a00','0x208880'),('0xab8','0xb30')]:s=s.replace(a,b)
  s=re.sub(r'\b23040\b','22656',s);s=re.sub(r'\b23039\b','22655',s);s=re.sub(r'\b23041\b','22657',s)
  s=re.sub(r'\b2680\b','2800',s);s=s.replace('<670I','<700I')
 if n=='payload_build008.py':s=s.replace('probe-compact-native.c','probe-shared-native.c')
 if n in ['relocate003.py','relocate004.py']:s=s.replace('len(rows)==19','len(rows)==22')
 if n=='host_build009.py':s=s.replace('len(absolute)==14','len(absolute)==15').replace('payload_reloc[14]','payload_reloc[15]')
 if n=='page002.c':s=s.replace('count!=14','count!=15')
 if n=='page_tool003.c':s=s.replace('rel[14]','rel[15]').replace('i<14','i<15').replace(',rel,14,',',rel,15,')
 if n=='main004.c':s=s.replace('payload_reloc,14,','payload_reloc,15,')
 if n in ['page_review008.py','page_boundary009.py']:s=s.replace('relptr,14,','relptr,15,')
 if n=='link_review012.py':s=s.replace("'absolute_relocations':14","'absolute_relocations':15")
 if n=='bridge003.S':
  old=' .long 0,0x8d4,0x6ab8,0x6bd0,0x6bf0,0x7274,0x72ec,0x7364,0x73dc,0x7454,0x7440,0x744c,0x7450'
  assert old in s
  offsets=[0,0x8d4]+[0x68c0+4*j for j in [30,100,108,555,585,615,645,675,670,673,674]]
  s=s.replace(old,' .long '+','.join(hex(x) for x in offsets)).replace('2KiB stack','768-byte stack')
 (K/n).write_bytes(s.encode());r['outputs'][n]=hashlib.sha256((K/n).read_bytes()).hexdigest()
(K/'derivation001.json').write_text(json.dumps(r,indent=2)+'\n')
print('Derived804 sources; integration/optical reviewers still require extension')

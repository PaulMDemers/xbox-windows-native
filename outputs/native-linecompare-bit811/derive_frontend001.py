"""Host-only source derivative of808, expanded result and compact pair tables."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;A=K.parent/'native-linecompare-high808'
names=['main004.c','layout004.c','layout.h','plan.c','plan.h','page002.c','page.h','page_tool003.c','bridge003.S','fixture.S','link.ld','Makefile','payload_build008.py','host_build009.py','plan_test004.py','relocate003.py','relocate004.py','integration012.py','cpu006.py','optical_oracle.py','optical_review005.py','build013.py','link_review012.py','linked_review007.py','page_review008.py','page_boundary009.py','plan_review003.py']
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x808(?=[0-9a-f]{0,2}$)','0x811',p) if i%2 else p.replace('808','811') for i,p in enumerate(parts)).replace('0x8080000d','0x8110000d').replace('native-linecompare-high811','native-linecompare-bit811')
r={'source_only':True,'physical_admission':False,'parents':{},'outputs':{}}
rows=[30,100,108,645,675,705,735,765,760,763,764]
for n in names:
 p=A/n;s=ns(p.read_text());r['parents'][n]=hashlib.sha256(p.read_bytes()).hexdigest()
 if n!='layout004.c':
  s=s.replace('0x73e0','0x7458').replace('0xc20','0xc98').replace('<760I','<790I')
  s=re.sub(r'\b3040\b','3160',s)
 if n=='payload_build008.py':s=s.replace('probe-bitmap-native.c','probe-pairs-native.c')
 if n=='bridge003.S':
  a=s.index('report_offsets:\n');z=s.index('bridge_code_end:',a)
  s=s[:a]+'report_offsets:\n .long '+','.join(hex(x) for x in [0,0x8d4]+[0x6800+4*j for j in rows])+'\n'+s[z:]
 if n=='optical_review005.py':
  a=s.index('offsets = (');z=s.index('\nr =',a);s=s[:a]+'offsets = '+repr(tuple([0x8d4]+[0x6800+4*j for j in rows]))+s[z:]
 if n in ['relocate003.py','relocate004.py']:s=s.replace('len(rows)==22','len(rows)==42')
 if n=='host_build009.py':s=s.replace('len(absolute)==15','len(absolute)==34').replace('payload_reloc[15]','payload_reloc[34]')
 if n=='page002.c':s=s.replace('count!=15','count!=34')
 if n=='page_tool003.c':s=re.sub(r'\b15\b','34',s)
 if n=='main004.c':s=s.replace('payload_reloc,15,','payload_reloc,34,')
 if n in ['page_review008.py','page_boundary009.py']:
  s=s.replace('24256,relptr,15,','24256,relptr,34,').replace('for i in range(15):','for i in range(34):')
 if n=='link_review012.py':s=s.replace("'absolute_relocations':15","'absolute_relocations':34")
 assert not (K/n).exists();(K/n).write_bytes(s.encode());r['outputs'][n]=hashlib.sha256((K/n).read_bytes()).hexdigest()
r['layout']={'payload':[0x900,0x67c0],'request':[0x67c0,0x67fc],'result':[0x6800,0x7458],'IDT':[0x7500,0x7d00],'stack':[0x7d00,0x8000],'total_bytes':32768,'report_word_indices':rows,'absolute_relocations':34,'all_relocations':42}
(K/'frontend-derivation001.json').write_text(json.dumps(r,indent=2)+'\n')
print('811 frontend derived; integration requires CR09 coverage; hardware blocked on810')

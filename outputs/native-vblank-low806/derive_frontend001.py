"""Fresh806 frontend sources; payload starts at0xb00, IDT/stack unchanged."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;A=K.parent/'native-vblank-overflow804'
names=['main004.c','layout004.c','layout.h','plan.c','plan.h','page002.c','page.h','page_tool003.c','bridge003.S','fixture.S','link.ld','Makefile','payload_build008.py','host_build009.py','plan_test004.py','relocate003.py','relocate004.py','integration012.py','cpu005.py','optical_oracle.py','optical_review005.py','build012.py','link_review012.py','linked_review007.py','page_review008.py','page_boundary009.py','plan_review003.py','physical008.py']
def rename(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x804(?=[0-9a-f]{0,2}$)','0x806',p) if i%2 else p.replace('804','806') for i,p in enumerate(parts)).replace('0x8040000d','0x8060000d').replace('native-vblank-overflow806','native-vblank-low806')
r={'source_only':True,'no_parent_runtime':True,'parents':{},'outputs':{}}
for n in names:
 p=A/n;s=rename(p.read_text());r['parents'][n]=hashlib.sha256(p.read_bytes()).hexdigest()
 if n!='layout004.c':
  for a,b in [('0x5880','0x5cc0'),('0x6880','0x67c0'),('0x6884','0x67c4'),('0x68bc','0x67fc'),('0x68c0','0x6800'),('0x73b0','0x7368'),('0x208880','0x208cc0'),('0xb30','0xba8')]:s=s.replace(a,b)
  for a,b in [('22656','23744'),('22655','23743'),('22657','23745'),('2800','2920')]:s=re.sub(r'\b'+a+r'\b',b,s)
  s=s.replace('<700I','<730I')
 if n=='page002.c':
  s=s.replace('memcpy(p,code,4096);memcpy(p+4096,payload,size)','memcpy(p,code,2816);memcpy(p+2816,payload,size)').replace('4096+rel[i].offset','2816+rel[i].offset').replace('base+4096','base+2816').replace('memset(p+0x800,0,0x800)','memset(p+0x800,0,0x300)')
 if n=='page_tool003.c':s=s.replace('code[4096]','code[2816]')
 if n=='bridge003.S':
  s=s.replace('sub $4096,%eax','sub $2816,%eax').replace('.org 4096,0','.org 2816,0')
  a=s.index('report_offsets:\n');z=s.index('bridge_code_end:',a)
  s=s[:a]+'report_offsets:\n .long '+','.join(hex(x) for x in [0,0x8d4]+[0x6800+4*j for j in [30,100,108,585,615,645,675,705,700,703,704]])+'\n'+s[z:]
 if n=='host_build009.py':s=s.replace("len((O/'bridge.bin').read_bytes())==4096","len((O/'bridge.bin').read_bytes())==2816")
 if n in ['relocate003.py','relocate004.py']:s=s.replace('base=load-4096','base=load-2816').replace('len(blob)<=0x4000','len(blob)<=0x5cc0')
 if n=='link_review012.py':s=s.replace('0x1ef1000,0x1ed9000','0x1ef0b00,0x1ed8b00')
 if n=='optical_review005.py':
  a=s.index('offsets = (');z=s.index('\nr =',a);s=s[:a]+'offsets = '+repr(tuple([0x8d4]+[0x6800+4*j for j in [30,100,108,585,615,645,675,705,700,703,704]]))+s[z:]
 assert not (K/n).exists();(K/n).write_bytes(s.encode());r['outputs'][n]=hashlib.sha256((K/n).read_bytes()).hexdigest()
r['layout']={'payload':[0xb00,0x67c0],'request':[0x67c0,0x67fc],'result':[0x6800,0x7368],'IDT':[0x7500,0x7d00],'stack':[0x7d00,0x8000],'unchanged_total_bytes':32768}
(K/'frontend-derivation001.json').write_text(json.dumps(r,indent=2)+'\n')
print('806 frontend derived; integration still requires new operation coverage')

"""Derive808 sources only; bitmap payload at0900, request67c0, result6800..73e0."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;A=K.parent/'native-vblank-low806'
names=['main004.c','layout004.c','layout.h','plan.c','plan.h','page002.c','page.h','page_tool003.c','bridge003.S','fixture.S','link.ld','Makefile','payload_build008.py','host_build009.py','plan_test004.py','relocate003.py','relocate004.py','integration012.py','cpu006.py','optical_oracle.py','optical_review005.py','build013.py','link_review012.py','linked_review007.py','page_review008.py','page_boundary009.py','plan_review003.py','physical009.py','controller_review001.py','publish_receipts001.py','restore_receipts001.py','dashboard_preflight001.py']
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x806(?=[0-9a-f]{0,2}$)','0x808',p) if i%2 else p.replace('806','808') for i,p in enumerate(parts)).replace('0x8060000d','0x8080000d').replace('native-vblank-low808','native-linecompare-high808')
r={'source_only':True,'no_parent_runtime':True,'parents':{},'outputs':{}}
rows=[30,100,108,615,645,675,705,735,730,733,734]
for n in names:
 p=A/n;s=ns(p.read_text());r['parents'][n]=hashlib.sha256(p.read_bytes()).hexdigest()
 if n!='layout004.c':
  for a,b in [('0x5cc0','0x5ec0'),('0x7368','0x73e0'),('0x208cc0','0x208ec0'),('0xba8','0xc20'),('0xb00','0x900'),('0x1ef0b00','0x1ef0900'),('0x1ed8b00','0x1ed8900')]:s=s.replace(a,b)
  for a,b in [('23744','24256'),('23743','24255'),('23745','24257'),('2816','2304'),('2920','3040')]:s=re.sub(r'\b'+a+r'\b',b,s)
  s=s.replace('<730I','<760I')
 if n=='payload_build008.py':s=s.replace('probe-shared-native.c','probe-bitmap-native.c')
 if n=='page002.c':s=s.replace('memset(p+0x800,0,0x300)','memset(p+0x800,0,0x100)')
 if n=='bridge003.S':
  a=s.index('report_offsets:\n');z=s.index('bridge_code_end:',a)
  s=s[:a]+'report_offsets:\n .long '+','.join(hex(x) for x in [0,0x8d4]+[0x6800+4*j for j in rows])+'\n'+s[z:]
 if n=='optical_review005.py':
  a=s.index('offsets = (');z=s.index('\nr =',a);s=s[:a]+'offsets = '+repr(tuple([0x8d4]+[0x6800+4*j for j in rows]))+s[z:]
 if n=='physical009.py':s=s.replace('CR15 vertical-blank-start low byte','CR07 line-compare high bit').replace('then CR07 36/3E/36 and CR15 CF/DF/CF, eight neighbors','then CR07 line-compare3E/3E/3E, eight neighbors').replace('own recovery before CR07, CR09 and CR12','own CR07 recovery before CR15 and earlier prefix')
 assert not (K/n).exists();(K/n).write_bytes(s.encode());r['outputs'][n]=hashlib.sha256((K/n).read_bytes()).hexdigest()
r['layout']={'payload':[0x900,0x67c0],'request':[0x67c0,0x67fc],'result':[0x6800,0x73e0],'IDT':[0x7500,0x7d00],'stack':[0x7d00,0x8000],'total_bytes':32768,'report_word_indices':rows}
(K/'frontend-derivation001.json').write_text(json.dumps(r,indent=2)+'\n')
print('808 frontend derived; integration still requires new operation coverage')

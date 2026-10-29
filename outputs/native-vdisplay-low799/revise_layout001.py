"""Preserve rejected23040 extent; admit23424 only with fresh complete bounds checks."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;old=K/'rejected-layout001';old.mkdir()
mapping={'23040':'23424','23039':'23423','23041':'23425','0x5a00':'0x5b80','0x6a00':'0x6b80','0x6a04':'0x6b84','0x6a3c':'0x6bbc','0x6a40':'0x6bc0','0x7440':'0x75c0','0x7500':'0x7600','0x7d00':'0x7e00','0x7d04':'0x7e04','0x208a00':'0x208b80','768':'512'}
before=','.join(hex(i) for i in [0x8d4]+[0x6a40+4*j for j in [30,100,108,495,525,555,585,615,610,613,614]])
after=','.join(hex(i) for i in [0x8d4]+[0x6bc0+4*j for j in [30,100,108,495,525,555,585,615,610,613,614]])
pins={}
for p in list(K.iterdir()):
 if p.suffix not in ['.c','.h','.S','.py','.ld'] or p.name in ['prepare.py','revise_layout001.py']:continue
 (old/p.name).write_bytes(p.read_bytes());pins[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
 if p.name=='payload_build006.py':continue
 s=p.read_text()
 if p.name in ['bridge002.S','optical_review003.py']:
  assert before in s;s=s.replace(before,'OFFSET_PLACEHOLDER')
 s=re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,mapping))+r')(?![0-9a-zA-Z])',lambda m:mapping[m[0]],s)
 s=s.replace('OFFSET_PLACEHOLDER',after).replace('payload006','payload007');p.write_bytes(s.encode())
s=(K/'payload_build006.py').read_text().replace('payload006','payload007').replace('23040','23424');(K/'payload_build007.py').write_bytes(s.encode())
(K/'qualification-failure001.json').write_text(json.dumps({'passed':False,'reason':'raw23416 exceeds23040 reserve; failed before padding or host construction','receipt':'payload006.json','preserved_sources':pins,'physical_access':False,'correction':'23424 reserve, request6b80..6bbc, result6bc0..75c0, guard64bytes, IDT7600..7e00, stack7e00..8000 (512bytes); all executable bounds/CPU/stack tests required'},indent=2)+'\n')
(K/'layout-revision001.json').write_text(json.dumps({'mapping':mapping,'allocation_bytes':32768,'alias_pages':8,'payload':[4096,0x6b80],'request':[0x6b80,0x6bbc],'request_guard':[0x6bbc,0x6bc0],'result':[0x6bc0,0x75c0],'result_guard':[0x75c0,0x7600],'IDT':[0x7600,0x7e00],'stack':[0x7e00,0x8000],'stack_bytes':512,'requires_fresh_executable_bounds_tests':True},indent=2)+'\n')
print('Revised799 layout; no stage or launch')

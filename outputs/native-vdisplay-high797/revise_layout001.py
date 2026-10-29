"""Preserve rejected candidate; fresh payload reserve and separately checked stack layout."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;old=K/'rejected-layout001';assert not old.exists();old.mkdir()
files=[p for p in K.iterdir() if p.is_file() and p.suffix in ['.c','.h','.S','.py','.ld'] and p.name not in ['prepare.py','revise_layout001.py']]
mapping={'22016':'22272','22015':'22271','22017':'22273','0x5600':'0x5700','0x6600':'0x6700','0x6604':'0x6704','0x663c':'0x673c','0x6640':'0x6740','0x6fc8':'0x70c8','0x7000':'0x7100','0x7800':'0x7900','0x7804':'0x7904','0x208600':'0x208700'}
pins={}
for p in files:
 (old/p.name).write_bytes(p.read_bytes());pins[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
 if p.name=='payload_build005.py':continue
 s=p.read_text();s=re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,mapping))+r')(?![0-9a-zA-Z])',lambda m:mapping[m[0]],s)
 s=s.replace('payload005','payload006')
 if p.name=='integration009.py':s=s.replace("'admitted_stack_bytes':2048","'admitted_stack_bytes':1792")
 if p.name=='fixture.S':s=s.replace('mov ecx,22272','mov ecx,21504')
 p.write_bytes(s.encode())
s=(K/'payload_build005.py').read_text().replace('payload005','payload006').replace('22016','22272');(K/'payload_build006.py').write_bytes(s.encode())
# Report offsets embed result addresses, independently regenerate from declared word indexes.
before=','.join(hex(i) for i in [0x8d4]+[0x6640+4*j for j in [30,100,108,465,495,525,555,585,580,583,584]])
after=','.join(hex(i) for i in [0x8d4]+[0x6740+4*j for j in [30,100,108,465,495,525,555,585,580,583,584]])
for n in ['bridge002.S','optical_review003.py']:
 p=K/n;s=p.read_text();assert before in s;s=s.replace(before,after);p.write_bytes(s.encode())
(K/'qualification-failure001.json').write_text(json.dumps({'passed':False,'attempt':'payload005','reason':'raw22200 exceeds22016 candidate reserve','stage_or_launch':False,'preserved_source_directory':'rejected-layout001','source_sha256':pins,'failed_receipt_sha256':hashlib.sha256((K/'payload005.json').read_bytes()).hexdigest(),'next':'fresh payload006,22272-byte reserve; request6700..673c,result6740..70c8,IDT7100..7900,1792-byte bounded stack7900..8000; require all memory and CPU checks'},indent=2)+'\n')
(K/'layout-revision001.json').write_text(json.dumps({'mapping':mapping,'allocation_bytes':32768,'alias_pages':8,'result_bytes':2440,'payload_reserve':22272,'payload':[4096,0x6700],'request':[0x6700,0x673c],'result':[0x6740,0x70c8],'result_guard':[0x70c8,0x7100],'IDT':[0x7100,0x7900],'stack':[0x7900,0x8000],'stack_bytes':1792,'requires_fresh_executable_bounds_tests':True},indent=2)+'\n')
print('Revised unrun layout; failed build and inputs preserved')

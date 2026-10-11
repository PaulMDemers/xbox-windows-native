"""Review exact source-only delta and unchanged guest fixture before fresh launch."""
import ast,hashlib,json,importlib.util
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
b=read(k/'build002.json');assert b['passed'] and b['borrowed_sources_restored'] and b['changed_sources']==['hw/xbox/nv2a/pgraph/gl/surface.c']
assert sha(k/'artifacts/build002/xemu-surface257.exe')==b['executable_sha256']
p=k/'artifacts/build002/source/hw/xbox/nv2a/pgraph/gl/surface.c';s=p.read_text();helper=(k/'observation.c').read_text();assert s.count(helper)==1
inverse=s.replace(helper+'\n','')
import re
inverse=re.sub(r'^ *trace_surface257\(d, (?:surface|other_surface|s|found), (?:[1-6]|write \? 12 : 11)\);\n','',inverse,flags=re.M)
parent=k.parent/'worker-barrier247/artifacts/build004/source/hw/xbox/nv2a/pgraph/gl/surface.c'
assert inverse==parent.read_text(),'Any non-observational source delta refused'
f=read(k/'fixture-preserve001.json');old=read(k.parent/'installer-focus250/fixture-preserve001.json')
assert f['files']==old['files'] and f['seed_sha256']==old['seed_sha256'] and f['device_policy']==old['device_policy']
assert sha(Path(f['fixture_path_windows']))==f['seed_sha256']
# Real parser must reject missing parts/duplicates and retain bounded coverage.
spec=importlib.util.spec_from_file_location('sites',k/'analyze-sites.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
lines=[f'nv2a_lifecycle244 phase={e} when=10 thread=20 ref=1 a={1 if e==100 else 0} b=0' for e in range(100,107)]
raw=('\n'.join(lines)+'\n').encode();assert m.parse(raw)['groups']==1
for bad in [('\n'.join(lines[:-1])+'\n').encode(),raw+(lines[0]+'\n').encode(),raw[:-1]]:
 try:m.parse(bad)
 except AssertionError:pass
 else:raise AssertionError('Incomplete/duplicate trace accepted')
required=set(re.findall(r"k/'([^']+)'",(k/'trace.py').read_text()))
for n in required:assert (k/n).is_file(),n
r=dict(passed=True,exact_inverse_equals_parent=True,only_source_change=b['changed_sources'],guest_files_unchanged=True,source_sha256=sha(p),fixture_sha256=f['seed_sha256'],parser_negative_tests=3,physical_access=False,pixel_preservation_proved=False)
(k/'prelaunch-review001.json').write_text(json.dumps(r,indent=2)+'\n')
pins={}
for p in k.rglob('*'):
 if p.is_file() and ('__pycache__' not in p.parts):
  if p.suffix=='.py':ast.parse(p.read_text())
  pins[p.relative_to(ws).as_posix()]=sha(p)
for n,h in read(k.parent/'installer-focus250/emulator-frozen.json').items():assert sha(ws/n)==h; pins[n]=h
(k/'emulator-frozen.json').write_text(json.dumps(pins,indent=2)+'\n');print('257 source inverse, immutable fixture, negative parser and frozen inputs PASS',len(pins))

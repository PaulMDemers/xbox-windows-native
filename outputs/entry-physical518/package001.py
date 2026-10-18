"""Freeze actual controller qualification and exact existing entry-only executable."""
import ast,hashlib,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'package001.json';assert not out.exists()
h=read(K/'controller-host001.json');assert h['passed'] and len(h['cases'])==29 and h['source_sha256']==sha(K/'physical.py')
h=read(K/'supervisor-host001.json');assert h['passed'] and h['all_children_closed'] and h['source_sha256']==sha(K/'supervise.py')
assert read(K.parent/'entry-colocated516/review001.json')['passed']
assert read(K.parent/'entry-observer517/final-review.json')['passed']
assert (K/'entry_decode.py').read_bytes()==(K.parent/'entry-receipt498/decode.py').read_bytes()
old=(K.parent/'entry-scene501/physical.py').read_text(encoding='utf-8');new=(K/'physical.py').read_text(encoding='utf-8')
for a,b in [('def receipt(', 'def classify('),('def classify(', 'def stage('),('def cold_pair(', 'def collect(')]:
 assert old[old.index(a):old.index(b)]==new[new.index(a):new.index(b)],a
assert 'put(f,HOOK' not in new and 'f.rename(' not in new and 'run501.exe' not in new
p=Path('C:/xwn516/build001/default.xbe');assert p.stat().st_size==545088 and sha(p)=='a272c18d32f96719ddf5ec07dcc551f74165f797b8247b361c1a4e3b3d84da1d'
deps=list(K.glob('*.py'))+[K/n for n in ['DESIGN.md','controller-host001.json','supervisor-host001.json','.gitattributes']]
deps += [W/n for n in ['outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py','tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json','outputs/native-windows-physical-f/physical-cache-preflight.json','outputs/device-hardware220/state/demo251-claimed.json','outputs/clean-media404/hive_audit004.py','outputs/native-windows-physical-f/decode-legacy-events.py','outputs/entry-scene501/physical.py','outputs/entry-scene501/supervise.py','outputs/entry-receipt498/decode.py','outputs/entry-colocated516/build001.json','outputs/entry-colocated516/review001.py','outputs/entry-colocated516/review001.json','outputs/entry-colocated516/final-review.json','outputs/entry-observer517/actual-review001.json','outputs/entry-observer517/final-review.json','outputs/entry-observer517/emu001/trace.json','outputs/entry-observer517/emu001/protected.json']]
deps+=list(Path('C:/xwn516/build001').glob('*.S'))
for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
free={d:shutil.disk_usage(d+':/').free for d in ['C','E']};assert free['C']-64*1024**2>=20*1024**3
p=Path('C:/xwn516/build001/default.xbe')
r=dict(passed=True,files={'default.xbe':dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))},dependencies={str(p.resolve()):sha(p) for p in deps},capacity_free_bytes=free,projected_C_bytes=64*1024**2,E_allocation=0,controller_cases=29,actual_supervisor_children=3,physical_access=False,unchanged_helpers=['receipt','classify','cold_pair'],scope='new physical entry-only controller; no Windows launch or hook')
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print('PASS',len(r['dependencies']),'inputs pinned')

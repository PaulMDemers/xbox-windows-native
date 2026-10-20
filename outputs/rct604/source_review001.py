"""Check frozen604 source plus preserved601 core before fresh execution."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'source-review001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((K/'build002.json').read_text());assert b['status']=='compiled'
for name,v in b['files'].items():
 p=Path(name.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256']
 if p.suffix in ['.c','.h'] and p.name!='target_iat.h':assert p.read_bytes()==(K/p.name).read_bytes()
norm=lambda p:p.read_text(encoding='utf-8').replace('xwn604','xwn601').replace('XWN604','XWN601')
for n in ['calls.h','graphics002.h','host_calls.c']:assert norm(K/n)==(K.parent/'rct601'/n).read_text(encoding='utf-8')
trace=(K/'trace.c').read_text();cold=(K/'cold002.py').read_text();vm=(K/'vm.py').read_text()
assert 'event_id\']==6006' in cold and '6016' not in cold
assert '>60000' in trace and 'nargs[16]' in trace and 'f.api==11?10:0' in trace
assert 'choices=[604]' in vm and 'default=600)' in vm and 'retail_media' not in vm
for n in ['host-dib001.json','host-tests001.json','header-tests001.json','binary-review001.json']:assert json.loads((K/n).read_text())['passed']
out.write_text(json.dumps(dict(passed=True,core601_preserved=['calls.h','graphics002.h','host_calls.c'],frozen_sources={p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h']},memory_scope='Fixed4+40 checked remote reads; raw snapshot and independent interpretation; no palette/pixel reads. Actual inaccessible-page test pending.'),indent=2)+'\n')
print('604 frozen sources and unchanged601 core passed')

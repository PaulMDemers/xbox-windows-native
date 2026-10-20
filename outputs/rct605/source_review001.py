"""Verify compiled bytes and exact reuse of already qualified code."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct604';out=K/'source-review001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((K/'build002.json').read_text());assert b['status']=='compiled'
for n,v in b['files'].items():
 p=Path(n.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256']
 if p.suffix in ['.c','.h'] and p.name!='target_iat.h':assert p.read_bytes()==(K/p.name).read_bytes()
for n in ['dib_header.h','calls.h','host_calls.c','host_dib.c']:assert (K/n).read_bytes()==(old/n).read_bytes()
for n in ['graphics002.h','dib_control.h']:
 assert (K/n).read_text().replace('xwn605','xwn604').replace('XWN605','XWN604')==(old/n).read_text()
for n in ['host-dib001.json','host-tests001.json']:assert json.loads((old/n).read_text())['passed']
for n in ['host-phase001.json','binary-review001.json']:assert json.loads((K/n).read_text())['passed']
assert "event_id']==6006" in (K/'cold002.py').read_text()
trace=(K/'trace.c').read_text();assert 'if(!phasecheck605()||!observe(' in trace and '>60000' in trace and 'count>10000' in trace
out.write_text(json.dumps(dict(passed=True,unchanged_qualified_code=['dib_header.h','calls.h','host_calls.c','host_dib.c'],qualified_parent='604 closed original control; reuse code/results by exact identity, not its runtime',parent_tests={n:sha(old/n) for n in ['host-dib001.json','host-tests001.json','review001.json']},frozen_sources={p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h']}),indent=2)+'\n')
print('605 frozen sources and exact qualified604 core passed')

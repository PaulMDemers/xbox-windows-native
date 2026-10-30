"""Freeze fixed720p reproduction before staging; no physical access."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;A=K.parent/'boot720-bridge842'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=['bridge001','load-host003','driver003','driver-host002','driver-review002','qualify002','chain002','host007','cpu-build011','cpu-run011','build004']
for n in records:assert read(K/(n+'.json'))['passed']
assert read(K/'cpu-run011.json')['closed'] and read(K/'restore-hives001.json')['completed']
assert read(K/'source001.json')['parents'].keys()==read(A/'source001.json')['trees'].keys()
for label,row in read(K/'source001.json')['parents'].items():assert row['tree']==read(A/'source001.json')['trees'][label] and row['source_only']
for key in ['retention_unchanged_sha256','loader_fat_unchanged_sha256']:assert read(K/'source001.json')[key]==read(A/'source001.json')[key]
assert read(K/'chain002.json')['definitions']==read(A/'chain002.json')['definitions']
assert read(K/'driver003.json')['definitions']==read(A/'driver003.json')['definitions']
records+=['source001','baseline001','restore-hives001']
pins={p.name:sha(p) for p in K.iterdir() if p.is_file() and (p.suffix in ['.py','.c','.h','.S','.ld','.patch'] or p.name in ['Makefile','.gitattributes']+[n+'.json' for n in records])}
with (K/'launch-source-pins001.json').open('x') as f:f.write(json.dumps(pins,indent=2)+'\n')
print('843 exact launch inputs frozen')

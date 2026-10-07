"""Verify immutable diagnostic evidence and byte-exact helper source in Git."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'001'
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
q=read(out/'qualification.json');assert q['passed'] and q['ui_assisted_diagnostic'] and not q['ordinary_stability_qualified'] and not q['physical_qualified']
for name,digest in q['evidence_sha256'].items():
 p=out/name;assert sha(p.read_bytes())==digest
 assert sha(subprocess.check_output(['git','show',':'+p.relative_to(ws).as_posix()],cwd=ws))==digest
r=read(k/'helper-review.json');assert sha((k/'probe.c').read_bytes())==r['source_sha256']
f=read(k/'fixture-001.json');assert f['fatx_sha256']=='ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9'
a=read(out/'audit.json');assert next(p for p in a['payloads'] if p['path']=='xwnidle/probe.exe')['sha256']==r['probe_sha256']
for p in k.iterdir():
 if p.suffix in ['.c','.py','.ps1']:assert subprocess.check_output(['git','show',':'+p.relative_to(ws).as_posix()],cwd=ws)==p.read_bytes()
print(json.dumps(dict(evidence_verified=True,ui_assisted_diagnostic=True,hardware_qualified=False)))

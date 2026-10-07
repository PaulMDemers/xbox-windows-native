"""Verify both immutable case reports and Git-preserved source/evidence bytes."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text())
review=read(k/'probe-review.json')
for filename,key in [('probe.c','source_sha256'),('Build.ps1','build_script_sha256')]:
    assert sha((k/filename).read_bytes())==review[key]
checked=[]
for case in ['001','002']:
    q=read(k/case/'qualification.json');assert q['passed'] and not q['hardware_qualified']
    for name,digest in q['evidence_sha256'].items():
        p=k/case/name;assert sha(p.read_bytes())==digest
        assert sha(subprocess.check_output(['git','show',':'+p.relative_to(ws).as_posix()],cwd=ws))==digest
        checked.append(p.relative_to(k).as_posix())
    c=read(k/case/'collection.json')
    for stage in c['stages'].values():assert sha((k/case/stage['output']).read_bytes())==stage['sha256']
    a=read(k/case/'audit.json');assert len(a['append_files'])==96 and all(v['exact'] for v in a['append_files'])
    assert next(v for v in a['payloads'] if v['path']=='xwnidle/append.exe')['sha256']==review['probe_sha256']
    f=read(k/('fixture-'+case+'.json'));assert f['parent_fixture_sha256']==read(k/'fixture-001.json')['parent_fixture_sha256']
for p in k.iterdir():
    if p.suffix in ['.c','.ps1','.py']:
        assert subprocess.check_output(['git','show',':'+p.relative_to(ws).as_posix()],cwd=ws)==p.read_bytes(),p
print(json.dumps(dict(passed=True,cases=2,exact_append_files=192,staged_hash_records_verified=checked,hardware_qualified=False)))

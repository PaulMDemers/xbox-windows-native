"""Verify the compiled source pins, artifact pins and closure of these owned trials."""
import ast,hashlib,json,os
from pathlib import Path
k=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
result=dict(scope=__doc__,physical_access=False,builds=[],trials=[],syntax_files=0)
h=k/'handoff001';b=read(h/'build001.json');meta=read(h/'metadata-followup.json')
for name,digest in b['sources'].items():
    p=h/name
    if name=='.gitattributes':
        assert sha(p)==meta['after_sha256']
        p=h/meta['build_snapshot']
    assert sha(p)==digest,name
assert sha(h/'0001-hal-shared-smbus.patch')==b['patch_sha256']
assert sha(h/'artifacts/build001/halxboxnt5.dll')==b['candidate_sha256']
result['builds'].append(dict(name='handoff001',compiled_sources_unchanged=True,metadata_followup=meta,artifact_sha256=b['candidate_sha256']))
for n in range(1,5):
    folder=k/f'lifecycle{n:03d}';attempt='004' if n==2 else '001'
    b=read(folder/f'build{attempt}.json')
    for row in b['sources']:assert sha(folder/row['name'])==row['sha256'],str(folder/row['name'])
    for row in b['files']:assert sha(folder/f'artifacts/build{attempt}'/row['name'])==row['sha256']
    result['builds'].append(dict(name=folder.name,attempt=attempt,source_count=len(b['sources']),artifact_count=len(b['files']),pins_match=True))
    out=folder/'emulator001';r=read(out/'run.json');a=read(out/'audit.json');p=read(out/'pnp-review.json')
    assert r['closed'] and r['source_unchanged'] and not r['physical_access']
    assert a['integrity_passed'] and a['setupapi_history_preserved'] and a['event_history_preserved']
    result['trials'].append(dict(name=folder.name,closed=True,closed_utc=r['closed_utc'],source_unchanged=True,integrity_passed=True,pnp_started=p['pnp_started'],lifecycle_completed=p['lifecycle_completed'],normal_restart_qualified=p['normal_restart_qualified'],hardware_ready=False,do_not_relaunch=True,run_sha256=sha(out/'run.json'),audit_sha256=sha(out/'audit.json'),pnp_review_sha256=sha(out/'pnp-review.json')))
for n in range(1,4):
    folder=k/'lifecycle002';b=read(folder/f'build{n:03d}-failure.json')
    for row in b['sources']:assert sha(folder/f'failed-build{n:03d}'/row['name'])==row['sha256']
for folder in [h]+[k/f'lifecycle{n:03d}' for n in range(1,5)]:
    for directory,dirs,names in os.walk(folder):
        dirs[:]=[n for n in dirs if n not in ('artifacts','__pycache__')]
        for name in names:
            path=Path(directory)/name
            if path.suffix=='.py':ast.parse(path.read_text(encoding='utf-8-sig'),filename=str(path));result['syntax_files']+=1
result['passed']=True
dest=k/'handoff-lifecycle-review001.json';assert not dest.exists()
dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

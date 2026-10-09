"""Exact184 OFF/ON payloads with identical shared providers and exact194 helper and186 probe; no console access."""
import hashlib,json,zipfile
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'package-review.json';assert not dest.exists()
assert read(k/'capture.json')['passed'] and read(k/'binding-edit.json')['passed']
assert read(k.parent/'video-word-store184/driver-review.json')['passed']
assert read(k.parent/'video-word-store184/instruction-review.json')['passed']
assert read(k.parent/'video-word-store184/host-tests002.json')['passed']
assert read(k.parent/'video-word-order186/evidence-review.json')['passed']
providers=read(k.parent/'video-hardware-candidate158/package-review.json')['candidate'][:2]
rows={};zips={}
for case,digest in [('control001','feba078e38a187496e2904ca7de54915b57ec25224fc2bfd260bac87297bc188'),
                    ('candidate001','ac68dcc2ff6cfd27ed1580ffa17d99ff1a512b86d8cf99f8f54eef63d96a8ba8')]:
    own=k.parent/'video-word-store184'/case/'artifacts/xwnown.dll'
    assert sha(own)==digest
    rows[case]=[dict(v) for v in providers]+[dict(target='F/winnt/system32/xwnown.dll',
        source=own.relative_to(ws).as_posix(),bytes=own.stat().st_size,sha256=digest)]
    p=k/'artifacts'/('display195-'+case+'.zip');names=[]
    with zipfile.ZipFile(p,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for row in rows[case]:
            source=ws/row['source'];assert sha(source)==row['sha256'] and source.stat().st_size==row['bytes']
            z.writestr(row['target'],source.read_bytes());names.append(row['target'])
        z.writestr('F/winnt/system32/config/system',(k/'artifacts/proposed-system').read_bytes())
        names.append('F/winnt/system32/config/system')
    with zipfile.ZipFile(p) as z:
        assert z.namelist()==names
        for row in rows[case]:assert hashlib.sha256(z.read(row['target'])).hexdigest()==row['sha256']
        assert z.read(names[-1])==(k/'artifacts/proposed-system').read_bytes()
    zips[case]=dict(path=p.relative_to(ws).as_posix(),sha256=sha(p),readback_verified=True)
result=dict(passed=True,physical_launch=False,physical_qualified=False,scope=__doc__,cases=rows,
    private_archives=zips,proposal_sha256=read(k/'binding-edit.json')['after_sha256'],
    helpers={n:sha(k/'artifacts'/n) for n in ['runner.exe','gdi-probe.exe']},
    same_providers=True,display_tokens_only=True,original_baseline_preserved=True)
dest.write_text(json.dumps(result,indent=2)+'\n');print('Exact OFF/ON packages reviewed and private archives readback verified')

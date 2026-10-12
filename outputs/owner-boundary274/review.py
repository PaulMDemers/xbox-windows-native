"""Read-only closure of compiled274; no runtime qualification."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'final-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((k/n).read_text())
parent=Path('E:/Codex-archive/xbox-windows-native/lifetime273-build001/source')
basepins=json.loads((k.parent/'owned-lifetime273/renderer-source-pins001.json').read_text())
reports={};counts={};sources=[]
for attempt in ['001','002']:
    b=read('renderer-build'+attempt+'.json');assert b['passed'] and b['borrowed_sources_restored']
    assert set(b['changed_sources'])=={'hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h','hw/xbox/nv2a/pgraph/gl/texture.c'}
    art=Path('E:/Codex-archive/xbox-windows-native/boundary274-build'+attempt)
    exe=art/'xemu-boundary274.exe';assert sha(exe)==b['executable_sha256'] and exe.stat().st_size==b['executable_bytes']
    for n,h in b['inputs'].items():assert sha(art/'inputs'/n)==h
    if attempt=='002':
        for n,h in b['inputs'].items():assert sha(k/n)==h
    else:assert sha(k/'prior-build001/patch-renderer.py')==b['inputs']['patch-renderer.py']
    pins=read('renderer-source-pins'+attempt+'.json');files=[p for p in (art/'source').rglob('*') if p.is_file()]
    for p in files:assert sha(p)==pins[p.relative_to(art/'source').as_posix()]
    assert sha(k/('renderer-delta'+attempt+'.patch'))==b['delta_sha256']
    warnings=re.findall(r'warning: (.*)',(k/('renderer-build'+attempt+'.log')).read_text())
    inherited=re.findall(r'warning: (.*)',(k.parent/'owned-lifetime273/renderer-build001.log').read_text())
    assert not set(warnings)-set(inherited)
    reports[attempt]=dict(executable_sha256=sha(exe),executable_bytes=exe.stat().st_size,
        private_sources_rehashed=len(files),inputs_rehashed=len(b['inputs']),warning_instances=len(warnings),new_warning_messages=[])
    sources.append((art/'source/hw/xbox/nv2a/pgraph/gl/renderer.c').read_text())
def extract(s,name):
    m=re.search(r'(?m)^(?:static )?(?:bool|void|unsigned|char \*)\s*'+name+r'\([^)]*\)\s*\{',s);assert m,name
    n=m.end();depth=1
    while depth:depth+=(s[n]=='{')-(s[n]=='}');n+=1
    return s[m.start():n]
for name in ['x274_pending','x274_check','x274_context_match','pgraph_gl_ledger265_worker','pgraph_gl_ledger265_request','pgraph_gl_ledger265_page']:
    assert extract(sources[0],name)==extract(sources[1],name),name
one=extract(sources[0],'pgraph_gl_ledger265_report');two=extract(sources[1],'pgraph_gl_ledger265_report')
assert one!=two and sources[0].replace(one,two)==sources[1],'Build002 must change only report formatter'
art=Path('E:/Codex-archive/xbox-windows-native/boundary274-build002/source')
for name in read('renderer-build002.json')['original_sources']:
    if name not in ['hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h','hw/xbox/nv2a/pgraph/gl/texture.c']:
        assert sha(art/name)==basepins[name]
texture=(art/'hw/xbox/nv2a/pgraph/gl/texture.c').read_text()
ready=extract(texture,'pgraph_gl_reuse274_ready')+'\n'
assert texture.replace(ready,'')==(parent/'hw/xbox/nv2a/pgraph/gl/texture.c').read_text(),'Original273 watch and binder must remain exact'
verified=0
for attempt in ['001','002']:
    r=read('host-tests'+attempt+'.json');assert r['passed']
    capsule=Path('E:/Codex-archive/xbox-windows-native/boundary274-host'+attempt)
    for name,h in r['files'].items():assert sha(capsule/name)==h;verified+=1
result=dict(closed=True,builds=reports,reviewed_build='002',guest_prepared=False,guest_launched=False,
    runtime_owner_acknowledgments=False,full_reuse_qualified=False,release_installed=False,
    physical_access=False,borrowed_sources_restored=True,host_admission_context_cases=262938,
    actual_worker_model_paths=24,private_host_files_rehashed=verified,
    build002_changes_only_report=True,transaction_bodies_identical=True,
    original273_observer_and_normal_texture_source_identical=True,
    host_test_limits='CPU jobs, GL fences, locks and graph use explicit models; actual queued acknowledgments untested',
    running_sessions=[])
dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

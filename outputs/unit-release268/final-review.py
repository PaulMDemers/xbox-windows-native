import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
pins=read(k.parent/'backend-actors267/renderer-source-pins001.json')
paths={
 'hw/xbox/nv2a/pgraph/gl/texture.c':Path('E:/Codex-archive/xbox-windows-native/retirement264-source001/hw/xbox/nv2a/pgraph/gl/texture.c'),
 'hw/xbox/nv2a/nv2a.c':Path('E:/Codex-archive/xbox-windows-native/actors267-build001/source/hw/xbox/nv2a/nv2a.c'),
 'hw/xbox/nv2a/pgraph/gl/renderer.c':Path('E:/Codex-archive/xbox-windows-native/actors267-build001/source/hw/xbox/nv2a/pgraph/gl/renderer.c')}
for n,p in paths.items():assert sha(p)==pins[n],n
def function(text,name):
    m=re.search(r'(?m)^(?:static )?void '+name+r'\([^)]*\)\s*\{',text);assert m
    depth=1;end=m.end()
    while depth:depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[m.start():end]
reset=function(paths['hw/xbox/nv2a/nv2a.c'].read_text(),'nv2a_reset')
flush=function(paths['hw/xbox/nv2a/pgraph/gl/renderer.c'].read_text(),'pgraph_gl_flush')
assert 'flush_pending, true' in reset and 'pgraph_gl_mark_textures_possibly_dirty' in flush
assert 'lru_flush' not in reset+flush and 'texture_binding[' not in reset+flush
records=[]
for attempt in ['001','002','003']:
    r=read(k/('host-test'+attempt+'.json'));art=Path('E:/Codex-archive/xbox-windows-native/unit-release268-host'+attempt)
    for n,h in r['files'].items():assert sha(art/n)==h,(attempt,n)
    records.append(r)
assert records[0]['compile_exit']!=0 and records[1]['compile_exit']==0 and not records[1]['passed'] and records[2]['passed']
assert records[1]['files']['proposed-release.c']==records[2]['files']['proposed-release.c']
assert records[1]['files']['actual-functions.h']==records[2]['files']['actual-functions.h']
for n in ['test-rebind.c','release-core.h','proposed-release.c','test-host.py']:
    assert sha(k/n)==records[2]['files'][n]
assert records[2]['compile_output']=='' and 'PASS 32 original-bind/rebind cases; 28 refusal cases; 212 model uploads/deletes' in records[2]['test_output']
r=dict(passed=True,host_only=True,real_gl=False,guest_prepared=False,guest_launched=False,
    renderer_changed=False,physical_access=False,native_gpu_grant=False,ordinary_qualified=False,
    rebind_cases=32,refusal_cases=28,model_uploads=212,model_deletes=212,
    original_source_functions=records[2]['exact_function_sha256'],
    sources={n:pins[n] for n in paths},reset_sha256=hashlib.sha256(reset.encode()).hexdigest(),
    flush_sha256=hashlib.sha256(flush.encode()).hexdigest(),
    reset_retains_texture_cache_by_source=True,actual_guest_reuse_proved=False,
    earlier_failures_preserved=['001 missing model constant/warning','002 incorrect control-refcount expectation'],
    unchanged_proposed_helper_between002and003=True,all_owned_processes_closed=True,
    next='New generation-aware read-only guest reuse control, without release helper; actual source bytes/readback and full cold audit',
    prior267_scoped_pass=True,prior267_strict_failure='Ftdisk49',
    inputs={p.name:sha(p) for p in k.iterdir() if p.is_file()})
dest=k/'final-review.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

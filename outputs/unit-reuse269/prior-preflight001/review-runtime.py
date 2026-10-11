"""Freeze unique269 runtime only after source, lifetime and transport review."""
import ast,hashlib,importlib.util,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];parent=k.parent/'backend-actors267'
read=lambda p:json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert not (k/'runtime-review.json').exists() and not (k/'emulator-frozen.json').exists()
frozen=read(parent/'emulator-frozen.json')
for n,h in frozen.items():assert sha(ws/n)==h,n
assert read(parent/'emu001/host-state.json')['closed']
for name in ['common.py','atomic_json.py','kernel-discovery.py','close-host.py','typed-state.py','runtime-dependencies.py','attest.py','attestation-inputs001.json','analyze-base.py','analyze-extra.py','analyze-ledger.py']:
    assert (k/name).read_bytes()==(parent/name).read_bytes(),name
for name in ['Invoke.ps1','audit.py','trace.py']:
    expected=(parent/name).read_text().replace('backend-actors267','unit-reuse269').replace('/actors267/','/reuse269/').replace('nt5-actors267','nt5-reuse269').replace('windows-native-actors267','windows-native-reuse269')
    assert (k/name).read_text()==expected,name
b=read(k/'renderer-build004.json');assert b['passed'] and b['borrowed_sources_restored']
assert read(k/'parser-tests001.json')['passed'] and read(k/'seal-tests002.json')['passed']
assert not read(k/'seal-tests001.json')['passed']
assert read(k/'seal-tests002.json')['watch_sha256']==sha(k/'watch.c')
art=Path('E:/Codex-archive/xbox-windows-native/reuse269-build004');exe=art/'xemu-reuse269.exe'
assert sha(exe)==b['executable_sha256']
pins=read(k/'renderer-source-pins004.json');old=read(parent/'renderer-source-pins001.json')
changed={n for n in old if old[n]!=pins[n]};assert changed==set(b['changed_sources'])
assert changed=={'hw/xbox/nv2a/pgraph/gl/texture.c','hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h'}
for n in b['original_sources']:assert sha(art/'source'/n)==pins[n],n
for n,h in b['inputs'].items():assert sha(k/n)==sha(art/'inputs'/n)==h,n
oldtexture=Path('E:/Codex-archive/xbox-windows-native/retirement264-source001/hw/xbox/nv2a/pgraph/gl/texture.c').read_text()
new=(art/'source/hw/xbox/nv2a/pgraph/gl/texture.c').read_text()
restored=new.replace((k/'watch.c').read_text()+'\n','',1)
for line in ['                x269_bound(d,i,r->texture_binding[i],1);\n','        x269_bound(d,i,binding,2);\n','    x269_destroying(binding);\n']:
    assert restored.count(line)==1;restored=restored.replace(line,'',1)
assert restored==oldtexture,'Original complete texture source reconstructed'
watch=(k/'watch.c').read_text()
assert not any(s in watch for s in ['texture_binding_destroy(', 'glDelete', 'glGen', 'glTexImage', 'glDraw', 'glClear', 'refcnt--', 'refcnt++'])
priorlog=(parent/'renderer-build001.log').read_text(errors='replace');log=(k/'renderer-build004.log').read_text(errors='replace')
warnings=lambda t:set(re.findall(r'warning: (.*)',t))
assert not (warnings(log)-warnings(priorlog)),warnings(log)-warnings(priorlog)
assert 'error:' not in log
f=read(k/'emu001/fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']==read(parent/'emu001/fixture.json')['fixture_sha256']
assert read(k/'emu001/before/allocation.json')['allocation_consistent']
for n in ['system','software','default','sam','security']:assert sha(k/'emu001/artifacts'/('before-'+n))==sha(parent/'emu001/artifacts'/('before-'+n))
watchdir=Path(read(k/'emu001/watch-location.json')['path']);assert watchdir.is_dir() and not list(watchdir.iterdir())
assert str(exe).replace('\\','/') in (k/'Run.ps1').read_text() and b['executable_sha256'] in (k/'Run.ps1').read_text()
for p in k.glob('*.py'):ast.parse(p.read_text())
sp=importlib.util.spec_from_file_location('deps269',k/'runtime-dependencies.py');d=importlib.util.module_from_spec(sp);sp.loader.exec_module(d)
host=d.inventory();(k/'host-dependencies.json').write_text(json.dumps(dict(files=host,physical_access=False),indent=2)+'\n')
r=dict(passed=True,guest_launched=False,physical_access=False,debugger=True,ordinary_qualified=False,
    original_complete_texture_source_reconstructed=True,changed_sources=sorted(changed),host_dependencies=len(host),probe_driver_unchanged=True,
    warning_instances=len(re.findall('warning:',log)),new_warning_messages=[],
    scoped_test='Actual normal guest binding reuse of four original generations, independent source and RGBA equality',
    observer_seal='One atomic closed/active gate;4096 exact-function host races pass; failed two-variable predecessor retained',
    limitations=['No per-call GL/filesystem deadline; outer owned-run watchdog','Post-resume double source sampling cannot exclude arbitrary CPU ABA writes','No final-frame visual correctness'],
    release_installed=False,retirement_ready=False,native_gpu_grant=False)
(k/'runtime-review.json').write_text(json.dumps(r,indent=2)+'\n')
for p in k.iterdir():
    if p.is_file() and p.suffix in ['.py','.ps1','.json','.c','.h','.md']:frozen[p.relative_to(ws).as_posix()]=sha(p)
for n in ['fixture.json','watch-location.json']:frozen[(k/'emu001'/n).relative_to(ws).as_posix()]=sha(k/'emu001'/n)
(k/'emulator-frozen.json').write_text(json.dumps(frozen,indent=2)+'\n')
print('269 runtime preflight PASS;',len(frozen),'frozen inputs')

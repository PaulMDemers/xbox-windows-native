"""Review fresh telemetry-only model and actual host-test pins before freeze."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'prelaunch-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(k/'build001.json');assert b['passed'] and b['borrowed_sources_restored']
assert sorted(b['changed_sources'])==sorted(['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/renderer.c'])
pins=read(k/'candidate001-source-pins.json');old=read(k.parent/'xemu-backend-reason228/candidate002-source-pins.json')
for p in (k/'artifacts/build001/source').rglob('*'):
    if p.is_file():assert sha(p)==pins[str(p.relative_to(k/'artifacts/build001/source')).replace('\\','/')]
assert sha(k/'artifacts/build001/xemu-preserve227.exe')==b['executable_sha256']
for n in ['hw/xbox/nv2a/pfifo.c','hw/xbox/nv2a/pgraph/gl/surface.c','include/qemu/atomic.h','include/qemu/compiler.h']:
    assert pins[n]==old[n]
t=read(k/'publication-test003.json');assert t['passed'] and len(t['runs'])==2
assert t['source_sha256']==sha(k/'test-publication.py') and t['test_sha256']==sha(k/'test-publication.c')
for run in t['runs']:
    assert run['exit_code']==0 and not run['stderr']
    assert 'concurrent_pairs=100000 publication_pairs=10000' in run['stdout']
assert read(k/'guard-test001.json')['passed']
assert not (k/'trace001/runner-start.json').exists()
f=read(k/'fixture-trace001.json');assert f['prepared'] and not f['inherited_null_policy'] and sha(Path(f['fixture_path_windows']))==f['seed_sha256']
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
source=(k/'artifacts/build001/source/hw/xbox/nv2a/nv2a.c').read_text()
assert 'bool published = state == 3 || state == 4 || state == 6;' in source
assert 'qatomic_store_release(&d->preserve227.state, result)' in source
assert 'qatomic_load_acquire(&d->preserve227.state)' in source
dest.write_text(json.dumps(dict(passed=True,build_sha256=sha(k/'build001.json'),executable_sha256=b['executable_sha256'],host_tests_sha256=sha(k/'publication-test003.json'),source_manifest_sha256=sha(k/'candidate001-source-pins.json'),no_pusher_or_surface_predicate_change=True,physical_access=False,guest_launched=False,scope='Telemetry and publication only; no GPU preservation, consuming drain or ownership qualification'),indent=2)+'\n')
print('231 fresh telemetry/build/host tests/prepared fixture reviewed')

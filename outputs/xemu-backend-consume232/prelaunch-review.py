"""Review exact bounded model/host adapters and immutable fresh fixture."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'prelaunch-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(k/'build001.json');assert b['passed'] and b['borrowed_sources_restored']
assert sorted(b['changed_sources'])==sorted(['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pfifo.c'])
assert b['source_sha256']==sha(k/'build.py') and b['patch_generator_sha256']==sha(k/'patch.py')
assert sha(k/'artifacts/build001/xemu-preserve227.exe')==b['executable_sha256']
pins=read(k/'candidate001-source-pins.json');old=read(k.parent/'xemu-backend-publication231/candidate001-source-pins.json')
for p in (k/'artifacts/build001/source').rglob('*'):
    if p.is_file():assert sha(p)==pins[str(p.relative_to(k/'artifacts/build001/source')).replace('\\','/')]
for n in ['hw/xbox/nv2a/pgraph/gl/surface.c','include/qemu/atomic.h','include/qemu/compiler.h']:
    assert pins[n]==old[n]
for name,test,csource in [('consume-test001.json','test-consume.c','test-consume.py'),('publication-test001.json','test-publication.c','test-publication.py')]:
    t=read(k/name);assert t['passed'] and len(t['runs'])==2
    assert t['test_sha256']==sha(k/test) and t['source_sha256']==sha(k/csource)
    assert all(v['exit_code']==0 and not v['stderr'] for v in t['runs'])
assert read(k/'guard-test001.json')['passed']
assert not (k/'trace001/runner-start.json').exists()
f=read(k/'fixture-trace001.json');assert f['prepared'] and not f['inherited_null_policy'] and sha(Path(f['fixture_path_windows']))==f['seed_sha256']
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
s=(k/'artifacts/build001/source/hw/xbox/nv2a/pfifo.c').read_text()
assert 'pfifo_run_pusher(d, NULL);' in s and '.steps_left = 32768, .words_left = 32768' in s
assert 'MIN(num_words_available, budget->words_left)' in s
assert 'if (budget && !pfifo_budget232(d, budget))' in s
assert 'if not r[\'reserved_bytes_unchanged\']:quarantined=True' in (k/'trace.py').read_text()
dest.write_text(json.dumps(dict(passed=True,build_sha256=sha(k/'build001.json'),executable_sha256=b['executable_sha256'],source_manifest_sha256=sha(k/'candidate001-source-pins.json'),actual_parser_host_tests_passed=True,ordinary_calls_null_budget=True,surface_predicates_unchanged=True,guest_launched=False,physical_access=False,scope='Bounded opt-in actual consumer; host adapter checks and publication only, no GPU/ownership qualification'),indent=2)+'\n')
print('232 bounded source/host tests/fresh fixture review PASS')

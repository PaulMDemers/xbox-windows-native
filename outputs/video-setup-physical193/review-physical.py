"""Freeze fresh physical193 protocol and exact184/186 inputs; hardware results remain unqualified."""
import ast,hashlib,importlib.util,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
dest=k/'physical-ready.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
capture=read(k/'capture.json');package=read(k/'package-review.json');tests=read(k/'protocol-tests.json')
assert capture['passed'] and capture['current_rollback']['readback_verified'] and package['passed'] and tests['passed'] and not tests['physical_access']
for name,digest in tests['source_pins'].items():assert sha(k/name)==digest
assert read(k/'binding-edit.json')['only_two_expected_values_changed']
assert next(v['sha256'] for v in capture['files'] if v['path'].endswith('/win32k.sys'))==read(k.parent/'video-word-store184/driver-review.json')['provider_sha256']
build=read(k.parent/'video-word-order186/build-review.json');assert build['passed']
runner_build=read(k.parent/'video-setup-preflight190/build-review.json');assert runner_build['passed']
assert sha(k/'artifacts/runner.exe')==package['helpers']['runner.exe']==runner_build['binary_sha256']
assert sha(k/'artifacts/gdi-probe.exe')==package['helpers']['gdi-probe.exe']==build['binaries']['gdi-probe.exe']['sha256']
assert read(k.parent/'video-setup-fresh192/evidence-review.json')['passed']
assert read(k.parent/'video-setup-runtime191/idle001/audit.json')['diagnostic_usable']
for name in ['runner.c','restart_gate.h','setup_gate.h']:
    assert (k/name).read_bytes()==(k.parent/'video-setup-preflight190'/name).read_bytes()
assert (k/'gdi-probe.c').read_bytes()==(k.parent/'video-word-order186/gdi-probe.c').read_bytes()
fields=['source','event_id','type','strings','data_hex'];sig=lambda v:{f:v[f] for f in fields}
expected=read(k.parent/'video-word-order186/control001/audit.json')['warnings_errors']
assert len(expected)==1 and expected[0]['source']=='Ftdisk' and expected[0]['event_id']==49
old=read(k.parent/'video-paired-timing166/control001/physical-audit.json');assert [sig(v) for v in old['warnings_errors']]==[sig(v) for v in expected]
inputs=[k/'creation.json',k/'capture.json',k/'binding-review.json',k/'binding-edit.json',k/'package-review.json',k/'protocol-tests.json',
    k.parent/'video-word-store184/driver-review.json',k.parent/'video-word-store184/instruction-review.json',
    k.parent/'video-word-store184/host-tests002.json',k.parent/'video-word-order186/evidence-review.json',
    k.parent/'video-word-order186/order-comparison.json',k.parent/'video-word-order186/build-review.json',
    k.parent/'video-paired-timing166/control001/physical-audit.json',k/'artifacts/proposed-system']
for case in ['control001','candidate001']:
    a=read(k.parent/'video-word-order186'/case/'audit.json')
    assert a['workload_passed'] and a['integrity_passed'] and not a['strict_qualification_passed']
    assert read(k.parent/'video-word-order186'/case/'closure.json')['closed']
    assert [sig(v) for v in a['warnings_errors']]==[sig(v) for v in expected] and not a['new_events']['application']
    assert a['actual_caps']==old['actual_caps'] and a['actual_modes']==old['actual_modes']
    sys.argv=['physical-controller.py','inspect',case]
    spec=importlib.util.spec_from_file_location('review_'+case,k/'physical-controller.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
    assert len(c.changes)==3 and c.namespace==('xwnpre193a' if case=='control001' else 'xwnpre193b')
    assert c.rollback_dir==('xwn-display193a' if case=='control001' else 'xwn-display193b')
    assert not c.record.exists() and not c.art.exists()
    assert c.test_startup==('@echo off\r\nC:\\'+c.namespace+'\\runner.exe\r\nexit\r\n').encode('ascii')
    inputs += [k.parent/'video-word-order186'/case/n for n in ['audit.json','closure.json']]
    inputs += [ws/v['source'] for v in package['cases'][case]]
inputs += [k/'artifacts'/n for n in package['helpers']]
inputs += [k.parent/'video-setup-preflight190/build-review.json',k.parent/'video-setup-fresh192/evidence-review.json',k.parent/'video-setup-fresh192/pending001/audit.json',k.parent/'video-setup-runtime191/idle001/audit.json']
sources=sorted(p for p in k.iterdir() if p.suffix in ['.py','.c','.h'])
for p in sources:
    if p.suffix=='.py':ast.parse(p.read_text())
result=dict(prepared=True,scope=__doc__,physical_launch_performed=False,release_qualified=False,
    source_pins={p.name:sha(p) for p in sources},input_pins={p.relative_to(ws).as_posix():sha(p) for p in inputs},
    control_before_candidate=True,single_launch_per_case=True,current_capture_only=True,
    source_review=['Both cases use same physical-tested shared miniport/bootvideo and same proposal; only184 scalar flag changes',
    'Actual installed win32k matches reviewed184 imports; exact186v8 probe/178 guarded runner copied without build',
    'Private readback-verified rollback and console copy precede driver/hive edits; startup LAST/FIRST',
    'Partial collection evidence retained; finally restores baseline; no recollection of restored failure',
    'Candidate requires complete scoped control, ten valid hive snapshots, unchanged policy, exact inherited event and restored baseline',
    'Unknown introduced file is never deleted; uncertain launch never repeated',
    'No physical device-policy, cache, storage, crash-dump, service or mode settings edits'],
    expected_inherited_errors=[sig(v) for v in expected],strict_error_waiver=False,
    full_physical_storage_audit=False,physical_or_release_promotion=False)
dest.write_text(json.dumps(result,indent=2)+'\n');print('Fresh physical193 protocol/input pins frozen; no console write or launch')

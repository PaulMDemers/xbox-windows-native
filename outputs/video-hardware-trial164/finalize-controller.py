"""Finish controller eligibility with exact165/control event pairing before any hardware write."""
import ast,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];p=k/'physical-controller.py'
original=p.read_bytes();backup=k/'physical-controller-initial.py';assert not backup.exists();backup.write_bytes(original)
s=original.decode('utf-8');needle="    assert not r['strict_qualification_passed']"
assert s.count(needle)==1
s=s.replace(needle,needle+"\n    control=read(k.parent/'video-physical-rehearsal162/control001/audit.json')\n    fields=['source','event_id','type','strings','data_hex']\n    assert len(control['warnings_errors'])==1 and all(r['warnings_errors'][0][f]==control['warnings_errors'][0][f] for f in fields)\n    assert r['copy_checks_passed'] and r['loop_coverage'] and r['normal_shutdown_count']==1")
ast.parse(s);p.write_text(s,encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((k/'controller-source-review.json').read_text(encoding='utf-8'))
(k/'controller-initial-review.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
review.update(controller_sha256=sha(p),previous_controller_sha256=sha(backup),
    exact_control_event_signature_required=True,explicit_copy_loop_shutdown_gates=True,physical_access=False)
(k/'controller-source-review.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
a=json.loads((k.parent/'video-helper-runtime165/candidate001/audit.json').read_text(encoding='utf-8'))
assert a['workload_passed'] and a['integrity_passed'] and not a['strict_qualification_passed']
(k/'hardware-diagnostic-ready.json').write_text(json.dumps(dict(diagnostic_preparation_complete=True,physical_access=False,
    physical_deployment_performed=False,physical_qualified=False,strict_release_ready=False,
    helper_runtime='video-helper-runtime165/candidate001',helper_audit_sha256=sha(k.parent/'video-helper-runtime165/candidate001/audit.json'),
    controller_sha256=sha(p),runner_sha256=sha(k/'artifacts/runner.exe'),
    pending='User-reported unplugged Razer keyboard and UnleashX state, then controller rechecks all actual baseline hashes before ONE launch',
    restoration='Original display files and SYSTEM restored after preserving results; normal startup restored first'),indent=2)+'\n',encoding='utf-8')
print('Concrete one-shot hardware diagnostic prepared; no physical deployment')

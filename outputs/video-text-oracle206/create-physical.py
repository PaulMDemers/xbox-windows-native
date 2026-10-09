"""Prepare fresh206 physical protocol only; same validated new probe/driver binaries."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-unattended202'
assert not (k/'physical-controller.py').exists()
for name in ['capture.py','capture-probe-providers.py','review.py','edit-binding.py','prepare-package.py','prepare-physical.py',
             'physical-controller.py','watch-physical.py','finish-physical.py','audit-physical.py','audit-physical-hives.py','verify-restored.py','close-case.py']:
 s=(old/name).read_text(encoding='utf-8').replace('video-unattended202','video-text-oracle206').replace('xwnpre202a','xwntxt206a').replace('xwnpre202b','xwntxt206b').replace('display202','display206').replace('rollback202','rollback206')
 s=s.replace("'gdi-probe.exe'","'replay.exe'")
 if name=='capture-probe-providers.py':s=s.replace("k.parent/'video-phase-runtime199/build-review.json'","k/'build-review.json'")
 if name=='prepare-package.py':
  s=s.replace("video-phase-profile198/driver-review.json","video-text-clip205/build-review.json").replace("video-phase-profile198/host-tests.json","video-text-bounds203/host-tests.json")
  s=s.replace("for case,digest in [('control001','144269d9d557026bd1bc34157c4b9436cee648922493982235c7b5af0b5cec4b'),\n                    ('candidate001','db8aa1debd131b2e8106b77fe4cc96655b08e4d08a570654aa8911b7febcd04f')]:", "for case in ['control001','candidate001']:\n    digest=read(k.parent/'video-text-clip205/build-review.json')['cases'][case]['sha256']")
  s=s.replace("k.parent/'video-phase-profile198'/case", "k.parent/'video-text-clip205'/case")
 if name=='prepare-physical.py':
  s=s.replace("assert read(k/name)['passed'],name", "assert read(k/name)['passed'],name")
  s=s.replace("prior=k.parent/", "assert read(k/'emulator-pair-review.json')['optimization_demonstrated']\nprior=k.parent/",1)
 if name=='audit-physical.py':
  s=s.replace('from window_analysis import window','from window_analysis import window\nfrom text_analysis import analyze as text_analyze')
  s=s.replace("timing(v,int(case=='candidate001'))",'timing(v,0)').replace("window(v,int(case=='candidate001'))",'window(v,0)')
  s=s.replace("windows=[window(v,0) for v in logs]", "windows=[window(v,0) for v in logs]\ntexts=[text_analyze(v,int(case=='candidate001')) for v in logs]")
  s=s.replace("phase_coverage_passed=", "text_samples=texts,text_coverage_passed=all(v['passed'] for v in texts),\n    phase_coverage_passed=",1)
  s=s.replace("'window_coverage_passed','normal_restart_requested'", "'window_coverage_passed','text_coverage_passed','normal_restart_requested'")
 for phrase in ['Exact198 profile OFF/ON payloads','Two one-shot physical profile OFF/ON display observations']:
  s=s.replace(phrase,'Exact205 text bounds OFF/ON with actual clip metadata')
 (k/name).write_text(s,encoding='utf-8',newline='\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(k/'creation.json').write_text(json.dumps(dict(passed=True,physical_access=False,physical_launch=False,runner_sha256=sha(k/'artifacts/runner.exe'),probe_sha256=sha(k/'artifacts/replay.exe'),wizard_sha256=sha(k/'artifacts/wizard.exe'),limits='New206 strict text/clip/byte protocol with identical202 joined runner/201helper194 guards. No physical launch.'),indent=2)+'\n')
print('Fresh206 physical capture/proposal/rollback protocol prepared; no access/launch')

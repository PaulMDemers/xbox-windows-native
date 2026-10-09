"""Fresh209 scalar siblings using exact closed206 binaries and unchanged gates."""
import ast, hashlib, json, shutil
from pathlib import Path
k=Path(__file__).resolve().parent; ws=k.parents[1]; old=k.parent/'video-text-oracle206'
assert not (k/'common.py').exists()
names=['common.py','Run.ps1','supervise-emulator.py','typed-state.py','audit-emulator.py','prepare-emulator.py',
 'runner_analysis.py','boundary_analysis.py','interval_policy.py','sample_analysis.py','dib_analysis.py',
 'timing_analysis.py','window_analysis.py','text_analysis.py','review-build.py','test-parser.py',
 'capture.py','capture-probe-providers.py','review.py','edit-binding.py','prepare-package.py','prepare-physical.py',
 'physical-controller.py','watch-physical.py','finish-physical.py','audit-physical.py','audit-physical-hives.py',
 'verify-restored.py','close-case.py','gdi-probe.c','text-cases.c']
for name in names:
 s=(old/name).read_text(encoding='utf-8')
 s=s.replace('video-text-oracle206','video-scalar-runtime209').replace('video-text-clip205','video-scalar208')
 s=s.replace('xwntxt206','xwnuc209').replace('text206','scalar209').replace('display206','display209').replace('rollback206','rollback209')
 if name=='review-build.py':
  s=s.replace("only_driver_definition_difference='XWN_TEXT_BOUNDS'", "only_driver_definition_difference='XWN_UC_STORES'")
  s=s.replace('Actual204','Exact reused206').replace('new117 pair','scalar208 pair')
 if name=='audit-emulator.py':
  s=s.replace('dib(v,0)','dib(v,int(case==\'candidate001\'))')
  s=s.replace("text_analysis(v,int(case=='candidate001'))",'text_analysis(v,0)')
 if name=='audit-physical.py':
  s=s.replace('rows_analyze(v,0)',"rows_analyze(v,int(case=='candidate001'))")
  s=s.replace("text_analyze(v,int(case=='candidate001'))",'text_analyze(v,0)')
  s=s.replace('Profile OFF/ON synchronous GDI plus actual window observation, scalar OFF both', 'Scalar stores OFF/ON synchronous GDI plus actual window observation, text bounds and clocks OFF both')
 if name=='prepare-package.py':
  s=s.replace('Exact205 text bounds OFF/ON with actual clip metadata, scalar OFF both','Exact208 scalar UC stores OFF/ON with118 metadata, text bounds and clocks OFF both')
  s=s.replace("assert read(k.parent/'video-text-bounds203/host-tests.json')['passed']", "assert read(k.parent/'video-word-store184/host-tests002.json')['passed']\nassert read(k.parent/'video-scalar208/instruction-review.json')['passed']")
 if name=='prepare-physical.py':
  s=s.replace("assert read(k/'emulator-pair-review.json')['optimization_demonstrated']", "assert read(k/'emulator-pair-review.json')['actual_scalar_coverage_passed']")
  s=s.replace('Same198 profileOFF/ON display providers/scalarOFF, exact199 probe', 'Only208 scalar UC stores OFF/ON; clocks/text bounds OFF both, exact206 v11 probe')
 if name=='physical-controller.py':
  s=s.replace("k/'artifacts/gdi-probe.exe'", "k/'artifacts/replay.exe'")
  s=s.replace('Exact205 text bounds OFF/ON with actual clip metadata, scalar OFF both', 'Exact208 scalar UC stores OFF/ON, clocks and text bounds OFF both')
  # Preflight every local helper before opening a connection or creating evidence.
  s=s.replace("ready();assert not record.exists();art.mkdir", "ready();assert all((k/'artifacts'/n).is_file() for n in package['helpers']);assert not record.exists();art.mkdir")
 if name=='Run.ps1':
  marker="@{utc=[DateTime]::UtcNow.ToString('o');pid=$PID;"
  start=s.index(marker); end=s.index('\n',start)
  line=s[start:end]; s=s[:start]+s[end+1:]
  s=s.replace("-Resource build -Action {\n", "-Resource build -Action {\n "+line+'\n',1)
 if name.endswith('.py'): ast.parse(s)
 (k/name).write_text(s,encoding='utf-8',newline='\n')
(k/'artifacts').mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['runner.exe','replay.exe','wizard.exe']:
 shutil.copyfile(old/'artifacts'/name,k/'artifacts'/name)
 assert sha(k/'artifacts'/name)==sha(old/'artifacts'/name)
shutil.copyfile(old/'probe-build001.json',k/'probe-build001.json')
(k/'creation.json').write_text(json.dumps(dict(passed=True,physical_access=False,physical_launch=False,
 runner_sha256=sha(k/'artifacts/runner.exe'),probe_sha256=sha(k/'artifacts/replay.exe'),wizard_sha256=sha(k/'artifacts/wizard.exe'),
 reused_probe_build_report_sha256=sha(old/'probe-build001.json'),
 exact_reused_source={n:sha(old/n) for n in ['gdi-probe.c','text-cases.c']},
 limits='Fresh209 namespaces; exact206 v11 binary/source reused, not recompiled. Scalar208 is the only paired driver flag difference. Historical206 never altered or repeated.'),indent=2)+'\n')
(k/'DESIGN.md').write_text('''# Scalar hardware discriminator209

Only UC stores differ between fresh208 driver siblings. Exact206 v11 probe and
202 joined runner/201 helper are reused byte-for-byte. Text bounds and body clocks
stay OFF both. Independent115 row parser requires actual fast rows/bytes in every
eligible candidate case and timed upload interval, and zero in control.118 text
oracle expects bounds OFF both. Keep full pixel/clip/ownership/measurement idle,
SetupAPI bookends, typed policy/cold integrity and strict event gates.

All namespaces and run IDs are fresh. Collect physical startup FIRST; preserve
before/after evidence and restore original0093 display/SYSTEM in finally. Local
replay.exe is preflighted directly, without the old206 alias mistake. Known Ft49
remains strict failure; scoped display results cannot establish storage/release.

Report raw five samples, per-operation elapsed times, fast coverage and unchanged
readback discriminator. Control-first order/background activity are limitations.
No desktop FPS or overall dragging claim from global window counters.
''',encoding='utf-8')
print('Fresh209 scalar protocol/source and exact206 binaries prepared; no launch')

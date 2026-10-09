"""Fresh ordinary matched113 children, no physical access or reused case."""
import ast,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-hook-counters167';driver=k.parent/'video-body-timing170'
assert not (k/'Run.ps1').exists();assert json.loads((driver/'driver-review.json').read_text())['passed']
for name in ['common.py','prepare.py','preflight.py','audit.py','supervise.py','check-leases.ps1','Run.ps1','freeze.py','close-emulator.py']:
 text=(old/name).read_text().replace('video-hook-counters167','video-body-runtime171').replace('vhooks167','vbody171').replace('xwnvh167','xwnvt171')
 text=text.replace("['candidate001']","['control001','candidate001']")
 if name=='prepare.py':
  text=text.replace("('fixture-'+case+'.json'))","('fixture-candidate001.json'))",1)
  needle="startup=b'@echo off"
  at=text.index(needle)
  addition="payload=k.parent/'video-body-timing170'/case/'artifacts/xwnown.dll'\nm.replace(w,'winnt/system32/xwnown.dll',payload.read_bytes());files['F/winnt/system32/xwnown.dll']=sha(payload)\n"
  text=text[:at]+addition+text[at:]
 if name=='preflight.py':
  text=text.replace("('proposed-system' if case=='candidate001' else 'F/winnt/system32/config/system')","'proposed-system'")
  text=text.replace("'xwnown' if case=='candidate001' else 'framebuf'","'xwnown'")
 if name=='audit.py':
  text=text.replace('from sample_analysis import analyze','from sample_analysis import analyze\nfrom timing_analysis import timing')
  text=text.replace("r['probe_passed']=", "r['profiles']=[timing(r.get('sample%d/gdi-baseline.txt'%i),int(case=='candidate001')) for i in range(5)]\nr['profile_contract_passed']=all(v['passed'] for v in r['profiles'])\nr['probe_passed']=",1)
  text=text.replace("r['workload_passed']=r['caps_consistent']","r['workload_passed']=r['profile_contract_passed'] and r['caps_consistent']")
  text=text.replace('Generic v3 guest live checks','v5 independently expected black/white/pattern pixels and version113 calibration/snapshots')
 if name=='Run.ps1':
  text=text.replace("[ValidateSet('candidate001')]","[ValidateSet('control001','candidate001')]")
  text=text.replace("'../video-physical-rehearsal162/control001/audit.json'","'control001/audit.json'")
 if name=='freeze.py':
  marker="    save(dest,{str(p.relative_to(ws)).replace('\\\\','/'):sha(p) for p in paths})"
  assert marker in text
  text=text.replace(marker,"    paths += [k.parent/'video-body-timing170'/v for v in ['driver-review.json','build-report.json','source-review.json','0113-body-timing.patch','host-tests.json']]\n    paths += list((k.parent/'video-body-timing170/display').iterdir())\n    paths += [k.parent/'video-body-timing170'/case/'artifacts/xwnown.dll' for case in ['control001','candidate001']]\n"+marker)
 ast.parse(text) if name.endswith('.py') else None
 (k/name).write_bytes(text.encode())
(k/'artifacts').mkdir(exist_ok=False)
for name in ['runner.exe','gdi-probe.exe']:shutil.copyfile(driver/'artifacts'/name,k/'artifacts'/name)
for name in ['gdi-probe.c','sample_analysis.py','build-review.json']:shutil.copyfile(driver/name,k/name)
print('Fresh ordinary controlOFF/candidateON kit, physical unchanged')

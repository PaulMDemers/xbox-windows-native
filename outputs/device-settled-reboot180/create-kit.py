"""Independent no-action subsequent boot from179's normally shut down state."""
import ast,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'device-unused-package179';assert not (k/'Run.ps1').exists()
for n in ['atomic_json.py','audit.py','check-leases.ps1','close-emulator.py','common.py','preflight.py','Run.ps1','sample_analysis.py','timing-interface.json','sites.json','freeze.py','supervise.py','inventory-devices.py','audit-package.py']:
 s=(old/n).read_text().replace('device-unused-package179','device-settled-reboot180').replace('unused179','settled180').replace('xwnup179','xwnsr180')
 # The already installed INF retains179 identity and bytes. It is not reinstalled.
 s=s.replace('xwnsettled180.inf','xwnunused179.inf')
 if n=='preflight.py':
  start=s.index("    expected=k.parent/");end=s.index("    for p in",start)
  s=s[:start]+"    expected=k.parent/'device-unused-package179/candidate001/artifacts/after-system'\n    assert actual==expected.read_bytes()\n    assert rr['F'].read('winnt/system32/config/software')==(k.parent/'device-unused-package179/candidate001/artifacts/after-software').read_bytes()\n"+s[end:]
  s=s.replace('physical_device_policy_preserved=True','inherited_explicit_unused_policy=True,physical_device_policy_preserved=False')
 if n=='freeze.py':s=s.replace('Ordinary unused-device package configuration diagnostic; no debugger or physical access','Independent ordinary subsequent boot; inherited explicit179 unused policy, no new setup or UI action')
 if n=='audit-package.py':s=s.replace('Subsequent no-action boot not yet validated.','This new subsequent boot has no installer helper, INF restaging or UI action.')
 if n.endswith('.py'):ast.parse(s)
 (k/n).write_text(s)
for n in ['gdi-probe.c','runner.c','restart_gate.h','test-gate.c','xwnunused179.inf']:shutil.copyfile(old/n,k/n)
(k/'artifacts').mkdir(exist_ok=False)
for p in (old/'artifacts').iterdir():
 if p.is_file():shutil.copyfile(p,k/'artifacts'/p.name)
sites=json.loads((k/'sites.json').read_text())
for name,row in sites['binaries'].items():
 if (k/'artifacts'/name).exists():row['path']='outputs/device-settled-reboot180/artifacts/'+name
(k/'sites.json').write_text(json.dumps(sites,indent=2)+'\n')
print('Fresh180 independent subsequent boot kit; no setup actions or binary change')

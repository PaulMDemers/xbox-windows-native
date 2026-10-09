"""Fresh sibling subsequent boot; preserve failed180 and use portable copied-parent metadata."""
import ast,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'device-settled-reboot180';assert not (k/'Run.ps1').exists()
assert json.loads((old/'candidate001/host-closure.json').read_text())['closed']
for n in ['atomic_json.py','audit.py','check-leases.ps1','close-emulator.py','common.py','preflight.py','prepare.py','Run.ps1','sample_analysis.py','timing-interface.json','sites.json','freeze.py','supervise.py','inventory-devices.py','audit-package.py','review-inputs.py']:
 s=(old/n).read_text().replace('device-settled-reboot180','device-settled-reboot181').replace('settled180','settled181').replace('xwnsr180','xwnsr181')
 if n=='prepare.py':
  s=s.replace("backing=Path(chain[1]['filename']).resolve()","backing=Path(chain[1]['filename']).resolve()\nassert backing.parent==parent.parent, 'Portable copy must share backing directory'\nassert all(not v.get('backing-filename','').startswith('/') for v in chain), 'Source has POSIX-absolute stored backing path'")
  s=s.replace("'-b',str(backing),str(parent)","'-b',backing.name,str(parent)")
  s=s.replace("assert sha(source)==original","assert sha(source)==original\nportable=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(parent)]))\nassert all(not v.get('backing-filename','').startswith('/') for v in portable)\nsave(k/'backing-portability.json',dict(passed=True,stored_backings=[v.get('backing-filename') for v in portable],copied_parent_backing=backing.name,same_directory_verified=True,virtual_disk_compare_passed=True,source_sha256_unchanged=original))")
  assert "'-b',backing.name,str(parent)" in s
 if n.endswith('.py'):ast.parse(s)
 (k/n).write_text(s)
for n in ['gdi-probe.c','runner.c','restart_gate.h','test-gate.c','xwnunused179.inf']:shutil.copyfile(old/n,k/n)
(k/'artifacts').mkdir(exist_ok=False)
for p in (old/'artifacts').iterdir():
 if p.is_file():shutil.copyfile(p,k/'artifacts'/p.name)
sites=json.loads((k/'sites.json').read_text())
for name,row in sites['binaries'].items():
 if (k/'artifacts'/name).exists():row['path']='outputs/device-settled-reboot181/artifacts/'+name
(k/'sites.json').write_text(json.dumps(sites,indent=2)+'\n')
print('New181 portable backing copy; failed180 unchanged, same guest sources/binaries/configuration')

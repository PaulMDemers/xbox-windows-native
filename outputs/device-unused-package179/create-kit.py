"""Create a fresh explicitly scoped unused-device configuration diagnostic."""
import ast,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-restart-guard178'
assert not (k/'Run.ps1').exists()
names=['atomic_json.py','audit.py','check-leases.ps1','close-emulator.py','common.py','gdi-probe.c','runner.c','restart_gate.h','test-gate.c',
       'preflight.py','prepare.py','Run.ps1','sample_analysis.py','timing-interface.json','sites.json','freeze.py','supervise.py','inventory-devices.py']
for n in names:
 s=(old/n).read_text(encoding='utf-8').replace('video-restart-guard178','device-unused-package179').replace('vguard178','unused179').replace('xwnvg178','xwnup179')
 if n=='prepare.py':
  s=s.replace("w.flush()\nwith ColdIO(target)","w.write('winnt/inf/xwnunused179.inf',(k/'xwnunused179.inf').read_bytes());files['F/winnt/inf/xwnunused179.inf']=sha(k/'xwnunused179.inf');w.flush()\nwith ColdIO(target)")
  assert "w.write('winnt/inf/xwnunused179.inf'" in s
 if n=='freeze.py':
  s=s.replace("k/'Build-host-refused001.txt'","k/'xwnunused179.inf',k/'runner.c',k/'test-gate.c'")
  s=s.replace("Read-only installer ownership trace on unchanged guest","Ordinary unused-device package configuration diagnostic; no debugger or physical access")
  s=s.replace("k/'restart_gate.h',k/'timing-interface.json'","k/'restart_gate.h',k/'runner.c',k/'test-gate.c',k/'xwnunused179.inf',k/'timing-interface.json'")
 if n=='inventory-devices.py':
  s=s.replace("if not any(name.startswith('VEN_10DE&DEV_'+v) for v in ['01B0','01B4']):continue","if not (any(name.startswith('VEN_10DE&DEV_'+v) for v in ['01B0','01B4']) or name.startswith('VEN_1B36&DEV_0005')):continue")
  s=s.replace("assert len(row['devices'])==2","assert len(row['devices'])==3")
 if n.endswith('.py'):ast.parse(s)
 (k/n).write_text(s,encoding='utf-8')
(k/'artifacts').mkdir(exist_ok=False)
for p in (old/'artifacts').iterdir():
 if p.is_file():shutil.copyfile(p,k/'artifacts'/p.name)
sites=json.loads((k/'sites.json').read_text());sites['binaries'].pop('setupapi.dll',None)
# Preserve actual provider identity, but locate copied private providers in the new kit.
for label,meta in sites['binaries'].items():
 if (k/'artifacts'/label).exists():meta['path']='outputs/device-unused-package179/artifacts/'+label
setup=json.loads((old/'sites.json').read_text())['binaries']['setupapi.dll'];setup['path']='outputs/device-unused-package179/artifacts/setupapi.dll';sites['binaries']['setupapi.dll']=setup
(k/'sites.json').write_text(json.dumps(sites,indent=2)+'\n')
print('Fresh179 kit; unchanged compiled guard/probe, only staged unused-device INF and namespace/startup differ')

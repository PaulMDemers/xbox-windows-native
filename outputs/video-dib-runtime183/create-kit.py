"""Fresh matched ordinary114 upload kit from closed settled181, no launches."""
import ast,shutil,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'device-settled-reboot181'
assert not (k/'Run.ps1').exists()
assert json.loads((old/'candidate001/closure.json').read_text())['closed']
for n in ['common.py','atomic_json.py','check-leases.ps1','audit.py','preflight.py','sample_analysis.py','supervise.py','inventory-devices.py','audit-package.py']:
 s=(old/n).read_text().replace('device-settled-reboot181','video-dib-runtime183').replace('settled181','dib183').replace('xwnsr181','xwndb183')
 s=s.replace("['candidate001']","['control001','candidate001']")
 s=s.replace("ValidateSet('candidate001')","ValidateSet('control001','candidate001')")
 if n=='preflight.py':
  s=s.replace("k.parent/'device-unused-package179/candidate001/artifacts/after-system'","k.parent/'device-settled-reboot181/candidate001/artifacts/after-system'")
  s=s.replace("k.parent/'device-unused-package179/candidate001/artifacts/after-software'","k.parent/'device-settled-reboot181/candidate001/artifacts/after-software'")
  s=s.replace("display_token='xwnown' if case=='candidate001' else 'framebuf'","display_token='xwnown'")
 if n=='sample_analysis.py':
  s=s.replace('v4 counters','v6 counters').replace("'4','256','128'","'6','256','128'")
 if n=='supervise.py':
  s=s.replace("out=k/'candidate001';run=ws/'work/runs/nt5-dib183-candidate001'","case=sys.argv[1];assert case in ['control001','candidate001'];out=k/case;run=ws/('work/runs/nt5-dib183-'+case)")
  s=s.replace("'-Case','candidate001'","'-Case',case").replace('time.monotonic()+270','time.monotonic()+370')
 if n in ['inventory-devices.py','audit-package.py']:
  s=s.replace("out=k/'candidate001'","case=sys.argv[1];assert case in ['control001','candidate001'];out=k/case")
 if n=='audit-package.py':
  s=s.replace("dest=k/'candidate001/package-verification.json';assert not dest.exists()\nout=k/'candidate001';inv=read(out/'device-inventory.json');a=read(out/'audit.json');f=read(k/'fixture-candidate001.json')","case=sys.argv[1];assert case in ['control001','candidate001'];out=k/case\ndest=out/'package-verification.json';assert not dest.exists()\ninv=read(out/'device-inventory.json');a=read(out/'audit.json');f=read(k/('fixture-'+case+'.json'))") if "dest=k/'candidate001/package-verification.json'" in s else s
  # Replacement above has already changed out declaration: handle exact result.
  s=s.replace("dest=k/'candidate001/package-verification.json';assert not dest.exists()\ncase=sys.argv[1];assert case in ['control001','candidate001'];out=k/case;inv=read(out/'device-inventory.json');a=read(out/'audit.json');f=read(k/'fixture-candidate001.json')","case=sys.argv[1];assert case in ['control001','candidate001'];out=k/case\ndest=out/'package-verification.json';assert not dest.exists()\ninv=read(out/'device-inventory.json');a=read(out/'audit.json');f=read(k/('fixture-'+case+'.json'))")
  s=s.replace("disk=ws/'work/runs/nt5-dib183-candidate001/hdd.qcow2'","disk=ws/('work/runs/nt5-dib183-'+case+'/hdd.qcow2')")
 if n.endswith('.py'):ast.parse(s)
 (k/n).write_bytes(s.encode())
s=(k.parent/'video-body-runtime172/Run.ps1').read_text().replace('video-body-runtime172','video-dib-runtime183').replace('vbody172','dib183').replace('-GdbPort 4595 ','').replace('-Seconds 480','-Seconds 300')
(k/'Run.ps1').write_bytes(s.encode())
for n in ['xwnunused179.inf']:shutil.copyfile(old/n,k/n)
shutil.copyfile(old/'sites.json',k/'sites.json')
# Existing provider artifacts remain at181; do not invent new same-name pins.
s=(k.parent/'video-body-timing170/review-build.py').read_text().replace("assert binaries['runner.exe']['sha256']==sha(k.parent/'video-paired-timing166/artifacts/runner.exe')","assert binaries['runner.exe']['sha256']==sha(k.parent/'device-settled-reboot181/artifacts/runner.exe')").replace('v5 ExtEscape','v6 ExtEscape')
(k/'review-build.py').write_bytes(s.encode())
(ws/'.gitattributes').write_bytes((ws/'.gitattributes').read_bytes()+b'\n/outputs/video-dib-runtime183/** -text whitespace=cr-at-eol\n/outputs/video-dib-copy182/*-disassembly.txt whitespace=cr-at-eol,-blank-at-eol\n')
print('Fresh183 ordinary paired scripts; no hardware, debugger or launch')

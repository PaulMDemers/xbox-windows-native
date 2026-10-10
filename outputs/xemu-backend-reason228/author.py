"""Unique228 exact-reason kit; old227 frozen files are unchanged."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'xemu-backend-preserve227';dest=k/'author.json';assert not dest.exists();pins={}
for name in ['common.py','typed-state.py','Prepare.ps1','prepare.py','Run.ps1','Invoke-227.ps1','run-emulator.py','supervise-emulator.py','audit-emulator.py','trace.py','Build.ps1','build.py','freeze.py']:
 p=old/name;pins[name]=hashlib.sha256(p.read_bytes()).hexdigest();text=p.read_text()
 # Change new-kit paths/run IDs only; diagnostic ABI/name227 deliberately retained.
 text=text.replace('xemu-backend-preserve227','xemu-backend-reason228').replace('preserve227-runs','reason228-runs').replace('preserve227-scratch','reason228-scratch').replace('xbox-windows-native/preserve227','xbox-windows-native/reason228').replace('nt5-preserve227-','nt5-reason228-').replace('windows-native-preserve227','windows-native-reason228').replace('Invoke-227.ps1','Invoke-228.ps1')
 if name in ['build.py','Run.ps1','freeze.py']:text=text.replace('build005','build001').replace('candidate005','candidate001')
 if name=='build.py':
  text=text.replace("prior=ws/'outputs/xemu-cpu-surface-evict/build003';pins=json.loads((prior/'candidate-source-pins.json').read_text())", "prior=ws/'outputs/xemu-backend-preserve227';pins=json.loads((prior/'candidate005-source-pins.json').read_text())")
  start=text.index(' for n in names:\n  if n.endswith');end=text.index(' baseline=',start)
  text=text[:start]+" for n in names:\n  p=prior/'artifacts/build005/source'/n\n  assert sha(p)==pins[n];(s/n).write_bytes(p.read_bytes())\n"+text[end:]
  text=text.replace("assert sorted(r['changed_sources'])==sorted(names)","assert sorted(r['changed_sources'])==sorted(n for n in names if not n.endswith('renderer.h'))")
 if name=='freeze.py':
  text=text.replace("p=k/'artifacts/build001/xemu-preserve227.exe'", "p=k/'artifacts/build001/xemu-preserve227.exe'")
 if name=='trace.py':text=text.replace('bytes|error|references_retired','bytes|error|reason|references_retired')
 q=k/('Invoke-228.ps1' if name=='Invoke-227.ps1' else name);assert not q.exists();q.write_text(text)
dest.write_text(json.dumps(dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),parents=pins,physical_access=False,guest_launch=False,predicates_relaxed=False,native_payload_changed=False),indent=2)+'\n')

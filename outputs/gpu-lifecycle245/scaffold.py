"""Fresh corrected245 host run;244 failure stays closed and unchanged."""
import json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'gpu-lifecycle244'
names=['audit-emulator.py','close-host.py','common.py','parsing.py','preservation.py','typed-state.py','supervise-emulator.py','run-emulator.py','Run.ps1','Invoke-244.ps1','matrix.py','trace.py','freeze.py','test-close.py','test-connection.py','test-guards003.py','schema.py','test-pair.py','lifecycle.py','test-lifecycle.py','analyze-lifecycle.py','prelaunch-review.py','test-callback.c','test-callback.py']
for name in names:
 p=k/name.replace('Invoke-244','Invoke-245');assert not p.exists()
 s=(old/name).read_text().replace('gpu-lifecycle244','gpu-lifecycle245').replace('phase244','phase245').replace('Invoke-244','Invoke-245')
 # Actual model/event/marker ABI remains244; actual build005 belongs244.
 if name in ['Run.ps1','freeze.py','prelaunch-review.py','test-callback.py']:
  s=s.replace('build004','build005').replace('candidate004-source-pins','candidate005-source-pins')
 if name=='freeze.py':
  s=s.replace("k.parent/'gpu-reference-pair243/emulator-frozen.json'","k.parent/'gpu-lifecycle244/emulator-frozen.json'")
 if name=='prelaunch-review.py':
  s=s.replace("old=k.parent/'gpu-reference-pair242/artifacts/build005/source'","old=k.parent/'gpu-reference-pair242/artifacts/build004/source'")
  s=s.replace("assert not (k/'build003.json').is_relative_to(k/'preserve001')","assert read(k.parent/'gpu-lifecycle244/preserve001/host-state.json')['closed']")
  anchor="phy=(src/'system/physmem.c').read_text();"
  s=s.replace(anchor,"header=(src/'hw/xbox/nv2a/nv2a_int.h').read_text();first=header[header.index('typedef struct NV2AState {'):].split(';',1)[0]\nassert 'PCIDevice parent_obj' in first and 'lifecycle244_marks' not in first\nassert 'G_STATIC_ASSERT(offsetof(NV2AState, parent_obj) == 0);' in header\nassert read(k/'layout-test001.json')['passed']\n"+anchor)
 if name=='analyze-lifecycle.py':
  s=s.replace("from lifecycle import parse","from lifecycle import parse")
 p.write_text(s,encoding='utf-8')
for name in ['fixture-preserve001.json','fixture-seed001.json','inventory001.json','inventory.c','build001.json','build002.json','build003.json','build005.json','candidate005-source-pins.json']:
 shutil.copyfile(old/name,k/name)
for name in ['inputs','ram-source']:shutil.copytree(old/'artifacts'/name,k/'artifacts'/name)
shutil.copytree(old/'source',k/'source')
(k/'preserve001/artifacts').mkdir(parents=True)
for name in ['fixture-preserve001.json','fixture-seed001.json']:
 p=k/name;d=json.loads(p.read_text());d['new_unique_runtime']='nt5-phase245-preserve001';d['compiled_emulator_from']='outputs/gpu-lifecycle244/build005.json';p.write_text(json.dumps(d,indent=2)+'\n')
print('Fresh245 kit staged; actual compile005 remains244; no launch')

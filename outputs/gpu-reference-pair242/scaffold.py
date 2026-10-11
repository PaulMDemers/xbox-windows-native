"""Fresh242 kit: copy reviewed241 harness, never alter an old attempt."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'gpu-preserve-empty241'
names=['audit-emulator.py','close-host.py','common.py','parsing.py','preservation.py','typed-state.py','supervise-emulator.py','run-emulator.py','Run.ps1','Invoke-241.ps1','matrix.py','trace.py','build.py','Build.ps1','freeze.py','test-close.py','test-connection.py','test-guards.py','test-consume.c','test-consume.py']
for name in names:
 p=k/name.replace('Invoke-241','Invoke-242');assert not p.exists()
 s=(old/name).read_text(encoding='utf-8').replace('gpu-preserve-empty241','gpu-reference-pair242').replace('phase241','phase242').replace('preserve241','inventory242').replace('Invoke-241','Invoke-242')
 p.write_text(s,encoding='utf-8')
# Same immutable239 seed, same unchanged native224/219/211 payload and policy.
for name in ['fixture-preserve001.json','fixture-seed001.json','inventory001.json']:
 shutil.copyfile(old/name,k/name)
(k/'preserve001/artifacts').mkdir(parents=True)
for name in ['before','inputs','ram-source']:
 p=old/'artifacts'/name
 if p.exists():shutil.copytree(p,k/'artifacts'/name)
# Cold audit independently opens the unchanged seed and closed runtime child.
portable=(k.parent/'gpu-preserve-entry239/portable-offload.ps1').read_text(encoding='utf-8')
portable=portable.replace('closed-portable-239b','closed-portable-242').replace('237,238,239','240,241').replace("$case=if($phase -eq 239){'control001'}else{'xbe001'}","$case='preserve001'").replace('gpu-preserve-entry239/portable-offload001','gpu-reference-pair242/portable-offload001')
(k/'portable-offload.ps1').write_text(portable,encoding='utf-8')
print('242 fresh harness staged; no guest launched')

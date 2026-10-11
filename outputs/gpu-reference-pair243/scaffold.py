"""Fresh243 host interpretation; same already compiled242 executable, no patch."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'gpu-reference-pair242'
for name in ['audit-emulator.py','close-host.py','common.py','parsing.py','preservation.py','typed-state.py','supervise-emulator.py','run-emulator.py','Run.ps1','Invoke-242.ps1','matrix.py','trace.py','freeze.py','test-close.py','test-connection.py','test-guards003.py','schema.py','test-pair.py','prelaunch-review.py']:
 p=k/name.replace('Invoke-242','Invoke-243');assert not p.exists()
 s=(old/name).read_text(encoding='utf-8').replace('gpu-reference-pair242','gpu-reference-pair243').replace('phase242','phase243').replace('Invoke-242','Invoke-243')
 # Actual executable protocol remains242. No recompilation/native change.
 if name=='freeze.py':
  s=s.replace("k.parent/'gpu-preserve-empty241/emulator-frozen.json'","k.parent/'gpu-reference-pair242/emulator-frozen.json'")
 p.write_text(s,encoding='utf-8')
for name in ['fixture-preserve001.json','fixture-seed001.json','inventory001.json','build004.json','candidate004-source-pins.json','inventory.c','OWNERS.md']:
 shutil.copyfile(old/name,k/name)
for name in ['inputs','ram-source']:
 shutil.copytree(old/'artifacts'/name,k/'artifacts'/name)
shutil.copytree(old/'source',k/'source')
(k/'preserve001/artifacts').mkdir(parents=True)
for p in (old/'preserve001/artifacts').glob('before-*'):shutil.copyfile(p,k/'preserve001/artifacts'/p.name)
p=k/'schema.py';s=p.read_text(encoding='utf-8');assert "assert not s['fifo'][2] and not any(s['stats'][1:7])" in s
s=s.replace("assert not s['fifo'][2] and not any(s['stats'][1:7])","assert not s['fifo'][2] and not any(s['stats'][i] for i in [1,2,4,5,6])\n  assert s['stats'][3]==pre['current_pg_only'][5], 'Enabled mask must match observed source; it is not pending work'")
p.write_text(s,encoding='utf-8')
p=k/'test-pair.py';s=p.read_text(encoding='utf-8').replace("stats[0]=1;","stats[0]=1;stats[3]=pre['current_pg_only'][5];")
s=s.replace("('stats',1,13,1)","('stats',1,3,0),('stats',1,13,1)")
p.write_text(s,encoding='utf-8')
# Point reuse review to the actual completed242 compile/host evidence, with hashes.
p=k/'prelaunch-review.py';s=p.read_text(encoding='utf-8')
s=s.replace("['inventory-test005','consume-test001','pair-test001','guard-test003','connection-test001','host-close-test001']","['pair-test001','guard-test003','connection-test001','host-close-test001']")
s=s.replace("inventory=(k/'inventory.c').read_text", "for name in ['inventory-test005','consume-test001']:\n assert read(k.parent/'gpu-reference-pair242'/(name+'.json'))['passed']\nassert sha(k/'inventory.c')==sha(k.parent/'gpu-reference-pair242/inventory.c')\nassert read(k.parent/'gpu-reference-pair242/preserve001/host-state.json')['closed']\nassert read(k.parent/'gpu-reference-pair242/matrix001.json')['closed']\ninventory=(k/'inventory.c').read_text")
s=s.replace("print('242 compiled", "print('243 compiled")
p.write_text(s,encoding='utf-8')
for name in ['fixture-preserve001.json','fixture-seed001.json']:
 p=k/name;d=json.loads(p.read_text(encoding='utf-8'));d['new_unique_runtime']='nt5-phase243-preserve001';d['compiled_emulator_reused_from']='outputs/gpu-reference-pair242/build004.json';p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print('243 fresh host kit, same actual compiled242 binary; no launch')

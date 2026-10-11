"""New runtime from the never-executed265 seed, not either completed run disk."""
import json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;p=k.parent/'backend-ledger266'
for name in ['common.py','atomic_json.py','kernel-discovery.py','close-host.py','typed-state.py','runtime-dependencies.py','attest.py','attestation-inputs001.json']:
    assert not (k/name).exists();shutil.copyfile(p/name,k/name)
for name in ['run.py','Run.ps1','Invoke.ps1','audit.py','trace.py']:
    t=(p/name).read_text().replace('backend-ledger266','backend-actors267').replace('/ledger266/','/actors267/').replace('nt5-ledger266','nt5-actors267').replace('windows-native-ledger266','windows-native-actors267')
    if name=='Run.ps1':
        b=json.loads((k/'renderer-build001.json').read_text());assert b['passed'] and b['borrowed_sources_restored']
        t=t.replace('ledger265-build003/xemu-ledger265.exe','actors267-build001/xemu-actors267.exe').replace('b52c671e6f5ea643eaac1e1a8970cf5454fa776fdb763debfba5030b43b41624',b['executable_sha256'])
    assert not (k/name).exists();(k/name).write_text(t)
shutil.copyfile(p/'analyze-ledger.py',k/'analyze-base.py')
out=k/'emu001';out.mkdir(exist_ok=False)
shutil.copytree(p/'emu001/before',out/'before')
(out/'artifacts').mkdir()
for n in ['system','software','default','sam','security']:shutil.copyfile(p/'emu001/artifacts'/('before-'+n),out/'artifacts'/('before-'+n))
f=json.loads((p/'emu001/fixture.json').read_text())
f.update(new_unique_runtime='nt5-actors267-emu001',compiled_emulator_from='E:/Codex-archive/xbox-windows-native/actors267-build001',
    emulator_source_changed_only=json.loads((k/'renderer-build001.json').read_text())['changed_sources'],
    fixture_reuse='Never-executed265 standalone preparation.267 makes a new private runtime copy; no265/266 runtime disk parented.')
(out/'fixture.json').write_text(json.dumps(f,indent=2)+'\n')
print('267 fresh runtime inputs prepared; no guest launch')

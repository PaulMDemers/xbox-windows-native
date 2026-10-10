"""Read-only private snapshot/hash review; save small manifests before physical writes."""
import ast
from common001 import *
ticket();assert read(k/'before-audit002.json')['passed'] and read(k/'providers001.json')['passed']
assert not (k/'frozen001.json').exists() and not (k/'ready001.json').exists()
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
root=helpers();snapshot=before();files={}
for path,row in snapshot['files'].items():
    data=incoming(path);assert sha(data)==row['sha256'] and row['second_read_exact']
    lowered=path.lower()
    if lowered in files:assert row['sha256']==files[lowered][1]
    else:files[lowered]=(path,row['sha256'])
inputs=list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'PLAN.md',k/'capture002.json',k/'before-audit002.json',k/'providers001.json',root/'MANIFEST.json',canonical/'outputs/device-hardware220/HANDOFF.md',canonical/'outputs/device-hardware220/queue.py',canonical/'outputs/video-upload-runtime211/capture.json',repo/'outputs/native-windows-physical-f/physical-cache-preflight.json',repo/'outputs/native-windows-physical-f/decode-legacy-events.py',repo/'outputs/native-windows-fatx-preflight/analyze.py',canonical/'outputs/native-windows-fatx-preflight/artifacts/default.xbe']
inputs += [p for p in root.rglob('*') if p.is_file()]
frozen={str(p.resolve()):sha(p.read_bytes()) for p in inputs};save(k/'frozen001.json',frozen)
save(k/'ready001.json',dict(ready_for_single_installation_trial=True,physical_qualified=False,source_package_commit='7cdb191bd2ef72e24001370726f97a7383a7250b',legacy_bootstrap='Same build004 bytes replace ac97xnt5.sys before boot; no binding edit; original captured for exact restoration.',rollback=dict(kind='complete private directory plus per-file SHA256 manifest',path=str(k/'artifacts/before002'),manifest=str(k/'capture002.json'),manifest_sha256=sha((k/'capture002.json').read_bytes()),entries=len(files),readback_verified=True),frozen_inputs=len(frozen),audit_resources='Independent read-only private files; no shared NBD, emulator monitor or build tree access. Small result manifests only, as authorized by hardware220 coordinator guidance.'))
print('Physical inputs frozen; complete rollback directory rehashed; no console write or launch',flush=True)

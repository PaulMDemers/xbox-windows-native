"""Reassemble immutable 0.2.0 entries from hash-matched retained artifacts."""
import hashlib
import importlib.util
import json
import shutil
import zipfile
from pathlib import Path

K = Path(__file__).resolve().parent
W = K.parents[1]
OUT = Path('E:/Codex-archive/xbox-windows-native/0.2.0-recovered329')
RELEASE = W/'outputs/release-0.2.0'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
encoded = lambda obj: (json.dumps(obj, indent=2)+'\n').encode()

def sha(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

assert not OUT.exists() and not (K/'package001.json').exists(), 'Consumed attempt'
assert shutil.disk_usage('C:/').free > 20*1024**3
assert shutil.disk_usage('E:/').free > 2*1024**3
original = read(RELEASE/'bundle.json')
expected = original['archives'][0]['entries']
docs = {n: (RELEASE/n).read_bytes() for n in ['README.md', 'USAGE.md', 'user-observation.json']}
docs.update({'MANIFEST.json': encoded(original['manifest']), 'QUALIFICATION.json': encoded(original['qualification'])})
payload = dict(docs)
provenance = {n: 'unchanged release evidence' for n in docs}
inventory = read(Path('E:/xwn328/inventory001.json'))['files']
preferred = list(Path('E:/xwn329/retained-builds001').glob('*')) + list(Path('E:/xwn300/build001').rglob('*'))
cache = {}
for name, info in expected.items():
    if name in payload:
        assert len(payload[name]) == info['bytes'] and hashlib.sha256(payload[name]).hexdigest() == info['sha256'], name
        continue
    candidates = preferred + [Path(x['path']) for x in inventory if x['bytes'] == info['bytes']]
    for p in candidates:
        if not p.is_file() or p.stat().st_size != info['bytes']:
            continue
        key = str(p.resolve())
        if key not in cache:
            cache[key] = sha(p)
        if cache[key] == info['sha256']:
            payload[name] = p.read_bytes()
            provenance[name] = dict(path=str(p), sha256=cache[key])
            break
    assert name in payload, ('Missing exact release payload', name, info)
assert set(payload) == set(expected)
spec = importlib.util.spec_from_file_location('original_packager', RELEASE/'build-bundle.py')
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)
OUT.mkdir(parents=True)
overlay = packager.make_zip(OUT/'xwn-0.2.0-hd-overlay.zip', payload)
assert overlay['entries'] == expected
assert overlay['sha256'] == original['archives'][0]['sha256'], 'Reconstructed overlay differs'
retained = read(W/'outputs/storage-trim328/recovery-retained.json')
recovery = {}
for row in retained['bundles']:
    p = Path(row['path'])
    assert sha(p) == row['sha256']
    recovery['recovery/'+p.name] = p
manifest = Path(retained['bundles'][0]['path']).parent/'capture-manifest.json'
assert sha(manifest) == retained['manifest_sha256']
recovery['recovery/capture-manifest.json'] = manifest
items = dict(docs, **recovery)
items['xwn-0.2.0-hd-overlay.zip'] = Path(overlay['path'])
items['recovery/capture-summary.json'] = W/'outputs/demo-audio-level256/capture-summary.json'
combined = packager.make_zip(OUT/'xwn-0.2.0-private-demo.zip', items)
assert combined['entries'] == original['archives'][1]['entries']
result = dict(passed=True, original_bundle_evidence_sha256=sha(RELEASE/'bundle.json'),
              archives=[overlay, combined], provenance=provenance,
              overlay_archive_byte_identical=True,
              combined_archive_byte_identical=combined['sha256'] == original['archives'][1]['sha256'],
              all_entry_bytes_identical=True, rebuilt=False, tags_changed=False,
              physical_access=False, guest_launched=False)
for target in [K/'package001.json', OUT/'recovery-receipt.json']:
    target.write_bytes(encoded(result))
for name, data in docs.items():
    (OUT/name).write_bytes(data)
print(json.dumps({n: result[n] for n in ['passed', 'overlay_archive_byte_identical', 'combined_archive_byte_identical', 'all_entry_bytes_identical']}))

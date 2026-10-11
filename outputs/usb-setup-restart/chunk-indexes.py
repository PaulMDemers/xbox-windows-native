"""Losslessly split oversized derived JSON arrays; preserve original bytes privately."""
import hashlib, json, shutil, sys
from pathlib import Path

k = Path(__file__).resolve().parent
case = sys.argv[1]
assert case in ['emu001', 'emu002']
out = k / case
private = out / 'artifacts/full-json'
private.mkdir(parents=True, exist_ok=True)
records = {}
for name in ['dma-index.json', 'backend-index.json', 'transfer-analysis.json']:
    path = out / name
    raw = path.read_bytes()
    if len(raw) < 5 * 1024 * 1024:
        continue
    original = json.loads(raw)
    rows = original.pop('chunks') if name == 'transfer-analysis.json' else original
    assert isinstance(rows, list)
    dest = out / (path.stem + '-parts')
    dest.mkdir(exist_ok=False)
    parts = []
    restored = []
    for at in range(0, len(rows), 2000):
        batch = rows[at:at+2000]
        part = dest / ('part%03d.json' % (at // 2000 + 1))
        data = (json.dumps(batch, separators=(',', ':')) + '\n').encode('utf-8')
        assert len(data) < 5 * 1024 * 1024
        part.write_bytes(data)
        restored.extend(json.loads(part.read_bytes()))
        parts.append(dict(path=part.relative_to(out).as_posix(), start_index=at,
                          count=len(batch), bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    assert restored == rows
    manifest = dict(count=len(rows), parts=parts, original_bytes=len(raw),
                    original_sha256=hashlib.sha256(raw).hexdigest(), reconstruction_verified=True)
    saved = private / name
    assert saved.resolve().is_relative_to(out.resolve())
    assert not saved.exists()
    shutil.move(str(path), str(saved))
    assert saved.read_bytes() == raw
    result = dict(original, chunks_external=manifest) if isinstance(original, dict) else dict(records_external=manifest)
    path.write_text(json.dumps(result, indent=2) + '\n')
    records[name] = manifest
(out / 'chunked-indexes.json').write_text(json.dumps(records, indent=2) + '\n')
print(json.dumps({name:v['count'] for name,v in records.items()}))

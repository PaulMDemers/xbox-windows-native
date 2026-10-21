"""Validate LF-normalized policy package against exact staged source bytes."""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

K = Path(__file__).resolve().parent
ROOT = K.parents[1]
OUT = K / 'package002.json'
assert not OUT.exists()
sha = lambda b: hashlib.sha256(b).hexdigest()
old = Path('C:/xwn644/xwn-display-selector644.zip')
new = Path('C:/xwn644/xwn-display-selector644-002.zip')
previous = json.loads((K / 'host001.json').read_text())
assert previous['host_tests_exit'] == 0 and previous['archive_verified']
for path in ('tools/configure-e-display.py', 'tools/package-e-display.py',
             'tests/test_e_display_selector.py'):
    assert sha((ROOT / path).read_bytes()) == previous['source_pins'][path]
with zipfile.ZipFile(old) as a, zipfile.ZipFile(new) as b:
    assert a.namelist() == b.namelist()
    assert a.read('tools/e-display-policy.json').replace(b'\r\n', b'\n') == b.read('tools/e-display-policy.json')
    manifest = json.loads(b.read('manifest.json'))
    for name in b.namelist():
        data = b.read(name)
        if name not in ('tools/e-display-policy.json', 'manifest.json'):
            assert data == a.read(name)
        if name in manifest:
            assert manifest[name] == {'bytes': len(data), 'sha256': sha(data)}
        if name.startswith(('tools/', 'docs/')):
            staged = subprocess.check_output(['git', 'show', ':' + name], cwd=ROOT, timeout=20)
            assert data == (ROOT / name).read_bytes() == staged, name
record = dict(passed=True, physical_access=False, archive=str(new), bytes=new.stat().st_size,
              sha256=sha(new.read_bytes()), entries_verified=8, exact_staged_sources=True,
              prior_archive_preserved=True, change='Policy CRLF normalized to LF; JSON meaning unchanged',
              host_tests='host001:16 passing tests; selector/test code unchanged')
with OUT.open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')

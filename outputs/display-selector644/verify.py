"""Record host-only selector tests and independent private ZIP readback."""
import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

K = Path(__file__).resolve().parent
ROOT = K.parents[1]
OUT = K / 'host001.json'
assert not OUT.exists(), 'Never overwrite evidence'
result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests',
                         '-p', 'test_e_display_selector.py', '-v'], cwd=ROOT,
                        capture_output=True, text=True, timeout=60)
archive_path = Path('C:/xwn644/xwn-display-selector644.zip')
sha = lambda b: hashlib.sha256(b).hexdigest()
record = {'utc': datetime.now(timezone.utc).isoformat(), 'physical_access': False,
          'guest_launch': False, 'host_tests_exit': result.returncode,
          'host_tests_output': result.stdout + result.stderr, 'archive_verified': False}
try:
    assert result.returncode == 0
    with zipfile.ZipFile(archive_path) as archive:
        manifest = json.loads(archive.read('manifest.json'))
        assert len(archive.namelist()) == len(set(archive.namelist())) == 8
        assert set(archive.namelist()) == set(manifest) | {'manifest.json'}
        for name, pin in manifest.items():
            data = archive.read(name)
            assert {'bytes': len(data), 'sha256': sha(data)} == pin
            if name.startswith(('tools/', 'docs/')):
                assert data == (ROOT / name).read_bytes()
        policy = json.loads(archive.read('tools/e-display-policy.json'))
        for mode in ('480p', '720p'):
            assert manifest[f'resolution/{mode}/default.xbe'] == policy['profiles'][mode]
    record.update(archive_verified=True, archive_sha256=sha(archive_path.read_bytes()),
                  archive_bytes=archive_path.stat().st_size, manifest=manifest)
    record['source_pins'] = {name: sha((ROOT / name).read_bytes()) for name in (
        'tools/configure-e-display.py', 'tools/e-display-policy.json',
        'tools/package-e-display.py', 'tests/test_e_display_selector.py',
        'outputs/display-selector644/verify.py')}
finally:
    with OUT.open('x') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')

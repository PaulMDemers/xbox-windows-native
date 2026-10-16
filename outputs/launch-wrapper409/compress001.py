"""Transparent NTFS compression of one closed fixture; no logical byte/path change."""
import datetime, hashlib, json, shutil, subprocess
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
p = (W / 'outputs/raw-c-inventory/artifacts/flat-002.qcow2').resolve()
assert p.is_relative_to(W) and str(p).startswith('C:')
out = K / 'compression001.json'
assert not out.exists()
assert json.loads((W/'outputs/raw-c-inventory/validation.json').read_text())['passed']
def digest():
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
before = digest()
assert before == json.loads((W/'outputs/raw-c-inventory/flat-fixture.json').read_text())['flat_sha256']
r = dict(path=str(p), sha256=before, started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         free_before=shutil.disk_usage('C:/').free, completed=False, path_unchanged=True,
         scope='Host transparent NTFS compression only; no guest filesystem/chain movement or console access')
out.write_text(json.dumps(r, indent=2)+'\n')
cp = subprocess.run(['compact.exe', '/C', '/I', '/Q', str(p)], capture_output=True, text=True, timeout=180)
(K/'compression001.log').write_text(cp.stdout+cp.stderr)
r.update(returncode=cp.returncode, after_sha256=digest(), free_after=shutil.disk_usage('C:/').free)
r['completed'] = cp.returncode == 0 and r['after_sha256'] == before
out.write_text(json.dumps(r, indent=2)+'\n')
assert r['completed']
print(json.dumps(r))

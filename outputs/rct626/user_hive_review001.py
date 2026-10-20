"""Read-only independent audit of collected user hives; no console access."""
import hashlib, json, sys
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
sys.path.insert(0, str(W / 'work/python-packages'))
sys.path.insert(0, str(K.parent / 'clean-media404'))
from hive_audit004 import audit

out = K / 'user-hive-review001.json'
assert not out.exists()
results = {}
for phase, name in [('before', 'before001.json'), ('after', 'collection001.json')]:
    record = json.loads((K / name).read_text())
    row = record['files']['/E/documents and settings/Win2K/NTUSER.DAT']
    path = Path('/mnt/' + row['path'][0].lower() + row['path'][2:].replace('\\', '/'))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
    results[phase] = audit(path)
passed = all(r['clean'] and r['header_valid'] and r['independent_raw_values_agree'] for r in results.values())
out.write_text(json.dumps(dict(passed=passed,results=results),indent=2)+'\n')
print(json.dumps(dict(user_hives_passed=passed)))
assert passed

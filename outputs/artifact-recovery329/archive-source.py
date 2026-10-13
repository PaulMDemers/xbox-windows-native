"""Recover source and complete history from immutable existing tags."""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

K = Path(__file__).resolve().parent
W = K.parents[1]
GIT = 'C:/devkitPro/msys2/usr/bin/git.exe'
OUT = Path('E:/Codex-archive/xbox-windows-native/0.2.0-recovered329')
old = json.loads((W/'outputs/release-0.2.0/source-evidence-bundles.json').read_text())
def git(*args):
    return subprocess.check_output([GIT, *args], cwd=W)
def record(p):
    with p.open('rb') as f:
        return dict(path=str(p), bytes=p.stat().st_size, sha256=hashlib.file_digest(f, 'sha256').hexdigest())

assert not (K/'source001.json').exists()
tag = old['tag']
assert git('rev-parse', tag).decode().strip() == old['tag_object']
assert git('rev-list', '-n', '1', tag).decode().strip() == old['revision']
assert git('rev-parse', 'v0.1.0').decode().strip() == old['immutable_v0_1_0_tag_object']
source = OUT/'xwn-0.2.0-source-evidence.zip'
history = OUT/'xwn-0.2.0-history.bundle'
assert not source.exists() and not history.exists()
git('archive', '--format=zip', '--output='+str(source), tag)
blobs = {}
for row in git('ls-tree', '-r', '-z', tag).split(b'\0'):
    if not row:
        continue
    metadata, name = row.split(b'\t', 1)
    mode, kind, oid = metadata.split()
    assert kind == b'blob'
    blobs[name.decode()] = oid.decode()
with zipfile.ZipFile(source) as z:
    entries = [x for x in z.infolist() if not x.is_dir()]
    assert len(entries) == len(blobs) and {x.filename for x in entries} == set(blobs)
    for entry in entries:
        data = z.read(entry.filename)
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == blobs[entry.filename]
git('bundle', 'create', str(history), 'refs/tags/v0.2.0', 'refs/tags/v0.1.0')
verify = subprocess.run([GIT, 'bundle', 'verify', str(history)], cwd=W, capture_output=True, text=True, check=True)
heads = git('bundle', 'list-heads', str(history)).decode()
assert old['tag_object']+' refs/tags/v0.2.0' in heads
assert old['immutable_v0_1_0_tag_object']+' refs/tags/v0.1.0' in heads
archives = [record(source), record(history)]
result = dict(passed=True, tag=tag, tag_object=old['tag_object'], revision=old['revision'],
              entries_verified=len(blobs), complete_history_verified=True, archives=archives,
              outer_hash_matches_original=[x['sha256'] == y['sha256'] for x,y in zip(archives,old['archives'])],
              verify=verify.stdout+verify.stderr, private_only=True, tags_changed=False)
(K/'source001.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({n:result[n] for n in ['passed','entries_verified','outer_hash_matches_original']}))

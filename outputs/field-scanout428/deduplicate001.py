"""Consolidate two exact cold compressed archives on NTFS, retaining both paths."""
import hashlib,json,os,shutil
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]
out=K/'deduplicate001.json'; assert not out.exists()
a=(W/'outputs/native-windows-nt5-kernel/artifacts/windows2000-audio-003.qcow2.zst').resolve()
b=(W/'work/runs/nt5-kernel-044/hdd.qcow2.zst').resolve()
assert a.is_relative_to(W) and b.is_relative_to(W) and a.drive==b.drive
assert a.suffix==b.suffix=='.zst' and not os.path.samefile(a,b)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for p in (a,b):
 r=json.loads(Path(str(p)[:-4]+'.archived328.json').read_text())
 assert r['roundtrip_verified'] and r['source_removed']
 assert p.stat().st_size==r['archive_bytes'] and sha(p)==r['archive_sha256']
assert sha(a)==sha(b)=='b84f10a7eab6017708618b23f5669b70660c8b318bc2f0a73b3c3784d9da6097'
tmp=b.with_name(b.name+'.428link'); assert not tmp.exists()
record=dict(canonical=str(a),duplicate=str(b),sha256=sha(a),bytes=b.stat().st_size,
            free_before=shutil.disk_usage(W).free,complete=False,backing_disks_changed=False)
out.write_text(json.dumps(record,indent=2)+'\n')
# Establish and validate the replacement before atomically replacing duplicate.
os.link(a,tmp); assert os.path.samefile(a,tmp) and sha(tmp)==record['sha256']
os.replace(tmp,b)
assert os.path.samefile(a,b) and sha(b)==record['sha256']
record.update(complete=True,free_after=shutil.disk_usage(W).free,both_original_paths_retained=True)
out.write_text(json.dumps(record,indent=2)+'\n'); print(json.dumps(record))

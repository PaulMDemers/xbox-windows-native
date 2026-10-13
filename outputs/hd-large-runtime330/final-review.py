"""Join all new and unchanged gates; no hardware performance inference."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
out=K/'emu001';run=Path('E:/xwn330/runs/nt5-hd330-emu001')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
dest=out/'final-review.json';assert not dest.exists()
for name in ['emulator-frozen.json','host-frozen.json']:
 for p,h in read(K/name).items():
  p=Path(p);p=p if p.is_absolute() else W/p;assert sha(p)==h,p
f=read(out/'fixture.json');parent=read(K.parent/'artifact-recovery329/seed001/fixture.json')
assert f['parent_sha256']==parent['fixture_sha256'] and sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
changes=[n for n in parent['files'] if parent['files'][n]!=f['files'][n]]
assert changes==['F/xwndemo251/replay.exe'] and parent['files'].keys()==f['files'].keys()
for n,h in parent['helpers'].items():
 assert n=='replay.exe' or f['helpers'][n]==h
a=read(out/'audit.json');closure=read(out/'closure.json')
assert closure['closed'] and closure['audit_sha256']==sha(out/'audit.json')
assert closure['cleanup_sha256']==sha(run/'cleanup.json')
combined=read(out/'combined-review.json') if (out/'combined-review.json').exists() else {'scoped_combined_passed':False,'strict_qualification_passed':False}
host=read(run/'host-exit.json');allocation=read(out/'allocation.json')
large=all(r['passed'] for r in a['large_samples']) and len(a['large_samples'])==5
caps={int(v[1]):int(v[2]) for v in a['actual_caps']}
mode=(caps.get(8),caps.get(10),caps.get(12))==(1920,1080,32) and all(v.get('identity',[None]*7)[2:7]==[1920,1080,7680,32,8294400] for v in a['samples'])
private={p.relative_to(out).as_posix():sha(p) for p in sorted((out/'artifacts').rglob('*')) if p.is_file()}
(out/'private-artifacts.json').write_text(json.dumps(private,indent=2)+'\n')
scoped=large and mode and combined['scoped_combined_passed'] and host['passed'] and host['exit_code']==0 and not host['fallback_kill']
r=dict(closed=True,never_relaunch_or_recollect_or_parent=True,scoped_passed=scoped,
 strict_passed=scoped and combined['strict_qualification_passed'],large_passed=large,
 mode_passed=mode,changed_files=changes,large_samples=a['large_samples'],
 integrity_passed=a['integrity_passed'],normal_shutdown_count=a['normal_shutdown_count'],
 host_exit=host,combined=combined,allocation={n:allocation[n] for n in ['directories','files','directory_clusters','errors','orphan_cluster_count']},
 protected_files=len(a['files']),hives=len(a['hives']),private_capture_count=len(private),
 physical_access=False,performance_qualified=False,release_qualified=False,
 limits='Emulator correctness and scoped workload only; new reconstructed seed explicitly qualified separately, strict events retained. No physical speed result or driver change.')
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['closed','scoped_passed','strict_passed','large_passed','integrity_passed','normal_shutdown_count']}))

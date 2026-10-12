import datetime,hashlib,json
from pathlib import Path
from activation_analysis import analyze
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001';run=Path('D:/xwn313/runs/nt5-hd313-candidate001')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
dest=k/'final-review.json';assert not dest.exists()
counts={}
for file in ['emulator-frozen.json','host-frozen.json']:
 pins=read(k/file)
 for name,digest in pins.items():
  p=Path(name);p=p if p.is_absolute() else ws/p;assert sha(p)==digest,name
 counts[file]=len(pins)
f=read(out/'fixture.json');parent=read(k.parent/'hd-boot312/candidate001/fixture.json')
assert f['parent_sha256']==parent['fixture_sha256'] and sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
assert f['files'].keys()==parent['files'].keys()
changed=[n for n in f['files'] if f['files'][n]!=parent['files'][n]]
assert changed==['F/xwndemo251/wizard.exe']
assert f['helpers']['wizard.exe']==f['files'][changed[0]]
a=read(out/'audit.json');closure=read(out/'closure.json');assert closure['closed'] and closure['audit_sha256']==sha(out/'audit.json')
assert closure['cleanup_sha256']==sha(run/'cleanup.json')
try:activation=analyze((out/'artifacts/wizard201.log').read_bytes())
except (AssertionError,ValueError,UnicodeError) as exc:activation=dict(passed=False,error=repr(exc))
(out/'activation-review.json').write_text(json.dumps(activation,indent=2)+'\n')
combined=read(out/'combined-review.json') if (out/'combined-review.json').exists() else {'scoped_combined_passed':False,'strict_qualification_passed':False}
caps={int(v[1]):int(v[2]) for v in a['actual_caps']}
mode=(caps.get(8),caps.get(10),caps.get(12))==(1280,720,32) and all(v.get('identity',[None]*7)[2:7]==[1280,720,5120,32,3686400] for v in a['samples'])
host=read(run/'host-exit.json');allocation=read(out/'allocation.json')
private={p.relative_to(out).as_posix():sha(p) for p in sorted((out/'artifacts').rglob('*')) if p.is_file()}
(out/'private-artifacts.json').write_text(json.dumps(private,indent=2)+'\n')
hostrecords={n:dict(sha256=sha(run/n),record=read(run/n)) for n in ['cleanup.json','host-exit.json','host-close.json','input-hashes.json']}
(out/'host-records.json').write_text(json.dumps(hostrecords,indent=2)+'\n')
scoped=mode and activation['passed'] and combined['scoped_combined_passed'] and host['passed'] and host['exit_code']==0 and not host['fallback_kill']
r=dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),closed=True,never_relaunch_or_recollect_or_parent=True,pins=counts,changed_files=changed,mode_passed=mode,activation=activation,combined=combined,scoped_passed=scoped,strict_passed=scoped and combined['strict_qualification_passed'],actual_caps=a['actual_caps'],integrity_passed=a['integrity_passed'],normal_shutdown_count=a['normal_shutdown_count'],orderly_host_exit=host['passed'],allocation={n:allocation[n] for n in ['directories','files','directory_clusters','errors','orphan_cluster_count']},protected_files=len(a['files']),hives=len(a['hives']),private_capture_count=len(private),physical_access=False,physical_qualified=False,windows1080i_qualified=False,release_qualified=False,limits='One ordinary unchanged311720p emulator workload with313 helper. Whole-boot warnings remain strict failures. No physical/performance/1080i or release qualification.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

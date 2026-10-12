import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001';run=Path('D:/xwn317/runs/nt5-hd317-candidate001')
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
f=read(out/'fixture.json');parent=read(k.parent/'hd-ui313/candidate001/fixture.json')
assert f['parent_sha256']==parent['fixture_sha256'] and sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
assert f['files'].keys()==parent['files'].keys()
changed=[n for n in f['files'] if f['files'][n]!=parent['files'][n]]
assert changed==['E/Applications/XWNFBoot/default.xbe']
assert f['helpers']==parent['helpers']
a=read(out/'audit.json');closure=read(out/'closure.json');assert closure['closed'] and closure['audit_sha256']==sha(out/'audit.json')
assert closure['cleanup_sha256']==sha(run/'cleanup.json')
combined=read(out/'combined-review.json') if (out/'combined-review.json').exists() else {'scoped_combined_passed':False,'strict_qualification_passed':False}
caps={int(v[1]):int(v[2]) for v in a['actual_caps']}
mode=(caps.get(8),caps.get(10),caps.get(12))==(1920,1080,32) and all(v.get('identity',[None]*7)[2:7]==[1920,1080,7680,32,8294400] for v in a['samples'])
host=read(run/'host-exit.json');allocation=read(out/'allocation.json')
private={p.relative_to(out).as_posix():sha(p) for p in sorted((out/'artifacts').rglob('*')) if p.is_file()}
(out/'private-artifacts.json').write_text(json.dumps(private,indent=2)+'\n')
hostrecords={n:dict(sha256=sha(run/n),record=read(run/n)) for n in ['cleanup.json','host-exit.json','host-close.json','input-hashes.json']}
(out/'host-records.json').write_text(json.dumps(hostrecords,indent=2)+'\n')
scoped=mode and combined['scoped_combined_passed'] and host['passed'] and host['exit_code']==0 and not host['fallback_kill']
r=dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),closed=True,never_relaunch_or_recollect_or_parent=True,pins=counts,changed_files=changed,mode_passed=mode,combined=combined,scoped_passed=scoped,strict_passed=scoped and combined['strict_qualification_passed'],actual_caps=a['actual_caps'],integrity_passed=a['integrity_passed'],normal_shutdown_count=a['normal_shutdown_count'],orderly_host_exit=host['passed'],allocation={n:allocation[n] for n in ['directories','files','directory_clusters','errors','orphan_cluster_count']},protected_files=len(a['files']),hives=len(a['hives']),private_capture_count=len(private),physical_access=False,physical_qualified=False,windows1080i_qualified=False,release_qualified=False,limits='One ordinary3161080i emulator mode workload with unchanged313 helper.313activation coverage remains independently unproved. Whole-boot warnings stay strict failures. No actualTV field-quality/physical/performance/release qualification.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

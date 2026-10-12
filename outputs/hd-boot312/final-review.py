"""Mode-specific matched review; retain every strict or scoped failure."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'final-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
pins={}
for name in ['emulator-frozen.json','host-frozen.json']:
 data=read(k/name)
 for n,h in data.items():
  p=Path(n);p=p if p.is_absolute() else ws/p;assert sha(p)==h,n
 pins[name]=len(data)
fixtures=[read(k/c/'fixture.json') for c in ['control001','candidate001']]
assert fixtures[0]['parent_sha256']==fixtures[1]['parent_sha256']
changed=[n for n in fixtures[0]['files'] if fixtures[0]['files'][n]!=fixtures[1]['files'][n]]
assert changed==['E/Applications/XWNFBoot/default.xbe']
rows={}
for case,expected in [('control001',(720,480,2880)),('candidate001',(1280,720,5120))]:
 out=k/case;run=Path('D:/xwn312/runs')/('nt5-hd312-'+case)
 a=read(out/'audit.json');c=read(out/'combined-review.json');f=read(out/'fixture.json')
 closure=read(out/'closure.json');assert closure['closed'] and closure['never_relaunch_or_recollect']
 assert closure['audit_sha256']==sha(out/'audit.json') and closure['cleanup_sha256']==sha(run/'cleanup.json')
 assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
 caps={int(v[1]):int(v[2]) for v in a['actual_caps']}
 dimensions=(caps.get(8),caps.get(10),caps.get(8,0)*4)
 mode_pass=dimensions==expected and caps.get(12)==32 and all(v.get('identity',[None]*7)[2:7]==[expected[0],expected[1],expected[2],32,expected[0]*expected[1]*4] for v in a['samples'])
 host=read(run/'host-exit.json');allocation=read(out/'allocation.json');launch=read(out/'launch.json')
 artifact={p.relative_to(out).as_posix():sha(p) for p in sorted((out/'artifacts').rglob('*')) if p.is_file()}
 (out/'private-artifacts.json').write_text(json.dumps(artifact,indent=2)+'\n')
 hostrecords={n:dict(sha256=sha(run/n),record=read(run/n)) for n in ['cleanup.json','host-exit.json','host-close.json','input-hashes.json']}
 (out/'host-records.json').write_text(json.dumps(hostrecords,indent=2)+'\n')
 rows[case]=dict(expected=expected,observed=dimensions,mode_passed=mode_pass,scoped_passed=mode_pass and c['scoped_combined_passed'],strict_passed=mode_pass and c['strict_qualification_passed'],warning_errors=a['warnings_errors'],normal_shutdown_count=a['normal_shutdown_count'],orderly_host_exit=host['passed'] and host['exit_code']==0 and not host['fallback_kill'],launch=launch,allocation={n:allocation[n] for n in ['directories','files','directory_clusters','errors','orphan_cluster_count']},protected_files=len(a['files']),hives=len(a['hives']),private_capture_count=len(artifact))
r=dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,pins=pins,changed_files=changed,scoped_passed=all(v['scoped_passed'] for v in rows.values()),strict_passed=all(v['strict_passed'] for v in rows.values()),physical_access=False,physical_qualified=False,windows1080i_qualified=False,release_qualified=False,limits='Ordinary emulated720p boot/audio/drawing/cold integrity only. All warnings remain strict failures. No hardware timing/performance or renewed live PTE proof.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

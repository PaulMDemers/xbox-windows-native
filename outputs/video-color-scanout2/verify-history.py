"""Pin all three closed outcomes, explicitly retaining the incomplete failure."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def host(s):return Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
rows=[];binaries=[]
for name,expected in [('video-color-cursor',True),('video-color-scanout',False),('video-color-scanout2',True)]:
 kit=k.parent/name;out=kit/'candidate001';v=read(kit/'verification.json');a=read(out/'audit.json');c=read(out/'closure.json')
 assert v['passed'] is expected and not v['physical_qualified'] and a['strict_qualification_passed'] and a['normal_shutdown_count']==1
 assert v['ordinary_qualified'] is (name=='video-color-cursor')
 assert sha(kit/('verify-partial.py' if not expected else 'verify.py'))==v['verifier_sha256']
 for n,h in v['pins'].items():assert sha(out/n)==h
 for n,h in read(out/'preflight.json')['sources'].items():assert sha(out/'source'/n)==h
 disk=Path(c['private_disk']);assert sha(disk)==c['private_disk_sha256'] and (disk.parent/'cleanup.json').exists()
 for n,h in c['run_metadata_sha256'].items():assert sha(disk.parent/n)==h
 f=read(kit/'fixture-candidate001.json')
 for row in f['parents']:assert sha(host(row['path']))==row['sha256']
 assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
 assert sha(ws/('work/'+name+'-candidate001-seed.qcow2'))==f['seed_sha256']
 binaries.append([sha(kit/'probe.c'),sha(kit/'artifacts/probe.exe'),sha(out/'artifacts/xwnown.dll')])
 rows.append(dict(kit=name,expected_pass=expected,actual_pass=v['passed'],ordinary_qualified=v['ordinary_qualified'],closed=True,verification_sha256=sha(kit/'verification.json'),audit_sha256=sha(out/'audit.json'),closure_sha256=sha(out/'closure.json')))
assert binaries[0]==binaries[1]==binaries[2]
dest=k/'history-review.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,meaning='Evidence consistency only; first diagnostic remains failed.',cases=rows,identical_probe_source_sha256=binaries[0][0],identical_probe_sha256=binaries[0][1],identical_driver_sha256=binaries[0][2],verifier_sha256=sha(Path(__file__))),indent=2)+'\n')
print('All three outcomes pinned; incomplete diagnostic remains FAIL')

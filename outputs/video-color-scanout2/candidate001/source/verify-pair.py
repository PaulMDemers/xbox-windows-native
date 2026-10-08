"""Recheck matched source/binaries and closed immutable evidence for both cases."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def host(s):return Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
rows=[];digests=[]
for kit in [k.parent/'video-color-cursor',k]:
 out=kit/'candidate001';v=read(kit/'verification.json');assert v['passed'] and v['cold_qualification'] and not v['physical_qualified']
 closure=read(out/'closure.json');assert sha(Path(closure['private_disk']))==closure['private_disk_sha256']
 run=Path(closure['private_disk']).parent;assert (run/'cleanup.json').exists()
 for n,h in closure['run_metadata_sha256'].items():assert sha(run/n)==h
 for n,h in read(out/'preflight.json')['sources'].items():assert sha(out/'source'/n)==h
 for n,h in v['pins'].items():assert sha(out/n)==h
 f=read(kit/'fixture-candidate001.json')
 for p in f['parents']:assert sha(host(p['path']))==p['sha256']
 assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
 assert sha(ws/('work/'+kit.name+'-candidate001-seed.qcow2'))==f['seed_sha256']
 a=read(out/'audit.json');assert a['strict_qualification_passed'] and a['normal_shutdown_count']==1
 assert all(r['matched'] for r in a['files'])
 for i,r in enumerate(a['files']):assert sha(out/'artifacts'/('ref%02d.rgb'%i))==r['sha256']
 digests.append([sha(kit/'probe.c'),sha(kit/'artifacts/probe.exe'),sha(out/'artifacts/xwnown.dll')])
 rows.append(dict(kit=kit.name,passed=True,ordinary_qualified=v['ordinary_qualified'],physical_qualified=False,verification_sha256=sha(kit/'verification.json'),closure_sha256=sha(out/'closure.json'),never_relaunch=True))
assert digests[0]==digests[1] and rows[0]['ordinary_qualified'] and not rows[1]['ordinary_qualified']
for n in ['protocol-tests.json']:
 assert read(k.parent/'video-color-cursor'/n)['passed']
assert read(k/'oracle-tests.json')['passed']
dest=k/'pair-review.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,cases=rows,identical_probe_source_sha256=digests[0][0],identical_probe_sha256=digests[0][1],identical_display_sha256=digests[0][2],verifier_sha256=sha(Path(__file__)),limits='Matched ordinary and observational debugger evidence remain distinct; no physical qualification.'),indent=2)+'\n')
print('Matched cursor pair and closed evidence PASS')

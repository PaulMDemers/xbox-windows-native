"""Check frozen inputs and closed artifacts across ordinary and diagnostic cases."""
import ast,datetime,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
read=lambda p:json.loads(p.read_text());rows=[]
cases=[(k,'control001'),(k,'candidate001')]+[(k.parent/n,'candidate001') for n in ['video-ram-scanout','video-ram-scanout2','video-ram-scanout3']]
for kit,case in cases:
 out=kit/case;closure=read(out/'closure.json');preflight=read(out/'preflight.json')
 assert sha(Path(closure['private_disk']))==closure['private_disk_sha256']
 for name,h in preflight['sources'].items():assert sha(out/'source'/name)==h
 f=read(kit/('fixture-'+case+'.json'));base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];assert sha(base)==f['fixture_sha256']
 for row in f['parents']:
  p=Path(row['path'].replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'));assert sha(p)==row['sha256']
 a=read(out/'audit.json');rows.append(dict(kit=kit.name,case=case,snapshot_files=len(preflight['sources']),private_disk_unchanged=True,cold_workload_pass=a['strict_qualification_passed'],debugger=a['debugger'],closure_sha256=sha(out/'closure.json')))
for kit in [k,k.parent/'video-ram-scanout',k.parent/'video-ram-scanout2',k.parent/'video-ram-scanout3']:
 for p in kit.glob('*.py'):ast.parse(p.read_text())
 for name,h in read(kit/'patch-review.json')['source_files'].items():assert sha(kit/'display'/name)==h
assert read(k/'pair-review.json')['passed']
assert not read(k.parent/'video-ram-scanout/verification.json')['passed']
assert not read(k.parent/'video-ram-scanout2/verification.json')['passed']
assert read(k.parent/'video-ram-scanout3/verification.json')['passed']
dest=k/'evidence-verification.json';assert not dest.exists()
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,closed_cases=rows,verifier_sha256=sha(Path(__file__)),limits='Preserves failed observers; cold PASS does not waive failed diagnostic qualification.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Frozen sources, all five closed disks, parent chains and failed/passed distinctions verified')

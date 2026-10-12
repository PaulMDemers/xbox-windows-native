"""Final frozen-input and exact-stage verification; no guest/FTP access."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'stage-review.json';assert not dest.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
frozen={}
for n in ['emulator-frozen.json','host-frozen.json']:
 rows=json.loads((k/n).read_text())
 for name,h in rows.items():
  p=Path(name);p=p if p.is_absolute() else ws/p;assert sha(p.read_bytes())==h,name
 frozen[n]=len(rows)
names=subprocess.check_output(['git','diff','--cached','--name-only','--','outputs/hd-loader311','outputs/hd-boot312'],cwd=ws,text=True).splitlines()
for name in names:
 expected=(ws/name).read_bytes();actual=subprocess.check_output(['git','show',':'+name],cwd=ws)
 assert actual==expected,name
sample=json.loads((k/'candidate001/diagnostic-captures.json').read_text())
for n,h in sample['files'].items():assert sha((Path('D:/xwn312/runs/nt5-hd312-candidate001')/n).read_bytes())==h,n
for c in ['control001','candidate001']:
 for n,h in json.loads((k/c/'private-artifacts.json').read_text()).items():assert sha((k/c/n).read_bytes())==h,n
r=dict(passed=True,frozen=frozen,exact_staged_files=len(names),diagnostic_captures_rehashed=len(sample['files']),all_private_case_artifacts_rehashed=True,scope='Evidence integrity only; candidate and strict workload results remain FALSE')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

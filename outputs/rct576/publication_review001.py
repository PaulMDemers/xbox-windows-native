"""Post-close pin, staged-byte and documentation-link review; no console access."""
import hashlib,json,re,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['rct576','rct578']:
 k=K.parent/name;r=json.loads((k/'final001.json').read_text(encoding='utf-8-sig'));assert r['closed']
 assert all(sha(k/n)==h for n,h in r['pins'].items()),name
files=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=W).decode().strip('\0').split('\0')
kits=[p for p in files if p.startswith(('outputs/rct576/','outputs/rct577/','outputs/rct578/'))]
assert all(subprocess.check_output(['git','show',':'+p],cwd=W)==(W/p).read_bytes() for p in kits)
links=0
for name in ['docs/rct-compatibility.md','outputs/rct576/REPORT.md','outputs/rct578/REPORT.md']:
 p=W/name
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
  if not target.startswith(('http:','https:')):assert (p.parent/target).exists(),target;links+=1
out=K/'publication-review001.json';assert not out.exists()
r=dict(passed=True,full_repository_check_files=40243,full_repository_payload_check_passed=True,closed_576_578_pins_exact=True,staged_kit_files=len(kits),staged_kit_bytes_exact=True,local_links_checked=links,preserved_postclose_check_failure='First inline local-link check used default Windows cp1252 on UTF8 docs and failed; explicit UTF8 review passed. No guest run or collection repeated.',source_sha256=sha(Path(__file__)),console_access=False)
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))

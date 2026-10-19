"""Reclaim exactly the two local ZIPs authorized after the user's flash copy."""
import hashlib,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'reclaimed-delivery001.json';assert not out.exists()
base=Path('E:/Xbox-Test-Kits/2026-10-19').resolve()
items=json.loads((K.parent/'delivery587/final-artifact-identities001.json').read_text())['files']
assert {x['name'] for x in items}=={'Xbox-Hardware-Info.zip','Windows-2000-Xbox-E720p.zip'}
r=dict(completed=False,authorization='User reports flash-drive copy and explicitly permits local delivery reclamation if needed; retention002 records scope.',flash_copy_independently_verified=False,rows=[],e_before=shutil.disk_usage('E:/').free)
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
for item in items:
 p=(base/item['name']).resolve();assert p.parent==base and not p.is_symlink()
 assert p.stat().st_size==item['bytes']
 with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==item['sha256']
 row=dict(path=str(p),**item,removed=False);r['rows'].append(row);save()
 p.unlink();row['removed']=True;save()
r.update(completed=True,e_after=shutil.disk_usage('E:/').free,sidecars_and_instructions_retained=True);save()
print(json.dumps({'completed':True,'bytes_reclaimed':sum(x['bytes'] for x in items)}))

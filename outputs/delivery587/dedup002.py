"""Retain one byte-identical executable and restoration catalog for closed builds."""
from pathlib import Path
import hashlib,json,shutil,subprocess
K=Path(__file__).resolve().parent;out=K/'dedup002.json';assert not out.exists()
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
rows=json.loads((K/'dedup-plan001.json').read_text())
rows=[r for r in rows if r['closures'] and all(c['closed'] for c in r['closures'])]
paths=[]
for r in rows:
    root=Path(r['root']).resolve();assert root.parent==Path('E:/')
    for c in r['closures']:
        assert sha(c['path'])==c['sha256'] and json.loads(Path(c['path']).read_text())['closed']
    for name in r['exes']:
        p=Path(name).resolve();assert p.is_relative_to(root/'instances') and p.suffix=='.exe'
        assert sha(p)=='ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3'
        paths.append(p)
assert subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-Process | Where-Object ProcessName -match '^(xemu|qemu)').Count"],timeout=20).strip()==b'0'
canonical=paths[0]
r={'completed':False,'canonical':str(canonical),'sha256':sha(canonical),'before_free':shutil.disk_usage('E:/').free,'rows':[{'path':str(p),'bytes':p.stat().st_size,'removed':False} for p in paths[1:]],'restoration':'For evidence access, copy canonical to any original path listed after verifying SHA256. Never relaunch closed runtimes. Logs, disks, firmware and configs untouched.'}
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
for row in r['rows']:
    p=Path(row['path']);assert p.resolve()==p and p.parent.is_relative_to(Path('E:/')) and p!=canonical
    assert sha(p)==sha(canonical)==r['sha256']
    p.unlink();row['removed']=True;save()
r.update(completed=True,after_free=shutil.disk_usage('E:/').free);save()
print(json.dumps({'duplicates_removed':len(r['rows']),'bytes_recovered':r['after_free']-r['before_free']}))

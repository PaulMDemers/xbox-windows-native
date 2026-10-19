"""Deduplicate closed, identical E-volume emulator executables; preserve paths."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess
K=Path(__file__).resolve().parent
out=K/'dedup001.json'
assert not out.exists()
sha=lambda p: hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
rows=json.loads((K/'dedup-plan001.json').read_text())
rows=[r for r in rows if r['closures'] and all(c['closed'] for c in r['closures'])]
paths=[]
for r in rows:
    root=Path(r['root']).resolve()
    assert root.parent==Path('E:/') and root.name.startswith('xwn')
    for c in r['closures']:
        assert sha(c['path'])==c['sha256'] and json.loads(Path(c['path']).read_text())['closed']
    for name in r['exes']:
        p=Path(name).resolve()
        assert p.is_relative_to(root/'instances') and p.suffix=='.exe' and p.stat().st_nlink==1
        assert sha(p)=='ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3'
        paths.append(p)
active=subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-Process | Where-Object ProcessName -match '^(xemu|qemu)').Count"],timeout=20).strip()
assert active==b'0',active
canonical=paths[0]
r={'completed':False,'canonical':str(canonical),'before_free':shutil.disk_usage('E:/').free,'rows':[]}
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    for p in paths[1:]:
        backup=p.with_suffix('.exe.dedup587-backup')
        assert not backup.exists() and p.resolve()==p and p.parent.is_relative_to(Path('E:/'))
        row={'path':str(p),'sha256':sha(p),'renamed':False,'linked':False,'duplicate_removed':False};r['rows'].append(row);save()
        p.rename(backup);row['renamed']=True;save()
        os.link(canonical,p);row['linked']=True;save()
        assert sha(p)==sha(backup)==row['sha256'] and os.path.samefile(p,canonical)
        backup.unlink();row['duplicate_removed']=True;save()
    r.update(completed=True,after_free=shutil.disk_usage('E:/').free);save()
except BaseException as e:
    r['error']=repr(e);save();raise
print(json.dumps({'completed':True,'duplicates':len(r['rows']),'free_bytes_gained':r['after_free']-r['before_free']}))

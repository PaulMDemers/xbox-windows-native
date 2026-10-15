"""Losslessly archive closed, superseded emulator executables; never touch disks."""
import hashlib,json,shutil,subprocess,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent
root=Path('E:/Codex-archive/xbox-windows-native').resolve()
names=[('renderer259-build001', 'xemu-renderer259.exe'), ('bridge260-build001', 'xemu-bridge260.exe'), ('reuse269-build005', 'xemu-reuse269.exe'), ('ledger265-build003', 'xemu-ledger265.exe'), ('boundary278-build002', 'xemu-boundary278.exe'), ('runtime281-build001', 'xemu-runtime281.exe')]
out=K/'archive-executables002.json';assert not out.exists()
active=subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-Process xemu* -ErrorAction SilentlyContinue).Count"],text=True).strip()
assert active=='0'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rows=[]
for directory,name in names:
    p=(root/directory/name).resolve();assert p.is_relative_to(root) and p.is_file() and p.suffix=='.exe' and not p.is_symlink()
    dest=p.with_suffix('.exe.retained.zip');assert not dest.exists()
    size=p.stat().st_size;original=sha(p)
    assert shutil.disk_usage(root).free-40*1024**2>=20*1024**3
    with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:z.write(p,name)
    with zipfile.ZipFile(dest) as z:
        assert z.namelist()==[name] and z.getinfo(name).file_size==size
        with z.open(name) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==original
    row=dict(original=str(p),archive=str(dest),original_sha256=original,archive_sha256=sha(dest),
             original_bytes=size,archive_bytes=dest.stat().st_size,status='verified-before-removal')
    rows.append(row);out.write_text(json.dumps(rows,indent=2)+'\n')
    assert sha(p)==original;p.unlink();row['status']='closed-executable-retained-losslessly-in-zip'
    out.write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(dict(files=len(rows),bytes_reclaimed=sum(r['original_bytes']-r['archive_bytes'] for r in rows),
                     free_bytes=shutil.disk_usage(root).free,restore='Extract the single named member to original path and verify original_sha256 before future reuse.')))

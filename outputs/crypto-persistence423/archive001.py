"""Lossless closed-executable retention using C staging; never move backing disks."""
import hashlib,json,shutil,subprocess,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
root=Path('E:/Codex-archive/xbox-windows-native').resolve();temp=Path('C:/xwn423/archive001')
out=K/'archive001.json';assert not out.exists() and not temp.exists()
assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process xemu* -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0'
items=[('phase241-build001','xemu-preserve241.exe','gpu-preserve-empty241/build001.json'),('phase242-build001','xemu-inventory242.exe','gpu-reference-pair242/build001.json'),('phase242-build004','xemu-inventory242.exe','gpu-reference-pair242/build004.json')]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
reserve=20*1024**3;temp.mkdir(parents=True);rows=[]
def save():out.write_text(json.dumps(rows,indent=2)+'\n')
for folder,name,manifest in items:
 p=(root/folder/name).resolve();assert p.is_relative_to(root) and p.is_file() and not p.is_symlink() and p.suffix=='.exe'
 original=sha(p);expected=json.loads((W/'outputs'/manifest).read_text());assert original==expected['executable_sha256']
 dest=p.with_suffix('.exe.retained.zip');staged=temp/(folder+'.zip');assert not dest.exists() and not staged.exists()
 assert shutil.disk_usage(temp).free>=reserve+64*1024**2
 row={'original':str(p),'original_sha256':original,'original_bytes':p.stat().st_size,'build_manifest':manifest,'staging':str(staged),'archive':str(dest),'status':'compressing-original-retained'};rows.append(row);save()
 with zipfile.ZipFile(staged,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  with p.open('rb') as src,z.open(name,'w') as member:
   while b:=src.read(1024**2):
    assert shutil.disk_usage(temp).free>=reserve+4*1024**2
    member.write(b)
 with zipfile.ZipFile(staged) as z:
  assert z.namelist()==[name] and z.getinfo(name).file_size==row['original_bytes']
  with z.open(name) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==original
 row.update(archive_sha256=sha(staged),archive_bytes=staged.stat().st_size,status='staging-readback-exact-original-retained');save()
 assert sha(p)==original and shutil.disk_usage(root).free+row['original_bytes']-row['archive_bytes']>=reserve
 p.unlink();row['status']='original-removed-verified-staging-retained';save()
 with staged.open('rb') as src,dest.open('xb') as dst:shutil.copyfileobj(src,dst,1024**2)
 assert sha(dest)==row['archive_sha256']
 with zipfile.ZipFile(dest) as z:
  with z.open(name) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==original
 row['status']='archive-readback-exact';save();staged.unlink();row['staging_removed']=True;save()
print(json.dumps({'files':len(rows),'bytes_reclaimed':sum(r['original_bytes']-r['archive_bytes'] for r in rows),'C_free':shutil.disk_usage(temp).free,'E_free':shutil.disk_usage(root).free,'backing_disks_moved':False}))

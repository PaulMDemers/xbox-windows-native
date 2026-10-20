"""Compress retained335 raw source in place; preserve every byte and path."""
import datetime,hashlib,json,pathlib,shutil,subprocess
K=pathlib.Path(__file__).resolve().parent;out=K/'compression002.json';assert not out.exists()
p=pathlib.Path('E:/xwn335/seed003/stock10gb.raw').resolve()
assert p==pathlib.Path('E:/xwn335/seed003/stock10gb.raw') and not p.is_symlink()
assert json.loads((K.parent/'stock-runtime335/emu001/closure.json').read_text())['closed']
assert p.stat().st_size==10000000000
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
r=dict(completed=False,path=str(p),bytes=p.stat().st_size,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),free_before=shutil.disk_usage('E:/').free,scope='Lossless NTFS compression of retained source bytes only; no guest mount/boot, deletion, path or backing change.')
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 assert shutil.disk_usage('E:/').free-32*1024**2>=20*1024**3
 r['sha256_before']=sha(p);save()
 run=subprocess.run(['compact.exe','/C','/I','/Q',str(p)],capture_output=True,text=True,timeout=600)
 r.update(returncode=run.returncode,stdout=run.stdout);save();assert run.returncode==0
 assert p.stat().st_size==r['bytes']
 r['sha256_after']=sha(p);assert r['sha256_after']==r['sha256_before']
 r.update(completed=True,free_after=shutil.disk_usage('E:/').free)
finally:save()
print(json.dumps({n:r[n] for n in ['completed','free_before','free_after']}))

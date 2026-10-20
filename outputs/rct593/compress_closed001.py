"""Lossless NTFS compression of closed owned evidence; no path/byte deletion."""
import datetime,hashlib,json,pathlib,shutil,subprocess
K=pathlib.Path(__file__).resolve().parent
out=K/'compression001.json';assert not out.exists()
sha=lambda p:hashlib.file_digest(pathlib.Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
check=subprocess.run(['wsl','-d','Ubuntu','-u','paul','--','pgrep','-a','-f','^(/[^ ]*/)?(qemu-system[^ ]*|xemu)( |$)'],capture_output=True,text=True,timeout=30)
assert check.returncode==1,check.stdout
win=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process -Name 'qemu*','xemu*' -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True,timeout=30)
assert win.returncode==0 and win.stdout.strip()=='0'
r=dict(completed=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),before_free_bytes=shutil.disk_usage('C:/').free,rows=[],scope='NTFS lossless compression, exact path and byte preservation. No guest mount, boot, recollection, deletion or backing-chain change.')
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for n in [589,574,573,575,568,572]:
  d=K.parent/f'rct{n}';final=read(d/'final001.json');state=read(d/'ntfs-phase1.json');cold=read(d/'ntfs-cold1-002.json')
  assert final['closed'] and state['closed'] and cold['complete']
  p=pathlib.Path(f'C:/xwn{n}/pc001/disk.qcow2').resolve()
  assert p==pathlib.Path(f'C:/xwn{n}/pc001/disk.qcow2') and p.is_file() and not p.is_symlink()
  h=sha(p);assert h==state['disk_sha256']==cold['disk_sha256']
  row=dict(path=str(p),bytes=p.stat().st_size,sha256=h,already_compressed=bool(p.stat().st_file_attributes&0x800),verified=False)
  r['rows'].append(row);save()
  if not row['already_compressed']:
   assert shutil.disk_usage('C:/').free-32*1024**2>=20*1024**3
   run=subprocess.run(['compact.exe','/C','/I','/Q',str(p)],capture_output=True,text=True,timeout=180)
   row.update(exit_code=run.returncode,compression_stdout=run.stdout);save();assert run.returncode==0
  assert p.stat().st_size==row['bytes'] and sha(p)==h
  row.update(verified=True,compressed=bool(p.stat().st_file_attributes&0x800),free_bytes=shutil.disk_usage('C:/').free);save()
  print(n,row['compressed'],row['free_bytes'],flush=True)
  if row['free_bytes']>=22*1024**3:break
 r.update(completed=True,after_free_bytes=shutil.disk_usage('C:/').free)
finally:save()

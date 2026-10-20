"""Lossless archive of verified closed leaf bytes; never mount or boot them."""
from pathlib import Path
from compression import zstd
import datetime,hashlib,json,shutil,struct
K=Path(__file__).resolve().parent;out=K/'archive001.json';assert not out.exists()
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
inv=json.loads((K/'backing-inventory001.json').read_text());assert inv['completed'] and not inv['pending']
targets=[Path(f'C:/xwn{n}/pc001/disk.qcow2').resolve() for n in (612,)]
parents=[];headers=0
for drive in ('C:/','E:/'):
 for root in Path(drive).glob('xwn*'):
  if not root.is_dir():continue
  for p in root.rglob('*.qcow2'):
   with p.open('rb') as f:
    h=f.read(24);assert h[:4]==b'QFI\xfb',str(p)
    offset,length=struct.unpack('>QI',h[8:20]);assert length<4096
    if length:
     assert offset+length<=p.stat().st_size
     f.seek(offset);back=f.read(length).decode().replace('/mnt/c/','C:/').replace('/mnt/e/','E:/')
     if not back.startswith('/home/'):parents.append(str((p.parent/back).resolve()))
   headers+=1
for p in targets:
 assert str(p) not in parents and not p.is_symlink()
 assert not any(row['parent']=='/mnt/c/'+p.as_posix()[3:] for row in inv['qcow'])
base=Path('E:/xwn616/archives');base.mkdir(parents=True,exist_ok=False)
r=dict(completed=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),c_before=shutil.disk_usage('C:/').free,e_before=shutil.disk_usage('E:/').free,windows_headers=headers,wsl_inventory_sha256=sha(K/'backing-inventory001.json'),rows=[],
 scope='Exact lossless host-byte archive with roundtrip hash verification. No filesystem mount, guest boot, recollection or new backing parent. Restore only to the exact original path for evidence recovery; closed runtimes stay closed.')
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for disk in targets:
  n=int(disk.parts[1][3:]);D=K.parent/f'rct{n}'
  final=json.loads((D/'final001.json').read_text());runtime=json.loads((D/'ntfs-phase1.json').read_text());cold=json.loads((D/'ntfs-cold1-002.json').read_text())
  assert final['closed'] and (final.get('cleanup_passed') or final['passed']) and runtime['closed'] and cold['complete']
  assert runtime['exit_code']==0 and cold['normal_shutdown_delta']==1
  assert not any(runtime.get(k) for k in ['host_quit','host_terminate','host_kill','deadline','space_stop'])
  expected=runtime['disk_sha256'];assert sha(disk)==expected==cold['disk_sha256']
  archive=base/f'rct{n}-pc001-disk.qcow2.zst';assert not archive.exists()
  row=dict(original_path=str(disk),archive=str(archive),bytes=disk.stat().st_size,sha256=expected,verified=False,original_removed=False);r['rows'].append(row);save()
  assert shutil.disk_usage('E:/').free-disk.stat().st_size-16*1024**2>=20*1024**3
  with disk.open('rb') as src,zstd.open(archive,'xb',level=6) as dst:
   while block:=src.read(1024*1024):
    assert shutil.disk_usage('E:/').free>20*1024**3+16*1024**2
    dst.write(block)
  h=hashlib.sha256();count=0
  with zstd.open(archive,'rb') as src:
   while block:=src.read(1024*1024):h.update(block);count+=len(block)
  assert count==row['bytes'] and h.hexdigest()==expected and sha(disk)==expected
  row.update(verified=True,archive_bytes=archive.stat().st_size,archive_sha256=sha(archive));save()
  assert n in (612,) and disk.resolve()==Path(f'C:/xwn{n}/pc001/disk.qcow2').resolve()
  disk.unlink();row['original_removed']=True;save()
  print(json.dumps(dict(archived=n,archive_bytes=row['archive_bytes'],c_free=shutil.disk_usage('C:/').free)),flush=True)
 r.update(completed=True,c_after=shutil.disk_usage('C:/').free,e_after=shutil.disk_usage('E:/').free)
except BaseException as e:r['error']=repr(e);raise
finally:save()

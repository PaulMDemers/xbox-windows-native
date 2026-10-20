"""Exact archives of owned closed evidence, with backing references excluded."""
import hashlib,json,pathlib,shutil,struct
from compression import zstd
K=pathlib.Path(__file__).resolve().parent;out=K/'archive003.json';assert not out.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
inv=read(K/'backing-inventory001.json');assert inv['completed'] and not inv['pending']
parents={r['parent'] for r in inv['qcow'] if r['parent']};count=0
for drive in ['C:/','E:/']:
 for root in pathlib.Path(drive).glob('xwn*'):
  if not root.is_dir():continue
  for p in root.rglob('*.qcow2'):
   with p.open('rb') as f:
    h=f.read(24);assert h[:4]==b'QFI\xfb';offset,length=struct.unpack('>QI',h[8:20]);assert length<4096
    if length:
     f.seek(offset);back=f.read(length).decode().replace('/mnt/c/','C:/').replace('/mnt/e/','E:/')
     parents.add(str((p.parent/back).resolve()))
   count+=1
base=pathlib.Path('E:/xwn593/archives');base.mkdir(parents=True,exist_ok=False)
targets=[pathlib.Path('E:/xwn335/seed003/stock10gb.raw')]+[pathlib.Path(f'C:/xwn{n}/pc001/disk.qcow2') for n in [589,574,573,575,568,572,566,570,571,569]]
r=dict(completed=False,rows=[],windows_qcow_headers=count,wsl_inventory_sha256=sha(K/'backing-inventory001.json'),scope='Lossless archive, no guest reopen/recollection or backing-chain change; exact original paths recorded for evidence restoration only.')
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for source in targets:
  p=source.resolve();assert p==source and not p.is_symlink() and p.is_file()
  linux='/mnt/'+str(p)[0].lower()+p.as_posix()[2:]
  assert str(p) not in parents and linux not in parents
  n=int(p.parts[1][3:])
  if n==335:
   rec=read(K/'compression002.json');assert rec['completed'];expected=rec['sha256_after'];name='stock335-seed003-stock10gb.raw.zst'
   assert read(K.parent/'stock-runtime335/emu001/closure.json')['closed']
  else:
   d=K.parent/f'rct{n}';state=read(d/'ntfs-phase1.json');cold=read(d/'ntfs-cold1-002.json')
   assert read(d/'final001.json')['closed'] and state['closed'] and cold['complete']
   expected=state['disk_sha256'];assert expected==cold['disk_sha256'];name=f'rct{n}-pc001-disk.qcow2.zst'
  assert sha(p)==expected
  archive=base/name;assert not archive.exists()
  row=dict(original_path=str(p),archive=str(archive),bytes=p.stat().st_size,sha256=expected,verified=False,original_removed=False);r['rows'].append(row);save()
  with p.open('rb') as src,zstd.open(archive,'xb',level=6) as dst:
   while block:=src.read(1024*1024):
    assert shutil.disk_usage('E:/').free-2*1024**2>=20*1024**3+16*1024**2
    dst.write(block)
  digest=hashlib.sha256();length=0
  with zstd.open(archive,'rb') as src:
   while block:=src.read(1024*1024):digest.update(block);length+=len(block)
  assert digest.hexdigest()==expected and length==row['bytes'] and sha(p)==expected
  row.update(verified=True,archive_bytes=archive.stat().st_size,archive_sha256=sha(archive));save()
  assert p.resolve()==source and p.parent==source.parent
  p.unlink();row.update(original_removed=True,c_free=shutil.disk_usage('C:/').free,e_free=shutil.disk_usage('E:/').free);save();print(n,row['c_free'],row['e_free'],flush=True)
  if n!=335 and row['c_free']>=22*1024**3:break
 r['completed']=True
finally:save()

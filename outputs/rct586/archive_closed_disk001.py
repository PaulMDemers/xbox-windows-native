"""Lossless bounded archive of a closed disposable leaf, preserving every byte."""
import argparse,hashlib,json,os,shutil,struct,time,subprocess
from compression import zstd
from pathlib import Path
K=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('attempt',type=int,choices=[585,584,582,581,578]);a=p.parse_args()
n=a.attempt;D=K.parent/f'rct{n}';root=Path(f'C:/xwn{n}/pc001').resolve();disk=root/'disk.qcow2';archive=root/'disk.qcow2.zst'
out=K/f'disk-archive-{n}-001.json';assert not out.exists() and not archive.exists()
assert disk.resolve()==disk and disk.is_file()
final=json.loads((D/'final001.json').read_text());runtime=json.loads((D/'ntfs-phase1.json').read_text());cold=json.loads((D/'ntfs-cold1-002.json').read_text())
assert final['closed'] and runtime['closed'] and cold['complete']
sha=lambda f:hashlib.file_digest(Path(f).open('rb'),'sha256').hexdigest()
expected=runtime['disk_sha256'];assert sha(disk)==expected==cold['disk_sha256']
# Known descendants must never use a closed runtime. Inspect raw QCOW headers
# without starting, mounting or collecting any guest.
references=[];inspected=0
for base in list(Path('C:/').glob('xwn[0-9]*'))+list(Path('E:/').glob('xwn[0-9]*')):
    for candidate in base.rglob('*.qcow2'):
        with candidate.open('rb') as f:
            h=f.read(24)
            if len(h)<24 or h[:4]!=b'QFI\xfb':continue
            offset,length=struct.unpack('>QI',h[8:20]);inspected+=1
            if not length:continue
            assert length<4096 and offset<candidate.stat().st_size
            f.seek(offset);back=f.read(length).decode()
        back=back.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/')
        if not back.startswith('/home/'):
            parent=Path(back) if Path(back).is_absolute() else candidate.parent/back
            if parent.resolve()==disk:references.append(str(candidate))
assert not references,'Disk is a backing dependency'
linux_check="""import json,struct
from pathlib import Path
running=[str(p) for p in Path('/proc').glob('[0-9]*/exe') if p.exists() and p.resolve().name.startswith('qemu-system')]
assert not running,running
rows=[]
for p in Path('/home/paul/xbox-windows-native').rglob('*.qcow2'):
 with p.open('rb') as f:
  h=f.read(24)
  if len(h)<24 or h[:4]!=b'QFI\\xfb':continue
  offset,length=struct.unpack('>QI',h[8:20])
  if not length:continue
  assert length<4096
  f.seek(offset);back=f.read(length).decode()
  rows.append(str((p.parent/back).resolve()))
print(json.dumps(rows))
"""
linux_parents=json.loads(subprocess.check_output(['wsl','-d','Ubuntu','-u','paul','--','python3','-c',linux_check],timeout=90))
assert f'/mnt/c/xwn{n}/pc001/disk.qcow2' not in linux_parents
# Complete cold manifests, extracted hives/events, private captures and runner
# collections stay in place. This is host-byte archival, not runtime reopening.
assert (root/'cold0-002/manifest.json').is_file() and (root/'cold1-002/manifest.json').is_file() and (root/'collection001').is_dir()
r=dict(attempt=n,completed=False,source=str(disk),archive=str(archive),bytes=disk.stat().st_size,sha256=expected,before_free_bytes=shutil.disk_usage('C:/').free,known_ce_qcow_headers_checked=inspected,wsl_backing_headers_checked=len(linux_parents),backing_references=references,archive_verified=False,original_removed=False,scope='Lossless host-byte archive of a closed disposable leaf. No guest reopen, recollection or parent reuse. All disk bytes retained and verified; restore exact original path only for evidence access, never a new guest. Immutable404 and private recovery untouched.')
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    with disk.open('rb') as src,zstd.open(archive,'xb',level=6) as dst:
        while block:=src.read(1024*1024):
            assert shutil.disk_usage('C:/').free>=20*1024**3+16*1024**2,'Bounded write reserve'
            dst.write(block)
    h=hashlib.sha256();count=0
    with zstd.open(archive,'rb') as src:
        while block:=src.read(1024*1024):h.update(block);count+=len(block)
    assert count==r['bytes'] and h.hexdigest()==expected and sha(disk)==expected
    r.update(archive_verified=True,archive_bytes=archive.stat().st_size,archive_sha256=sha(archive));save()
    assert disk.resolve()==root/'disk.qcow2' and root==Path(f'C:/xwn{n}/pc001').resolve()
    disk.unlink();r.update(original_removed=True,completed=True,after_free_bytes=shutil.disk_usage('C:/').free);save()
except BaseException as e:r['error']=repr(e);save();raise
print(json.dumps({k:r[k] for k in ['attempt','completed','archive_bytes','before_free_bytes','after_free_bytes']}))

"""Archive closed disposable leaf bytes on E; verify roundtrip before removing C copy."""
from pathlib import Path
from compression import zstd
import hashlib,json,os,shutil,struct,time
K=Path(__file__).resolve().parent;out=K/'archive001.json';assert not out.exists()
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
inv=json.loads((K/'backing-inventory001.json').read_text());assert inv['completed'] and not inv['pending']
targets=[Path(f'C:/xwn{n}/pc001/disk.qcow2').resolve() for n in (586,)]
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
                    if not back.startswith('/home/'):
                        parent=(p.parent/back).resolve();parents.append(str(parent))
            headers+=1
for p in targets:
    assert str(p) not in parents
    linux='/mnt/c/'+p.as_posix()[3:]
    assert not any(row['parent']==linux for row in inv['qcow'])
base=Path('E:/xwn589/archives');base.mkdir(parents=True,exist_ok=False)
r={'completed':False,'c_before':shutil.disk_usage('C:/').free,'e_before':shutil.disk_usage('E:/').free,'windows_headers':headers,'wsl_inventory_sha256':sha(K/'backing-inventory001.json'),'rows':[],'scope':'Exact lossless host-byte archive, no guest mount/boot/recollection. Original path stored for evidence restoration only. Closed runtime must never be relaunched or parented.'}
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    for disk in targets:
        n=int(disk.parts[1][3:]);D=K.parent/f'rct{n}'
        final=json.loads((D/'final002.json').read_text());runtime=json.loads((D/'ntfs-phase2.json').read_text());cold=json.loads((D/'ntfs-cold2-002.json').read_text())
        assert final['closed'] and runtime['closed'] and cold['complete']
        expected=runtime['disk_sha256'];assert sha(disk)==expected==cold['disk_sha256']
        archive=base/f'rct{n}-pc001-disk.qcow2.zst';assert not archive.exists()
        row={'original_path':str(disk),'archive':str(archive),'bytes':disk.stat().st_size,'sha256':expected,'verified':False,'original_removed':False};r['rows'].append(row);save()
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
        assert disk.resolve()==Path(f'C:/xwn{n}/pc001/disk.qcow2').resolve() and n in (586,)
        disk.unlink();row['original_removed']=True;save()
        print(json.dumps({'archived':n,'archive_bytes':row['archive_bytes'],'C_free':shutil.disk_usage('C:/').free}),flush=True)
    r.update(completed=True,c_after=shutil.disk_usage('C:/').free,e_after=shutil.disk_usage('E:/').free)
except BaseException as e:r['error']=repr(e);raise
finally:save()

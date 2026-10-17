"""Fresh, small, nonbootable raw FATX fixture with real mkntfs payload. No console."""
import hashlib,importlib.util,json,os,struct,subprocess,sys,uuid
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/e/xwn429/fixture001')
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sys.path.insert(0,str(K));from reader import Volume
from ntfs_header import validate
sys.path.insert(0,str(W/'outputs/image-handoff427'));from projection import Header,decode
sys.path.insert(0,'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts');import fatx_stage_boot as fatx
sys.path.insert(0,str(W/'outputs/native-windows-fatx-runtime'));from bulk_fatx import Writer
assert not P.exists() and not (K/'fixture001.json').exists()
space=require_space(P,20+160/1024)
tools=Path('/home/paul/xbox-windows-native/toolchains/offline-disk/root')
mk=tools/'usr/sbin/mkntfs';cp=tools/'usr/sbin/ntfscp';cat=tools/'usr/bin/ntfscat'
env=dict(os.environ,LD_LIBRARY_PATH=str(tools/'usr/lib/x86_64-linux-gnu'))
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
r=dict(passed=False,space=space,physical_access=False,guest_launched=False,tools={str(p):sha(p) for p in (mk,cp,cat)},inputs={n:sha(K/n) for n in ('reader.py','ntfs_header.py','fixture001.py')})
P.mkdir(parents=True)
out=K/'fixture001.json'
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    start=1048576;size=64*1024**2;disk_bytes=start+size;cluster=4096
    fat_size=((size//cluster)*2+4095)&~4095
    file_start=start+4096+fat_size+cluster;inner_start=file_start+65536
    image=P/'inner.ntfs';inner_bytes=32*1024**2
    with image.open('xb') as f:f.truncate(inner_bytes)
    cmd=[str(mk),'-F','-Q','-s','512','-c','4096','-p',str(inner_start//512),'-L','XWN429',str(image)]
    r['format_command']=cmd;save()
    with (P/'mkntfs.log').open('xb') as f:subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
    payload=bytes((i*73+19)%256 for i in range(8193));(P/'payload.bin').write_bytes(payload)
    longname='key_'+('x'*65);assert len(longname)==69
    with (P/'ntfscp.log').open('xb') as f:subprocess.run([str(cp),str(image),str(P/'payload.bin'),'/'+longname],env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
    assert subprocess.check_output([str(cat),str(image),'/'+longname],env=env,timeout=30)==payload
    inner=image.read_bytes();serial=struct.unpack_from('<Q',inner,72)[0]
    r['ntfs_geometry']=validate(inner[:512],inner[-512:],len(inner),inner_start,serial)
    ident=uuid.uuid4().bytes
    h=Header(ident,disk_bytes,start,size,file_start,65536+inner_bytes,65536,inner_bytes,serial)
    blob=h.encode()+bytes(65536-512)+inner
    disk=P/'fatx.raw'
    with disk.open('xb') as f:f.truncate(disk_bytes)
    fatx.PARTITIONS['T']=(start,size)
    with disk.open('r+b') as f:
        # Owned miniature test filesystem, not a stock Xbox disk or boot image.
        f.seek(0);f.write(bytes([0x6d])*start)
        head=bytearray(4096);head[:4]=b'FATX';struct.pack_into('<III',head,4,429,8,1);f.seek(start);f.write(head)
        table=bytearray(fat_size);struct.pack_into('<HH',table,0,0xfff8,0xffff);f.write(table)
        f.write(bytes([255])*cluster);f.flush()
        writer=Writer(f,fatx.open_partition(f,disk,'T'))
        result=writer.write('WINDOWS.IMG',blob);writer.flush()
        assert writer.read('WINDOWS.IMG')==blob
    original=sha(disk)
    with disk.open('rb') as f:
        def read(at,n):f.seek(at);return f.read(n)
        v=Volume(read,disk_bytes,start,size).scan();file=v.contiguous(b'/windows.img')
        assert file.size==len(blob) and file.starts[0]==file_start
        header=decode(v.fetch(file_start,512),ident);assert header==h
        validate(v.fetch(inner_start,512),v.fetch(inner_start+inner_bytes-512,512),inner_bytes,inner_start,serial)
        projected=P/'projected.ntfs'
        with projected.open('xb') as target:
            for at in range(0,inner_bytes,65536):
                b=v.fetch(inner_start+at,min(65536,inner_bytes-at))
                assert b==inner[at:at+len(b)];target.write(b)
        f.seek(0);assert f.read(start)==bytes([0x6d])*start
        r['discovery']=dict(directories=v.directory_count,entries=v.entry_count,owned_clusters=sum(v.owned),image_clusters=len(file.chain),bytes_read=v.read_bytes,all_image_bytes_exact=True,file_start=file_start,inner_start=inner_start)
    assert sha(image)==sha(projected) and sha(disk)==original
    assert subprocess.check_output([str(cat),str(projected),'/'+longname],env=env,timeout=30)==payload
    r.update(passed=True,disk_sha256=original,ntfs_sha256=sha(image),payload_sha256=sha(P/'payload.bin'),long_name_bytes=len(longname),raw_disk_unchanged_by_reader=True,outside_partition_marker_exact=True,files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in P.iterdir()},scope='Real formatted NTFS file inside new miniature FATX bytes, independent writer/read/cat. No Windows mount, boot, live exclusion or native memory/IRP qualification.')
except BaseException as e:r['error']=repr(e);raise
finally:save()
print(json.dumps({'passed':r['passed'],'discovery':r.get('discovery')}))

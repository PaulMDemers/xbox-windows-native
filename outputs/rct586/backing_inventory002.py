"""Bounded native inventory; no VM, mount, or guest-file collection."""
import datetime,json,struct,subprocess,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'backing-inventory002.json'
assert not out.exists()
r=dict(completed=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False)
try:
    active=[str(p) for p in Path('/proc').glob('[0-9]*/exe') if p.exists() and p.resolve().name.startswith('qemu-system')]
    assert not active,active
    result=subprocess.run(['timeout','45','find','/home/paul/xbox-windows-native','-type','f','-name','*.qcow2','-print0'],capture_output=True,timeout=50)
    r['find_exit']=result.returncode
    assert result.returncode==0,result.stderr.decode(errors='replace')[:500]
    names=[x.decode() for x in result.stdout.split(b'\0') if x];parents=[]
    for name in names:
        p=Path(name)
        with p.open('rb') as f:
            h=f.read(24);assert h[:4]==b'QFI\xfb'
            offset,length=struct.unpack('>QI',h[8:20]);assert length<4096
            if not length:continue
            f.seek(offset);back=f.read(length).decode();parents.append(str((p.parent/back).resolve()))
    private=Path('/mnt/c/xwn586/backing-inventory002-private.json');assert not private.exists()
    private.write_text(json.dumps(dict(paths=names,parents=parents),indent=2)+'\n')
    targets=[f'/mnt/c/xwn{n}/pc001/disk.qcow2' for n in [585,584,582,581,578]]
    r.update(completed=True,files=len(names),parents=len(parents),target_references=[x for x in parents if x in targets],private_inventory_sha256=hashlib.sha256(private.read_bytes()).hexdigest(),private_inventory=str(private))
except BaseException as e:r['error']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))

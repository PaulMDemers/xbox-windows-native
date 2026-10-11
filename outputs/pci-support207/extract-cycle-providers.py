"""Read actual native001 provider DLLs and installed payload after owned closure."""
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[1]
sys.path.insert(0,str(repo/'outputs/setup-wizard-automation201'))
from common import ColdIO,readers,read,sha,save
assert read(k/'native001/run.json')['closed']
out=k/'artifacts/providers002';assert not out.exists();out.mkdir()
disk=k/'native001/artifacts/runtime/hdd.qcow2';r=dict(disk_sha256=sha(disk),files={})
with ColdIO(disk) as io:
    w=readers(io,disk)['F']
    for name in ('kernel32.dll','setupapi.dll','user32.dll','advapi32.dll','ntdll.dll'):
        data=w.read('winnt/system32/'+name);p=out/name;p.write_bytes(data);r['files'][name]=sha(p)
    for path in ('winnt/system32/drivers/xwnsmb.sys','winnt/inf/oem3.inf'):
        data=w.read(path);r['files'][path]=hashlib.sha256(data).hexdigest()
assert r['files']['winnt/system32/drivers/xwnsmb.sys']=='15dba6948fd9184d09d94a4ab1517c2b86e8497af0e361b41359d1c20fc8057e'
assert r['files']['winnt/inf/oem3.inf']=='c9983c46f645005bd4aaecc5060203dd5703d350d9ba045f7e40eecfe004b045'
save(k/'providers002.json',r)

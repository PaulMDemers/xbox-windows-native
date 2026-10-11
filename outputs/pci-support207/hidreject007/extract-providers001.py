"""Extract and compare exact HID providers in immutable source and closed006 disk."""
import contextlib,json,os,sys,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[2]
assert os.environ.get('XWN_BUILD_LEASE')=='held'
sys.path.insert(0,str(repo/'outputs/setup-wizard-automation201'))
from common import ColdIO,readers,read,sha,save
old=k.parent/'inputtrace006/veto001';f=read(old/'fixture.json');run=read(old/'run.json')
assert run['closed'] and run['source_unchanged']
source=old/'artifacts/source.qcow2';disk=old/'artifacts/runtime/hdd.qcow2'
assert sha(source)==f['source_sha256']
out=k/'artifacts/providers001';assert not out.exists();out.mkdir(parents=True)
rows=[]
with contextlib.ExitStack() as stack:
    rr=[readers(stack.enter_context(ColdIO(p)),p) for p in (source,disk)]
    for name in ('hidclass.sys','kbdhid.sys','mouhid.sys','hidusb.sys'):
        path='winnt/system32/drivers/'+name;a,b=[r['F'].read(path) for r in rr];assert a==b,name
        p=out/name;p.write_bytes(a);rows.append(dict(name=name,guest_path=path,sha256=sha(p),source_equals_closed_runtime=True))
assert sha(source)==f['source_sha256']
save(k/'providers001.json',dict(scope=__doc__,physical_access=False,source_sha256=f['source_sha256'],source=str(source),closed_runtime=str(disk),run_sha256=sha(old/'run.json'),script_sha256=sha(Path(__file__)),providers=rows))
print(json.dumps(rows,indent=2))

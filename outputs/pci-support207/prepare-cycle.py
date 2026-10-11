"""Stage one restart probe onto a fresh copy of installed native001; no binding edits."""
import json,os,shutil,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[1]
assert os.environ.get('XWN_BUILD_LEASE')=='held'
sys.path.insert(0,str(repo/'outputs/setup-wizard-automation201'))
from common import ColdIO,readers,read,save,sha,hive,scan,m,STARTUP
from restore import restore
assert read(k/'native001/run.json')['closed'] and read(k/'native001/audit.json')['integrity_passed']
assert read(k/'cycle001-review.json')['passed']
build=read(k/'cycle001-build.json');exe=k/'artifacts/cycle001/cycle.exe'
assert sha(exe)==build['sha256'] and sha(k/'xwncycle.c')==build['source_sha256']
out=k/'native002';assert not out.exists();out.mkdir();art=out/'artifacts';art.mkdir()
base=k/'native001/artifacts/runtime/hdd.qcow2';source=art/'source.qcow2';basehash=sha(base)
files=dict(read(k/'native001/fixture.json')['files'])
with ColdIO(base) as io:
    rr=readers(io,base)
    for name,digest in list(files.items()):
        v,path=name.split('/',1);actual=m.sha(rr[v].read(path))
        if not path.lower().startswith('winnt/system32/config/') and path.lower() not in ('winnt/setupapi.log','winnt/system32/xwn-video-trace.bin'):assert actual==digest,name
        files[name]=actual
    for path in ('winnt/system32/drivers/xwnsmb.sys','winnt/inf/oem3.inf','xwnpci207/install.log','xwnpci207/probe-00.log'):
        files['F/'+path]=m.sha(rr['F'].read(path))
shutil.copyfile(base,source);assert sha(source)==basehash
m.target=source;io=m.SliceIO(source);w=m.Writer(io,m.fatx.open_partition(io,source,'F'))
data=exe.read_bytes();w.write('xwnpci207/cycle.exe',data);files['F/xwnpci207/cycle.exe']=m.sha(data)
data=b'@echo off\r\nC:\\xwnpci207\\cycle.exe\r\nexit\r\n'
restore(w,STARTUP,data);files['F/'+STARTUP]=m.sha(data);w.flush()
hives=[]
with ColdIO(source) as io:
    rr=readers(io,source)
    for name,digest in files.items():
        v,path=name.split('/',1);assert m.sha(rr[v].read(path))==digest,name
    for name in ('system','software','default','sam','security'):
        p=art/('before-'+name);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));hives.append(dict(name=name,**hive(p)))
scan(source,art/'before');allocation=read(art/'allocation.json')
assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
assert sha(base)==basehash
save(out/'fixture.json',dict(scope=__doc__,physical_access=False,base=str(base),base_sha256=basehash,source=str(source),source_sha256=sha(source),standalone=True,files=files,hives=hives,no_registry_edits=True,no_reinstallation=True))
print('native002 prepared from actual installed state')

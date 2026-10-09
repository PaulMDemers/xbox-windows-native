"""NEW cancellation child only after CLOSED passive002 actual observation/fullcold integrity."""
import subprocess
from common import *
from restore import restore
case='cancel003';out=k/case;assert not out.exists()
assert read(k/'observe002/closure.json')['closed'] and read(k/'observe002/audit.json')['diagnostic_usable']
assert read(k/'observe002/observation.json')['passive_observation_passed']
f=read(k/'fixture-observe002.json');base=Path(f['fixture_path_linux']);assert sha(base)==f['fixture_sha256']
review=read(k/'guardian-review003.json');assert review['passed']
observer=read(k.parent/'device-observation188/build-review.json');assert observer['passed']
observer_binary=k.parent/'device-observation188/artifacts/build003/observer.exe'
assert sha(observer_binary)==observer['binary_sha256']
assert sha(k.parent/'device-observation188/probe003.c')==observer['source_sha256']
helper=read(k/'build-review002.json');assert helper['passed']
assert sha(k/'artifacts/build002/wizard.exe')==helper['binary_sha256']
assert sha(k/'wizard002.c')==helper['source_sha256']
assert sha(k/'artifacts/guardian003/guardian.exe')==review['binary_sha256']
assert sha(k/'guardian003.c')==review['source_sha256']
root=Path('/mnt/e/Codex-archive/xbox-windows-native/wizard201')
target=root/'cancel003-preparation.qcow2';source=root/'cancel003-source.qcow2'
assert not target.exists() and not source.exists();out.mkdir()
files=dict(f['files']);protected=dict(f['protected'])
with ColdIO(base) as io:
    rr=readers(io,base)
    for name,digest in files.items():v,path=name.split('/',1);assert m.sha(rr[v].read(path))==digest,name
    for name,row in {**review['providers'],**observer['providers']}.items():
        path='winnt/system32/'+name;assert m.sha(rr['F'].read(path))==row['sha256'],name
        files['F/'+path]=row['sha256'];protected['F/'+path]=row['sha256']
    for name in ['guardian.exe','guardian201.log','wizard201.log','observer.exe','observer.log']:
        try:rr['F'].read('xwnwiz201/'+name)
        except KeyError:pass
        else:raise AssertionError('Unique new stage '+name)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
data=(k/'artifacts/guardian003/guardian.exe').read_bytes();w.write('xwnwiz201/guardian.exe',data)
files['F/xwnwiz201/guardian.exe']=m.sha(data);protected['F/xwnwiz201/guardian.exe']=m.sha(data)
data=(k/'artifacts/build002/wizard.exe').read_bytes();restore(w,'xwnwiz201/wizard.exe',data);files['F/xwnwiz201/wizard.exe']=m.sha(data);protected['F/xwnwiz201/wizard.exe']=m.sha(data)
data=observer_binary.read_bytes();w.write('xwnwiz201/observer.exe',data)
files['F/xwnwiz201/observer.exe']=m.sha(data);protected['F/xwnwiz201/observer.exe']=m.sha(data)
startup=b'@echo off\r\nC:\\xwnwiz201\\guardian.exe\r\nexit\r\n';restore(w,STARTUP,startup);files['F/'+STARTUP]=m.sha(startup);w.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(source)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(source)],check=True)
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)]));assert not info.get('backing-filename')
with ColdIO(source) as io:
    rr=readers(io,source)
    for name,digest in files.items():v,path=name.split('/',1);assert m.sha(rr[v].read(path))==digest,name
    for name in HIVES:
        path=out/'artifacts'/('before-'+name);path.parent.mkdir(exist_ok=True);path.write_bytes(rr['F'].read('winnt/system32/config/'+name));hive(path)
scan(source,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
for row in f['parents']:assert sha(Path(row['path']))==row['sha256']
assert sha(base)==f['fixture_sha256']
save(k/'fixture-cancel003.json',dict(f,case=case,files=files,protected=protected,guest_launch=False,fixture_path_linux=str(source),fixture_path_windows='E:/Codex-archive/xbox-windows-native/wizard201/cancel003-source.qcow2',fixture_sha256=sha(source),seed_sha256=sha(source),
    passive_closure_sha256=sha(k/'observe002/closure.json'),passive_audit_sha256=sha(k/'observe002/audit.json'),
    limits='NEW source: same immutable captured physical-core drivers/hives/device policy, unchanged helper002 plus guardian003 failure-path read-only188 observer added. Observer five samples after joined helper failure; no restart on failure. Known targeted Cancel explicit; no install/disable/null binding. Genuine idle/join/restart gates and strict events retained. Not physical qualification.'))
print('Fresh cancel003 prepared/fullcold pinned; no guest launch')

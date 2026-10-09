"""Fresh passive201 from immutable prelaunch188, never a live disk or old launch."""
import os,subprocess
from common import *
from restore import restore
case=sys.argv[1];assert case=='observe001';out=k/case;out.mkdir(exist_ok=False)
original=read(k.parent/'device-observation188/fixture-emulator001.json')
prior_out=k.parent/'device-observation188/emulator001';assert read(prior_out/'closure.json')['closed']
parent=ws/'outputs/native-windows-fatx-forensics/artifacts'/original['fixture_name'];assert sha(parent)==original['fixture_sha256']
parents=original['parents']+[dict(path=str(parent),sha256=sha(parent))]
assert read(k/'policy-tests.json')['passed']
old_files=original['files'];build=read(k/'build-review.json');assert build['passed']
assert sha(k/'artifacts/build001/wizard.exe')==build['binary_sha256']
assert sha(k/'wizard.c')==build['source_sha256']
assert sha(k/'policy.h')==read(k/'policy-tests.json')['source_sha256']
target=ws/'outputs/native-windows-fatx-forensics/artifacts'/('setup-wizard-automation201-'+case+'.qcow2')
seed=ws/('work/setup-wizard-automation201-'+case+'-seed.qcow2');assert not target.exists() and not seed.exists()
files={};protected={}
with ColdIO(parent) as io:
    rr=readers(io,parent)
    for name,digest in old_files.items():
        volume,path=name.split('/',1);actual=m.sha(rr[volume].read(path));files[name]=actual
        mutable=path==STARTUP or path.startswith('winnt/system32/config/') or path in ['winnt/setupapi.log','winnt/system32/xwn-video-trace.bin']
        if not mutable:assert actual==digest,name;protected[name]=actual
    for name,row in build['providers'].items():
        path='winnt/system32/'+name;assert m.sha(rr['F'].read(path))==row['sha256'],name
        protected['F/'+path]=row['sha256'];files['F/'+path]=row['sha256']
    for name in ['wizard.exe','wizard201.log','startup-result.txt']:
        try:rr['F'].read('xwnwiz201/'+name)
        except KeyError:pass
        else:raise AssertionError('Unique namespace required')
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
data=(k/'artifacts/build001/wizard.exe').read_bytes();w.write('xwnwiz201/wizard.exe',data);files['F/xwnwiz201/wizard.exe']=m.sha(data);protected['F/xwnwiz201/wizard.exe']=m.sha(data)
startup=b'@echo off\r\nC:\\xwnwiz201\\wizard.exe /observe-emulator\r\necho WIZARD_EXIT %errorlevel% > C:\\xwnwiz201\\startup-result.txt\r\nexit\r\n';restore(w,STARTUP,startup);files['F/'+STARTUP]=m.sha(startup);w.flush()
with ColdIO(target) as io:
    rr=readers(io,target)
    for name,digest in files.items():volume,path=name.split('/',1);assert m.sha(rr[volume].read(path))==digest,name
    for name in HIVES:
        path=out/'artifacts'/('before-'+name);path.parent.mkdir(exist_ok=True);path.write_bytes(rr['F'].read('winnt/system32/config/'+name));hive(path)
scan(target,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
# Parent stays at its original verified path; only new child metadata is rebased.
relative_parent=os.path.relpath(parent,target.parent)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',relative_parent,str(target)],check=True)
with ColdIO(target) as io:
    rr=readers(io,target)
    for name,digest in files.items():volume,path=name.split('/',1);assert m.sha(rr[volume].read(path))==digest,name
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/('fixture-'+case+'.json'),dict(prepared=True,case=case,guest_launch=False,physical_access=False,parents=parents,files=files,protected=protected,fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),
    prior_closure_sha256=sha(prior_out/'closure.json'),stored_relative_parent=relative_parent,inherited_emulator_null_policy=False,same_physical_device_policy=False,
    limits='Fresh immutable prelaunch188 captured physical-core child with emulator devices; same drivers/hives/device policy. Only unique201 helper/startup staged. Observation never sends Cancel, never requests restart; bounded host closure is not normal shutdown.'))
print('Fresh201 observation prepared without guest launch:',case)

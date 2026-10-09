"""Fresh read-only observer child with captured original physical registry/core. Emulator only."""
import subprocess
from common import *
from restore import restore
out=k/'emulator001';out.mkdir(exist_ok=False)
source=ws/'outputs/native-windows-fatx-forensics/artifacts/video-physical-rehearsal162-control001.qcow2'
original=read(k.parent/'video-physical-rehearsal162/fixture-control001.json')
assert sha(source)==original['fixture_sha256']
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
target=source.parent/'device-observation188-emulator001.qcow2';seed=ws/'work/device-observation188-emulator001-seed.qcow2'
assert not target.exists() and not seed.exists()
capture=k.parent/'video-word-physical187';rows=read(capture/'capture.json')['files']
build=read(k/'build-review.json');assert build['passed'] and sha(k/'artifacts/build003/observer.exe')==build['binary_sha256']
with ColdIO(source) as io:
    rr=readers(io,source)
    for path in ['xwnobs188/observer.exe','xwnobs188/observer.log']:
        try:rr['F'].read(path)
        except KeyError:pass
        else:raise AssertionError('Stale unique path: '+path)
    # Check actual providers in selected guest, not merely link libraries.
    for name,row in build['providers'].items():
        assert m.sha(rr['F'].read('winnt/system32/'+name))==row['sha256'],name
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
m.target=target;io=m.SliceIO(target);expected={}
for volume in ['E','F']:
    w=m.Writer(io,m.fatx.open_partition(io,target,volume))
    for row in rows:
        v,path=row['path'].lstrip('/').split('/',1)
        if v!=volume or path==STARTUP:continue
        p=capture/'artifacts'/row['path'].lstrip('/');assert sha(p)==row['sha256']
        restore(w,path,p.read_bytes());expected[v+'/'+path]=row['sha256']
    if volume=='F':
        p=k/'artifacts/build003/observer.exe';w.write('xwnobs188/observer.exe',p.read_bytes());expected['F/xwnobs188/observer.exe']=sha(p)
        startup=b'@echo off\r\nC:\\xwnobs188\\observer.exe\r\nexit\r\n'
        restore(w,STARTUP,startup);expected['F/'+STARTUP]=m.sha(startup)
    w.flush()
with ColdIO(target) as io:
    rr=readers(io,target);hives=[]
    for name,digest in expected.items():v,path=name.split('/',1);assert m.sha(rr[v].read(path))==digest,name
    for name in HIVES:
        p=out/'artifacts'/('before-'+name);p.parent.mkdir(exist_ok=True);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));hives.append(dict(name=name,**hive(p)))
scan(target,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/'fixture-emulator001.json',dict(prepared=True,guest_launch=False,physical_access=False,parents=parents,files=expected,hives=hives,
    fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),capture_sha256=sha(capture/'capture.json'),
    inherited_emulator_null_policy=False,physical_registry_exact=True,ordinary_qualified=False,
    limits='Original physical captured hives/core on older emulator filesystem and emulated devices; not a whole-console clone. No UI action or guest restart. Bounded owned host closure is diagnostic only.'))
print('Unique188 captured-baseline child readback/provider/hive/allocation checks passed; NEVER launched yet')

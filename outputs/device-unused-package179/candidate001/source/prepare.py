"""Fresh control/candidate children with identical five-sample helpers."""
import subprocess
from common import *
case=sys.argv[1];assert case in ['candidate001']
out=k/case;out.mkdir(exist_ok=False)
f=read(k.parent/'video-physical-rehearsal162'/('fixture-'+case+'.json'))
source=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];assert sha(source)==f['fixture_sha256']
target=source.parent/('device-unused-package179-'+case+'.qcow2');seed=ws/('work/device-unused-package179-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists()
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
with ColdIO(source) as io:
    rr=readers(io,source)
    caller=k/'artifacts/umpnpmgr.dll'
    assert m.sha(rr['F'].read('winnt/system32/umpnpmgr.dll'))==sha(caller),'Actual caller DLL differs from owned review'
    f['files']['F/winnt/system32/umpnpmgr.dll']=sha(caller)
    for label,meta in read(k/'sites.json')['binaries'].items():
        p=ws/meta['path'];assert sha(p)==meta['sha256']
        assert m.sha(rr['F'].read('winnt/system32/'+label))==meta['sha256'],label
        f['files']['F/winnt/system32/'+label]=meta['sha256']
    for path in ['xwnup179/runner.exe','xwnup179/replay.exe','xwnup179/attempt.log']:
        try:rr['F'].read(path)
        except KeyError:pass
        else:raise AssertionError('Namespace already exists')
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'));files=dict(f['files'])
for path,p in [('xwnup179/runner.exe',k/'artifacts/runner.exe'),('xwnup179/replay.exe',k/'artifacts/gdi-probe.exe')]:
    w.write(path,p.read_bytes());files['F/'+path]=sha(p)
startup=b'@echo off\r\nC:\\xwnup179\\runner.exe\r\nexit\r\n';m.replace(w,STARTUP,startup);files['F/'+STARTUP]=m.sha(startup);w.write('winnt/inf/xwnunused179.inf',(k/'xwnunused179.inf').read_bytes());files['F/winnt/inf/xwnunused179.inf']=sha(k/'xwnunused179.inf');w.flush()
with ColdIO(target) as io:
    rr=readers(io,target)
    for name,digest in files.items():v,path=name.split('/',1);assert m.sha(rr[v].read(path))==digest,name
scan(target,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/('fixture-'+case+'.json'),dict(case=case,prepared=True,launched=False,physical_writes=False,parents=parents,fixture_name=target.name,
    fixture_sha256=sha(target),seed_sha256=sha(seed),files=files,limits='Same fresh five-sample launcher/probe; captured-core162 children; no physical timing qualification.'))
print('New five-sample fixture prepared:',case)

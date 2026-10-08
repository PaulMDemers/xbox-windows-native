"""Add only the new helper namespace to immutable captured-core candidate162."""
import subprocess
from common import *
case='candidate001';out=k/case;out.mkdir(exist_ok=False)
f=read(k.parent/'video-physical-rehearsal162/fixture-candidate001.json')
source=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];assert sha(source)==f['fixture_sha256']
target=source.parent/'video-hardware-trial164-candidate001.qcow2';seed=ws/'work/video-hardware-trial164-candidate001-seed.qcow2'
assert not target.exists() and not seed.exists()
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
with ColdIO(source) as io:
    rr=readers(io,source)
    for path in ['xwnv164/runner.exe','xwnv164/replay.exe','xwnv164/attempt.log','xwnv164/gdi-baseline.txt']:
        try:rr['F'].read(path)
        except KeyError:pass
        else:raise AssertionError('Private helper namespace already exists')
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
files=dict(f['files'])
for path,p in [('xwnv164/runner.exe',k/'artifacts/runner.exe'),('xwnv164/replay.exe',k.parent/'video-next/probe-v3/artifacts/gdi-probe.exe')]:
    w.write(path,p.read_bytes());files['F/'+path]=sha(p)
startup=b'@echo off\r\nC:\\xwnv164\\runner.exe\r\nexit\r\n';m.replace(w,STARTUP,startup);files['F/'+STARTUP]=m.sha(startup);w.flush()
with ColdIO(target) as io:
    rr=readers(io,target)
    for name,digest in files.items():v,path=name.split('/',1);assert m.sha(rr[v].read(path))==digest,name
scan(target,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/'fixture-candidate001.json',dict(case=case,prepared=True,launched=False,physical_writes=False,parents=parents,fixture_name=target.name,
    fixture_sha256=sha(target),seed_sha256=sha(seed),files=files,limits='New namespace helper runtime on unchanged162 display/core/settings; no physical qualification.'))
print('New one-shot namespace prepared and cold verified')

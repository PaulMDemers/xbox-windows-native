"""Create one fresh video measurement child of the verified ordinary0105 fixture."""
import subprocess
from common import *
from allocation import scan
case='baseline001';out=k/case;out.mkdir(exist_ok=False)
parent=k.parent/'atapi-lba48-network';f=read(parent/'fixture-candidate001.json')
assert all(v['strict'] for v in read(parent/'pair-review.json')['results'])
source=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];assert sha(source)==f['fixture_sha256']
target=source.parent/'video-copy-profile-visible-baseline001.qcow2';seed=ws/'work/video-copy-profile-visible-baseline001-seed.qcow2'
assert not target.exists() and not seed.exists() and not (k/'fixture-baseline001.json').exists()
b=read(k/'build-review.json');assert b['passed'] and sha(k/'artifacts/probe.exe')==b['probe_sha256'] and sha(k/'probe.c')==b['source_sha256']
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
with ColdIO(source) as io:
 rr=readers(io,source);protected=[dict(volume=v,path=p,sha256=m.sha(rr[v].read(p))) for v,p in PROTECTED+[('F','winnt/system32/framebuf.dll'),('F','winnt/system32/hidserv.exe')]]
 for row in f['protected']:assert m.sha(rr[row['volume']].read(row['path']))==row['sha256']
 hives=[dict(path='winnt/system32/config/'+n,sha256=m.sha(rr['F'].read('winnt/system32/config/'+n))) for n in HIVES]
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
startup=b'@echo off\r\nC:\\xwnvid106\\probe.exe\r\nexit\r\n';m.replace(w,STARTUP,startup)
payloads=[w.write('xwnvid106/probe.exe',(k/'artifacts/probe.exe').read_bytes())];w.flush()
with ColdIO(target) as io:
 rr=readers(io,target);assert rr['F'].read(STARTUP)==startup
 for row in protected:assert m.sha(rr[row['volume']].read(row['path']))==row['sha256']
 for row in hives+payloads:assert m.sha(rr['F'].read(row['path']))==row['sha256']
 try:rr['F'].read('xwnvid106/result.log')
 except KeyError:pass
 else:raise AssertionError('Output already exists')
scan(target,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/'fixture-baseline001.json',dict(case=case,physical_access=False,debugger=False,parents=parents,fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),protected=protected,preserved_hives=hives,payloads=payloads,startup_sha256=m.sha(startup),readback_verified=True,result_absent=True,build_review_sha256=sha(k/'build-review.json'),parent_manifest='atapi-lba48-network/fixture-candidate001.json',parent_manifest_sha256=sha(parent/'fixture-candidate001.json'),inherited_configuration='Same settled emulator device policy: GPU registered, QEMU null INF, 01B0/01B4 FAILEDINSTALL. No registry/driver/mode/cache changes. FATX0103/HAL0102/NVNet0104/ATAPI0105/video0093 plus restored HidServ; Microsoft framebuf.dll.'))
print('Prepared unique baseline001; not launched')

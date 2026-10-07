"""Fresh matched control/candidate; only the miniport bytes differ."""
import subprocess,sys
from common import *
from allocation import scan
case=sys.argv[1];assert case in ['control001','candidate001']
out=k/case;out.mkdir(exist_ok=False)
parent=k.parent/'atapi-lba48-network';f=read(parent/'fixture-candidate001.json')
assert all(v['strict'] for v in read(parent/'pair-review.json')['results'])
source=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];assert sha(source)==f['fixture_sha256']
target=source.parent/('video-map-profile-'+case+'.qcow2');seed=ws/('work/video-map-profile-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists() and not (k/('fixture-'+case+'.json')).exists()
b=read(k/'build-review.json');assert b['passed'] and sha(k/'artifacts/probe.exe')==b['probe_sha256'] and sha(k/'probe.c')==b['source_sha256']
candidate=k.parent/'video-direct-map/artifacts/xboxvnt5.sys';candidate_sha='e8021879bd606eb9cfc6927fbf50565c41781779af86e56f4678fa890b6eb6ec'
assert sha(candidate)==candidate_sha and read(k.parent/'video-direct-map/compiled-tests.json')['passed']
pins=read(k.parent/'video-direct-map/inputs.json')
for p,h in pins['patch_sha256'].items():assert sha(ws/p)==h
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
with ColdIO(source) as io:
 rr=readers(io,source);protected=[dict(volume=v,path=p,sha256=m.sha(rr[v].read(p))) for v,p in PROTECTED+[('F','winnt/system32/framebuf.dll'),('F','winnt/system32/hidserv.exe')]]
 for row in f['protected']:assert m.sha(rr[row['volume']].read(row['path']))==row['sha256']
 hives=[dict(path='winnt/system32/config/'+n,sha256=m.sha(rr['F'].read('winnt/system32/config/'+n))) for n in HIVES]
 original_video=rr['F'].read('winnt/system32/drivers/xboxvnt5.sys')
 assert m.sha(original_video)=='3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf'
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
startup=b'@echo off\r\nC:\\xwnvid106\\probe.exe\r\nexit\r\n';m.replace(w,STARTUP,startup)
payloads=[w.write('xwnvid106/probe.exe',(k/'artifacts/probe.exe').read_bytes())]
trace=b'XWN-VID-TRACE01\n'+bytes(4080);assert len(trace)==4096
m.replace(w,'winnt/system32/xwn-video-trace.bin',trace)
if case=='candidate001':
 m.replace(w,'winnt/system32/drivers/xboxvnt5.sys',candidate.read_bytes())
 for row in protected:
  if row['path']=='winnt/system32/drivers/xboxvnt5.sys':row['sha256']=candidate_sha
w.flush()
with ColdIO(target) as io:
 rr=readers(io,target);assert rr['F'].read(STARTUP)==startup and rr['F'].read('winnt/system32/xwn-video-trace.bin')==trace
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
save(k/('fixture-'+case+'.json'),dict(case=case,physical_access=False,debugger=False,parents=parents,fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),protected=protected,preserved_hives=hives,payloads=payloads,startup_sha256=m.sha(startup),initial_trace_sha256=m.sha(trace),readback_verified=True,result_absent=True,build_review_sha256=sha(k/'build-review.json'),candidate_inputs_sha256=sha(k.parent/'video-direct-map/inputs.json'),candidate_tests_sha256=sha(k.parent/'video-direct-map/compiled-tests.json'),parent_manifest='atapi-lba48-network/fixture-candidate001.json',parent_manifest_sha256=sha(parent/'fixture-candidate001.json'),inherited_configuration='Settled emulator: GPU registered, QEMU null INF,01B0/01B4 FAILEDINSTALL. Same Microsoft framebuf, FATX0103/HAL0102/NVNet0104/ATAPI0105/HidServ.0093 control vs bounded0096 direct-RAM candidate. Both trace files freshly seeded identically. No mode/device policy/cache-register change. Generic PnP stop/remove lifecycle remains unqualified.'))
print('Prepared unique '+case+'; not launched')

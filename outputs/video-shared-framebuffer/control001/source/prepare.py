"""Fresh matched UC control/candidate; only miniport and bootvid differ."""
import subprocess,sys
from common import *
from allocation import scan
case=sys.argv[1];assert case in ['control001','candidate001']
out=k/case;assert (out/'build.json').exists() and not (out/'before').exists()
parent=k.parent/'atapi-lba48-network';f=read(parent/'fixture-candidate001.json')
assert all(v['strict'] for v in read(parent/'pair-review.json')['results'])
source=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];assert sha(source)==f['fixture_sha256']
target=source.parent/('video-shared-framebuffer-'+case+'.qcow2');seed=ws/('work/video-shared-framebuffer-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists() and not (k/('fixture-'+case+'.json')).exists()
b=read(k/'build-review.json');assert b['passed'] and sha(k/'artifacts/probe.exe')==b['probe_sha256'] and sha(k/'probe.c')==b['source_sha256']
review=read(k/'pe-review.json');assert review['passed'] and sha(k/'build-report.json')==review['build_sha256']
row=read(out/'build.json');files={r['name']:r for r in row['files']}
for name,r in files.items():assert sha(out/'artifacts'/name)==r['sha256']
patch=read(k/'patch-review.json')
assert sha(k/'0106-shared-uc-framebuffer.patch')==patch['patch_sha256']==row['patch_sha256']
for n,h in patch['authored_sources'].items():assert sha(k/n)==h
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
startup=b'@echo off\r\nC:\\xwnvid107\\probe.exe\r\nexit\r\n';m.replace(w,STARTUP,startup)
payloads=[w.write('xwnvid107/probe.exe',(k/'artifacts/probe.exe').read_bytes())]
trace=b'XWN-VID-TRACE01\n'+bytes(4080);assert len(trace)==4096
m.replace(w,'winnt/system32/xwn-video-trace.bin',trace)
m.replace(w,'winnt/system32/drivers/xboxvnt5.sys',(out/'artifacts/xboxvnt5.sys').read_bytes());w.flush()
e=m.Writer(io,m.fatx.open_partition(io,target,'E'))
m.replace(e,'Applications/XWNFBoot/loader/xboxbvid.dll',(out/'artifacts/xboxbvid.dll').read_bytes());e.flush()
for row in protected:
 if row['path']=='winnt/system32/drivers/xboxvnt5.sys':row['sha256']=files['xboxvnt5.sys']['sha256']
 if row['path']=='Applications/XWNFBoot/loader/xboxbvid.dll':row['sha256']=files['xboxbvid.dll']['sha256']
with ColdIO(target) as io:
 rr=readers(io,target);assert rr['F'].read(STARTUP)==startup and rr['F'].read('winnt/system32/xwn-video-trace.bin')==trace
 for row in protected:assert m.sha(rr[row['volume']].read(row['path']))==row['sha256']
 for row in hives+payloads:assert m.sha(rr['F'].read(row['path']))==row['sha256']
 try:rr['F'].read('xwnvid107/result.log')
 except KeyError:pass
 else:raise AssertionError('Output already exists')
scan(target,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/('fixture-'+case+'.json'),dict(case=case,physical_access=False,debugger=False,parents=parents,fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),protected=protected,preserved_hives=hives,payloads=payloads,startup_sha256=m.sha(startup),initial_trace_sha256=m.sha(trace),readback_verified=True,result_absent=True,build_review_sha256=sha(k/'build-review.json'),pe_review_sha256=sha(k/'pe-review.json'),case_build_sha256=sha(out/'build.json'),parent_manifest='atapi-lba48-network/fixture-candidate001.json',parent_manifest_sha256=sha(parent/'fixture-candidate001.json'),inherited_configuration='Settled emulator: GPU registered, QEMU null INF,01B0/01B4 FAILEDINSTALL. Same Microsoft framebuf, FATX0103/HAL0102/NVNet0104/ATAPI0105/HidServ.Reconstructed0093 UC control vs shared-UC0106 bootvid/miniport candidate. Both trace files freshly seeded identically. No mode/device policy/cache-register change. Generic PnP stop/remove lifecycle remains unqualified.'))
print('Prepared unique '+case+'; not launched')

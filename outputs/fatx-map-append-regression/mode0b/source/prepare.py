"""Stage fresh paired children; retain and hash every backing parent. WSL only."""
import contextlib,subprocess,sys
from common import *
from allocation import scan
case=sys.argv[1];assert case in ['mode0b','mode1'];mode='0' if case=='mode0b' else '1'
out=k/case;out.mkdir(exist_ok=True)
manifest=k/('fixture-'+case+'.json')
source=ws/'outputs/native-windows-fatx-forensics/artifacts/map-append-parent.qcow2'
target=ws/('outputs/native-windows-fatx-forensics/artifacts/fatx-map-append-'+case+'.qcow2')
seed=ws/('work/fatx-map-append-'+case+'-seed.qcow2')
parent_copy=read(k/'parent-copy.json')
assert parent_copy['virtual_contents_identical'] and sha(source)==parent_copy['copy_sha256']
assert sha(Path(parent_copy['source']))==parent_copy['source_sha256']
parent_analysis=read(k.parent/'fatx-mapped-lifecycle/002/lifecycle-analysis.json')
assert parent_analysis['cold_checks_passed'] and parent_analysis['target_mapped_lifecycle_verified']
assert not manifest.exists() and not target.exists() and not seed.exists()
review=read(k/'build-review.json');assert review['passed']
assert sha(k/'artifacts/probe.exe')==review['probe_sha256'] and sha(k/'probe.c')==review['source_sha256']
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
with ColdIO(source) as io:
    before=readers(io,source)
    protected=[dict(volume=v,path=p,sha256=m.sha(before[v].read(p))) for v,p in PROTECTED]
    hives=[dict(path='winnt/system32/config/'+n,sha256=m.sha(before['F'].read('winnt/system32/config/'+n))) for n in HIVES]
    try:before['F'].read('xwnmap01/result.log')
    except KeyError:pass
    else:raise AssertionError('Parent already contains regression result')
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
startup=b'@echo off\r\nC:\\xwnmap01\\probe.exe\r\nexit\r\n'
m.replace(w,STARTUP,startup)
payloads=[w.write('xwnmap01/probe.exe',(k/'artifacts/probe.exe').read_bytes()),w.write('xwnmap01/mode.txt',mode.encode())]
w.flush()
with ColdIO(target) as io:
    after=readers(io,target)
    for row in payloads:assert m.sha(after['F'].read(row['path']))==row['sha256']
    assert after['F'].read(STARTUP)==startup
    for row in protected:assert m.sha(after[row['volume']].read(row['path']))==row['sha256']
    for row in hives:assert m.sha(after['F'].read(row['path']))==row['sha256']
    try:after['F'].read('xwnmap01/result.log')
    except KeyError:pass
    else:raise AssertionError('Result must be absent')
scan(target,out/'before/artifacts')
allocation=read(out/'before/allocation.json');assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(manifest,dict(case=case,mode=int(mode),physical_access=False,debugger=False,parents=parents,fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),protected=protected,preserved_hives=hives,payloads=payloads,startup_sha256=m.sha(startup),readback_verified=True,result_absent=True,build_review_sha256=sha(k/'build-review.json')))
print('Prepared '+case+'; not launched')

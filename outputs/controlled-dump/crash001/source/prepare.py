"""Stage one never-booted disposable crash child; preserve every input and parent."""
import subprocess
from common import *
from allocation import scan
case='crash001';out=k/case;out.mkdir(exist_ok=False)
baseline=read(k.parent/'dump-map-trace/fixture-trace001.json');review=read(k/'build-review.json')
source=ws/'outputs/native-windows-fatx-forensics/artifacts'/baseline['fixture_name']
target=source.parent/'controlled-dump-crash001.qcow2';seed=ws/'work/controlled-dump-crash001-seed.qcow2'
assert sha(source)==baseline['fixture_sha256'] and review['passed']
assert not target.exists() and not seed.exists() and not (k/'fixture-crash001.json').exists()
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
protected=list(baseline['protected']);hives=[]
with ColdIO(source) as io:
    rr=readers(io,source)
    for n in ['atapi.sys','diskdump.sys','disk.sys','scsiport.sys','classpnp.sys','ftdisk.sys']:
        protected.append(dict(volume='F',path='winnt/system32/drivers/'+n,sha256=m.sha(rr['F'].read('winnt/system32/drivers/'+n))))
    for row in protected:assert m.sha(rr[row['volume']].read(row['path']))==row['sha256']
    hives=[dict(path='winnt/system32/config/'+n,sha256=m.sha(rr['F'].read('winnt/system32/config/'+n))) for n in HIVES]
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
startup=b'@echo off\r\nC:\\xwndump103\\probe.exe\r\nexit\r\n';m.replace(w,STARTUP,startup);payloads=[]
for n in ['probe.exe','trigger.sys']:
    p=k/'artifacts'/n;assert sha(p)==review['binaries'][n]['sha256'];payloads.append(w.write('xwndump103/'+n,p.read_bytes()))
w.flush()
with ColdIO(target) as io:
    rr=readers(io,target)
    assert rr['F'].read(STARTUP)==startup
    for row in payloads:assert m.sha(rr['F'].read(row['path']))==row['sha256']
    for row in protected:assert m.sha(rr[row['volume']].read(row['path']))==row['sha256']
    for row in hives:assert m.sha(rr['F'].read(row['path']))==row['sha256']
    try:rr['F'].read('xwndump103/intent.log')
    except KeyError:pass
    else:raise AssertionError('Intent guard must be absent')
scan(target,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/'fixture-crash001.json',dict(case=case,physical_access=False,intentional_crash=True,ordinary_qualified=False,fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),parents=parents,protected=protected,preserved_hives=hives,payloads=payloads,startup_sha256=m.sha(startup),readback_verified=True,guard_absent=True,build_review_sha256=sha(k/'build-review.json'),parent_manifest_sha256=sha(k.parent/'dump-map-trace/fixture-trace001.json'),inherited_configuration=baseline['inherited_configuration']))
print('Prepared crash001; never launched')

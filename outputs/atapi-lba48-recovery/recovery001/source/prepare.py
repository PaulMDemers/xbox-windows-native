"""Readback-verified recovery child of the preserved successful crash disk."""
import subprocess
from common import *
from allocation import scan
from dumps import dump_files,cookie
case='recovery001';out=k/case;out.mkdir(exist_ok=False)
prior=k.parent/'atapi-lba48-crash';closed=read(prior/'crash006/closure.json')
gate=read(prior/'payload-verification.json');assert gate['passed'] and gate['high_lba_dump_write_qualified']
source=ws/'work/runs/nt5-atapi-lba48-crash-crash006/hdd.qcow2'
assert (source.parent/'cleanup.json').exists() and sha(source)==closed['private_disk_sha256']
baseline=read(prior/'fixture-crash006.json');review=read(k/'toolchain-review.json')
helper=k/'artifacts/recovery-probe.exe';assert sha(helper)==review['recovery_helper_sha256']
target=ws/'outputs/native-windows-fatx-forensics/artifacts/atapi-lba48-recovery-recovery001.qcow2'
seed=ws/'work/atapi-lba48-recovery-recovery001-seed.qcow2';assert not target.exists() and not seed.exists()
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
with ColdIO(source) as io:
    before=readers(io,source);saved=dump_files(before['F']);assert not any(cookie(b) for b in saved.values())
    page=before['F'].read('pagefile.sys')[:65536];assert cookie(page)
    assert m.sha(page)==m.sha((prior/'crash006/artifacts/after-pagefile-prefix.bin').read_bytes())
    hives=[dict(path='winnt/system32/config/'+n,sha256=m.sha(before['F'].read('winnt/system32/config/'+n))) for n in HIVES]
    for row in baseline['protected']:assert m.sha(before[row['volume']].read(row['path']))==row['sha256']
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
startup=b'@echo off\r\nC:\\xwnrecover105\\probe.exe\r\nexit\r\n';m.replace(w,STARTUP,startup)
payloads=[w.write('xwnrecover105/probe.exe',helper.read_bytes())];w.flush()
with ColdIO(target) as io:
    after=readers(io,target)
    assert after['F'].read(STARTUP)==startup
    assert after['F'].read('pagefile.sys')[:65536]==page
    assert dump_files(after['F'])==saved
    for row in payloads:assert m.sha(after['F'].read(row['path']))==row['sha256']
    for row in baseline['protected']:assert m.sha(after[row['volume']].read(row['path']))==row['sha256']
    for row in hives:assert m.sha(after['F'].read(row['path']))==row['sha256']
    try:after['F'].read('xwnrecover105/result.log')
    except KeyError:pass
    else:raise AssertionError('One-shot guard exists')
scan(target,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/'fixture-recovery001.json',dict(case=case,physical_access=False,debugger=False,
    fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),parents=parents,
    source_crash_sha256=closed['private_disk_sha256'],high_lba_gate_sha256=sha(prior/'payload-verification.json'),
    crash_payload_sha256=m.sha(page),before_dump_files={name:m.sha(b) for name,b in saved.items()},
    protected=baseline['protected'],preserved_hives=hives,payloads=payloads,startup_sha256=m.sha(startup),
    readback_verified=True,result_absent=True,inherited_configuration=baseline['inherited_configuration']))
print('Prepared recovery child; successful crash disk remains immutable and never booted')

"""Stage fresh paired children; retain and hash every backing parent. WSL only."""
import contextlib,subprocess,sys
from common import *
from allocation import scan
case=sys.argv[1];assert case in ['trace001'];mode='0'
out=k/case;out.mkdir(exist_ok=True)
manifest=k/('fixture-'+case+'.json')
baseline=read(k.parent/'fatx-directory-order/fixture-001.json')
source=ws/'outputs/native-windows-fatx-forensics/artifacts'/baseline['fixture_name']
target=ws/('outputs/native-windows-fatx-forensics/artifacts/dump-fsctl-trace-'+case+'.qcow2')
seed=ws/('work/dump-fsctl-trace-'+case+'-seed.qcow2')
assert sha(source)==baseline['fixture_sha256']
assert read(k.parent/'fatx-directory-order/candidate-eligibility.json')['eligible_for_controlled_hardware_trial']
assert not manifest.exists() and not target.exists() and not seed.exists()
review=read(k/'build-review.json');assert review['passed']
hal_review=read(k/'hal-review.json');hal_record=hal_review['candidate001'];hal=k/'artifacts'/hal_record['name']
assert sha(hal)==hal_record['sha256']
hid=Path('/mnt/e/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/hidserv.exe')
hid_hash='031a1fb5ca4194284d6ecfbfe8afe63589700c1376873267f131ead06946dc6a'
assert sha(hid)==hid_hash
assert sha(k/'artifacts/probe.exe')==review['probe_sha256'] and sha(k/'probe.c')==review['source_sha256']
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
with ColdIO(source) as io:
    before=readers(io,source)
    protected=[dict(volume=v,path=p,sha256=m.sha(before[v].read(p))) for v,p in PROTECTED]
    assert m.sha(before['F'].read('winnt/system32/drivers/xwnfatx.sys'))=='ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9'
    assert m.sha(before['F'].read('winnt/system32/drivers/xboxvnt5.sys'))=='3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf'
    hives=[dict(path='winnt/system32/config/'+n,sha256=m.sha(before['F'].read('winnt/system32/config/'+n))) for n in HIVES]
    try:before['F'].read('winnt/system32/hidserv.exe')
    except KeyError:pass
    else:raise AssertionError('Missing executable evidence no longer matches')
    try:before['F'].read('xwndf01/result.log')
    except KeyError:pass
    else:raise AssertionError('Parent already contains regression result')
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
startup=b'@echo off\r\nC:\\xwndf01\\probe.exe\r\nexit\r\n'
m.replace(w,STARTUP,startup)
payloads=[w.write('xwndf01/probe.exe',(k/'artifacts/probe.exe').read_bytes()),w.write('xwndf01/mode.txt',mode.encode())]
payloads.append(w.write('winnt/system32/hidserv.exe',hid.read_bytes()))
w.flush()
e=m.Writer(io,m.fatx.open_partition(io,target,'E'))
hal_path='Applications/XWNFBoot/loader/halxboxnt5.dll'
hal_row=next(row for row in protected if row['volume']=='E' and row['path']==hal_path)
assert hal_row['sha256']=='a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648'
hal_before=hal_row['sha256'];m.replace(e,hal_path,hal.read_bytes());e.flush()
hal_row['sha256']=sha(hal)
with ColdIO(target) as io:
    after=readers(io,target)
    for row in payloads:assert m.sha(after['F'].read(row['path']))==row['sha256']
    assert after['F'].read(STARTUP)==startup
    for row in protected:assert m.sha(after[row['volume']].read(row['path']))==row['sha256']
    for row in hives:assert m.sha(after['F'].read(row['path']))==row['sha256']
    try:after['F'].read('xwndf01/result.log')
    except KeyError:pass
    else:raise AssertionError('Result must be absent')
scan(target,out/'before/artifacts')
allocation=read(out/'before/allocation.json');assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(manifest,dict(case=case,mode=int(mode),physical_access=False,debugger=True,ordinary_qualified=False,parents=parents,fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),protected=protected,preserved_hives=hives,payloads=payloads,startup_sha256=m.sha(startup),readback_verified=True,result_absent=True,build_review_sha256=sha(k/'build-review.json'),hal_review_sha256=sha(k/'hal-review.json'),hal_before_sha256=hal_before,hal_after_sha256=sha(hal),parent_manifest='fatx-directory-order/fixture-001.json',parent_manifest_sha256=sha(k.parent/'fatx-directory-order/fixture-001.json'),inherited_configuration='Settled GPU and QEMU1B36:0005 null package; inherited01B0/01B4 FAILEDINSTALL flags from old emulator isolation. No hive/device-policy edits. Only rebuilt HAL and helper payloads differ; FATX0101/video0093 unchanged. Not physical device support.'))
print('Prepared '+case+'; not launched')

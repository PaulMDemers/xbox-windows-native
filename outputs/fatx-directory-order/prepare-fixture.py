"""Prepare an owned concurrent file/volume-flush diagnostic with candidate0101 and unchanged video0093."""
import importlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
case=sys.argv[1];assert case in ['001','002']
if case=='002':assert json.loads((k/'001/qualification.json').read_text())['passed']
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
r=json.loads((k.parent/'shutdown-null-placeholder/fixture-001.json').read_text())
review=json.loads((k/'probe-review.json').read_text());helper=(k/'artifacts/probe.exe').read_bytes()
assert review['passed'] and m.sha(helper)==review['probe_sha256']
parent=ws/'outputs/native-windows-fatx-forensics/artifacts/shutdown-null-completed-001.qcow2'
parent_hash=json.loads((k.parent/'shutdown-null-placeholder/completed001-copy.json').read_text())['copied_rebased_sha256'];assert m.filehash(parent)==parent_hash
target=parent.with_name(('fatx-directory-order-'+case+'.qcow2'));seed=ws/('work/fatx-directory-order-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists() and not (k/('fixture-'+case+'.json')).exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
preserved={p:m.sha(w.read(p)) for p in ['winnt/system32/config/system','winnt/system32/config/software','winnt/system32/xwn-video-trace.bin']}
for row in r['payloads']+r['preserved_payloads']:assert m.sha(w.read(row['path']))==row['sha256']
driver=(k/'artifacts/xwnfatx.sys').read_bytes()
binary=json.loads((k/'binary-review.json').read_text());assert binary['passed'] and m.sha(driver)==binary['sha256']
driver_path='winnt/system32/drivers/xwnfatx.sys'
m.replace(w,driver_path,driver)
for row in r['payloads']+r['preserved_payloads']:
    if row['path']==driver_path:row.update(sha256=m.sha(driver),bytes=len(driver))
r['fatx_sha256']=m.sha(driver)
r['payloads'].append(w.write('xwnidle/concurrent.exe',helper))
startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
script=b'@echo off\r\nC:\\xwnidle\\concurrent.exe\r\nexit\r\n'
m.replace(w,startup,script);w.flush()
for row in r['payloads']:
    if row['path']==startup:row.update(sha256=m.sha(script),bytes=len(script))
fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'))
assert all(m.sha(fresh.read(p))==sha for p,sha in preserved.items())
for row in r['payloads']:assert m.sha(fresh.read(row['path']))==row['sha256']
assert m.filehash(parent)==parent_hash
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r.update(scope=__doc__,case=case,physical_access=False,parent_fixture_sha256=parent_hash,
         fixture_name=target.name,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),
         preserved_during_observer_staging=preserved,source_manifest='shutdown-null-placeholder/fixture-001.json',parent_completed_run='nt5-shutdown-null-placeholder-001',
         intervention='Add original concurrency helper and startup command only. Two regular-file workers, volume flush, metadata/rename and directory enumeration;500 rounds each. Only FATX driver changes to candidate0101. No raw writes, lock/dismount, registry edits or UI actions.',
         limits='Owned emulator diagnostic from settled setup; parent retains historical audio failed-install flags. No physical qualification.')
(k/('fixture-'+case+'.json')).write_text(json.dumps(r,indent=2)+'\n')
print('Observer fixture prepared')

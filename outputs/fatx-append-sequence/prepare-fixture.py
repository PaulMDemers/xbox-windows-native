"""Prepare one immutable ordinary append diagnostic with unchanged0101/video0093."""
import importlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
case=sys.argv[1];assert case in ['001','002']
if case=='002':assert json.loads((k/'001/qualification.json').read_text())['passed']
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
r=json.loads((k.parent/'fatx-directory-order/fixture-001.json').read_text())
review=json.loads((k/'probe-review.json').read_text());helper=(k/'artifacts/probe.exe').read_bytes()
assert review['passed'] and m.sha(helper)==review['probe_sha256']
assert m.sha((k/'probe.c').read_bytes())==review['source_sha256']
assert m.sha((k/'Build.ps1').read_bytes())==review['build_script_sha256']
parent=ws/'outputs/native-windows-fatx-forensics/artifacts/fatx-directory-order-001.qcow2'
parent_hash=r['fixture_sha256'];assert m.filehash(parent)==parent_hash
target=parent.with_name(('fatx-append-sequence-'+case+'.qcow2'));seed=ws/('work/fatx-append-sequence-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists() and not (k/('fixture-'+case+'.json')).exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
assert 'xwnas01' not in w.directory(1)['entries'], 'Diagnostic output already exists'
preserved={p:m.sha(w.read(p)) for p in ['winnt/system32/config/system','winnt/system32/config/software','winnt/system32/xwn-video-trace.bin']}
for row in r['payloads']+r['preserved_payloads']:assert m.sha(w.read(row['path']))==row['sha256']
driver_path='winnt/system32/drivers/xwnfatx.sys'
assert m.sha(w.read(driver_path))==r['fatx_sha256']=='ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9'
r['payloads'].append(w.write('xwnidle/sequence.exe',helper))
startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
script=b'@echo off\r\nC:\\xwnidle\\sequence.exe\r\nexit\r\n'
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
         preserved_during_observer_staging=preserved,source_manifest='fatx-directory-order/fixture-001.json',parent_completed_run='inherited settled emulator setup',
         intervention='Add original repeated append helper and change startup only; 16 exclusive files, 512 appends each, four offsets, two flush policies and two handle lifetimes. Exact0101/video0093 retained. No registry, raw disk, debugger or physical actions.',
         limits='Owned emulator diagnostic from settled setup; parent retains historical audio failed-install flags. No physical qualification.')
(k/('fixture-'+case+'.json')).write_text(json.dumps(r,indent=2)+'\n')
print('Observer fixture prepared')

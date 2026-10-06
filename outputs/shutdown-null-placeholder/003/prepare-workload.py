"""Run the exact original short mapping/BMP workload from completed emulator setup."""
import importlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
case=sys.argv[1];assert case=='003'
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
r=json.loads((k/'fixture-001.json').read_text())
assert json.loads((k/'002/audit.json').read_text())['diagnostic_checks_passed']
assert json.loads((k/'002/audit.json').read_text())['ordinary_run_valid']
assert json.loads((k/'002/package-audit.json').read_text())['null_setup_checks_passed']
startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
script=b'@echo off\r\nC:\\xwns98\\probe.exe rehearsal\r\nexit\r\n'
assert m.sha(script)=='0336b2d82047000656f22fb3231fae6763e3432534fbf71855d6239faa22783a'
parent=ws/'outputs/native-windows-fatx-forensics/artifacts/shutdown-null-completed-001.qcow2'
parent_hash=json.loads((k/'completed001-copy.json').read_text())['copied_rebased_sha256'];assert m.filehash(parent)==parent_hash
target=parent.with_name(('shutdown-null-placeholder-'+case+'.qcow2'));seed=ws/('work/shutdown-null-placeholder-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists() and not (k/('fixture-'+case+'.json')).exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
preserved={p:m.sha(w.read(p)) for p in ['winnt/system32/config/system','winnt/system32/config/software','winnt/system32/xwn-video-trace.bin']}
for row in r['payloads']+r['preserved_payloads']:assert m.sha(w.read(row['path']))==row['sha256']
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
r.update(scope=__doc__,case=case,physical_access=False,storage_workload=True,idle_ms=None,original_workload_minimum_ms=60000,parent_fixture_sha256=parent_hash,
         fixture_name=target.name,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),
         preserved_during_observer_staging=preserved,source_manifest='shutdown-null-placeholder/fixture-001.json',parent_completed_run='nt5-shutdown-null-placeholder-001',
         intervention='Only startup command restored to the exact original short rehearsal. Original probe/matched binaries and scribble unchanged. Settled GPU/null-device bindings and video trace retained; no UI helper, recorder, debugger or registry edits.',
         limits='Ordinary original short workload with settled emulator-only device configuration; no UI sampling/actions or host debugger/recorder. Physical qualification separate.')
(k/('fixture-'+case+'.json')).write_text(json.dumps(r,indent=2)+'\n')
print('Observer fixture prepared')

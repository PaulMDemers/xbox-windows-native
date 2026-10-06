"""Stage a specifically matched null INF for the unused emulator-only PCI test function."""
import importlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
case=sys.argv[1];assert case=='001'
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
r=json.loads((k.parent/'shutdown-installer-completion/fixture-004.json').read_text())
review=json.loads((k/'probe-review.json').read_text());helper=(k/'artifacts/probe.exe').read_bytes()
assert review['passed'] and m.sha(helper)==review['probe_sha256']
parent=ws/'outputs/native-windows-fatx-forensics/artifacts/shutdown-installer-completed-004.qcow2'
parent_hash=json.loads((k.parent/'shutdown-installer-completion/completed004-copy.json').read_text())['copied_rebased_sha256'];assert m.filehash(parent)==parent_hash
target=parent.with_name(('shutdown-null-placeholder-'+case+'.qcow2'));seed=ws/('work/shutdown-null-placeholder-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists() and not (k/('fixture-'+case+'.json')).exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
preserved={p:m.sha(w.read(p)) for p in ['winnt/system32/config/system','winnt/system32/config/software','winnt/system32/xwn-video-trace.bin']}
for row in r['payloads']+r['preserved_payloads']:assert m.sha(w.read(row['path']))==row['sha256']
m.replace(w,'xwnidle/probe.exe',helper)
r['payloads'].append(w.write('xwninf99/xwntest.inf',(k/'xwntest.inf').read_bytes()));w.flush()
for row in r['payloads']:
    if row['path']=='xwnidle/probe.exe':row.update(sha256=m.sha(helper),bytes=len(helper))
fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'))
assert all(m.sha(fresh.read(p))==sha for p,sha in preserved.items())
for row in r['payloads']:assert m.sha(fresh.read(row['path']))==row['sha256']
assert m.filehash(parent)==parent_hash
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r.update(scope=__doc__,case=case,physical_access=False,parent_fixture_sha256=parent_hash,
         fixture_name=target.name,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),
         preserved_during_observer_staging=preserved,source_manifest='shutdown-installer-completion/fixture-004.json',parent_completed_run='nt5-shutdown-installer-completion-004',
         intervention='Add emulator-only xwntest.inf null package to existing DevicePath directory; replace idle probe with read-only window/queue observation and pending-install restart guard. No UI actions, offline registry edits or driver binary changes.',
         limits='Guest observer changes timing; no host recorder/debugger; no stability or hardware qualification.')
(k/('fixture-'+case+'.json')).write_text(json.dumps(r,indent=2)+'\n')
print('Observer fixture prepared')

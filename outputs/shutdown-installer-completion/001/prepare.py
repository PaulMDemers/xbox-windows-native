"""Replace only the idle probe: inspect and finish the exact successful GPU wizard once."""
import importlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
r=json.loads((k.parent/'shutdown-install-idle/fixture-002.json').read_text())
review=json.loads((k/'probe-review.json').read_text());helper=(k/'artifacts/probe.exe').read_bytes()
assert review['passed'] and m.sha(helper)==review['probe_sha256']
parent=ws/'outputs/native-windows-fatx-forensics/artifacts'/r['fixture_name']
parent_hash=r['fixture_sha256'];assert m.filehash(parent)==parent_hash
target=parent.with_name('shutdown-installer-completion-001.qcow2');seed=ws/'work/shutdown-installer-completion-001-seed.qcow2'
assert not target.exists() and not seed.exists() and not (k/'fixture-001.json').exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
preserved={p:m.sha(w.read(p)) for p in ['winnt/system32/config/system','winnt/system32/config/software','winnt/system32/xwn-video-trace.bin']}
for row in r['payloads']+r['preserved_payloads']:assert m.sha(w.read(row['path']))==row['sha256']
m.replace(w,'xwnidle/probe.exe',helper);w.flush()
for row in r['payloads']:
    if row['path']=='xwnidle/probe.exe':row.update(sha256=m.sha(helper),bytes=len(helper))
fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'))
assert all(m.sha(fresh.read(p))==sha for p,sha in preserved.items())
for row in r['payloads']:assert m.sha(fresh.read(row['path']))==row['sha256']
assert m.filehash(parent)==parent_hash
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r.update(scope=__doc__,case='001',physical_access=False,parent_fixture_sha256=parent_hash,
         fixture_name=target.name,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),
         preserved_during_observer_staging=preserved,source_manifest='shutdown-install-idle/fixture-002.json',
         intervention='Only xwnidle/probe.exe replaced; window samples, pending-install status, and one verified GPU Finish notification; no unknown dialog action.',
         limits='Guest observer changes timing; no host recorder/debugger; no stability or hardware qualification.')
(k/'fixture-001.json').write_text(json.dumps(r,indent=2)+'\n')
print('Observer fixture prepared')

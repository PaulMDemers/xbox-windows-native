"""Preserve completed setup disk and validate subsequent boot with no UI completion actions."""
import importlib,json,subprocess,sys,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
case=sys.argv[1];assert case=='006'
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
r=json.loads((k/'fixture-004.json').read_text())
result=json.loads((k/'004/outcome-review.json').read_text());assert result['targeted_setup_checks_passed']
assert (ws/'work/runs/nt5-shutdown-installer-completion-004/cleanup.json').exists()
review=json.loads((k/'repeat-probe-review.json').read_text());helper=(k/'artifacts/repeat-probe.exe').read_bytes()
assert review['passed'] and m.sha(helper)==review['probe_sha256']
original=ws/'work/runs/nt5-shutdown-installer-completion-004/hdd.qcow2'
original_sha=m.filehash(original)
parent=ws/'outputs/native-windows-fatx-forensics/artifacts/shutdown-installer-completed-004.qcow2'
assert not parent.exists();shutil.copyfile(original,parent)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',r['fixture_name'],str(parent)],check=True)
comparison=subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(original),str(parent)],capture_output=True,text=True)
assert comparison.returncode==0,(comparison.stdout,comparison.stderr)
assert m.filehash(original)==original_sha
parent_hash=m.filehash(parent)
(k/'completed004-copy.json').write_text(json.dumps(dict(original_sha256=original_sha,copied_rebased_sha256=parent_hash,virtual_disks_equal=True,comparison= comparison.stdout,original_unchanged=True),indent=2)+'\n')
target=ws/'outputs/native-windows-fatx-forensics/artifacts'/('shutdown-installer-completion-'+case+'.qcow2');seed=ws/('work/shutdown-installer-completion-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists() and not (k/('fixture-'+case+'.json')).exists()
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
r.update(scope=__doc__,case=case,physical_access=False,parent_fixture_sha256=parent_hash,
         fixture_name=target.name,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),
         preserved_during_observer_staging=preserved,source_manifest='shutdown-installer-completion/fixture-004.json',parent_completed_run='nt5-shutdown-installer-completion-004',
         intervention='Subsequent boot from completed004 disk; only idle probe replaced. New repeat.log, no UI observation/action, pending-install restart guard. Hives and trace retained as produced by004.',
         limits='Ordinary bounded idle/restart check; no host recorder/debugger or UI actions, no explicit storage workload or hardware qualification.')
(k/('fixture-'+case+'.json')).write_text(json.dumps(r,indent=2)+'\n')
print('Observer fixture prepared')

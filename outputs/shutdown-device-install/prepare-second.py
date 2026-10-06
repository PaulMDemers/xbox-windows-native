"""Preserve completed installation and first workload; add a fresh second-boot test folder."""
import importlib,json,shutil,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
audit=json.loads((k/'001/audit.json').read_text());package=json.loads((k/'001/package-audit.json').read_text())
assert package['installation_checks_passed'] and audit['probe_completed']
assert audit['normal_shutdown_count']==1 and audit['persistence_passed']
termination=json.loads((k/'001/termination.json').read_text()) if (k/'001/termination.json').exists() else None
# A diagnostic boot of a retained failed attempt is not promotion or a waiver.
# Require completed workload and EventLog shutdown even if host return failed.
assert audit['dashboard_return'] or (termination and termination['owned_runner_cleanup_requested'])
assert all(v['matched'] for v in audit['payloads']) and all(audit['baseline_checks'].values())
r=json.loads((k/'fixture-001.json').read_text())
source=ws/'work/runs/nt5-shutdown-device-install-001/hdd.qcow2';assert (source.parent/'cleanup.json').exists()
parent=ws/'outputs/native-windows-fatx-forensics/artifacts'/r['fixture_name'];assert m.filehash(parent)==r['fixture_sha256']
target=parent.with_name('shutdown-device-install-002.qcow2');seed=ws/'work/shutdown-device-install-002-seed.qcow2'
assert not target.exists() and not seed.exists()
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)]))
assert (source.parent/info['backing-filename']).resolve()==parent.resolve()
source_hash=m.filehash(source);shutil.copyfile(source,target);assert m.filehash(target)==source_hash
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
preserved={p:m.sha(w.read(p)) for p in ['winnt/system32/config/system','winnt/system32/config/software','winnt/system32/xwn-video-trace.bin','xwns98/result.log']}
startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
script=b'@echo off\r\nC:\\xwns99\\probe.exe rehearsal\r\nexit\r\n'
m.replace(w,startup,script)
for row in r['payloads']:
    if row['path']==startup:row.update(sha256=m.sha(script),bytes=len(script))
for name in ['probe','matched']:
    report=json.loads((k/(name+'-review.json')).read_text());data=(k/'artifacts'/(name+'.exe')).read_bytes()
    assert report['passed'] and m.sha(data)==report['probe_sha256']
    r['payloads'].append(w.write('xwns99/'+name+'.exe',data))
r['payloads'].append(w.write('xwns99/scribble.bmp',(k.parent/'fatx0098-soak/artifacts/scribble.bmp').read_bytes()))
w.flush();fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'))
assert all(m.sha(fresh.read(p))==sha for p,sha in preserved.items())
for row in r['payloads']:assert m.sha(fresh.read(row['path']))==row['sha256']
assert m.filehash(source)==source_hash
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r.update(scope=__doc__,postinstall_source_sha256=source_hash,parent_fixture_sha256=r['fixture_sha256'],
    fixture_name=target.name,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),
    installation_run_strict_passed=package['combined_checks_passed'],
    preceding_dashboard_return=audit['dashboard_return'],preceding_host_termination=termination,
    preserved_during_staging=preserved,video_trace_reset=False,
    installation_method='Second ordinary boot of installed state. Only startup and new helper folder changed; no driver, registry or trace reset.',
    workload_directory='xwns99',workload_change='Same probe source with xwns98 replaced by xwns99, rebuilt with pinned compiler.')
# Do not present first-stage SOFTWARE metadata as a second-stage edit.
r['first_stage_software_edit']={n:r.pop(n) for n in ['software_edit','software_before_sha256','software_after_sha256']}
r['startup_unchanged']=False
r['software_unchanged_during_second_staging']=True
(k/'fixture-002.json').write_text(json.dumps(r,indent=2)+'\n');print('Installed state and old workload preserved; second workload staged')

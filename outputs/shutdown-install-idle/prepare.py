"""Paired idle/restart fixtures: unchanged control001 and GPU package002."""
import importlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
review=json.loads((k/'probe-review.json').read_text());helper=(k/'artifacts/probe.exe').read_bytes()
assert review['passed'] and m.sha(helper)==review['probe_sha256']
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
for case,source in [('001','shutdown-popup-workload'),('002','shutdown-device-install')]:
 r=json.loads((k.parent/source/'fixture-001.json').read_text())
 parent=ws/'outputs/native-windows-fatx-forensics/artifacts'/r['fixture_name']
 parent_hash=r['fixture_sha256'];assert m.filehash(parent)==parent_hash
 target=parent.with_name('shutdown-install-idle-'+case+'.qcow2');seed=ws/('work/shutdown-install-idle-'+case+'-seed.qcow2')
 assert not target.exists() and not seed.exists()
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
 m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
 preserved={p:m.sha(w.read(p)) for p in ['winnt/system32/config/system','winnt/system32/config/software','winnt/system32/xwn-video-trace.bin']}
 for row in r['payloads']+r['preserved_payloads']:assert m.sha(w.read(row['path']))==row['sha256']
 startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
 script=b'@echo off\r\nC:\\xwnidle\\probe.exe\r\nexit\r\n'
 m.replace(w,startup,script)
 for row in r['payloads']:
  if row['path']==startup:row.update(sha256=m.sha(script),bytes=len(script))
 r['payloads'].append(w.write('xwnidle/probe.exe',helper));w.flush()
 fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'))
 assert all(m.sha(fresh.read(p))==sha for p,sha in preserved.items())
 for row in r['payloads']:assert m.sha(fresh.read(row['path']))==row['sha256']
 assert m.filehash(parent)==parent_hash
 subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
 subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
 r.update(scope=__doc__,case=case,physical_access=False,parent_fixture_sha256=parent_hash,
  fixture_name=target.name,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),
  source_manifest=source+'/fixture-001.json',preserved_during_idle_staging=preserved,
  startup_unchanged=False,idle_ms=120000,storage_workload=False,
  intervention='none beyond common idle helper/startup' if case=='001' else 'prior verified INF/miniport staging and DevicePath append; common idle helper/startup')
 for field in ['software_edit','software_before_sha256','software_after_sha256','installation_method','limits']:
  if field in r:r['inherited_'+field]=r.pop(field)
 r['limits']='Paired 120-second idle/restart experiment; prior parent metadata is inherited. No storage workload or physical qualification.'
 (k/('fixture-'+case+'.json')).write_text(json.dumps(r,indent=2)+'\n')
 print(case+' prepared',flush=True)

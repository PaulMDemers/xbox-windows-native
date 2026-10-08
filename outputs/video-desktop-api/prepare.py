"""Fresh desktop API child from immutable RAM0109 fixture; no driver or registry edits."""
import subprocess
from common import *
from allocation import scan
assert read(k.parent/'video-mode-trace3/verification.json')['passed']
assert read(k.parent/'video-mode-reset/verification.json')['passed']
assert read(k.parent/'video-shared-framebuffer/pair-review.json')['passed']
assert read(k.parent/'video-desktop-lifecycle/verification.json')['ordinary_qualified']
assert read(k.parent/'video-desktop-trace/failure-verification.json')['failure_preserved']
case='candidate001';out=k/case;out.mkdir(exist_ok=False)
parent=k.parent/'video-mode-reset/fixture-candidate001.json';f=read(parent)
source=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];assert sha(source)==f['fixture_sha256']
target=source.parent/'video-desktop-api-candidate001.qcow2';seed=ws/'work/video-desktop-api-candidate001-seed.qcow2'
assert not target.exists() and not seed.exists() and not (k/'fixture-candidate001.json').exists()
b=read(k/'pe-review.json');assert b['passed']
assert sha(k/'probe.c')==b['probe_source_sha256'] and sha(k/'artifacts/probe.exe')==b['probe_sha256']
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
with ColdIO(source) as io:
 rr=readers(io,source);protected=list(f['protected'])
 for name,digest in b['files'][0]['targets'].items():assert m.sha(rr['F'].read('winnt/system32/'+name))==digest
 for path in ['xwndesk126/probe.exe','xwndesk126/result.log']+['xwndesk126/ref%02d.rgb'%i for i in range(9)]:
  try:rr['F'].read(path)
  except KeyError:pass
  else:raise AssertionError('New path already exists: '+path)
 for row in f['payloads']:protected.append(dict(volume='F',path=row['path'],sha256=row['sha256']))
 for n in ['diskdump.sys','disk.sys','scsiport.sys','classpnp.sys','ftdisk.sys']:
  p='winnt/system32/drivers/'+n;protected.append(dict(volume='F',path=p,sha256=m.sha(rr['F'].read(p))))
 for row in protected:assert m.sha(rr[row['volume']].read(row['path']))==row['sha256']
 hives=[dict(path='winnt/system32/config/'+n,sha256=m.sha(rr['F'].read('winnt/system32/config/'+n))) for n in HIVES]
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
startup=b'@echo off\r\nC:\\xwndesk126\\probe.exe\r\nexit\r\n';m.replace(w,STARTUP,startup)
payloads=[w.write('xwndesk126/'+n,(k/'artifacts'/n).read_bytes()) for n in ['probe.exe']]
w.flush()
with ColdIO(target) as io:
 rr=readers(io,target);assert rr['F'].read(STARTUP)==startup
 for row in protected:assert m.sha(rr[row['volume']].read(row['path']))==row['sha256']
 for row in hives+payloads:assert m.sha(rr['F'].read(row['path']))==row['sha256']
 try:rr['F'].read('xwndesk126/result.log')
 except KeyError:pass
 else:raise AssertionError('One-shot intent already exists')
scan(target,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/'fixture-candidate001.json',dict(case=case,physical_access=False,intentional_crash=False,ordinary_qualified=False,fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),parents=parents,protected=protected,preserved_hives=hives,payloads=payloads,startup_sha256=m.sha(startup),guard_absent=True,readback_verified=True,pe_review_sha256=sha(k/'pe-review.json'),alias_verification_sha256=sha(k.parent/'video-shared-trace2/verification.json'),ram_mode_verification_sha256=sha(k.parent/'video-mode-trace3/verification.json'),parent_manifest_sha256=sha(parent),inherited_configuration=f['inherited_configuration']))
print('Prepared unique desktop API child; not launched')

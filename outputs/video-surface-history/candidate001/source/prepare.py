"""Fresh isolated RAM0110 parent; reviewed display payload and owned probe only."""
import subprocess
from common import *
from allocation import scan
assert read(k.parent/'video-mode-trace3/verification.json')['passed']
assert read(k.parent/'video-mode-reset/verification.json')['passed']
assert read(k.parent/'video-shared-framebuffer/pair-review.json')['passed']
case=sys.argv[1];assert case in ['candidate001'];out=k/case;out.mkdir(exist_ok=False)
parent=k.parent/'video-line-gdi/fixture-candidate001.json';f=read(parent)
driver=k.parent/('video-clip-upload/candidate001/artifacts/xwnown.dll' if case=='candidate001' else 'video-line-upload/candidate001/artifacts/xwnown.dll')
source=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];assert sha(source)==f['fixture_sha256']
target=source.parent/('video-surface-history-'+case+'.qcow2');seed=ws/('work/video-surface-history-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists() and not (k/('fixture-'+case+'.json')).exists()
b=read(k/'pe-review.json');assert b['passed']
assert sha(driver)==b['display_sha256' if case=='candidate001' else 'control_display_sha256']
assert sha(k/'probe.c')==b['probe_source_sha256'] and sha(k/'artifacts/probe.exe')==b['probe_sha256']
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
with ColdIO(source) as io:
 rr=readers(io,source);protected=list(f['protected'])
 for name,digest in b['files'][0]['targets'].items():assert m.sha(rr['F'].read('winnt/system32/'+name))==digest
 for path in ['xwnaddr141/probe.exe','xwnaddr141/result.log']+['xwnaddr141/'+pre+'%02d.rgb'%i for pre in ['ref','got'] for i in range(45)]:
  try:rr['F'].read(path)
  except KeyError:pass
  else:raise AssertionError('New path already exists: '+path)
 for row in f['payloads']:
  assert m.sha(rr['F'].read(row['path']))==row['sha256']
  if row['path']!='winnt/system32/xwnown.dll':protected.append(dict(volume='F',path=row['path'],sha256=row['sha256']))
 for n in ['diskdump.sys','disk.sys','scsiport.sys','classpnp.sys','ftdisk.sys']:
  p='winnt/system32/drivers/'+n;protected.append(dict(volume='F',path=p,sha256=m.sha(rr['F'].read(p))))
 for row in protected:assert m.sha(rr[row['volume']].read(row['path']))==row['sha256']
 hives=[dict(path='winnt/system32/config/'+n,sha256=m.sha(rr['F'].read('winnt/system32/config/'+n))) for n in HIVES]
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
startup=b'@echo off\r\nC:\\xwnaddr141\\probe.exe\r\nexit\r\n';m.replace(w,STARTUP,startup)
payloads=[w.write('xwnaddr141/'+n,(k/'artifacts'/n).read_bytes()) for n in ['probe.exe']]
m.replace(w,'winnt/system32/xwnown.dll',driver.read_bytes())
payloads.append(dict(path='winnt/system32/xwnown.dll',bytes=driver.stat().st_size,sha256=sha(driver)))
w.flush()
with ColdIO(target) as io:
 rr=readers(io,target);assert rr['F'].read(STARTUP)==startup
 for row in protected:assert m.sha(rr[row['volume']].read(row['path']))==row['sha256']
 for row in hives+payloads:assert m.sha(rr['F'].read(row['path']))==row['sha256']
 try:rr['F'].read('xwnaddr141/result.log')
 except KeyError:pass
 else:raise AssertionError('One-shot intent already exists')
scan(target,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/('fixture-'+case+'.json'),dict(case=case,physical_access=False,intentional_crash=False,ordinary_qualified=False,fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),parents=parents,protected=protected,preserved_hives=hives,payloads=payloads,startup_sha256=m.sha(startup),guard_absent=True,readback_verified=True,pe_review_sha256=sha(k/'pe-review.json'),alias_verification_sha256=sha(k.parent/'video-shared-trace2/verification.json'),ram_mode_verification_sha256=sha(k.parent/'video-mode-trace3/verification.json'),parent_manifest_sha256=sha(parent),inherited_configuration=f['inherited_configuration']))
print('Prepared unique desktop API child; not launched')

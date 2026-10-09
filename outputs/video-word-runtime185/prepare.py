"""New control/candidate siblings from identical normally shut down181 state."""
import subprocess
from common import *
case=sys.argv[1];assert case in ['control001','candidate001'];out=k/case;out.mkdir(exist_ok=False)
parent_info=read(k/'parent-copy.json');parent=Path(parent_info['copied_path']);assert sha(parent)==parent_info['copied_sha256']
parents=parent_info['parents']+[dict(path=str(parent),sha256=sha(parent))]
target=parent.with_name('video-word185-'+case+'.qcow2');seed=ws/('work/video-word-runtime185-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists()
files=dict(read(k.parent/'device-settled-reboot181/fixture-candidate001.json')['files'])
with ColdIO(parent) as io:
 rr=readers(io,parent)
 for name in list(files):
  v,p=name.split('/',1);actual=m.sha(rr[v].read(p))
  if p.startswith('winnt/system32/config/') or p in ['winnt/setupapi.log','winnt/system32/xwn-video-trace.bin']:files[name]=actual
  else:assert actual==files[name],name
 for n in HIVES:assert rr['F'].read('winnt/system32/config/'+n)==(k.parent/'device-settled-reboot181/candidate001/artifacts'/('after-'+n)).read_bytes(),n
 for label,meta in read(k/'sites.json')['binaries'].items():assert m.sha(rr['F'].read('winnt/system32/'+label))==meta['sha256']
 for p in ['xwnws185/runner.exe','xwnws185/replay.exe','xwnws185/attempt.log']:
  try:rr['F'].read(p)
  except KeyError:pass
  else:raise AssertionError('New namespace required')
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
preserved={p:m.sha(w.read(p)) for p in ['winnt/system32/config/system','winnt/system32/config/software','winnt/setupapi.log','winnt/system32/xwn-video-trace.bin','winnt/inf/xwnunused179.inf']}
for path,p in [('xwnws185/runner.exe',k/'artifacts/runner.exe'),('xwnws185/replay.exe',k/'artifacts/gdi-probe.exe')]:w.write(path,p.read_bytes());files['F/'+path]=sha(p)
payload=k.parent/'video-word-store184'/case/'artifacts/xwnown.dll'
assert read(k.parent/'video-word-store184/driver-review.json')['passed']
m.replace(w,'winnt/system32/xwnown.dll',payload.read_bytes());files['F/winnt/system32/xwnown.dll']=sha(payload)
startup=b'@echo off\r\nC:\\xwnws185\\runner.exe\r\nexit\r\n';m.replace(w,STARTUP,startup);files['F/'+STARTUP]=m.sha(startup);w.flush()
with ColdIO(target) as io:
 rr=readers(io,target)
 for name,digest in files.items():v,path=name.split('/',1);assert m.sha(rr[v].read(path))==digest,name
 for p,h in preserved.items():assert m.sha(rr['F'].read(p))==h,p
scan(target,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/('fixture-'+case+'.json'),dict(case=case,prepared=True,launched=False,physical_writes=False,parents=parents,fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),files=files,preserved_during_staging=preserved,display_build_sha256=sha(payload),limits='Same181 parent/hives/package/log history. Only matched115 display and new helper/startup; inherited emulator-only null policy, no physical qualification.'))
print('New185 matched ordinary child prepared:',case)

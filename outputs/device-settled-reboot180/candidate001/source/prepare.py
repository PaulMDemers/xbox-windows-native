"""Preserve179 closed image; verified metadata-only copy supplies a fresh child."""
import shutil,subprocess
from common import *
case=sys.argv[1];assert case=='candidate001';out=k/case;out.mkdir(exist_ok=False)
old=k.parent/'device-unused-package179';assert read(old/'candidate001/closure.json')['closed'];assert read(old/'candidate001/package-verification.json')['configuration_observed']
source=ws/'work/runs/nt5-unused179-candidate001/hdd.qcow2';original=sha(source)
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]));parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
parent=ws/'outputs/native-windows-fatx-forensics/artifacts/device-settled180-parent179.qcow2';assert not parent.exists()
shutil.copyfile(source,parent)
backing=Path(chain[1]['filename']).resolve()
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',str(backing),str(parent)],check=True)
subprocess.run(['qemu-img','compare',str(source),str(parent)],check=True)
assert sha(source)==original
save(k/'parent-copy.json',dict(original_path=str(source),original_sha256=original,copied_path=str(parent),copied_rebased_sha256=sha(parent),virtual_disk_equal=True,metadata_only_rebase=True,no_diagnostic_file_reset=True))
parents.append(dict(path=str(parent),sha256=sha(parent)))
target=parent.with_name('device-settled-reboot180-candidate001.qcow2');seed=ws/'work/device-settled-reboot180-candidate001-seed.qcow2';assert not target.exists() and not seed.exists()
f=read(old/'fixture-candidate001.json');files=dict(f['files'])
with ColdIO(parent) as io:
 rr=readers(io,parent)
 for name in list(files):
  v,p=name.split('/',1);actual=m.sha(rr[v].read(p))
  if p.startswith('winnt/system32/config/') or p in ['winnt/setupapi.log','winnt/system32/xwn-video-trace.bin']:files[name]=actual
  else:assert actual==files[name],name
 for n in HIVES:assert rr['F'].read('winnt/system32/config/'+n)==(old/'candidate001/artifacts'/('after-'+n)).read_bytes(),n
 for label,meta in read(k/'sites.json')['binaries'].items():assert m.sha(rr['F'].read('winnt/system32/'+label))==meta['sha256']
 for p in ['xwnsr180/runner.exe','xwnsr180/replay.exe','xwnsr180/attempt.log']:
  try:rr['F'].read(p)
  except KeyError:pass
  else:raise AssertionError('Fresh namespace required')
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
preserved={p:m.sha(w.read(p)) for p in ['winnt/system32/config/system','winnt/system32/config/software','winnt/setupapi.log','winnt/system32/xwn-video-trace.bin','winnt/inf/xwnunused179.inf']}
for path,p in [('xwnsr180/runner.exe',k/'artifacts/runner.exe'),('xwnsr180/replay.exe',k/'artifacts/gdi-probe.exe')]:w.write(path,p.read_bytes());files['F/'+path]=sha(p)
startup=b'@echo off\r\nC:\\xwnsr180\\runner.exe\r\nexit\r\n';m.replace(w,STARTUP,startup);files['F/'+STARTUP]=m.sha(startup);w.flush()
with ColdIO(target) as io:
 rr=readers(io,target)
 for name,digest in files.items():v,path=name.split('/',1);assert m.sha(rr[v].read(path))==digest,name
 for p,d in preserved.items():assert m.sha(rr['F'].read(p))==d,p
scan(target,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/'fixture-candidate001.json',dict(case=case,prepared=True,launched=False,physical_writes=False,parents=parents,fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),files=files,preserved_during_staging=preserved,
 limits='Fresh subsequent boot from179 normally shut down state; inherited explicit null policy, no INF restage/registry edits/trace reset. No physical qualification.'))
print('Fresh180 no-action subsequent boot prepared')

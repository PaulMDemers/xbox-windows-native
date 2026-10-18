"""Independent, read-only NTFS-3G extraction of the closed guest's results."""
import hashlib,json,os,struct,subprocess,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(K.parent/'crypto-persistence423'));from ntfs_read002 import sha,Reader
P=Path('/home/paul/xbox-windows-native/d3d-depth480-independent001')
source=Path('/home/paul/xbox-windows-native/d3d-depth480-pc001/disk.qcow2')
state=json.loads((K/'ntfs-phase1.json').read_text());assert state['closed'] and sha(source)==state['disk_sha256']
cold=json.loads((K/'ntfs-cold1-002.json').read_text());manifest=json.loads((Path(cold['private_path'])/'manifest.json').read_text())
selected={n for n in manifest if n.startswith('xwn480/')}
selected.update('winnt/system32/config/'+n for n in ['system','software','sam','security','default'])
selected.update('winnt/system32/'+n for n in ['kernel32.dll','user32.dll','gdi32.dll','ddraw.dll','advapi32.dll'])
runtime=json.loads((K/'runtime-review001.json').read_text())
for row in runtime['rows']:
 if 'review' in row:
  for name in row['review']['modules']:
   path=name[3:].replace('\\','/').lower();assert path in manifest
   selected.add(path)
assert 12<len(selected)<64 and not P.exists() and not (K/'independent001.json').exists()
with Reader(source) as reader:start=reader.start
P.mkdir();mount=P/'view';mount.mkdir();volume=mount/'volume'
root=Path('/home/paul/xbox-windows-native/nbd423-tools002');offline=Path('/home/paul/xbox-windows-native/toolchains/offline-disk/root')
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(root/'usr/lib/x86_64-linux-gnu')+':'+str(offline/'usr/lib/x86_64-linux-gnu')
prior=json.loads((K.parent/'crypto-persistence423/third-reader002.json').read_text())
for n,h in prior['tools'].items():assert sha(Path(n))==h
cmd=[str(root/'usr/bin/nbdfuse'),'-r','-s','-d',str(volume),'[','qemu-nbd','--read-only','-f','qcow2','--offset='+str(start),str(source),']']
record=dict(disk_sha256=sha(source),command=cmd,rows=[],closed=False,passed=False,private_path=str(P),tools=prior['tools'])
def save():(K/'independent001.json').write_text(json.dumps(record,indent=2)+'\n')
with (P/'fuse.log').open('xb') as log:
 proc=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT);record['pid']=proc.pid;save()
 try:
  for _ in range(100):
   if volume.exists():break
   assert proc.poll() is None;time.sleep(.1)
  assert volume.exists()
  for i,n in enumerate(sorted(selected)):
   dest=P/'files'/manifest[n]['path'];dest.parent.mkdir(parents=True,exist_ok=True)
   with dest.open('xb') as f:r=subprocess.run([str(offline/'usr/bin/ntfscat'),str(volume),'/'+manifest[n]['path']],stdout=f,stderr=subprocess.PIPE,env=env,timeout=30)
   (P/f'file{i}.stderr').write_bytes(r.stderr);assert r.returncode==0,r.returncode
   h=sha(dest);assert h==manifest[n]['sha256'],n
   record['rows'].append(dict(path=n,bytes=dest.stat().st_size,sha256=h,agrees_with_first_reader=True));save()
  record['passed']=True
 except BaseException as e:record['error']=repr(e);raise
 finally:
  if any(str(mount) in line for line in Path('/proc/self/mountinfo').read_text().splitlines()):
   r=subprocess.run(['fusermount3','-u',str(mount)],capture_output=True,timeout=10);record['unmount_exit']=r.returncode
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5);record['host_terminate']=True
  record.update(closed=True,exit_code=proc.returncode,disk_unchanged=sha(source)==record['disk_sha256'],mount_absent=not any(str(mount) in line for line in Path('/proc/self/mountinfo').read_text().splitlines()));save()
print(json.dumps({k:record[k] for k in ['passed','closed','disk_unchanged','mount_absent']}))

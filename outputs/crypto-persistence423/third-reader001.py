"""Resolve eight closed-source reader discrepancies with independent NTFS-3G.
NBD is exposed as one read-only FUSE file, not mounted as an NTFS filesystem.
No root/kernel block attachment; unmount only this process's unique mountpoint.
"""
import hashlib,json,os,subprocess,time
from pathlib import Path
from ntfs_read002 import sha
K=Path(__file__).resolve().parent;P=Path('/home/paul/xbox-windows-native/crypto423-reader001')
source=Path('/home/paul/xbox-windows-native/clean-media404-oem001/disk.qcow2')
assert not P.exists() and not (K/'third-reader001.json').exists()
assert sha(source)=='ece991e4dc6b662ece2a39dddba384a3c480173cafd89086135f6bb861b7f796'
old=json.loads((K/'reader-differences001.json').read_text());P.mkdir();mount=P/'view';mount.mkdir()
root=Path('/home/paul/xbox-windows-native/nbd423-tools002')
offline=Path('/home/paul/xbox-windows-native/toolchains/offline-disk/root')
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(root/'usr/lib/x86_64-linux-gnu')+':'+str(offline/'usr/lib/x86_64-linux-gnu')
volume=mount/'volume';cmd=[str(root/'usr/bin/nbdfuse'),'-r','-s','-d',str(volume),'[','qemu-nbd','--read-only','-f','qcow2','--offset=32256',str(source),']']
record={'source_sha256':sha(source),'command':cmd,'rows':[],'closed':False,'passed':False,'tools':{str(p):sha(p) for p in [root/'usr/bin/nbdfuse',root/'usr/lib/x86_64-linux-gnu/libnbd.so.0',offline/'usr/bin/ntfscat',offline/'usr/lib/x86_64-linux-gnu/libntfs-3g.so.89']},'packages':{p.name:sha(p) for p in Path('/mnt/e/xwn423/nbd-tools001').glob('*.deb')}}
def save():(K/'third-reader001.json').write_text(json.dumps(record,indent=2)+'\n')
with (P/'fuse.log').open('xb') as log:
 proc=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT);record['pid']=proc.pid;save()
 try:
  for _ in range(100):
   if volume.exists():break
   assert proc.poll() is None,'FUSE exited before ready'
   time.sleep(.1)
  assert volume.exists() and volume.stat().st_size==2*1024**3-32256
  assert any(str(mount) in line for line in Path('/proc/self/mountinfo').read_text().splitlines())
  for i,row in enumerate(old['differences']):
   out=P/f'file{i}.bin'
   with out.open('xb') as f:
    result=subprocess.run([str(offline/'usr/bin/ntfscat'),str(volume),'/'+row['path']],stdout=f,stderr=subprocess.PIPE,env=env,timeout=30)
   (P/f'file{i}.stderr').write_bytes(result.stderr);assert result.returncode==0,result.returncode
   h=sha(out);record['rows'].append({'path':row['path'],'sha256':h,'bytes':out.stat().st_size,'matches_prior_7zip':h==row['prior_7zip_sha256'],'matches_dissect_raw':h==row['raw_sha256'],'matches_dissect_zeroed_tail':h==row['logical_zero_tail_sha256']});save()
  record['passed']=all(r['matches_prior_7zip'] for r in record['rows'])
 except BaseException as exc:record['error']=repr(exc);raise
 finally:
  if any(str(mount) in line for line in Path('/proc/self/mountinfo').read_text().splitlines()):
   unmount=subprocess.run(['fusermount3','-u',str(mount)],capture_output=True,timeout=10);record['unmount_exit']=unmount.returncode
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5);record['host_terminate']=True
  record.update(closed=True,exit_code=proc.returncode,source_unchanged=sha(source)==record['source_sha256'],mount_absent=not any(str(mount) in line for line in Path('/proc/self/mountinfo').read_text().splitlines()));save()
print(json.dumps({'passed':record['passed'],'files':len(record['rows']),'mount_absent':record['mount_absent'],'source_unchanged':record['source_unchanged']}))

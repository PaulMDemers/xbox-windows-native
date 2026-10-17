"""Independent NTFS-3G cold read of the CLOSED two-boot witness and protected state."""
import hashlib,json,os,subprocess,time
from pathlib import Path
from ntfs_read002 import sha
from results import decode
K=Path(__file__).resolve().parent;P=Path('/home/paul/xbox-windows-native/crypto423-independent001')
source=Path('/home/paul/xbox-windows-native/crypto423-ntfs001/disk.qcow2')
state=json.loads((K/'ntfs-phase2.json').read_text());assert state['closed'] and sha(source)==state['disk_sha256']
cold=json.loads((K/'ntfs-cold2-002.json').read_text());manifest=json.loads((Path(cold['private_path'])/'manifest.json').read_text())
original={r['path'].lower():r for r in json.loads(Path('/mnt/c/xwn405/extract004/files.json').read_text())}
diff=json.loads((K/'reader-differences001.json').read_text())['differences']
selected={r['path'] for r in diff}
selected.update(n for n in manifest if n.startswith('xwn423/') or '/microsoft/crypto/' in n or '/microsoft/protect/' in n)
selected.update('winnt/system32/config/'+n for n in ['system','software','sam','security','default'])
selected.update('winnt/system32/'+n for n in ['advapi32.dll','crypt32.dll','rsaenh.dll','kernel32.dll'])
assert 20<len(selected)<100 and not P.exists() and not (K/'ntfs-independent001.json').exists()
P.mkdir();mount=P/'view';mount.mkdir();volume=mount/'volume'
root=Path('/home/paul/xbox-windows-native/nbd423-tools002');offline=Path('/home/paul/xbox-windows-native/toolchains/offline-disk/root')
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(root/'usr/lib/x86_64-linux-gnu')+':'+str(offline/'usr/lib/x86_64-linux-gnu')
prior=json.loads((K/'third-reader002.json').read_text())
for name,h in prior['tools'].items():assert sha(Path(name))==h
cmd=[str(root/'usr/bin/nbdfuse'),'-r','-s','-d',str(volume),'[','qemu-nbd','--read-only','-f','qcow2','--offset=32256',str(source),']']
record={'disk_sha256':sha(source),'command':cmd,'rows':[],'closed':False,'passed':False,'probe':{},'private_path':str(P)}
def save():(K/'ntfs-independent001.json').write_text(json.dumps(record,indent=2)+'\n')
with (P/'fuse.log').open('xb') as log:
 proc=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT);record['pid']=proc.pid;save()
 try:
  for _ in range(100):
   if volume.exists():break
   assert proc.poll() is None;time.sleep(.1)
  assert volume.exists()
  for i,name in enumerate(sorted(selected)):
   dest=P/'files'/manifest[name]['path'];dest.parent.mkdir(parents=True,exist_ok=True)
   with dest.open('xb') as f:result=subprocess.run([str(offline/'usr/bin/ntfscat'),str(volume),'/'+manifest[name]['path']],stdout=f,stderr=subprocess.PIPE,env=env,timeout=30)
   (P/f'file{i}.stderr').write_bytes(result.stderr);assert result.returncode==0,result.returncode
   h=sha(dest);row={'path':name,'bytes':dest.stat().st_size,'sha256':h,'matches_dissect_raw':h==manifest[name]['sha256']}
   if name.startswith('winnt/system32/dllcache/') or name in ['winnt/system32/'+n for n in ['advapi32.dll','crypt32.dll','rsaenh.dll','kernel32.dll']]:
    row['matches_original_7zip']=h==original[name]['sha256'];assert row['matches_original_7zip'],name
   elif not name.endswith('.evt'):assert row['matches_dissect_raw'],name
   if name in ['xwn423/create.log','xwn423/reopen.log']:
    phase=1 if name.endswith('/create.log') else 2
    record['probe'][str(phase)]=decode(dest.read_bytes(),phase)
    assert record['probe'][str(phase)]['all_api_operations_passed'] and record['probe'][str(phase)]['all_names_passed']
   record['rows'].append(row);save()
  assert len(record['probe'])==2
  record['passed']=True
 except BaseException as exc:record['error']=repr(exc);raise
 finally:
  if any(str(mount) in line for line in Path('/proc/self/mountinfo').read_text().splitlines()):
   unmount=subprocess.run(['fusermount3','-u',str(mount)],capture_output=True,timeout=10);record['unmount_exit']=unmount.returncode
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5);record['host_terminate']=True
  record.update(closed=True,exit_code=proc.returncode,disk_unchanged=sha(source)==record['disk_sha256'],mount_absent=not any(str(mount) in line for line in Path('/proc/self/mountinfo').read_text().splitlines()));save()
print(json.dumps({'passed':record['passed'],'files':len(record['rows']),'both_phase_api_passed':len(record['probe'])==2,'mount_absent':record['mount_absent'],'disk_unchanged':record['disk_unchanged']}))

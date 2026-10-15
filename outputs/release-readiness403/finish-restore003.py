"""Complete unstarted backup/restore stages after002 host hive-loader failure; no reinstall."""
import json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn403/install-restore002')
sys.path.insert(0,str(W/'tools'));import xwn_image as disk
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import m,sha,HIVES,hive
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not (K/'install-restore003.json').exists()
r=json.loads((K/'install-restore002.json').read_text());assert r['status']=='failed' and len(r['files'])==6571 and 'libhivex.so.0' in r['error']
r['prior_failure']=r.pop('error');r['prior_record_sha256']=sha(K/'install-restore002.json');r['status']='continuing-unstarted-restore'
raw=P/'installed.raw';parent=Path('/mnt/e/xwn329/seed001/source.qcow2');blank=Path('/mnt/c/Emulators/xemu/system/xbox_hdd.qcow2')
m.fatx.PARTITIONS['E']=(disk.START,disk.LENGTH)
def save():(K/'install-restore003.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 with raw.open('rb') as f:
  assert disk.outside(f)==r['outside_after_install']
  cold=m.Writer(f,m.fatx.open_partition(f,raw,'E'))
  for row in r['files']:assert m.sha(cold.read(row['path']))==row['sha256']
  r['hives']=[]
  for name in HIVES:
   p=P/('verified-hive-'+name);p.write_bytes(cold.read('winnt/system32/config/'+name));r['hives'].append(hive(p))
 r['backup']=disk.backup(raw,P/'backup')
 # Corrupt a known file's actual bytes in E, leaving the FATX geometry mountable.
 with raw.open('r+b') as f:
  cold=m.Writer(f,m.fatx.open_partition(f,raw,'E'));at=1
  for name in ['applications','xwneboot','default.xbe']:
   entry=cold.directory(at)['entries'][name][2];at=int.from_bytes(entry[44:48],'little')
  offset=cold.p.cluster_offset(at);f.seek(offset);before=f.read(32);f.seek(offset);f.write(bytes(x^0x55 for x in before));f.flush();os.fsync(f.fileno())
  r['damage']={'offset':offset,'bytes':32,'before_sha256':m.sha(before),'after_sha256':m.sha(bytes(x^0x55 for x in before))}
 r['restore']=disk.restore(raw,P/'backup',P/'restore')
 with raw.open('rb') as f:
  cold=m.Writer(f,m.fatx.open_partition(f,raw,'E'))
  assert all(cold.directory(1)['entries'][n][2].hex()==v for n,v in r['preserved_factory_roots'].items())
  for row in r['files']:assert m.sha(cold.read(row['path']))==row['sha256']
 r['restored_readback_files']=len(r['files'])
 target=P/'restored.qcow2'
 subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(raw),str(target)],check=True)
 subprocess.run(['qemu-img','compare','-f','raw','-F','qcow2',str(raw),str(target)],check=True)
 r['qcow_check']=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(target)]))
 r['fixture_sha256']=sha(target);r['fixture_path']=str(target)
 assert sha(parent)==r['dashboard_parent_sha256'] and sha(blank)==r['blank_sha256']
 r.update(status='restored-byte-exact',guest_boot_performed=False,source_inputs_unchanged=True)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:save()
print(r['status'],len(r['files']),flush=True)

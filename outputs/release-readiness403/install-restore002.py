"""Private prepared-payload install and full E restore on a disposable raw image."""
import hashlib,importlib,json,os,shutil,subprocess,sys,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn403/install-restore002')
sys.path.insert(0,str(W/'tools'));import xwn_image as disk
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha,HIVES,hive
assert not P.exists() and os.environ.get('XWN_BUILD_LEASE')=='held'
assert shutil.disk_usage('/mnt/c').free-12*1024**3>20*1024**3
archive=Path('/mnt/c/xwn399/system002/xwn-private-E-720p-demo-20261014.zip')
assert sha(archive)=='e1c242e7c9b3d2d0dbfd09d86106272845656ca116f6126858213fc9788f0546'
blank=Path('/mnt/c/Emulators/xemu/system/xbox_hdd.qcow2');parent=Path('/mnt/e/xwn329/seed001/source.qcow2')
pin=json.loads((W/'outputs/artifact-recovery329/seed001/fixture.json').read_text())
assert sha(parent)==pin['fixture_sha256']
P.mkdir(parents=True);raw=P/'installed.raw';r=dict(status='started',physical_access=False,source_archive_sha256=sha(archive),blank_sha256=sha(blank),dashboard_parent_sha256=sha(parent),files=[],scope='Prepared private payload, not fresh Windows-media installation')
def save():(K/'install-restore002.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(blank),str(raw)],check=True)
 with raw.open('r+b') as f,ColdIO(parent) as src:
  f.truncate(disk.SIZE)
  start=4609024*512;size=1024000*512
  for off in range(0,size,4*1024**2):
   src.seek(start+off);b=src.read(min(4*1024**2,size-off));f.seek(start+off);f.write(b)
  f.flush();r['outside_before_install']=disk.outside(f)
  m.fatx.PARTITIONS['E']=(disk.START,disk.LENGTH)
  writer=m.Writer(f,m.fatx.open_partition(f,raw,'E'))
  existing=writer.directory(1)['entries'];assert set(existing)=={'tdata','udata'}
  r['preserved_factory_roots']={n:row[2].hex() for n,row in existing.items()}
  assert all(n not in existing for n in ['winnt','documents and settings','program files','applications','xwndemo372'])
  with zipfile.ZipFile(archive) as z:
   manifest=json.loads(z.read('MANIFEST.json'));files={p:row for p,row in manifest['files'].items() if p.startswith('payload/E/')}
   assert len(files)==6571 and len(set(p.lower() for p in files))==len(files)
   for p,row in files.items():
    name=p.removeprefix('payload/E/');writer.parts(name);b=z.read(p);assert len(b)==row['bytes'] and m.sha(b)==row['sha256']
   launcher='payload/E/Applications/XWNEBoot/default.xbe'
   for p in sorted(set(files)-{launcher})+[launcher]:
    row=writer.write(p.removeprefix('payload/E/'),z.read(p));r['files'].append(row)
    if len(r['files'])%1000==0:print('Installed',len(r['files']),flush=True)
  writer.flush();os.fsync(f.fileno())
  cold=m.Writer(f,m.fatx.open_partition(f,raw,'E'))
  assert all(cold.directory(1)['entries'][n][2].hex()==v for n,v in r['preserved_factory_roots'].items())
  for row in r['files']:assert m.sha(cold.read(row['path']))==row['sha256']
  r['launcher_last']=r['files'][-1]['path']=='Applications/XWNEBoot/default.xbe'
  r['outside_after_install']=disk.outside(f);assert r['outside_before_install']==r['outside_after_install']
  r['hives']=[]
  for name in HIVES:
   p=P/('hive-'+name);p.write_bytes(cold.read('winnt/system32/config/'+name));r['hives'].append(hive(p))
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

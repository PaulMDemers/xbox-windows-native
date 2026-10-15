"""Instrument the never-booted restored image only after byte-exact restoration."""
import json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn403/install-restore002');out=K/'emu001';assert not out.exists() and os.environ.get('XWN_BUILD_LEASE')=='held'
r0=json.loads((K/'install-restore003.json').read_text());assert r0['status']=='restored-byte-exact'
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha,STARTUP
from stock_io002 import scan
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
parent=P/'restored.qcow2';assert sha(parent)==r0['fixture_sha256'];raw=P/'installed.raw';target=P/'boot-source.qcow2';assert raw.is_file() and not target.exists()
out.mkdir();(out/'artifacts').mkdir();ns='xwnrelease403'
r={'prepared':False,'physical_access':False,'parent':str(parent),'parent_sha256':sha(parent),'changes':[],'registry_edited':False,'instrumentation_after_verified_restore':True}
def save():(out/'preparation.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 donor=Path('/mnt/e/xwn339/seed001/source.qcow2');df=json.loads((W/'outputs/stock-repeat339/emu001/fixture.json').read_text());assert sha(donor)==df['fixture_sha256']
 r['program_donor_sha256']=sha(donor);r['program_donor_used_as_disk_parent']=False
 with raw.open('r+b') as fp,ColdIO(donor) as d:
  wr=m.Writer(fp,m.fatx.open_partition(fp,raw,'E'));dr=m.Writer(d,m.fatx.open_partition(d,donor,'E'));assert ns not in wr.directory(1)['entries']
  for name in ['runner.exe','wizard.exe','state.exe','probe.exe','replay.exe']:
   b=dr.read('xwnstock339/'+name)
   if name=='replay.exe':
    b=Path('/mnt/e/xwn370/build001/replay.exe').read_bytes();assert m.sha(b)==json.loads((W/'outputs/stretch-probe370/build-review001.json').read_text())['binary_sha256']
   r['changes'].append(wr.write(ns+'/'+name,b))
  r['changes'].append(wr.write(ns+'/display-settings.exe',wr.read('xwndemo372/display-settings.exe')))
  before=wr.read(STARTUP);(out/'artifacts/normal-startup.cmd').write_bytes(before)
  after=('@echo off\r\nC:\\'+ns+'\\display-settings.exe selftest > C:\\'+ns+'\\settings-selftest.txt\r\nif errorlevel 1 exit\r\nC:\\'+ns+'\\display-settings.exe outline > C:\\'+ns+'\\settings-outline.txt\r\nif errorlevel 1 exit\r\nC:\\'+ns+'\\display-settings.exe status > C:\\'+ns+'\\settings-status.txt\r\nC:\\'+ns+'\\runner.exe /emulator\r\nexit\r\n').encode()
  m.replace(wr,STARTUP,after);wr.flush();fp.flush();r['startup']={'before_sha256':m.sha(before),'after_sha256':m.sha(after)}
  for n in ['system','software','default','sam','security']:(out/'artifacts'/('before-'+n)).write_bytes(wr.read('winnt/system32/config/'+n))
  protected={}
  for row in r0['files']:
   name=row['path']
   if name.lower().startswith('applications/xwneboot/') or Path(name).suffix.lower() in ['.exe','.dll','.sys']:
    protected['E/'+name]=m.sha(wr.read(name))
  protected.update({'E/'+v['path']:v['sha256'] for v in r['changes']})
  files={'E/'+row['path']:row['sha256'] for row in r0['files']};files.update(protected);files['E/'+STARTUP]=m.sha(after)
 subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(raw),str(target)],check=True)
 subprocess.run(['qemu-img','compare','-f','raw','-F','qcow2',str(raw),str(target)],check=True)
 subprocess.run(['qemu-img','check',str(target)],check=True)
 f={'fixture_path_linux':str(target),'fixture_path_windows':'C:'+str(target)[6:],'fixture_sha256':sha(target),'parent':str(parent),'parent_sha256':sha(parent),'namespace':ns,'profile_mode':1,'stretch_mode':1,'files':files,'protected':protected}
 (out/'fixture.json').write_text(json.dumps(f,indent=2)+'\n')
 scan(target,out/'before-allocation/artifacts');assert json.loads((out/'before-allocation/allocation.json').read_text())['allocation_consistent']
 assert raw.resolve()==Path('/mnt/c/xwn403/install-restore002/installed.raw');raw.unlink()
 r.update(prepared=True,source_sha256=f['fixture_sha256'],raw_removed_after_virtual_equality=True);save()
except BaseException as e:r['error']=repr(e);save();raise
print('Prepared restore boot, no launch',flush=True)

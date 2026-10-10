"""Fresh standalone sacrificial221 fixtures; never mutate any parent."""
import subprocess
from common import *
sys.path.insert(0,str(k.parent/'setup-wizard-automation201'));from restore import restore
case=sys.argv[1];assert case in ['control001','candidate001'];out=k/case;assert not out.exists()
review=read(k/'review.json');assert review['passed']
f=read(k.parent/'video-upload-runtime211/fixture-candidate001.json');base=Path(f['fixture_path_linux']);assert sha(base)==f['fixture_sha256']
root=Path('/mnt/e/Codex-archive/xbox-windows-native/reset221');root.mkdir(exist_ok=True)
target=root/(case+'-preparation.qcow2');source=root/(case+'-source.qcow2');assert not target.exists() and not source.exists()
out.mkdir();art=out/'artifacts';art.mkdir();files=dict(f['files']);protected=dict(f['protected'])
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;io=m.SliceIO(target);rr=readers(io,target)
for name,digest in files.items():v,p=name.split('/',1);assert m.sha(rr[v].read(p))==digest,name
for name in ['intent.log','probe.exe','trigger.sys']:
 try:rr['F'].read('xwnguard221/'+name)
 except KeyError:pass
 else:raise AssertionError('Fresh namespace required')
for name in ['probe.exe','trigger.sys']:
 p=k/'artifacts'/name;assert sha(p)==review['helpers'][name]['sha256'];rr['F'].write('xwnguard221/'+name,p.read_bytes());files['F/xwnguard221/'+name]=sha(p);protected['F/xwnguard221/'+name]=sha(p)
binary=k.parent/'video-boot-layout219/artifacts/build001'/case/'xboxbvid.dll';assert sha(binary)==review['providers'][case]['sha256']
path='Applications/XWNFBoot/loader/xboxbvid.dll';restore(rr['E'],path,binary.read_bytes());files['E/'+path]=sha(binary);protected['E/'+path]=sha(binary)
startup=b'@echo off\r\nC:\\xwnguard221\\probe.exe\r\nexit\r\n';restore(rr['F'],STARTUP,startup);files['F/'+STARTUP]=m.sha(startup)
for reader in rr.values():reader.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(source)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(source)],check=True)
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)]));assert not info.get('backing-filename')
with ColdIO(source) as io:
 after=readers(io,source)
 for name,digest in files.items():v,p=name.split('/',1);assert m.sha(after[v].read(p))==digest,name
 for name in HIVES:
  p=art/('before-'+name);p.write_bytes(after['F'].read('winnt/system32/config/'+name));hive(p)
scan(source,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==f['fixture_sha256']
save(k/('fixture-'+case+'.json'),dict(case=case,prepared=True,namespace='xwnguard221',files=files,protected=protected,parent=str(base),parent_sha256=f['fixture_sha256'],fixture_path_linux=str(source),fixture_path_windows='E:/Codex-archive/xbox-windows-native/reset221/'+source.name,fixture_sha256=sha(source),seed_sha256=sha(source),physical_access=False,guest_launch=False,device_policy=f['device_policy'],inherited_null_policy=False,intentional_crash=True,ordinary_qualified=False))
print('Fresh221 prepared:',case)

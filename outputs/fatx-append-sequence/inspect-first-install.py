"""Read-only inventory of retained pre-install and settled emulator fixtures."""
import importlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'));from coldio import ColdIO
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
out=k/'artifacts/first-install-inventory';out.mkdir(parents=True,exist_ok=True)
assert not (k/'first-install-inventory.json').exists()
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
r=dict(physical_access=False,read_only=True,fixtures={})
for label,manifest in [('pre_install','shutdown-device-install/fixture-001.json'),('settled','fatx-directory-order/fixture-001.json')]:
 f=json.loads((k.parent/manifest).read_text());disk=k.parent/'native-windows-fatx-forensics/artifacts'/f['fixture_name']
 assert m.filehash(disk)==f['fixture_sha256']
 with ColdIO(disk) as io:
  w=m.Writer(io,m.fatx.open_partition(io,disk,'F'))
  entry=dict(manifest=manifest,fixture_sha256=f['fixture_sha256'],hashes={})
  for path in ['winnt/system32/drivers/xwnfatx.sys','winnt/system32/drivers/xboxvnt5.sys','winnt/system32/framebuf.dll','xwninf99/xwnvideo.inf','winnt/setupapi.log']:
   data=w.read(path);entry['hashes'][path]=m.sha(data)
   if path.endswith('setupapi.log'):entry['setup_log_bytes']=len(data);entry['setup_log_non_ascii']=sum(b>127 for b in data)
  for hive in ['system','software']:
   data=w.read('winnt/system32/config/'+hive);p=out/(label+'-'+hive);p.write_bytes(data);h=hivex.Hivex(str(p));entry['hashes'][hive]=m.sha(data)
   def values(path):
    n=h.root()
    for part in path.split('\\'):
     n=h.node_get_child(n,part)
     if not n:return {}
    result={}
    for v in h.node_values(n):
     t,b=h.value_value(v);result[h.value_key(v)]=int.from_bytes(b,'little') if t==4 else (b.decode('utf-16le').rstrip('\0') if t in [1,2,7] else b.hex())
    return result
   if hive=='system':
    cs='ControlSet%03d'%values('Select')['Current']
    entry['gpu']=values(cs+r'\Enum\PCI\VEN_10DE&DEV_02A0&SUBSYS_00000000&REV_A1\3&477a1ca&0&00F0')
    entry['service']=values(cs+r'\Services\XboxVnt5')
    driver=entry['gpu'].get('Driver');entry['class']=values(cs+'\\Control\\Class\\'+driver) if driver else {}
   else:entry['device_path']=values(r'Microsoft\Windows\CurrentVersion').get('DevicePath')
  r['fixtures'][label]=entry
 assert m.filehash(disk)==f['fixture_sha256']
a=r['fixtures']['pre_install'];b=r['fixtures']['settled']
r['pre_install_has_no_gpu_class_binding']=not a['gpu'].get('Driver')
r['settled_has_gpu_class_binding']=bool(b['gpu'].get('Driver'))
r['same_video_and_inf']=all(a['hashes'][p]==b['hashes'][p] for p in ['winnt/system32/drivers/xboxvnt5.sys','winnt/system32/framebuf.dll','xwninf99/xwnvideo.inf'])
r['filesystem_differs']=a['hashes']['winnt/system32/drivers/xwnfatx.sys']!=b['hashes']['winnt/system32/drivers/xwnfatx.sys']
r['limits']='Inventory only, not a launch or qualified new fixture. An actual pre-install fixture exists, but its older FATX0098 must be explicitly replaced/reviewed before an0101 comparison. Historical emulator device policies remain unlike physical hardware.'
(k/'first-install-inventory.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:v for n,v in r.items() if n!='fixtures'},indent=2))

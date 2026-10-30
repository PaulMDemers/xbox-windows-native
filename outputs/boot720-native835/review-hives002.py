"""Read-only check of the immutable Windows E binding and display service. No FTP."""
import hashlib,json,shutil,struct,sys,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn835/hive-review002');assert not P.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
space=require_space(P,20.05);P.mkdir()
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
sha=lambda b:hashlib.sha256(b).hexdigest()
pkg=json.loads((K/'package001.json').read_text());z=zipfile.ZipFile('/mnt/e/xwn343/bundle002/stock-e-1080i-001.zip')
assert sha(z.read('MANIFEST.json'))==pkg['manifest_sha256'];r={'passed':False,'physical_access':False,'hives':{},'space':space}
def node(h,path):
 n=h.root()
 for part in path.split('\\'):
  n=h.node_get_child(n,part)
  if not n:return None
 return n
def value(h,n,key):
 if not n:return None
 v=h.node_get_value(n,key)
 if not v:return None
 typ,data=h.value_value(v)
 if typ==4:return int.from_bytes(data,'little')
 if typ in (1,2):return data.decode('utf-16le').rstrip('\0')
 return data.hex()
try:
 for name in ['system','software','default','sam','security']:
  remote='/E/winnt/system32/config/'+name;meta=pkg['files'][remote];data=z.read('payload'+meta['archive_path']);assert len(data)==meta['bytes'] and sha(data)==meta['sha256']
  p=P/name;p.write_bytes(data);h=hivex.Hivex(str(p));assert h.root();r['hives'][name]={'bytes':len(data),'sha256':sha(data),'parsed':True}
  if name=='system':
   sel=node(h,'Select');current=value(h,sel,'Current');assert current in [1,2]
   mounted=node(h,'MountedDevices');expected=struct.pack('<IQ',0xaa55,2884108288).hex()
   binding=value(h,mounted,'\\DosDevices\\C:');assert binding==expected
   r['windows_C_maps_dashboard_E']=True;r['e_start']=2884108288;r['synthetic_disk_signature']=0xaa55
   services={}
   for service in ['xwnfatx','xboxvnt5','nvnetnt5','atapi']:
    n=node(h,f'ControlSet{current:03d}\\Services\\'+service)
    assert n,service
    services[service]={k:value(h,n,k) for k in ['Start','Type','ImagePath','Group']}
   r['services']=services
   assert services['xwnfatx']['Start']==0 and services['atapi']['Start']==0
   assert services['xboxvnt5']['ImagePath'].lower().endswith('xboxvnt5.sys')
  del h
 r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:(K/'hive-review002.json').write_text(json.dumps(r,indent=2)+'\n')
print('Private hives parsed; C maps standard Xbox E; boot and video services present:',r['passed'])

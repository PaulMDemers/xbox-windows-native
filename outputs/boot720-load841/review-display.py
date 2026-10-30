"""Read-only display binding inventory from immutable package or retained hive."""
import hashlib,json,sys,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
sha=lambda b:hashlib.sha256(b).hexdigest()
label=sys.argv[1];assert label in ['baseline','cold']
out=K/('display-'+label+'001.json');assert not out.exists()
p=Path('/mnt/c/xwn841/display-'+label+'001');assert not p.exists();p.mkdir()
pkg=json.loads((W/'outputs/boot720-native835/package001.json').read_text())
if label=='baseline':
 with zipfile.ZipFile('/mnt/e/xwn343/bundle002/stock-e-1080i-001.zip') as z:
  assert sha(z.read('MANIFEST.json'))==pkg['manifest_sha256'];m=pkg['files']['/E/winnt/system32/config/system'];data=z.read('payload'+m['archive_path']);assert sha(data)==m['sha256']
else:
 data=Path('/mnt/c/xwn841/audit001/winnt/system32/config/system').read_bytes()
(p/'system').write_bytes(data);h=hivex.Hivex(str(p/'system'))
def node(path):
 n=h.root()
 for part in path.split('\\'):
  n=h.node_get_child(n,part)
  if not n:return None
 return n
def values(n):
 r={}
 for v in h.node_values(n):
  t,b=h.value_value(v);name=h.value_key(v)
  if t==4:v=int.from_bytes(b,'little')
  elif t in [1,2,7]:v=b.decode('utf-16le',errors='replace').rstrip('\0')
  else:v=b.hex()
  r[name]={'type':t,'value':v}
 return r
def walk(path,n,r):
 r[path]=values(n)
 for child in h.node_children(n):walk(path+'\\'+h.node_name(child),child,r)
r={'physical_access':False,'system_sha256':sha(data),'select':values(node('Select')),'keys':{}}
c=r['select']['Current']['value'];root=f'ControlSet{c:03d}'
for path in [root+'\\Services\\XboxVnt5',root+'\\Control\\Video']:
 n=node(path)
 if n:walk(path,n,r['keys'])
for path in [root+'\\Enum\\PCI',root+'\\Control\\CriticalDeviceDatabase']:
 n=node(path)
 if n:
  for child in h.node_children(n):
   if '02a0' in h.node_name(child).lower():walk(path+'\\'+h.node_name(child),child,r['keys'])
out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))

"""Read startup registrations from the immutable fixture, without changing it."""
import importlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'))
m=importlib.import_module('prepare-fixture')
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
base=ws/'outputs/native-windows-fatx-forensics/artifacts/gdi-baseline-003.qcow2'
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(base);w=m.Writer(io,m.fatx.open_partition(io,base,'F'))
path=k/'artifacts/before-software';path.write_bytes(w.read('winnt/system32/config/software'))
h=hivex.Hivex(str(path));result={}
for path in [r'Microsoft\Windows\CurrentVersion\Run',r'Microsoft\Windows\CurrentVersion\RunOnce',r'Microsoft\Windows\CurrentVersion\RunOnceEx',r'Microsoft\Windows NT\CurrentVersion\Winlogon']:
 n=h.root()
 for part in path.split('\\'):
  n=h.node_get_child(n,part)
  if not n:break
 if not n:continue
 values={}
 for v in h.node_values(n):
  t,d=h.value_value(v);name=h.value_key(v)
  if 'password' in name.lower():continue
  values[name]=d.decode('utf-16le',errors='replace').rstrip('\0') if t in (1,2,7) else d.hex()
 result[path]=values
(k/'fixture-startup.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

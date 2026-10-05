"""Read retained setup logs and one traced device's registry entry; no writes to guest media."""
import hashlib,importlib,json,os,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'))
m=importlib.import_module('prepare-fixture')
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
run=ws/'work/runs/nt5-video-shutdown-resolved-001'
assert (run/'cleanup.json').exists()
tr=json.loads((k/'exit-trace.json').read_text())
commands=[v['target_command_line'] for v in tr['events'] if v.get('target_image','').lower()=='rundll32.exe' and 'target_command_line' in v]
assert len(commands)==1 and commands[0].startswith('rundll32.exe newdev.dll,DevInstall PCI\\')
device=commands[0].split('DevInstall ',1)[1]
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
out=k/'artifacts';out.mkdir(exist_ok=True)
result=dict(scope=__doc__,physical_access=False,traced_device=device,traced_command=commands[0],snapshots={})
for label,disk in [('before',ws/'outputs/native-windows-fatx-forensics/artifacts/gdi-baseline-003.qcow2'),('after',run/'hdd.qcow2')]:
 io=m.SliceIO(disk);w=m.Writer(io,m.fatx.open_partition(io,disk,'F'))
 raw=w.read('winnt/setupapi.log');(out/(label+'-setupapi.log')).write_bytes(raw)
 text=raw.decode('utf-16le') if raw.startswith(b'\xff\xfe') else raw.decode('cp1252')
 lines=text.splitlines();hits=[i for i,line in enumerate(lines) if 'VEN_10DE&DEV_01B0' in line.upper()]
 selected=sorted({j for i in hits for j in range(max(0,i-2),min(len(lines),i+15))})
 system=out/(label+'-system');system.write_bytes(w.read('winnt/system32/config/system'))
 h=hivex.Hivex(str(system))
 def node(path):
  n=h.root()
  for part in path.split('\\'):
   n=h.node_get_child(n,part)
   if not n:return None
  return n
 current=h.value_dword(h.node_get_value(node('Select'),'Current'))
 n=node('ControlSet%03d\\Enum\\'%current+device);assert n
 values={}
 for v in h.node_values(n):
  name=h.value_key(v)
  if name not in ['ConfigFlags','Problem','Service','Driver','ClassGUID','Class','DeviceDesc','HardwareID','CompatibleIDs']:continue
  t,data=h.value_value(v)
  values[name]=int.from_bytes(data,'little') if t==4 else data.decode('utf-16le').rstrip('\0') if t in [1,2,7] else data.hex()
 result['snapshots'][label]=dict(setupapi_sha256=hashlib.sha256(raw).hexdigest(),matching_log_lines=[dict(line=i+1,text=lines[i]) for i in selected],control_set=current,device_values=values)
(k/'device-install-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({n:dict(device_values=v['device_values'],matching_log_lines=len(v['matching_log_lines'])) for n,v in result['snapshots'].items()},indent=2))

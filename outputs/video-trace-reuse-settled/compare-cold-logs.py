"""Read only diagnostic and SetupAPI files from closed owned fixtures."""
import importlib,json,sys,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'))
m=importlib.import_module('prepare-fixture');m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
r={'scope':__doc__,'runs':{}}
for name in ['nt5-video-reuse-002','nt5-video-reuse-control-001','nt5-video-reuse-rebuilt-control-001']:
 run=ws/'work/runs'/name
 assert (run/'cleanup.json').exists()
 disk=run/'hdd.qcow2';io=m.SliceIO(disk);w=m.Writer(io,m.fatx.open_partition(io,disk,'F'))
 row={};out=k/'artifacts'/name;out.mkdir(exist_ok=True)
 for path in ['winnt/setupapi.log','winnt/system32/xwn-video-trace.bin']:
  try:data=w.read(path)
  except Exception as exc:
   row[path]={'read_error':str(exc)};continue
  (out/path.split('/')[-1]).write_bytes(data)
  entry={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
  if path.endswith('.bin'):
   entry['count']=int.from_bytes(data[16:20],'little');entry['skips']=int.from_bytes(data[20:24],'little')
   entry['records']=[list(int.from_bytes(data[j:j+4],'little') for j in range(i,i+16,4)) for i in range(32,32+min(entry['count'],254)*16,16)]
  row[path]=entry
 r['runs'][name]=row
(k/'cold-log-comparison.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:{p:{k:v for k,v in e.items() if k!='records'} for p,e in row.items()} for n,row in r['runs'].items()},indent=2))

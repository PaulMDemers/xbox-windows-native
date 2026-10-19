"""MIT. Read closed retail installation metadata; proprietary files stay private."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(K.parent/'crypto-persistence423'));from ntfs_read002 import Reader,sha
sys.path.insert(0,str(W/'work/python-packages'));import pefile
from Registry import Registry
num=int(sys.argv[1]);assert num in (561,562,563)
T=K.parent/f'rct{num}';P=Path(json.loads((T/'edition.json').read_text())['fixture'])
state=json.loads((T/'ntfs-phase1.json').read_text());cold=json.loads((T/'ntfs-cold1-002.json').read_text())
assert state['closed'] and cold['complete'] and sha(P/'disk.qcow2')==cold['disk_sha256']
out=T/'installed001.json';assert not out.exists();dest=P/'installed-inspection001';assert not dest.exists();dest.mkdir()
manifest=json.loads((P/'cold1-002/manifest.json').read_text())
roots={561:'rct99/',562:'rctlater/',563:'rctdx/'};rows=[];files=[r for n,r in manifest.items() if n.startswith(roots[num])]
with Reader(P/'disk.qcow2') as reader:
 for row in files:
  n=row['path'];low=n.lower()
  if not low.endswith(('.exe','.ini','.cfg','.sv4')):continue
  data=reader.read(n);assert hashlib.sha256(data).hexdigest()==row['sha256']
  p=dest/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);item=dict(row)
  if low.endswith('.exe'):
   pe=pefile.PE(data=data);item['imports']={e.dll.decode():[i.name.decode() if i.name else i.ordinal for i in e.imports] for e in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[])}
   item['versions']=[{a.decode(errors='replace'):v.decode(errors='replace') for a,v in t.entries.items()} for g in getattr(pe,'FileInfo',[]) for info in g for t in getattr(info,'StringTable',[])]
   item['named_dll_strings']=[n.decode() for n in [b'ddraw.dll',b'd3dim.dll',b'dinput.dll',b'dsound.dll'] if n in data.lower()]
  rows.append(item)
assert sha(P/'disk.qcow2')==cold['disk_sha256']
reg=Registry.Registry(str(P/'cold1-002/files/WINNT/system32/config/software'));keys=[]
def walk(key):
 path=key.path()
 if any(t in path.lower() for t in ['rollercoaster','fish technology','chris sawyer']):
  keys.append(dict(key=path,values={v.name():v.value() for v in key.values() if v.name().lower() in ['path','installed path','cd path','installpath','language','version','displayversion','displayname','installlocation']}))
 for child in key.subkeys():walk(child)
walk(reg.root())
long_names=[r['path'] for r in files if any(len(part.encode('utf-8'))>42 for part in r['path'].split('/'))]
report=dict(attempt=num,files=len(files),bytes=sum(r['bytes'] for r in files),executables_and_saves=rows,registry=keys,
 fatx_over42_names=long_names,normal_shutdown_delta=cold['normal_shutdown_delta'],new_system_events=cold.get('new_system_events'),
 hives_clean=all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in cold['hives']),
 private_files=str(dest),console_access=False,scope='Closed-disk installation metadata; no live API trace, sound or Xbox qualification')
out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({n:report[n] for n in ['files','bytes','fatx_over42_names','normal_shutdown_delta','hives_clean']}))

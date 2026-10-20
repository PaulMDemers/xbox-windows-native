"""Check built PE contracts and imports against retained immutable NT5 files."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pefile
sys.path.insert(0,str(K.parent/'crypto-persistence423'));from ntfs_read002 import Reader
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
b=json.loads((K/'build001.json').read_text());assert b['status']=='compiled'
out=K/'imports-review001.json';assert not out.exists()
seed=Path('/home/paul/xbox-windows-native/clean-media404-oem001/disk.qcow2')
before=sha(seed);assert before=='ece991e4dc6b662ece2a39dddba384a3c480173cafd89086135f6bb861b7f796'
rows=[];exports={};dllpins={}
with Reader(seed) as reader:
 for name in ['kernel32.dll','user32.dll','advapi32.dll','gdi32.dll']:
  data=reader.read('WINNT/system32/'+name);p=pefile.PE(data=data)
  exports[name]={e.name.decode() for e in p.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
  dllpins[name]=hashlib.sha256(data).hexdigest()
for name,v in b['files'].items():
 p=Path(name);assert sha(p)==v['sha256']
 if p.suffix=='.c':assert p.read_bytes()==(K/p.name).read_bytes()
for row in b['rows']:
 p=Path(row['path']);pe=pefile.PE(str(p))
 assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.Magic==0x10b
 assert (pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
 imports={d.dll.decode().lower():[v.name.decode() for v in d.imports] for d in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[])}
 for name,symbols in imports.items():assert set(symbols)<=exports[name],(name,set(symbols)-exports[name])
 if p.name=='fixture.dll':assert [(e.name,e.ordinal) for e in pe.DIRECTORY_ENTRY_EXPORT.symbols]==[(b'probe601',7),(b'probe_dib604',9),(b'probe_phase605',10)]
 rows.append(dict(path=str(p),sha256=sha(p),imports=imports))
assert sha(seed)==before
out.write_text(json.dumps(dict(passed=True,rows=rows,seed_sha256=before,nt5_dlls=dllpins,physical_access=False,scope='Exact sources and PE/import-name compatibility; runtime behavior remains untested.'),indent=2)+'\n')
print('601 PE and actual NT5 import-name checks passed')

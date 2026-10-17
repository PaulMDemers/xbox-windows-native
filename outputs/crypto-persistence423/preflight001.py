"""Pin tools/owned NT5 DLL exports and check the new reader against old cold hashes."""
import hashlib,io,json,sys,zipfile
from pathlib import Path
from ntfs_read import Reader,Volume,sha
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/e/xwn423')
sys.path.insert(0,str(W/'work/python-packages'));import pefile
source=Path('/home/paul/xbox-windows-native/clean-media404-oem001/disk.qcow2')
assert sha(source)=='ece991e4dc6b662ece2a39dddba384a3c480173cafd89086135f6bb861b7f796'
assert not (K/'preflight001.json').exists()
record={'source_sha256':sha(source),'wheels':{},'package_files':{},'binary_imports':{},'cold_comparisons':{},'namespace_probe_only':True}
for p in sorted((P/'ntfs-wheels001').glob('*.whl')):
 with zipfile.ZipFile(p) as z:
  md=[n for n in z.namelist() if n.endswith('.dist-info/METADATA')];assert len(md)==1
  fields=[s for s in z.read(md[0]).decode().splitlines() if s.startswith(('Name:','Version:','License:','License-Expression:'))]
 record['wheels'][p.name]={'sha256':sha(p),'metadata':fields}
for p in sorted((P/'ntfs-python001').rglob('*')):
 if p.is_file() and '__pycache__' not in p.parts:record['package_files'][p.relative_to(P/'ntfs-python001').as_posix()]=sha(p)
# Independent model checks of actual stream adapter, including partition bounds.
raw=io.BytesIO(bytes(range(256))*16);v=Volume(raw,512,1024);checks=0
for pos in [0,1,511,1023,1024]:
 for size in [0,1,17,1024]:
  v.seek(pos);assert v.read(size)==raw.getvalue()[512+pos:512+min(pos+size,1024)];checks+=1
for pos in [-1,1025]:
 try:v.seek(pos)
 except ValueError:checks+=1
 else:raise AssertionError('out-of-volume accepted')
v.seek(-1,2);assert v.tell()==1023;v.seek(-3,1);assert v.tell()==1020;checks+=2
old=json.loads((K.parent/'clean-media404/cold-phase04.json').read_text())
with Reader(source) as reader:
 for name in ['winnt/system32/config/'+n for n in ['system','software','sam','security','default']]+['winnt/system32/ntoskrnl.exe','winnt/system32/hal.dll']:
  h=hashlib.sha256(reader.read(name)).hexdigest();assert h==old['files'][name]['sha256'],name;record['cold_comparisons'][name]=h
 modules={}
 def module(name):
  name=name.lower()
  if name not in modules:
   data=reader.read('WINNT/system32/'+name);pe=pefile.PE(data=data)
   exports={s.name.decode('ascii'):s for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
   modules[name]=(pe,exports,hashlib.sha256(data).hexdigest())
  return modules[name]
 def resolve(dll,name,seen=()):
  assert len(seen)<8 and (dll,name) not in seen
  pe,exports,h=module(dll);assert name in exports,(dll,name)
  symbol=exports[name]
  if symbol.forwarder:
   target,sym=symbol.forwarder.decode().rsplit('.',1);assert not sym.startswith('#')
   return [(dll,name,h)]+resolve(target+'.dll',sym,seen+((dll,name),))
  assert 0<symbol.address<pe.OPTIONAL_HEADER.SizeOfImage
  return [(dll,name,h)]
 build=json.loads((K/'build001.json').read_text())
 for row in build['rows']:
  path=Path(row['path']);assert sha(path)==row['sha256'];pe=pefile.PE(str(path));imports=[]
  assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.MajorSubsystemVersion==5 and pe.OPTIONAL_HEADER.MinorSubsystemVersion==0
  for dll in pe.DIRECTORY_ENTRY_IMPORT:
   for symbol in dll.imports:
    assert symbol.name is not None;imports.append(resolve(dll.dll.decode(),symbol.name.decode()))
  record['binary_imports'][row['name']]={'sha256':sha(path),'imports':imports,'entry_rva':pe.OPTIONAL_HEADER.AddressOfEntryPoint}
 module('rsaenh.dll');record['provider_sha256']=modules['rsaenh.dll'][2]
 record['partition']={'start':reader.start,'size':reader.size};record['nbd_bytes_read']=reader.raw.read_bytes
assert sha(source)==record['source_sha256']
record.update(stream_model_checks=checks,source_unchanged=True,passed=True,scope='Actual imports resolved against owned NT5 DLL exports; reader checked against seven prior independent cold hashes. No runtime API qualification or full NTFS allocation audit.')
(K/'preflight001.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'passed':True,'reader_cross_checks':len(record['cold_comparisons']),'import_counts':{n:len(r['imports']) for n,r in record['binary_imports'].items()}}))

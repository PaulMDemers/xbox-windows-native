"""Pin actual qualified0106 binaries and COFF symbols; static addresses are leads."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(k.parent/'video-cache-handoff/sites.json');mods={}
paths={n:Path(v['path']) for n,v in old['modules'].items()}
paths.update({'probe.exe':k/'artifacts/probe.exe','bootvid.dll':k/'trace002/artifacts/xboxbvid.dll','xboxvnt5.sys':k/'trace002/artifacts/xboxvnt5.sys'})
for name,path in paths.items():
 p=pefile.PE(str(path));d=path.read_bytes();symbols={};at=p.FILE_HEADER.PointerToSymbolTable;count=p.FILE_HEADER.NumberOfSymbols;strings=at+18*count;i=0
 while i<count:
  row=d[at+18*i:at+18*(i+1)];z,off=struct.unpack_from('<II',row);n=d[strings+off:].split(b'\0')[0] if z==0 else row[:8].split(b'\0')[0]
  val,section=struct.unpack_from('<Ih',row,8)
  if section>0:symbols[n.decode('ascii')]=p.sections[section-1].VirtualAddress+val
  i+=1+row[17]
 mods[name]=dict(path=str(path.resolve()),sha256=sha(path),preferred_base=p.OPTIONAL_HEADER.ImageBase,timestamp=p.FILE_HEADER.TimeDateStamp,image_size=p.OPTIONAL_HEADER.SizeOfImage,exports={e.name.decode():e.address for e in p.DIRECTORY_ENTRY_EXPORT.symbols if e.name} if hasattr(p,'DIRECTORY_ENTRY_EXPORT') else {},symbols=symbols if name=='bootvid.dll' else {})
pair=read(k.parent/'video-shared-framebuffer/pair-review.json');assert pair['passed']
build=read(k/'trace002/build.json')
for n,f in [('bootvid.dll','xboxbvid.dll'),('xboxvnt5.sys','xboxvnt5.sys')]:assert mods[n]['sha256']==next(v['sha256'] for v in build['files'] if v['name']==f)
for n in ['_XwnFbPublish@4','_Published','_References','_Ready','_Owner','_FrameBufferStart','_BackBuffer']:assert n in mods['bootvid.dll']['symbols']
for n in ['MmMapIoSpace','MmMapVideoDisplay','InbvCheckDisplayOwnership','InbvNotifyDisplayOwnershipLost','InbvAcquireDisplayOwnership']:assert n in mods['ntoskrnl.exe']['exports']
r={n:old[n] for n in ['kernel_base_expected','module_list_rva','thread_owner_offset']}
r.update(modules=mods,dependencies={str(p.relative_to(ws)):sha(p) for p in [k/'layouts.json',k/'process-layouts.json',k.parent/'video-shared-framebuffer/pair-review.json',ws/'outputs/native-windows-nt5-kernel/trace-entry.py',ws/'outputs/native-windows-prebuild/monitor_capture.py']},source_sha256=sha(Path(__file__)))
dest=k/'sites.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print('Qualified0106 modules and actual symbols pinned')

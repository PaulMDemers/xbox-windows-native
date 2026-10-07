"""Pin installed mapping API leads and existing read-only observer provenance."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
system=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);modules={}
for name,path,names in [('ntoskrnl.exe',system/'ntoskrnl.exe',['MmMapIoSpace','MmMapVideoDisplay']),('videoprt.sys',system/'drivers/videoprt.sys',['VideoPortMapMemory']),('xboxvnt5.sys',k.parent/'video-mapping-audit/artifacts/xboxvnt5.sys',[])]:
 p=pefile.PE(str(path));exports={e.name.decode():e.address for e in p.DIRECTORY_ENTRY_EXPORT.symbols if e.name};functions={}
 for n in names:
  rva=exports[n];raw=p.get_data(rva,512)
  functions[n]=dict(rva=rva,raw=raw.hex(),disassembly=[dict(rva=i.address,mnemonic=i.mnemonic,operands=i.op_str) for i in md.disasm(raw,rva)])
 modules[name]=dict(path=str(path.resolve()),sha256=sha(path),image_size=p.OPTIONAL_HEADER.SizeOfImage,preferred_base=p.OPTIONAL_HEADER.ImageBase,timestamp=p.FILE_HEADER.TimeDateStamp,functions=functions)
old=k.parent/'video-mapping-audit';build=read(old/'build-report.json');tests=read(old/'compiled-tests.json')
assert tests['passed'] and modules['xboxvnt5.sys']['sha256']==tests['sha256']==build['artifacts'][0]['sha256']=='ea18fa6c831b4cd9478cd85c65d2670b5ef0cb7892f804e9a1ed8572fc6a98ce'
pins={str(p.relative_to(ws)):sha(p) for p in [old/'build-report.json',old/'compiled-tests.json',old/'inputs.json',old/'0094-video-readonly-mapping-audit.patch',old/'video_mapping_audit.c']}
for rel,h in read(old/'inputs.json')['patch_sha256'].items():assert sha(ws/rel)==h
dest=k/'map-sites.json';assert not dest.exists();dest.write_text(json.dumps(dict(modules=modules,dependencies=pins,source_sha256=sha(Path(__file__)),limits='Static leads only; runtime requests/returns must be paired. Existing0094 observer is not physical qualification.'),indent=2)+'\n')
print('Pinned actual mapping APIs and read-only0094 observer')

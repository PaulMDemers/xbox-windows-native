"""Pin owned NT5 modules and actual GDI syscall stubs; static sites are leads."""
import hashlib,json,sys,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
system=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
mods={};pes={}
for name in ['ntoskrnl.exe','gdi32.dll','win32k.sys','framebuf.dll','probe.exe']:
 path=k/'artifacts/probe.exe' if name=='probe.exe' else system/name;p=pefile.PE(str(path));pes[name]=p
 mods[name]=dict(path=str(path.resolve()),sha256=sha(path),preferred_base=p.OPTIONAL_HEADER.ImageBase,timestamp=p.FILE_HEADER.TimeDateStamp,image_size=p.OPTIONAL_HEADER.SizeOfImage,exports={x.name.decode():x.address for x in p.DIRECTORY_ENTRY_EXPORT.symbols if x.name} if hasattr(p,'DIRECTORY_ENTRY_EXPORT') else {})
assert mods['gdi32.dll']['sha256']=='4525e25c187364c82be9f1885b1edc9c6f0465fe326e5087b167257f9e75b46f'
assert mods['win32k.sys']['sha256']=='414cc2568ba7f11fa58490060c947477f44d6218e6c52e01deea1bbe8a364a92'
assert mods['framebuf.dll']['sha256']=='5da1fe7c3cdaf67a4a487c8872c2034fbc425bfd36d2b7715b2a1c4caa51df86'
p=pes['gdi32.dll'];stubs={}
for name,rva,number,args in [('NtGdiBitBlt',0x3211c,0x100d,11),('NtGdiFlush',0x32774,0x1093,0)]:
 raw=p.get_data(rva,14 if args else 12);assert raw[:1]==b'\xb8' and struct.unpack_from('<I',raw,1)[0]==number and raw[5:11]==bytes.fromhex('8d542404cd2e')
 assert raw[11:]==(b'\xc2'+struct.pack('<H',args*4) if args else b'\xc3')
 stubs[name]=dict(rva=rva,service_number=number,argument_count=args,raw=raw.hex())
pub=read(ws/'outputs/native-windows-nt5-kernel/kernel-publics.json')['symbols'];dump=read(ws/'outputs/dump-map-trace/sites.json')
r=dict(scope=__doc__,modules=mods,stubs=stubs,kernel_base_expected=dump['kernel_base_expected'],module_list_rva=pub['_PsLoadedModuleList']['rva'],service_shadow_rva=pub['_KeServiceDescriptorTableShadow']['rva'],thread_owner_offset=read(ws/'outputs/shutdown-popup-workload/site-review.json')['thread_owner_offset'],surfobj_x86_offsets=dict(sizlBitmap=16,cjBits=24,pvBits=28,pvScan0=32,lDelta=36,iBitmapFormat=44,iType=48,fjBitmap=50),dependencies={str(p.relative_to(ws)):sha(p) for p in [ws/'outputs/native-windows-nt5-kernel/kernel-publics.json',ws/'outputs/shutdown-popup-workload/site-review.json',k/'layouts.json',ws/'outputs/native-windows-nt5-kernel/trace-entry.py',ws/'outputs/native-windows-prebuild/monitor_capture.py']},limits='NT5 x86 SURFOBJ layout from owned historical winddi header, validated against actual dimensions/stride at runtime. Modern headers add fields and are not used as NT5 offsets. Service-table function addresses must be read from the live pinned kernel; static names alone are not proof of execution.')
assert 'XwnPhase' in mods['probe.exe']['exports'];r['source_sha256']=sha(Path(__file__))
dest=k/'sites.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print('Pinned NT5 modules, marker and syscall stubs')

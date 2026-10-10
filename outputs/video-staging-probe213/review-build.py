"""Actual NT5 provider imports and native helper section/byte pins before launch."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'build-review.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(k/'build003.json');assert build['status']=='compiled';assert read(k/'host-tests003.json')['passed']
assert read(k/'parser-tests.json')['passed']
capture=read(k.parent/'video-upload-runtime211/capture.json');base=k.parent/'video-upload-runtime211/artifacts'
providers={};names={'ntoskrnl.exe':'F/winnt/system32/ntoskrnl.exe','hal.dll':'E/Applications/XWNFBoot/loader/halxboxnt5.dll',
 'videoprt.sys':'F/winnt/system32/drivers/videoprt.sys','bootvid.dll':'E/Applications/XWNFBoot/loader/xboxbvid.dll'}
exports={}
for dll,name in names.items():
 expected=next(x['sha256'] for x in capture['files'] if x['path'].lower()=='/'+name.lower())
 p=base/name;assert sha(p)==expected;pe=pefile.PE(str(p))
 exports[dll]={s.name.decode() for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
 providers[dll]=dict(path=name,sha256=expected)
bins={};decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
for row in build['builds']:
 p=k/'artifacts/build003'/row['case']/'xboxvnt5.sys';assert sha(p)==row['sha256'];pe=pefile.PE(str(p));imports={}
 for d in pe.DIRECTORY_ENTRY_IMPORT:
  dll=d.dll.decode().lower();symbols=[s.name.decode() if s.name else s.ordinal for s in d.imports]
  assert dll in exports and set(symbols)<=exports[dll],(dll,symbols)
  imports[dll]=symbols
 path='/mnt/c/'+p.resolve().as_posix().split(':/',1)[1]
 nm='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-nm'
 text=subprocess.check_output(['wsl','-d','Ubuntu','--',nm,'-n','--defined-only',path],text=True)
 symbols=[(int(x.split()[0],16),x.split()[2]) for x in text.splitlines() if len(x.split())==3 and x.split()[1] in ['t','T']]
 start=next(a for a,n in symbols if n=='_XgtNativeProbe@0');end=min(a for a,n in symbols if a>start)
 rva=start-pe.OPTIONAL_HEADER.ImageBase;section=pe.get_section_by_rva(rva)
 assert section.Name.rstrip(b'\0')==b'.text' and not section.Characteristics&0x02000000
 code=pe.get_data(rva,end-start);ins=[dict(rva=i.address-pe.OPTIONAL_HEADER.ImageBase,mnemonic=i.mnemonic,operands=i.op_str) for i in decoder.disasm(code,start)]
 assert any(i['mnemonic']=='ret' for i in ins)
 bins[row['case']]=dict(sha256=row['sha256'],bytes=row['bytes'],mode=row['mode'],imports=imports,
  helper=dict(rva=rva,bytes=len(code),section='.text',section_flags=section.Characteristics,disk_sha256=hashlib.sha256(code).hexdigest(),disk_instructions=ins))
mm={'MmAllocateContiguousMemorySpecifyCache','MmFreeContiguousMemorySpecifyCache','MmGetPhysicalAddress'}
assert not mm&set(bins['control001']['imports']['ntoskrnl.exe'])
assert mm<=set(bins['candidate001']['imports']['ntoskrnl.exe'])
before=read(k.parent/'video-shared-framebuffer/pe-review.json')['cases'][1]['imports']['xboxvnt5.sys']
assert bins['control001']['imports']==before
assert {d:set(v) for d,v in bins['candidate001']['imports'].items()}=={
 d:set(v)|(mm if d=='ntoskrnl.exe' else set()) for d,v in before.items()}
main={c:sha(k/'artifacts/build003'/c/'main.obj') for c in bins};assert len(set(main.values()))==1
dest.write_text(json.dumps(dict(passed=True,physical_access=False,guest_launch=False,gpu_submission=False,
 source_sha256=sha(Path(__file__)),build_sha256=sha(k/'build003.json'),binaries=bins,providers=providers,main_object_sha256=main,
 limits='Captured211 actual providers/export names and on-disk helper bytes. No assertion of resident execution, GPU ownership/cache visibility/completion or acceleration.'),indent=2)+'\n')
print('Matched native213 imports, exact common main object and helper section PASS')

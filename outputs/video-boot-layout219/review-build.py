"""Native219 image imports, exports and named layout sites before guest launch."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'build-review.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(k/'build001.json');assert b['status']=='compiled' and read(k/'host-tests002.json')['passed']
captured=ws/'outputs/video-upload-runtime211/artifacts';providers={};exports={}
for dll,path in [('ntoskrnl.exe',captured/'F/winnt/system32/ntoskrnl.exe'),('hal.dll',captured/'E/Applications/XWNFBoot/loader/halxboxnt5.dll')]:
    pe=pefile.PE(str(path));exports[dll]={s.name.decode() for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
    providers[dll]=dict(path=str(path.relative_to(ws)),sha256=sha(path))
bins={};nm='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-nm'
for row in b['builds']:
    p=k/'artifacts/build001'/row['case']/'xboxbvid.dll';assert sha(p)==row['sha256'];pe=pefile.PE(str(p));imports={}
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        dll=entry.dll.decode().lower();names=[s.name.decode() if s.name else s.ordinal for s in entry.imports]
        assert dll in exports and set(names)<=exports[dll],(dll,names);imports[dll]=names
    exposed={s.name.decode():s.address for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
    linux='/mnt/c/'+p.resolve().as_posix().split(':/',1)[1]
    symbols=subprocess.check_output(['wsl','-d','Ubuntu','--',nm,'-n','--defined-only',linux],text=True)
    selected={}
    for line in symbols.splitlines():
        v=line.split()
        if len(v)==3 and v[2] in ['_FrameBufferStart','_BackBuffer','_BootWritableBytes','_ResetDisplay','_ResetDisplay@4','_VidInitialize@4']:
            selected[v[2]]=dict(rva=int(v[0],16)-pe.OPTIONAL_HEADER.ImageBase,kind=v[1])
    assert '_FrameBufferStart' in selected and '_BackBuffer' in selected
    if row['case']=='candidate001':assert '_BootWritableBytes' in selected
    bins[row['case']]=dict(sha256=sha(p),bytes=p.stat().st_size,imports=imports,exports=exposed,symbols=selected,
        image_base=pe.OPTIONAL_HEADER.ImageBase,image_size=pe.OPTIONAL_HEADER.SizeOfImage,timestamp=pe.FILE_HEADER.TimeDateStamp)
assert bins['control001']['imports']==bins['candidate001']['imports']
assert bins['control001']['exports'].keys()==bins['candidate001']['exports'].keys()
out=dict(passed=True,source_sha256=sha(Path(__file__)),build_sha256=sha(k/'build001.json'),binaries=bins,providers=providers,
    exports_unchanged=True,imports_unchanged=True,guest_launch=False,physical_access=False,
    limits='On-disk image/import/symbol review only; resident execution, layout guards, ordinary shutdown and physical ownership remain unqualified.')
dest.write_text(json.dumps(out,indent=2)+'\n');print('Native matched boot providers imports/exports reviewed')

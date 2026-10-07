"""Pin explicit crash helper/driver imports and actual owned kernel dump boundaries."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'))
import pefile,capstone
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
system=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
rows={};targets={}
for name in ['probe.exe','trigger.sys']:
    p=k/'artifacts'/name;pe=pefile.PE(str(p));imports={}
    assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.MajorSubsystemVersion==5
    assert pe.OPTIONAL_HEADER.Subsystem==(1 if name.endswith('.sys') else 3)
    assert pe.OPTIONAL_HEADER.CheckSum==pe.generate_checksum()
    for e in pe.DIRECTORY_ENTRY_IMPORT:
        dll=e.dll.decode();target=system/dll;ex={v.name for v in pefile.PE(str(target)).DIRECTORY_ENTRY_EXPORT.symbols if v.name}
        assert all(i.name in ex for i in e.imports);imports[dll]=[i.name.decode() for i in e.imports];targets[dll]=sha(target)
    rows[name]=dict(sha256=sha(p),size=p.stat().st_size,entry_rva=pe.OPTIONAL_HEADER.AddressOfEntryPoint,imports=imports,checksum_valid=True)
gcc='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
compiler_sha=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',gcc],text=True).split()[0]
assert compiler_sha=='83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
inputs=['trigger.c','probe.c','Build.ps1','review.py']
libs=['/home/paul/xbox-windows-native/build/fatx-dump-map-001/build-fatx/ntoskrnl/CMakeFiles/libntoskrnl.dir/libntoskrnl.a']
headers='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/i686-w64-mingw32/include/'
libs += [headers+'ddk/'+n for n in ['ntddk.h','wdm.h']]
r=dict(passed=True,scope=__doc__,physical_access=False,intentional_crash_only=True,binaries=rows,sources={n:sha(k/n) for n in inputs},targets=targets,compiler=gcc,compiler_sha256=compiler_sha,build_dependencies={p:subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',p],text=True).split()[0] for p in libs})
(k/'build-review.json').write_text(json.dumps(r,indent=2)+'\n')
kernel=system/'ntoskrnl.exe';pe=pefile.PE(str(kernel));syms=read(k.parent/'native-windows-nt5-kernel/kernel-publics.json')['symbols'];cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
names=['_KeBugCheckEx@20','_IoWriteCrashDump@24','_IopDumpControlBlock','_IopFinalCrashDumpStatus']
sites={n:syms[n]['rva'] for n in names};dis={}
for n,length in [('_KeBugCheckEx@20',80),('_IoWriteCrashDump@24',2000)]:
    rva=sites[n];dis[n]=[dict(rva=hex(i.address),bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in cs.disasm(pe.get_data(rva,length),rva)]
(k/'kernel-review.json').write_text(json.dumps(dict(kernel_sha256=sha(kernel),publics_sha256=sha(k.parent/'native-windows-nt5-kernel/kernel-publics.json'),sites=sites,disassembly=dis),indent=2)+'\n')
print('Reviewed NT5 imports, checksum, compiler inputs and static crash sites')

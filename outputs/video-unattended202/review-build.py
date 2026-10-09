"""Review new joined-helper runner against actual NT5 providers and unchanged probe/guards."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'build-review.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
archive=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
binaries={};providers={}
for name in ['runner.exe','replay.exe','wizard.exe']:
    path=k/'artifacts'/name;p=pefile.PE(str(path));imports={}
    assert p.FILE_HEADER.Machine==0x14c and (p.OPTIONAL_HEADER.MajorSubsystemVersion,p.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
    for entry in p.DIRECTORY_ENTRY_IMPORT:
        dllname=entry.dll.decode().lower();dll=archive/dllname;d=pefile.PE(str(dll))
        exports={v.name for v in d.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
        assert all(v.name in exports for v in entry.imports),dllname
        imports[dllname]=[v.name.decode() for v in entry.imports];providers[dllname]=dict(path=str(dll),sha256=sha(dll))
    binaries[name]=dict(sha256=sha(path),imports=imports)
for name in ['ntdll.dll','setupapi.dll']:
    dll=archive/name;providers[name]=dict(path=str(dll),sha256=sha(dll))
assert binaries['runner.exe']['sha256']==read(k/'build001.json')['binary_sha256']
assert binaries['replay.exe']['sha256']==read(k.parent/'video-phase-runtime199/build-review.json')['binaries']['gdi-probe.exe']['sha256']
assert binaries['wizard.exe']['sha256']==read(k.parent/'setup-wizard-automation201/build-review006.json')['binary_sha256']
old=k.parent/'video-phase-physical200'
assert all((k/name).read_bytes()==(old/name).read_bytes() for name in ['setup_gate.h','restart_gate.h'])
s=(k/'runner.c').read_text(encoding='utf-8')
assert s.index('WIZARD_JOIN_RESULT')<s.index('WIZARD_EXIT')<s.index('xwn_wait_setup_idle(NULL')<s.index('MEASUREMENT_BEGIN')<s.index('for(i=0;i<5;i++)')<s.index('xwn_guarded_restart(NULL')
assert 'WaitForSingleObject(pi.hProcess,150000)' in s and 'if(status!=WAIT_OBJECT_0)' in s
assert s.count('CreateProcessA(')==2 and s.count('ExitWindowsEx(')==1 and s.count('checkpoint(base,')==2
assert '900000,5000,250' in s and 'MEASUREMENT_BLOCKED_WIZARD_FAILURE' in s
assert not any(v in s for v in ['TerminateProcess','EWX_FORCE','SendMessage','SetupDi','SetForegroundWindow'])
compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
compiler_sha=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',compiler]).decode().split()[0]
assert compiler_sha=='83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
r=dict(passed=True,physical_access=False,runtime_qualified=False,binaries=binaries,providers=providers,
       source_sha256=sha(k/'runner.c'),compiler=compiler,compiler_sha256=compiler_sha,
       unchanged194_guards=True,unchanged199_probe=True,unchanged201_helper=True,
       limits='New bounded joined201 helper before exact194 setup/measurement/restart gates. No new Cancel behavior or driver algorithms. Physical mode excludes QEMU target; no dialog or visibility gates waived.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('New runner actual NT5 imports/order and exact unchanged probe/helper/guards reviewed')

"""Verify the probe imports against owned NT5 exports and pin build inputs."""
import hashlib,json,sys,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile
system=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
sha=lambda b:hashlib.sha256(b).hexdigest()
name=sys.argv[1];assert name in ['probe','repeat-probe']
data=(k/('artifacts/'+name+'.exe')).read_bytes();pe=pefile.PE(data=data)
assert pe.OPTIONAL_HEADER.MajorSubsystemVersion==5
imports={};targets={}
def exports(dll):
    p=next(p for p in system.iterdir() if p.name.lower()==dll.lower())
    targets[dll.lower()]=sha(p.read_bytes())
    return {e.name for e in pefile.PE(str(p)).DIRECTORY_ENTRY_EXPORT.symbols if e.name}
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    dll=entry.dll.decode();assert all(i.name in exports(dll) for i in entry.imports)
    imports[dll]=[i.name.decode() for i in entry.imports]
assert b'CMP_WaitNoPendingInstallEvents' in exports('setupapi.dll')
r=dict(passed=True,probe_sha256=sha(data),source_sha256=sha((k/(name+'.c')).read_bytes()),
       imports=imports, dynamic_exports={'setupapi.dll':['CMP_WaitNoPendingInstallEvents']},
       owned_export_targets=targets,
       note='All static imports exist in owned Windows 2000 DLLs; runtime qualification is separate.', compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc', build_script_sha256=sha((k/'Build.ps1').read_bytes()), subsystem=[pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion], checksum_valid=pe.OPTIONAL_HEADER.CheckSum==pe.generate_checksum())
r['compiler_sha256']=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',r['compiler']],text=True).split()[0]
r['compiler_version']=subprocess.check_output(['wsl','-d','Ubuntu','--',r['compiler'],'--version'],text=True).splitlines()[0]
assert r['checksum_valid']
(k/(name+'-review.json')).write_text(json.dumps(r,indent=2)+'\n');print('NT5 import review passed')

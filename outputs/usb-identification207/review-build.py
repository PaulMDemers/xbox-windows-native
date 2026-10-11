"""Verify the compiled probe imports against preserved NT5 providers."""
import hashlib,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent
canonical=Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path.insert(0,str(canonical/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
attempt=sys.argv[1];assert attempt.startswith('build') and attempt[5:].isdigit()
p=k/'artifacts'/attempt/'usbprobe.exe';exe=pefile.PE(str(p));providers={};imports={}
base=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
def provider(name):
 path=next(v for v in base.iterdir() if v.name.lower()==name.lower())
 pe=pefile.PE(str(path));exports={v.name.decode():v for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
 providers[name.lower()]=dict(path=str(path),sha256=sha(path));return exports
for entry in exe.DIRECTORY_ENTRY_IMPORT:
 name=entry.dll.decode();exports=provider(name);names=[v.name.decode() for v in entry.imports]
 assert all(n in exports for n in names),name
 imports[name]=names
 for n in names:
  f=exports[n].forwarder
  if f:
   module,symbol=f.decode().rsplit('.',1);assert symbol in provider(module+'.dll')
assert (exe.OPTIONAL_HEADER.MajorSubsystemVersion,exe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
assert exe.FILE_HEADER.Machine==0x14c
names={n for ns in imports.values() for n in ns}
assert not names.intersection({'ExitWindowsEx','SendInput','SetForegroundWindow','SetupDiCallClassInstaller','SetupDiSetDeviceRegistryPropertyA','RegSetValueExA','TerminateProcess','CancelIoEx'})
build=json.loads((k/(attempt+'.json')).read_text());assert build['source_sha256']==sha(k/'probe.c')
r=dict(passed=True,binary=p.relative_to(k).as_posix(),binary_sha256=sha(p),source_sha256=sha(k/'probe.c'),imports=imports,providers=providers,build=build,
 physical_access=False,runtime_qualified=False,write_scope='Exclusive usb.log beside its executable only; no reset/installation/registry writes. Classic NT5 USB hub IOCTLs; no vendor-control attempt through standard-descriptor API.',
 static_review='3s wait then same-thread CancelIo and 3s drain. Static buffers/OVERLAPPED never reused after failed drain; process abort logged. 120s request budget, 32 hubs/ports, 8 configurations, 8192-byte buffer, 4MiB log cap. External owner deadline still required for kernel open/cancel/exit stalls.')
(k/'build-review.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS actual NT5 exports, PE i386/subsystem 5.0, bounded query review')

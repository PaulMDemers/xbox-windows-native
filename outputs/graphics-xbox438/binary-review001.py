"""Static imports against owned NT5 exports; never run the restart controller here."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((K/'build001.json').read_text());assert build['exit_code']==0
exe=Path('//wsl.localhost/Ubuntu/home/paul/xbox-windows-native/graphics438-build001/run438.exe')
assert sha(exe)==build['rows'][0]['sha256']
pe=pefile.PE(str(exe));assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.Subsystem==3
assert (pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
pins=json.loads((W/'outputs/crypto-path425/modules001.json').read_text())['modules'];rows=[]
for entry in pe.DIRECTORY_ENTRY_IMPORT:
 dll=entry.dll.decode().lower();assert dll in ('kernel32.dll','user32.dll','advapi32.dll')
 p=Path('E:/xwn425/modules001')/dll;assert sha(p)==pins[dll]
 exports={s.name.decode():s for s in pefile.PE(str(p)).DIRECTORY_ENTRY_EXPORT.symbols if s.name}
 for imp in entry.imports:
  name=imp.name.decode();assert name in exports and not exports[name].forwarder
  rows.append(dict(dll=dll,name=name,dll_sha256=pins[dll]))
record=dict(executable_sha256=sha(exe),imports=rows,passed=True,host_execution=False)
out=K/'binary-review001.json';assert not out.exists();out.write_text(json.dumps(record,indent=2)+'\n')
print('NT5 import/export matches:',len(rows))

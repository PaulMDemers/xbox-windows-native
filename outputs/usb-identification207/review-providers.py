import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,r'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
base=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
rows={}
for name in ['openhci.sys','usbd.sys','usbhub.sys','hidusb.sys','hidclass.sys','hidparse.sys','kbdhid.sys','mouhid.sys','ntoskrnl.exe']:
 p=base/('drivers/'+name if name.endswith('.sys') else name)
 pe=pefile.PE(str(p));exports=[e.name.decode() for e in getattr(pe,'DIRECTORY_ENTRY_EXPORT',[]).symbols if e.name] if hasattr(pe,'DIRECTORY_ENTRY_EXPORT') else []
 row=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),machine=pe.FILE_HEADER.Machine,subsystem=[pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion],exports=exports if name!='ntoskrnl.exe' else [n for n in exports if any(s in n for s in ['RemoveLock','CancelIrp','CompletionRoutine'])],imports={e.dll.decode():[i.name.decode() if i.name else i.ordinal for i in e.imports] for e in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[])})
 rows[name]=row
 print(name,row['sha256'],row['exports'][:12])
(Path(__file__).resolve().parent/'owned-provider-review.json').write_text(json.dumps({'scope':'Owned immutable0.1.0 provider bytes; upcoming fixture readback must agree; not proof of current physical loaded bytes','files':rows},indent=2)+'\n')

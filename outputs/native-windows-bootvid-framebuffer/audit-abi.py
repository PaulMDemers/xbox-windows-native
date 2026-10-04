"""Audit NT5 boot-video exports, imports and the zero-argument reset adapter."""
from pathlib import Path
import hashlib,json,sys
kit=Path(__file__).resolve().parent;root=kit.parents[1]
sys.path.insert(0,str(root/'work/python-packages'))
import pefile,capstone
path=kit/'artifacts/xboxbvid.dll';pe=pefile.PE(str(path));kernel=root/'outputs/native-windows-nt5/installed-files/WINNT/system32/ntoskrnl.exe'
assert hashlib.sha256(kernel.read_bytes()).hexdigest()=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
kp=pefile.PE(str(kernel));hal=pefile.PE(str(root/'outputs/native-windows-hal-paging/artifacts/halxboxnt5.dll'))
libs={'ntoskrnl.exe':kp,'hal.dll':hal};imports=[]
for d in pe.DIRECTORY_ENTRY_IMPORT:
 names={s.name for s in libs[d.dll.decode().lower()].DIRECTORY_ENTRY_EXPORT.symbols}
 for s in d.imports:
  assert s.name in names;imports.append({'dll':d.dll.decode(),'name':s.name.decode()})
exports={s.name:s.address for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
required=[s.name for d in kp.DIRECTORY_ENTRY_IMPORT if d.dll.lower()==b'bootvid.dll' for s in d.imports]
assert all(n in exports for n in required)
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
checks=[]
for name,expected in ((b'VidResetDisplay',0),(b'VidInitialize',4)):
 at=exports[name];body=[]
 for i in md.disasm(pe.get_data(at,96),at):
  body.append({'rva':hex(i.address),'instruction':i.mnemonic+' '+i.op_str})
  if i.mnemonic=='ret':
   assert (int(i.op_str,0) if i.op_str else 0)==expected;break
 else:raise AssertionError('Adapter return not found')
 checks.append({'export':name.decode(),'expected_stack_argument_bytes':expected,'first_return':body})
# Exact supplied NT5 caller invokes the reset thunk with no stack arguments.
caller=list(md.disasm(kp.get_data(0x1cc68,0x1d),0x1cc68))
assert not any(i.mnemonic=='push' for i in caller)
assert any(i.mnemonic=='call' and i.op_str=='0x62bc2' for i in caller)
r={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'required_exports':[n.decode() for n in required],
   'imports':imports,'adapter_checks':checks,'native_reset_caller_rva':'0x1cc68','native_reset_argument_bytes':0,
   'scope':'Static import and adapter ABI audit; emulator shutdown validation is separate'}
(kit/'abi-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(r['sha256'],len(imports))

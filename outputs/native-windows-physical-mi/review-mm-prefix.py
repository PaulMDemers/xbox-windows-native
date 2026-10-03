"""Identify the pinned native MM prefix and the calls before our stop."""
from pathlib import Path
import sys,json,hashlib
kit=Path(__file__).resolve().parent;root=kit.parent.parent
sys.path.insert(0,str(root/'work/python-packages'))
import pefile,capstone
file=kit/'package/WINNT/system32/ntoskrnl.exe';pe=pefile.PE(str(file));im=pe.get_memory_mapped_image()
assert hashlib.sha256(file.read_bytes()).hexdigest()=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
sy=json.loads((kit.parent/'native-windows-nt5-kernel/kernel-publics.json').read_text())['symbols'];rev={v['rva']:n for n,v in sy.items()}
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
prefix=list(md.disasm(im[0x15542c:0x155b55],0x15542c));calls=[]
for i in prefix:
 if i.mnemonic=='call':
  target=int(i.op_str,16);calls.append({'site':hex(i.address),'target':hex(target),'symbol':rev[target]})
assert calls[-1]['symbol']=='_MiInitMachineDependent@4'
assert not any(i.mnemonic in ['out','in','invlpg','wrmsr'] or 'cr3' in i.op_str for i in prefix)
contract={'timestamp':pe.FILE_HEADER.TimeDateStamp,'checksum':pe.OPTIONAL_HEADER.CheckSum,'image_size':pe.OPTIONAL_HEADER.SizeOfImage,'entry_rva':pe.OPTIONAL_HEADER.AddressOfEntryPoint,'mi_rva':0x157d78,'caller_rva':0x155b55,'checked_prefix':im[0x157d78:0x157d78+14].hex(),'patched_entry_bytes':10,'patch_method':'E9 rel32 and five NOPs; restore original ten bytes before final capture','kernel_file_modified':False}
assert contract['checked_prefix']=='558bec83ec688065fe00535633f6'
(kit/'kernel-mi-contract.json').write_text(json.dumps(contract,indent=2)+'\n')
review={'kernel_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'prefix_rva':[hex(0x15542c),hex(0x155b55)],'calls':calls,'scope':'Phase-0 prefix only. Original MiInitMachineDependent is not allowed to execute.','memory_limits_review':'MmInitializeMemoryLimits compares descriptor type with 24 at RVA 0x156624 and skips types >=24. Type-26 BIOS allocations remain in the loader list but are omitted from this run count. This is not proof of later PFN compatibility.','triage_review':'MiTriageSystem reads loader extension TriageDump at +0x24. Fixture has zero; trace verifies it returns zero.','deferred':'MiInitMachineDependent clears low page-directory entries later. Relocate/preserve diagnostic code and display access before passing that boundary. Full physical memory-manager and storage paths remain untested.'}
(kit/'mm-prefix-review.json').write_text(json.dumps(review,indent=2)+'\n')
print('Pinned MM prefix reviewed: '+str(len(calls))+' direct call sites')

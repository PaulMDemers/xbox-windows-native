"""Resolve the user-transcribed PC using an explicit high-kernel-alias assumption."""
import pathlib,json,hashlib,sys
k=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(k.parents[1]/'work/python-packages'))
import pefile,capstone
p=k/'artifacts/physical-011-ntoskrnl.exe';data=p.read_bytes()
assert hashlib.sha256(data).hexdigest()=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
pe=pefile.PE(data=data);assert pe.FILE_HEADER.TimeDateStamp==0x4b7a1bd5
pub=json.loads((k.parent/'native-windows-nt5-kernel/kernel-publics.json').read_text())
assert pub['pdb_sha256']=='29f5de2a8db7959875b8a615945bd6f16e50e5c5a9465dd8f71b37f37d671e9e'
base=0x023d0000|0x80000000;pc=0x823e2d9b;rva=pc-base
symbol='_CcGetVirtualAddress@20';start=pub['symbols'][symbol]['rva']
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
ins=list(cs.disasm(pe.get_data(start,rva-start+32),start))
fault=next(i for i in ins if i.address==rva)
assert fault.mnemonic=='mov' and fault.op_str=='dword ptr [edx], ecx'
layout=json.loads((k/'native-cache-layouts.json').read_text())['_VACB']
assert layout['fields']['LruList']['offset']==0x10
r={'scope':__doc__,'kernel_sha256':hashlib.sha256(data).hexdigest(),'pdb_sha256':pub['pdb_sha256'],'user_pc':hex(pc),'user_reported_base':'0x023d0000','assumed_high_alias':hex(base),'rva':hex(rva),'symbol':symbol,'symbol_offset':hex(rva-start),'instructions':[{'rva':hex(i.address),'mnemonic':i.mnemonic,'operands':i.op_str} for i in ins if rva-16<=i.address<=rva+6],'interpretation':'EDX comes from VACB.LruList.Blink at +0x14. Write-to-zero at this instruction is consistent with a NULL Blink; the corrupting writer and call stack remain unknown.','limitation':'No physical memory dump; reported low base is interpreted through the 0x80000000 alias, not silently treated as the displayed high base.'}
(k/'physical-011-address-analysis.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

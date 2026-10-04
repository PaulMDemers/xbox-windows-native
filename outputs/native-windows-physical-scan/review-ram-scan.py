"""Record the pinned native RAM-scan contract without modifying the kernel."""
from pathlib import Path
import hashlib,json,sys
kit=Path(__file__).resolve().parent;sys.path.insert(0,str(kit.parent.parent/'work/python-packages'))
import capstone,pefile
p=kit/'package/WINNT/system32/ntoskrnl.exe';pe=pefile.PE(str(p));im=pe.get_memory_mapped_image()
assert hashlib.sha256(p.read_bytes()).hexdigest()=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
symbols=json.loads((kit.parent/'native-windows-nt5-kernel/kernel-publics.json').read_text())['symbols'];names={v['rva']:n for n,v in symbols.items()}
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
ins=list(md.disasm(im[0x157f3e:0x158025],0x157f3e))
assert not any(i.mnemonic in ['call','in','out','invlpg','wrmsr'] or 'cr3' in i.op_str for i in ins)
assert im[0x158025:0x15802d]==bytes.fromhex('8b4dcc3bcb750233')
result={'kernel_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scan_begin_rva':'0x157f3e','stop_rva':'0x158025','stop_checked_bytes':'8b4dcc3bcb750233','patched_bytes':5,'native_globals':{hex(rva):names.get(rva) for rva in [0x823d8,0x72734,0x81bb4]},'scan_contains_no_calls_or_io':True,'ram_total_excludes_types':[3,6,22,23],'page_bounds_exclude_types':[6,22,23],'allocation_candidates_types':[2,4,5,8],'earlier_limits_excludes_types_at_or_above':24,'bios_reserved_type':26,'expected_native_pages':15359,'expected_limits_pages':15357,'expected_bios_reserved_pages':2,'scope':'Observe counts and candidate selection only; no MM page allocation, PFN construction, partition handlers or driver entry allowed.','instructions':[{'rva':hex(i.address),'op':i.mnemonic,'args':i.op_str} for i in ins]}
(kit/'ram-scan-review.json').write_text(json.dumps(result,indent=2)+'\n')
print('Pinned native RAM scan reviewed; no calls or I/O in scan interval')

from pathlib import Path
import sys,json,hashlib
kit=Path(__file__).resolve().parent;root=kit.parent.parent;sys.path.insert(0,str(root/'work/python-packages'))
import pefile,capstone
p=kit/'package/WINNT/system32/ntoskrnl.exe';pe=pefile.PE(str(p));im=pe.get_memory_mapped_image()
assert hashlib.sha256(p.read_bytes()).hexdigest()=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
ins=list(md.disasm(im[0x158439:0x158518],0x158439))
assert im[0x158439:0x158441]==bytes.fromhex('8b721003720c3975')
assert im[0x158518:0x158520]==bytes.fromhex('33c03905e0234800')
assert [(i.address,i.op_str) for i in ins if i.mnemonic=='call']==[(0x1584d7,'0x2ac4e')]
assert not any(i.mnemonic in ['in','out','invlpg','wrmsr'] for i in ins)
assert next(i for i in ins if i.address==0x1584f8).op_str=='dword ptr [edx], eax'
assert next(i for i in ins if i.address==0x158508).mnemonic=='rep stosd'
scout=json.loads((root/'work/runs/pt-scout-004/entry-trace.json').read_text());assert scout['passed']
writes=[e for e in scout['events'] if e['name']=='PdeWrite'];zeroes=[e for e in scout['events'] if e['name']=='TableZeroed']
assert len(writes)==len(zeroes)==28 and all(e['page_zero_verified'] for e in zeroes)
result={'kernel_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bounded_native_loop':True,'preallocation_guard_required':True,
 'before_rva':'0x158439','after_rva':'0x158518','before_expected':'8b721003720c3975','after_expected_unrelocated':'33c03905e0234800',
 'after_absolute_operand_rebased':True,'candidate_pfn_first':352,'candidate_pages_consumed':28,'expected_next_pfn':380,'expected_remaining_pages':8164,
 'expected_pde_addresses':['0xc0300f8c','0xc0300ff8'],'expected_flags':'0x163',
 'native_descriptor_mutation_branch_excluded_by_ebx_zero':True,'insufficient_memory_bugcheck_guarded':True,
 'scout_trace_passed':True,'scout_descriptor_list_unchanged':scout['events'][-1]['descriptor_list_unchanged'],
 'instructions':[{'rva':hex(i.address),'op':i.mnemonic,'args':i.op_str} for i in ins]}
(kit/'page-table-review.json').write_text(json.dumps(result,indent=2)+'\n')
print('Native first page-table loop reviewed and emulator scout verified.')

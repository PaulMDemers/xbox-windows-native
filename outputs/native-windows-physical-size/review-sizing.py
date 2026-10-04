"""Inspect the exact native interval before allowing it on physical hardware."""
from pathlib import Path
import hashlib,json,sys
kit=Path(__file__).resolve().parent;sys.path.insert(0,str(kit.parent.parent/'work/python-packages'))
import capstone,pefile
p=kit/'package/WINNT/system32/ntoskrnl.exe';pe=pefile.PE(str(p));im=pe.get_memory_mapped_image()
assert hashlib.sha256(p.read_bytes()).hexdigest()=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True
ins=list(md.disasm(im[0x158025:0x158439],0x158025))
assert ins[-1].address+ins[-1].size==0x158439
assert im[0x158439:0x158441]==bytes.fromhex('8b721003720c3975')
assert not any(i.mnemonic in ['in','out','invlpg','wrmsr','stosd','rep stosd'] or 'cr3' in i.op_str for i in ins)
calls=[i for i in ins if i.mnemonic=='call'];assert len(calls)==1 and calls[0].address==0x1580ed and calls[0].op_str=='0x2ac4e'
pub=json.loads((kit.parent/'native-windows-nt5-kernel/kernel-publics.json').read_text())['symbols'];names={v['rva']:n for n,v in pub.items()}
assert pub['_KeBugCheckEx@20']['rva']==0x2ac4e
for i in ins:
 if i.group(capstone.CS_GRP_JUMP):
  assert i.operands[0].type==capstone.x86.X86_OP_IMM
  assert 0x158025<=i.operands[0].imm<=0x158439
writes=[]
for i in ins:
 for op in i.operands:
  if op.type!=capstone.x86.X86_OP_MEM or not op.access&capstone.CS_AC_WRITE:continue
  m=op.mem
  if m.base==capstone.x86.X86_REG_EBP:
   assert not m.index and -104<=m.disp<0
   destination='native stack local'
  else:
   assert not m.base and not m.index and 0x400000<=m.disp<0x400000+pe.OPTIONAL_HEADER.SizeOfImage,(hex(i.address),i.op_str)
   destination=names.get(m.disp-0x400000,'kernel data')
  writes.append({'rva':hex(i.address),'destination':destination,'instruction':i.mnemonic+' '+i.op_str})
result={'kernel_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'begin_rva':'0x158025','stop_rva':'0x158439','stop_checked_bytes':'8b721003720c3975','explicit_memory_writes_only_kernel_globals_or_stack':True,'all_jumps_within_interval_or_stop':True,
 'only_call':{'rva':'0x1580ed','target':'KeBugCheckEx','condition':'RAM count below 0x44c; pinned profile has 0x3bff and trace guards bugcheck entry'},
 'first_later_descriptor_write':'0x15845f','first_later_pde_write':'0x1584f8','first_later_page_zeroing':'0x158508',
 'scope':'Pool and allocation sizing only; no descriptor consumption, page-table allocation, PFN setup or storage.',
 'writes':writes,'instructions':[{'rva':hex(i.address),'op':i.mnemonic,'args':i.op_str} for i in ins]}
(kit/'sizing-review.json').write_text(json.dumps(result,indent=2)+'\n')
print('Pinned sizing interval reviewed: only globals/stack writes; allocation remains beyond stop.')

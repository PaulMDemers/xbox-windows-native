"""Review actual prototype inputs and retained outcomes without another execution."""
import hashlib,json,re,struct
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'entry-receipt498';out=K/'review001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((K/'host001.json').read_text());assert r['passed'] and r['closed']
assert (K/'entry498.S').read_bytes()==(P/'entry.S').read_bytes()
assert (K/'decode.py').read_bytes()==(P/'decode.py').read_bytes()
assert (K/'host.c').read_text(encoding='utf-8').split('\nextern uint32_t entry503_state')[0]==(P/'host.c').read_text(encoding='utf-8').split('\nint main(')[0]
for n,h in r['source_pins'].items():assert sha(K/n)==h
for n,v in r['files'].items():assert sha(Path(n.replace('/mnt/c/','C:/',1)))==v['sha256']
from decode import decode
full=partial=0
for case in r['cases']:
 p=Path('C:/xwn503/host001')/f"case{case['index']:03}.bin"
 data=p.read_bytes();assert sha(p)==case['receipt_sha256']
 if len(data)==112:
  decoded=decode(data);assert decoded['entry_witness'] and not decoded['final_flush_or_close_proved'];full+=1
 else:
  try:decode(data)
  except ValueError:partial+=1
  else:raise AssertionError('partial receipt accepted')
identity=json.loads((K/'kernel-identity001.json').read_text());assert identity['identities_differ']
for n,h in identity['pins'].items():assert sha(Path(n))==h
definitions=Path('C:/nxdk/lib/xboxkrnl/xboxkrnl.exe.def').read_text()
assert re.search(r'HalWriteSMBusValue@16\s+@\s+50\b',definitions)
assert re.search(r'KeDelayExecutionThread@12\s+@\s+99\b',definitions)
source=(K/'indicator.S').read_text();assert source.count('call dword ptr [Entry503HalWriteSMBusValue]')==1
assert source.count('call dword ptr [Entry503KeDelayExecutionThread]')==1
assert '.quad -20000000' in source
# Verify the private object, not raw opcode-byte searching through immediate data.
dis=Path('C:/xwn503/host001/disassembly.txt').read_text();instructions=[]
for line in dis.splitlines():
 match=re.match(r'^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+\s*([a-z][a-z0-9]*)\b(.*)$',line)
 if match:instructions.append(match.groups())
assert len(instructions)>150
assert not any(op in {'cli','sti','in','out','ins','outs','rdmsr','wrmsr','lgdt','lidt','hlt'} for op,_ in instructions)
assert not any(re.search(r'\bcr[034]\b',args) for _,args in instructions)
assert (K/'combined.S').read_text()=='#define DiagHalReturnToFirmware Entry503Return\n#include "entry498.S"\n#undef DiagHalReturnToFirmware\n.set entry498_continue, entry503_complete\n#include "indicator.S"\n'
v=dict(passed=True,actual_assembly_cases=r['case_count'],reentries=r['case_count'],full_receipts_independently_decoded=full,partial_receipts_rejected=partial,private_files_rehashed=len(r['files']),original498_gate_byte_exact=True,original498_decoder_byte_exact=True,original_file_model_prefix_byte_exact=True,production_instruction_count=len(instructions),no_raw_IO_or_interrupt_control_in_prototype=True,SDK_export_ABIs_match=True,physical_access=False,XBE_built=False,kernel_API_effects_modeled=True,ordinary_boot_qualified=False,helper_comment_erratum='entry503_led is labeled internal cdecl in the frozen source comment, but its actual internal convention is callee cleanup via ret8. Host tests exercise that exact stack behavior; no source bytes changed.')
out.write_bytes((json.dumps(v,indent=2)+'\n').encode());print(v)

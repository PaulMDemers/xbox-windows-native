"""Bounded actual NT5 entry CFGs and HAL providers; no resident/runtime claim."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'abi-review.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
capture=read(k.parent/'video-upload-runtime211/capture.json');inventory=read(k/'binary-inventory.json')
decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
requests={'ntoskrnl.exe':{'MmAllocateContiguousMemorySpecifyCache':32,'MmFreeContiguousMemorySpecifyCache':12,'MmGetPhysicalAddress':4},
 'drivers/videoprt.sys':{'VideoPortAllocateContiguousMemory':16,'VideoPortGetCommonBuffer':24,'VideoPortFreeCommonBuffer':24},
 'win32k.sys':{'EngDeviceIoControl':28}}
result={}
for module,wanted in requests.items():
 row=inventory['modules'][module];p=Path(row['path']);assert sha(p)==row['sha256']
 pe=pefile.PE(str(p));base=pe.OPTIONAL_HEADER.ImageBase
 exports={s.name.decode():s for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
 imports={s.address:(d.dll.decode(),s.name.decode() if s.name else s.ordinal)
  for d in pe.DIRECTORY_ENTRY_IMPORT for s in d.imports}
 functions={}
 for name,cleanup in wanted.items():
  symbol=exports[name];assert not symbol.forwarder;start=symbol.address
  todo=[start];seen={};returns=[];calls=[];pins=[]
  while todo:
   at=todo.pop()
   if at in seen:continue
   assert start<=at<start+2048,(name,'CFG escaped bounded entry range',hex(at))
   ins=next(decoder.disasm(pe.get_data(at,15),base+at,count=1),None);assert ins
   assert len(seen)<512,(name,'instruction bound')
   seen[at]=dict(rva=at,mnemonic=ins.mnemonic,operands=ins.op_str)
   pins.append(dict(rva=at,bytes=ins.bytes.hex()))
   if ins.mnemonic=='ret':
    actual=ins.operands[0].imm if ins.operands else 0;returns.append(dict(rva=at,stack_bytes=actual));assert actual==cleanup;continue
   if ins.mnemonic=='call':
    operand=ins.operands[0];target=None
    if operand.type==capstone.x86.X86_OP_MEM and operand.mem.base==0 and operand.mem.index==0:
     target=imports.get(operand.mem.disp)
    calls.append(dict(rva=at,operands=ins.op_str,import_target=target))
   if ins.group(capstone.CS_GRP_JUMP):
    assert ins.operands[0].type==capstone.x86.X86_OP_IMM,(name,'indirect jump unresolved')
    todo.append(ins.operands[0].imm-base)
    if ins.mnemonic=='jmp':continue
   todo.append(at+ins.size)
  assert returns
  functions[name]=dict(expected_stack_bytes=cleanup,returns=returns,calls=calls,
   instructions=[seen[i] for i in sorted(seen)],exact_disk_bytes=sorted(pins,key=lambda i:i['rva']),
   limits='Direct entry CFG only; calls are recorded, not recursively decoded. Disk ABI evidence, not resident execution or allocator qualification.')
 result[module]=dict(sha256=row['sha256'],functions=functions)
halpath=k.parent/'video-upload-runtime211/artifacts/E/Applications/XWNFBoot/loader/halxboxnt5.dll'
expected=next(x['sha256'] for x in capture['files'] if x['path'].lower().endswith('/halxboxnt5.dll'))
assert sha(halpath)==expected;pe=pefile.PE(str(halpath))
exports={s.name.decode():s for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
hal={}
for name in ['KeGetCurrentIrql','KeFlushIoBuffers','KeMemoryBarrier','MmClaimGpuInstanceMemory']:
 s=exports.get(name);hal[name]=dict(exported=s is not None)
 if s:
  section=pe.get_section_by_rva(s.address)
  hal[name].update(rva=s.address,section=section.Name.rstrip(b'\0').decode(),section_flags=section.Characteristics,
   forwarder=s.forwarder.decode() if s.forwarder else None)
r=dict(passed=True,source_sha256=sha(Path(__file__)),binary_inventory_sha256=sha(k/'binary-inventory.json'),
 modules=result,hal=dict(sha256=expected,functions=hal),guest_launch=False,physical_access=False,
 gpu_transfer_qualified=False,limits='No assertion about absent intrinsically implemented helpers. PRAMIN allocation and completion contracts remain unresolved.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Actual NT5 entry CFG stack cleanup and captured HAL providers PASS')

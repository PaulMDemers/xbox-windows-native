"""Read-only actual NT5 provider/ABI inventory; no kernel or hardware writes."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'binary-inventory.json';assert not out.exists()
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile,capstone
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
capture=read(ws/'outputs/video-upload-runtime211/capture.json');assert capture['passed']
base=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
wanted={
 'ntoskrnl.exe':['MmAllocateContiguousMemory','MmAllocateContiguousMemorySpecifyCache','MmAllocateContiguousMemoryEx','MmFreeContiguousMemory','MmFreeContiguousMemorySpecifyCache','MmGetPhysicalAddress','MmProbeAndLockPages','MmUnlockPages','MmBuildMdlForNonPagedPool','KeFlushIoBuffers','KeGetCurrentIrql','KeMemoryBarrier'],
 'win32k.sys':['EngAllocMem','EngFreeMem','EngDeviceIoControl','EngAllocUserMem','EngMapFile','EngMapSection','EngLockSection'],
 'drivers/videoprt.sys':['VideoPortAllocateContiguousMemory','VideoPortAllocateCommonBuffer','VideoPortGetCommonBuffer','VideoPortFreeCommonBuffer','VideoPortReleaseCommonBuffer','VideoPortGetDmaAdapter','VideoPortGetPhysicalAddress','VideoPortAllocatePool','VideoPortFreePool','VideoPortGetDeviceBase','VideoPortFreeDeviceBase','VideoPortSynchronizeExecution']}
decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);modules={}
for name,names in wanted.items():
 p=base/name;expected=next(row['sha256'] for row in capture['files'] if row['path'].lower()=='/f/winnt/system32/'+name.lower())
 assert sha(p)==expected,name
 pe=pefile.PE(str(p));exports={s.name.decode():s for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
 rows={}
 for symbol in names:
  s=exports.get(symbol)
  if s is None:rows[symbol]=dict(exported=False);continue
  section=pe.get_section_by_rva(s.address)
  code=pe.get_data(s.address,192);ins=[]
  for instruction in decoder.disasm(code,pe.OPTIONAL_HEADER.ImageBase+s.address):
   ins.append(dict(rva=instruction.address-pe.OPTIONAL_HEADER.ImageBase,mnemonic=instruction.mnemonic,operands=instruction.op_str))
   if instruction.mnemonic in ['ret','retf']:break
  rows[symbol]=dict(exported=True,rva=s.address,forwarder=s.forwarder.decode() if s.forwarder else None,
   section=section.Name.rstrip(b'\0').decode(),section_flags=section.Characteristics,
   disk_window_sha256=hashlib.sha256(code).hexdigest(),disk_instructions=ins,
   limits='Bounded on-disk entry window, not resident runtime, exhaustive body or ABI proof.')
 modules[name]=dict(path=str(p),sha256=expected,functions=rows)
nxdk=Path('C:/nxdk');revision=subprocess.check_output(['git','-C',str(nxdk),'rev-parse','HEAD']).decode().strip()
assert revision=='58427c078b4ccb0121f359b6b6c536b3b2914976'
paths=['lib/pbkit/pbkit.c','lib/pbkit/pbkit.h','lib/pbkit/nv_objects.h','lib/xboxkrnl/xboxkrnl.h']
art=k/'artifacts/nxdk';art.mkdir(parents=True,exist_ok=False)
nxpins={}
for name in paths:
 data=(nxdk/name).read_bytes();p=art/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);nxpins[name]=sha(p)
r=dict(passed=True,source_sha256=sha(Path(__file__)),capture_sha256=sha(ws/'outputs/video-upload-runtime211/capture.json'),
 modules=modules,nxdk_revision=revision,nxdk_sources=nxpins,physical_access=False,guest_launch=False,
 gpu_transfer_qualified=False,limits='Actual captured physical provider identities and bounded disk instructions. Xbox-kernel pbkit source is a pinned lead only; its API names/signatures are not NT5 ABI evidence. No driver changes or source migration.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({m:{n:v['exported'] for n,v in row['functions'].items()} for m,row in modules.items()},indent=2))

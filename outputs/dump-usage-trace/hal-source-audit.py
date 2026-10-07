"""Pin the owned HAL's usage selector, completion call and source-level policy."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'))
import pefile,capstone
sha=lambda data:hashlib.sha256(data).hexdigest()
path=k/'artifacts/cold-hal.dll';data=path.read_bytes();p=pefile.PE(data=data)
assert sha(data)=='a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648'
source='/home/paul/xbox-windows-native/build/fatx-directory-order-001/source/hal/halx86/legacy/halpnpdd.c'
s=subprocess.check_output(['wsl','-d','Ubuntu','--','cat',source]);(k/'artifacts/halpnpdd.c').write_bytes(s)
assert b'Dump/hibernate support' in s and b'deliberately not advertised' in s
assert b'if (Status == STATUS_NOT_SUPPORTED) Status = Irp->IoStatus.Status;' in s
# PDO jump-table selector 0x16 resolves to the explicit paging-only branch.
selector=struct.unpack('<I',p.get_data(0x1ff104+0x16*4,4))[0]-p.OPTIONAL_HEADER.ImageBase
assert selector==0x8493
checks={0x8493:'837a0801',0x8497:'0f8563ffffff',0x8400:'8b7318ebc6',0x83cb:'89731889d931d2ff15f8812100'}
c=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);rows=[]
for rva,expected in checks.items():
    raw=p.get_data(rva,len(bytes.fromhex(expected)));assert raw.hex()==expected,(hex(rva),raw.hex())
    rows.append(dict(rva=hex(rva),bytes=raw.hex(),instructions=[dict(rva=hex(i.address),mnemonic=i.mnemonic,operands=i.op_str) for i in c.disasm(raw,rva)]))
sec=p.get_section_by_rva(0x8290);assert not sec.Characteristics&0x02000000
imports=[i.name.decode() for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name]
r=dict(scope=__doc__,hal_sha256=sha(data),source_path=source,source_sha256=sha(s),patch='outputs/native-windows-hal-paging/0055-hal-paging-path-notification.patch',patch_sha256=sha((k.parent/'native-windows-hal-paging/0055-hal-paging-path-notification.patch').read_bytes()),usage_selector_rva=hex(selector),checks=rows,dispatch_section=sec.Name.rstrip(b'\0').decode(),dispatch_section_discardable=False,imports_idle_registration='PoRegisterDeviceForIdleDetection' in imports,conclusion='Paging type 1 takes the count path; dump type 3 takes the inherited-status path. For the observed IRP the inherited status is STATUS_NOT_SUPPORTED, and HAL completes it. Source and binary policy agree; this is not a full source-to-binary rebuild attestation.',limits='Only entry/completion resident windows were traced. Selector branch is static exact-binary evidence, not an additional runtime breakpoint. No code or configuration changed.')
target=k/'hal-source-audit.json'
if target.exists():assert json.loads(target.read_text())==r
else:target.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))

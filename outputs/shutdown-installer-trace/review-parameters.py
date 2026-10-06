"""Verify relative command-line decoding against the owned NT5 normalization routine."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile,capstone
f=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntdll.dll')
digest=hashlib.sha256(f.read_bytes()).hexdigest()
assert digest=='ed276d6a3ae93c71a6cef73672b82e3808211da1c63bf7d3e23d93294e54813a'
p=pefile.PE(str(f));e=next(e for e in p.DIRECTORY_ENTRY_EXPORT.symbols if e.name==b'RtlNormalizeProcessParams')
assert e.address==0x47a2
assert p.get_data(0x47ab,8).hex()=='8b5808f6c3017576'
assert p.get_data(0x47d7,12).hex()=='8b484485c9740503c8894844'
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
r=dict(scope=__doc__,path=str(f),sha256=digest,symbol=e.name.decode(),rva=hex(e.address),disassembly=[dict(rva=hex(i.address),bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in md.disasm(p.get_data(e.address,0x482d-e.address),e.address)],
       interpretation='Flags at params+8, bit0: if clear and command buffer at params+0x44 is nonzero, add params base before reading. Host decoder performs arithmetic only; it never normalizes or writes guest memory.')
(k/'parameter-review.json').write_text(json.dumps(r,indent=2)+'\n')

"""Pin the actual NT5 ANSI removal stub and Unicode export entry bytes."""
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile,capstone
k=Path(__file__).resolve().parent;pci=k.parent
manifest=json.loads((pci/'providers002.json').read_text())
p=pci/'artifacts/providers002/setupapi.dll'
digest=hashlib.sha256(p.read_bytes()).hexdigest()
assert manifest['files']['setupapi.dll']==digest
pe=pefile.PE(str(p));dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
rows=[]
for name in ('CM_Query_And_Remove_SubTreeA','CM_Query_And_Remove_SubTree_ExA','CM_Query_And_Remove_SubTreeW','CM_Query_And_Remove_SubTree_ExW'):
    v=next(v for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name==name.encode())
    code=pe.get_data(v.address,32)
    rows.append(dict(name=name,rva=hex(v.address),entry_hex=code.hex(),instructions=[dict(address=hex(i.address),mnemonic=i.mnemonic,operands=i.op_str) for i in dis.disasm(code,pe.OPTIONAL_HEADER.ImageBase+v.address)]))
assert rows[1]['entry_hex'].startswith('6a3458c21800')
dest=k/'removal-api001.json';assert not dest.exists()
dest.write_text(json.dumps(dict(provider_sha256=digest,ansi_ex_constant_return=52,observed_remove_result=52,exports=rows,limits='Entry inspection proves ANSI stub only; Unicode export requires a fresh real guest trial.'),indent=2)+'\n')

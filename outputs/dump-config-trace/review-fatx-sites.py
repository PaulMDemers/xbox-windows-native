"""Pin candidate0101 PnP forwarding instructions and its source; no rebuild."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
p=k.parent/'fatx-directory-order/artifacts/xwnfatx.sys';b=p.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(b)=='ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9'
pe=pefile.PE(data=b);sites=[]
for name,rva,n in [('fatx_pnp_entry',0x10f80,13),('fatx_pnp_forward',0x10fc0,6),('fatx_pnp_return',0x10fc6,2)]:
 raw=pe.get_data(rva,n);rels=[e.rva-rva for block in pe.DIRECTORY_ENTRY_BASERELOC for e in block.entries if e.type==3 and rva<=e.rva<rva+n];assert all(v+4<=n for v in rels)
 sites.append(dict(name=name,rva=rva,raw=raw.hex(),relocations=rels,instructions=[dict(address=hex(i.address),bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(raw,rva)]))
source=Path('//wsl.localhost/Ubuntu/home/paul/xbox-windows-native/build/fatx-directory-order-001/source/drivers/filesystems/vfatfs/pnp.c')
r=dict(scope=__doc__,driver_sha256=sha(b),preferred_base=pe.OPTIONAL_HEADER.ImageBase,timestamp=pe.FILE_HEADER.TimeDateStamp,sites=sites,source_path=str(source),source_sha256=sha(source.read_bytes()))
out=k/'fatx-sites.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n')

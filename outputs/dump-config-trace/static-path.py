"""Disassemble whole caller and dump-stack functions; static candidates only."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'))
import pefile,capstone
p=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntoskrnl.exe');b=p.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(b)==json.loads((k/'sites-v3.json').read_text())['kernel_sha256']
pe=pefile.PE(data=b);publics=k.parent/'native-windows-nt5-kernel/kernel-publics.json';symbols=json.loads(publics.read_text())['symbols'];rev={v['rva']:n for n,v in symbols.items()}
result=dict(scope=__doc__,kernel_sha256=sha(b),publics_sha256=sha(publics.read_bytes()),functions=[])
for name in ['_IopConfigureCrashDump@4','_IoGetDumpStack@16','_IopGetDumpStack@24']:
 start=symbols[name]['rva'];end=min(v['rva'] for v in symbols.values() if v['rva']>start)
 rows=[]
 for i in capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(pe.get_data(start,end-start),start):
  target=int(i.op_str,16) if i.mnemonic=='call' and i.op_str.startswith('0x') else None
  rows.append(dict(rva=hex(i.address),bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str,public_target=rev.get(target,'')))
 result['functions'].append(dict(name=name,start_rva=start,end_rva=end,instructions=rows))
out=k/'static-path.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n')
print('Pinned whole caller, wrapper and inner dump-stack disassembly')

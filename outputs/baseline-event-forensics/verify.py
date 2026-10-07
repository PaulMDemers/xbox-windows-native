"""Replay static instruction evidence against owned hash-pinned binaries."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
root=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
pubpath=ws/'outputs/native-windows-nt5-kernel/kernel-publics.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
for name in ['kernel-static-sites.json','dump-initialization-static.json']:
    r=json.loads((k/name).read_text());p=root/'ntoskrnl.exe';assert sha(p)==r['file_sha256'] and sha(pubpath)==r['publics_sha256']
    pe=pefile.PE(str(p));base=pe.OPTIONAL_HEADER.ImageBase
    groups=[r['instructions']] if 'instructions' in r else [s['instructions'] for s in r['sites']]
    for rows in groups:
        for row in rows:
            va=int(row['address'],16) if 'address' in row else base+int(row['rva'],16)
            raw=bytes.fromhex(row['bytes']);assert pe.get_data(va-base,len(raw))==raw
            ins=list(cs.disasm(raw,va));assert len(ins)==1 and ins[0].mnemonic+' '+ins[0].op_str==row['instruction']
state=json.loads((k/'cold-state.json').read_text())
for row in state['files']:
    if 'private_copy' in row:assert sha(k/'artifacts'/row['private_copy'])==row['sha256']
assert sha(k/'artifacts/system')==state['system_sha256']
r=json.loads((k/'hidserv-source.json').read_text())
for row in r['files']:assert sha(Path(row['path']))==row['sha256']
print('Cold extracted bytes, archive service copies and all static instruction windows verified')

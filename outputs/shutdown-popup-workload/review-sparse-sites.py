"""Verify sparse PnP boundaries against the owned binary and saved disassembly."""
import hashlib
import json
import sys
from pathlib import Path

root=Path(__file__).resolve().parent
sys.path.insert(0,str(root.parents[1]/'work/python-packages'))
import pefile

review=json.loads((root/'site-review-sparse.json').read_text())
path=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/umpnpmgr.dll')
sha=hashlib.sha256(path.read_bytes()).hexdigest()
assert sha==review['binaries']['umpnpmgr.dll']['sha256']
pe=pefile.PE(str(path))
imports={i.address:i.name.decode() for dll in pe.DIRECTORY_ENTRY_IMPORT for i in dll.imports if i.name}
assert imports[0x767a104c]=='CreateProcessAsUserW'
assert imports[0x767a1114]=='WaitForSingleObject'
verified=[]
for site in review['sites']:
    if site['module']!='umpnpmgr.dll':continue
    assert pe.get_data(site['rva'],len(bytes.fromhex(site['bytes']))).hex()==site['bytes']
    verified.append(site)
instructions={int(i['address'],16):i for block in review['pnp_disassembly'] for i in block['instructions']}
assert instructions[0x767a66d8]['bytes']=='ff154c107a76'
assert instructions[0x767a66ea]['bytes']=='ff1514117a76'
assert instructions[0x767a66be]['bytes']=='50'  # PROCESS_INFORMATION at EBP-0x278.
assert instructions[0x767a66b8]['bytes']=='8d8588fdffff'
assert instructions[0x767a66ca]['bytes']=='8d8598fdffff'  # Command at EBP-0x268.
result=dict(binary_sha256=sha,verified_sites=verified,
    imports={hex(a):imports[a] for a in [0x767a104c,0x767a1114]},
    process_information_ebp_offset=-0x278,command_ebp_offset=-0x268,
    limits='Interior-site stack values are raw data; no fabricated caller. Return EAX belongs to the just-completed imported call. A create return does not alone prove the child executed user code.')
(root/'sparse-site-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print('Verified sparse sites, stack layout and imports against owned umpnpmgr.')

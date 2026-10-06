"""Pin saved PnP token observations to the matching owned NT5 module."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root.parents[1] / 'work/python-packages'))
import pefile
import capstone

review = json.loads((root.parent / 'shutdown-createprocess/site-review.json').read_text())
archive = Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
pe = pefile.PE(str(archive / 'umpnpmgr.dll'))
base = pe.OPTIONAL_HEADER.ImageBase
assert base == 0x767a0000
review['binaries']['umpnpmgr.dll'] = {
    'sha256': hashlib.sha256((archive / 'umpnpmgr.dll').read_bytes()).hexdigest(),
    'preferred_base': hex(base),
}
review['token_global'] = base + 0x15b64
review['mutex_global'] = base + 0x15bf4
review['pnp_sites'] = []
for name, rva in [
    ('PnP_Control_entry', 0x5959),
    ('PnP_Control_wait_return', 0x5979),
    ('PnP_Token_close_call', 0x5999),
    ('PnP_Token_close_return', 0x599b),
    ('PnP_Token_clear_before', 0x59ad),
    ('PnP_Token_clear_after', 0x59b4),
    ('PnP_Logon_token_return', 0x5d82),
    ('PnP_Install_token_check', 0x665b),
    ('PnP_Install_token_push', 0x66d2),
]:
    site = dict(name=name, module='umpnpmgr.dll', rva=rva, address=base+rva,
                bytes=pe.get_data(rva, 3).hex(), argc=0, kind='pnp')
    review['sites'].append(site)
    review['pnp_sites'].append(site)

kernel32 = pefile.PE(str(archive / 'kernel32.dll'))
rva = next(e.address for e in kernel32.DIRECTORY_ENTRY_EXPORT.symbols if e.name == b'CloseHandle')
review['sites'].append(dict(name='CloseHandle_saved_token', module='kernel32.dll',
                           rva=rva, address=kernel32.OPTIONAL_HEADER.ImageBase+rva,
                           bytes=kernel32.get_data(rva,3).hex(), argc=1, kind='close'))
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
review['pnp_disassembly'] = []
for first, end in [(0x5959,0x59c7),(0x5caf,0x5de3),(0x662b,0x672e)]:
    review['pnp_disassembly'].append({
        'first_rva': hex(first), 'end_rva': hex(end),
        'instructions': [dict(address=hex(i.address), bytes=i.bytes.hex(),
                              instruction=i.mnemonic+' '+i.op_str)
                         for i in md.disasm(pe.get_data(first,end-first),base+first)]})
review['scope'] = __doc__
review['limits'] += ' PnP interior sites record raw registers/global values, not fabricated call arguments. CloseHandle is retained only when services.exe closes the current saved token.'
(root / 'site-review.json').write_text(json.dumps(review,indent=2)+'\n')

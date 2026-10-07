"""Pinned actual ATAPI dump address path; static findings are not runtime proof."""
import hashlib
import json
import sys
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
sys.path.insert(0, str(ws / 'work/python-packages'))
import capstone
import pefile

m = json.loads((k / 'modules.json').read_text())['atapi.sys']
data = Path(m['path']).read_bytes()
assert hashlib.sha256(data).hexdigest() == m['sha256']
p = pefile.PE(data=data)
c = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
sites = {
    'divide_call': 0x1359d, 'divide_return': 0x135a2,
    'dispatch_call': 0x1360e, 'decoded_lba': 0x28a6,
    'before_head_mask': 0x28e7, 'after_head_mask': 0x28e9,
    'select_write_command': 0x29fa, 'write_command_call': 0x2a05,
}
r = dict(scope=__doc__, source_sha256=m['sha256'], source_bytes=len(data),
         physical_access=False, sites=sites, functions=[], imports=[])
for name, start, end in [('dump_writer', 0x13454, 0x137fa),
                         ('legacy_dispatch', 0x27fe, 0x2af5)]:
    raw = p.get_data(start, end - start)
    instructions = [dict(rva=i.address, raw=i.bytes.hex(), op=i.mnemonic,
                         args=i.op_str) for i in c.disasm(raw, start)]
    assert sum(len(bytes.fromhex(i['raw'])) for i in instructions) == len(raw)
    r['functions'].append(dict(name=name, start=start, end=end,
                               sha256=hashlib.sha256(raw).hexdigest(),
                               instructions=instructions))
instructions = {i['rva']: i for f in r['functions'] for i in f['instructions']}
for address in sites.values():
    assert address in instructions
assert instructions[0x1360e]['args'] == '0x27fe'
assert instructions[0x28e7]['raw'] == '240f'
assert instructions[0x29fa]['args'] == 'al, byte ptr [eax + esi + 0x90d]'
for dll in p.DIRECTORY_ENTRY_IMPORT:
    for imp in dll.imports:
        r['imports'].append(dict(dll=dll.dll.decode(), rva=imp.address-p.OPTIONAL_HEADER.ImageBase,
                                 name=imp.name.decode() if imp.name else imp.ordinal))
r['static_conclusion'] = (
    'Writer adds a 64-bit partition offset to the 64-bit volume offset and divides '
    'by sector size, constructs a four-byte big-endian CDB LBA, then directly calls '
    'RVA27fe. Its LBA path masks the top byte to four bits at RVA28e7, writes three '
    'remaining address bytes and selects the command from per-device offset90d. '
    'No large-LBA alternate dispatch exists at the direct call. Runtime registers '
    'and the selected command still require the new diagnostic.')
(k / 'address-review.json').write_text(json.dumps(r, indent=2)+'\n')
print('Pinned ATAPI direct legacy dump dispatch and address mask; runtime pending.')

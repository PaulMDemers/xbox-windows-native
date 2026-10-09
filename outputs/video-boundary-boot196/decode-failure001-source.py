"""Offline process/module evidence from an already recorded196 snapshot; no monitor access."""
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
elapsed = int(sys.argv[1])
assert elapsed in [90, 300, 960]
out = k / 'pending002'
dest = out / ('snapshot-%d-analysis.json' % elapsed)
assert not dest.exists()
read_json = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
row, = [r for r in read_json(out / 'live-observation.json')['captures'] if r['target_elapsed_seconds'] == elapsed]
data = (out / 'artifacts' / ('live-%d' % elapsed) / 'ram.bin').read_bytes()
assert len(data) == 67108864 and hashlib.sha256(data).hexdigest() == row['ram_sha256']
cr3 = int(re.search(r'CR3=([0-9a-fA-F]+)', row['registers'])[1], 16)
cr4 = int(re.search(r'CR4=([0-9a-fA-F]+)', row['registers'])[1], 16)
assert not cr4 & 32, 'PAE decoding not implemented'

def phys32(a):
    assert 0 <= a <= len(data) - 4
    return struct.unpack_from('<I', data, a)[0]

def pa(va):
    pde = phys32((cr3 & 0xfffff000) + 4 * (va >> 22))
    assert pde & 1, 'Nonresident PDE'
    if pde & 128:
        return (pde & 0xffc00000) + (va & 0x3fffff)
    pte = phys32((pde & 0xfffff000) + 4 * ((va >> 12) & 1023))
    assert pte & 1, 'Nonresident PTE'
    return (pte & 0xfffff000) + (va & 4095)

def memory(va, size):
    result = bytearray()
    while size:
        at = pa(va)
        n = min(size, 4096 - (va & 4095))
        assert at + n <= len(data)
        result.extend(data[at:at + n])
        va += n
        size -= n
    return bytes(result)

u32 = lambda a: struct.unpack('<I', memory(a, 4))[0]
sys.path.insert(0, str(ws / 'work/python-packages'))
import pefile

nk = k.parent / 'native-windows-nt5-kernel'
kernel = k.parent / 'native-windows-nt5/installed-files/WINNT/system32/ntoskrnl.exe'
f = read_json(k / 'fixture-pending002.json')
assert sha(kernel) == f['protected']['F/winnt/system32/ntoskrnl.exe']
pe = pefile.PE(str(kernel))
symbols = read_json(nk / 'kernel-publics.json')
pdb = ws / 'work/symbols/ntoskrnl-2195-7376.pdb'
assert sha(pdb) == symbols['pdb_sha256']
pubs = symbols['symbols']
valid = []
for page in range(0x80000, 0xc0000):
    va = page * 4096
    try:
        if memory(va, 64) != kernel.read_bytes()[:64]:
            continue
        pos = va + pe.DOS_HEADER.e_lfanew
        if u32(pos + 8) != pe.FILE_HEADER.TimeDateStamp:
            continue
        node = u32(va + pubs['_PsLoadedModuleList']['rva'])
        if u32(node + 24) == va:
            valid.append(va)
    except (AssertionError, struct.error):
        pass
assert len(valid) == 1, valid
base = valid[0]

def code_pin(image, image_base, rva, size=64):
    candidate = pefile.PE(str(image))
    expected = bytearray(candidate.get_data(rva, size))
    assert len(expected) == size
    relocated = []
    for block in getattr(candidate, 'DIRECTORY_ENTRY_BASERELOC', []):
        for entry in block.entries:
            if entry.type == 3 and rva <= entry.rva and entry.rva + 4 <= rva + size:
                at = entry.rva - rva
                value = struct.unpack_from('<I', expected, at)[0]
                struct.pack_into('<I', expected, at, (value + image_base - candidate.OPTIONAL_HEADER.ImageBase) & 0xffffffff)
                relocated.append(hex(entry.rva))
            elif entry.type and entry.rva < rva + size and entry.rva + 4 > rva:
                raise AssertionError('Unsupported or partial relocation')
    actual = memory(image_base + rva, size)
    assert actual == bytes(expected), 'Resident code does not match pinned image'
    return dict(rva=hex(rva), bytes=size, actual_sha256=hashlib.sha256(actual).hexdigest(), relocations=relocated)

pins = [code_pin(kernel, base, pubs[name]['rva']) for name in ['_PsGetCurrentProcess@0', '_KeWaitForSingleObject@20']]
head = base + pubs['_PsLoadedModuleList']['rva']
link = u32(head)
modules = []
seen = set()
while link != head:
    assert link not in seen and len(seen) < 256
    seen.add(link)
    mb, entry, size = struct.unpack('<III', memory(link + 24, 12))
    length, maximum, pointer = struct.unpack('<HHI', memory(link + 44, 8))
    assert length <= maximum and length <= 1024 and length % 2 == 0
    modules.append(dict(name=memory(pointer, length).decode('utf-16le') if length else '', base=hex(mb), entry=hex(entry), bytes=size))
    next_link = u32(link)
    assert u32(next_link + 4) == link
    link = next_link

layout = read_json(nk / 'process-layouts.json')
ef, kf = [layout[name]['fields'] for name in ['_EPROCESS', '_KPROCESS']]
head = base + pubs['_PsActiveProcessHead']['rva']
link = u32(head)
seen = set()
processes = []
while link != head:
    assert link not in seen and len(seen) < 128
    seen.add(link)
    ep = link - ef['ActiveProcessLinks']['offset']
    item = dict(address=hex(ep), pid=u32(ep + ef['UniqueProcessId']['offset']),
                image=memory(ep + ef['ImageFileName']['offset'], 16).split(b'\0')[0].decode('ascii', 'replace'))
    peb = u32(ep + ef['Peb']['offset'])
    target_cr3 = u32(ep + ef['Pcb']['offset'] + kf['DirectoryTableBase']['offset'])
    saved = cr3
    try:
        assert 0x10000 <= peb < 0x80000000
        cr3 = target_cr3
        params = u32(peb + 0x10)
        assert 0x10000 <= params < 0x80000000
        flags = u32(params + 8)
        length, maximum, pointer = struct.unpack('<HHI', memory(params + 0x40, 8))
        assert length <= maximum and length <= 4096 and length % 2 == 0
        if not flags & 1 and pointer:
            pointer += params
        item['command_line'] = memory(pointer, length).decode('utf-16le') if length else ''
        if item['image'].lower() == 'runner.exe':
            source = k.parent / 'video-measurement-boundary194/artifacts/runner.exe'
            assert sha(source) == f['protected']['F/xwnpre194/runner.exe']
            candidate = pefile.PE(str(source))
            image_base = u32(peb + 8)
            item['entry_pin'] = code_pin(source, image_base, candidate.OPTIONAL_HEADER.AddressOfEntryPoint)
            item['binary_sha256'] = sha(source)
    except (AssertionError, struct.error, UnicodeError) as exc:
        item['nonresident_or_pin_error'] = repr(exc)
    finally:
        cr3 = saved
    processes.append(item)
    next_link = u32(link)
    assert u32(next_link + 4) == link
    link = next_link

result = dict(offline=True, physical_access=False, ordinary_qualified=False,
              debugger_observation=True, elapsed=elapsed, kernel_base=hex(base),
              kernel_sha256=sha(kernel), pdb_sha256=sha(pdb), resident_kernel_pins=pins,
              ram_sha256=row['ram_sha256'], source_sha256=sha(Path(__file__)),
              dependencies={str(p.relative_to(ws)).replace('\\', '/'): sha(p) for p in [nk / 'kernel-publics.json', nk / 'process-layouts.json', nk / 'read-publics.py', k.parent / 'native-windows-nt5-interrupts/read-pdb-layouts.py']},
              bugcheck_data=[hex(v) for v in struct.unpack('<5I', memory(base + pubs['_KiBugCheckData']['rva'], 20))],
              modules=modules, processes=processes,
              limits='Resident snapshot and bounded linked-list decoding, not continuous execution '
              'or proof of setup idle/helper deadline. Unknown user data stays unknown; no UI or guest changes.')
dest.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(elapsed=elapsed, kernel_base=hex(base), processes=processes), indent=2))

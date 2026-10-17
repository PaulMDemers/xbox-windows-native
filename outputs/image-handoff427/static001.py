# SPDX-License-Identifier: MIT
"""Read-only callsite review of the owned NT5 kernel; no runtime observation."""
from pathlib import Path
import hashlib
import json
import struct
import sys

K = Path(__file__).resolve().parent
R = K.parent.parent
P = Path('E:/xwn427/static001')
assert not P.exists() and not (K / 'kernel-calls001.json').exists()
sys.path.insert(0, str(R / 'work/python-packages'))
import pefile
import capstone

sha = lambda b: hashlib.sha256(b).hexdigest()
kernel = Path('E:/xwn425/modules001/ntoskrnl.exe').read_bytes()
assert sha(kernel) == '84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
pe = pefile.PE(data=kernel)
pubpath = R / 'outputs/native-windows-nt5-kernel/kernel-publics.json'
publics = json.loads(pubpath.read_text())
pdb = (R / 'work/symbols/ntoskrnl-2195-7376.pdb').read_bytes()
assert sha(pdb) == publics['pdb_sha256'] == '29f5de2a8db7959875b8a615945bd6f16e50e5c5a9465dd8f71b37f37d671e9e'
dbg = (R / 'work/symbols/Windows_2000_(SP4)-ntoskrnl.dbg').read_bytes()
header = struct.unpack_from('<HHHH10I', dbg)
assert dbg[:2] == b'DI'
assert header[4] == pe.FILE_HEADER.TimeDateStamp and header[7] == pe.OPTIONAL_HEADER.SizeOfImage
at = dbg.index(b'NB10')
_, _, stamp, age = struct.unpack_from('<4sIII', dbg, at)
# Parse PDB2 directory to independently bind its identity stream to DBG NB10.
magic = b'Microsoft C/C++ program database 2.00\r\n\x1aJG\0\0'
fmt = f'<{len(magic)}sIHHII'
sig, block, free, pages, rootlen, reserved = struct.unpack_from(fmt, pdb)
assert sig == magic and pages * block == len(pdb)
def gather(indices, length):
    assert all(i < pages for i in indices)
    return b''.join(pdb[i*block:(i+1)*block] for i in indices)[:length]
indices = struct.unpack_from('<'+'H'*((rootlen+block-1)//block), pdb, struct.calcsize(fmt))
directory = gather(indices, rootlen)
n, reserved = struct.unpack_from('<HH', directory)
sizes = [struct.unpack_from('<II', directory, 4+8*i)[0] for i in range(n)]
off = 4 + 8*n
streams = []
for size in sizes:
    size = 0 if size == 0xffffffff else size
    count = (size+block-1)//block
    ids = struct.unpack_from('<'+'H'*count, directory, off)
    off += count*2
    streams.append(gather(ids, size))
version, actual_stamp, actual_age = struct.unpack_from('<III', streams[1])
assert (actual_stamp, actual_age) == (stamp, age)
symbols = publics['symbols']
reverse = {v['rva']: name for name, v in symbols.items()}
imports = {s.address - pe.OPTIONAL_HEADER.ImageBase: s.name.decode()
           for d in pe.DIRECTORY_ENTRY_IMPORT for s in d.imports if s.name}
names = ['_IoInitSystem@4', '_IopInitializeBootDrivers@8', '_IopCreateArcNames@4',
         '_IopReassignSystemRoot@8', '_IopInitializeSystemDrivers@0',
         '@xHalIoAssignDriveLetters@16']
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True
P.mkdir(parents=True)
rows = []
for name in names:
    start = symbols[name]['rva']
    end = min(v['rva'] for v in symbols.values() if v['rva'] > start)
    raw = pe.get_data(start, end-start)
    calls = []
    instructions = []
    for ins in md.disasm(raw, start):
        instructions.append(dict(rva=ins.address, instruction=ins.mnemonic+' '+ins.op_str))
        if ins.mnemonic != 'call':
            continue
        operand = ins.operands[0]
        target = None
        if operand.type == capstone.x86.X86_OP_IMM:
            target = reverse.get(operand.imm)
        elif operand.type == capstone.x86.X86_OP_MEM and not operand.mem.base and not operand.mem.index:
            target = imports.get(operand.mem.disp - pe.OPTIONAL_HEADER.ImageBase)
        calls.append(dict(rva=ins.address, target=target, kind=operand.type))
    private = P / (name.replace('@', '_').replace(':', '_') + '.json')
    private.write_text(json.dumps(instructions, indent=2)+'\n')
    rows.append(dict(name=name, start_rva=start, next_public_rva=end,
                     interval_sha256=sha(raw), decoded_instructions=len(instructions),
                     decoded_bytes_end=(ins.address+ins.size if instructions else start),
                     calls=calls, private_disassembly=str(private),
                     private_sha256=sha(private.read_bytes())))
result = dict(scope='Static callsites only; next-public intervals are not proven function boundaries',
              kernel_sha256=sha(kernel), publics_sha256=sha(pubpath.read_bytes()),
              pdb_sha256=sha(pdb), dbg_sha256=sha(dbg),
              image_timestamp=pe.FILE_HEADER.TimeDateStamp, image_size=pe.OPTIONAL_HEADER.SizeOfImage,
              dbg_pdb_timestamp_age_match=True, capstone_version=capstone.__version__,
              functions=rows, guest_launched=False, physical_access=False)
with (K / 'kernel-calls001.json').open('x', encoding='utf-8', newline='\n') as f:
    f.write(json.dumps(result, indent=2)+'\n')
for row in rows:
    print(row['name'], [(hex(c['rva']), c['target']) for c in row['calls'] if c['target']])

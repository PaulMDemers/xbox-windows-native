"""Reproducible private ATAPI transformation; never distribute the vendor binary."""
import hashlib
import json
import struct
import sys
from pathlib import Path
k = Path(__file__).resolve().parent
ws = k.parents[1]
sys.path.insert(0, str(ws/'work/python-packages'))
import pefile
import capstone
sha = lambda b: hashlib.sha256(b).hexdigest()
source = k.parent/'dump-config-trace/serial005/artifacts/before-atapi.sys'
original = source.read_bytes()
assert sha(original) == 'faf9639ac8d14e9c72a4a2d7b8d3a6ceb9965f8bbc79c77d89a45733d745c675'
p = pefile.PE(data=original)
assert p.OPTIONAL_HEADER.SectionAlignment == p.OPTIONAL_HEADER.FileAlignment == 32
assert p.FILE_HEADER.NumberOfSections == 10
helper = (k/'artifacts/dispatch.bin').read_bytes()
start = (len(original)+31)&~31
assert start == 0x15800 and len(helper) < 256
first, second = p.sections[:2]
assert first.Name.rstrip(b'\0') == b'.text' and second.Name.rstrip(b'\0') == b'NONPAGE'
assert first.Characteristics == second.Characteristics == 0x68000020
assert first.VirtualAddress+first.SizeOfRawData == second.VirtualAddress
assert first.PointerToRawData+first.SizeOfRawData == second.PointerToRawData
assert all(s.VirtualAddress == s.PointerToRawData for s in p.sections)
# Merge contiguous sections with identical access/residency flags. All old RVAs,
# raw offsets, relocations, debug overlay and SizeOfHeaders stay unchanged.
merged = bytearray(first.__pack__())
length = second.VirtualAddress+second.SizeOfRawData-first.VirtualAddress
struct.pack_into('<I', merged, 8, length)
struct.pack_into('<I', merged, 16, length)
size = (len(helper)+31)&~31
new = struct.pack('<8sIIIIIIHHI', b'.xwndmp\0', len(helper), start, size, start, 0, 0, 0, 0, 0x68000020)
headers = bytes(merged)+b''.join(s.__pack__() for s in p.sections[2:])+new
assert len(headers) == 400
data = bytearray(original)
head = first.get_file_offset()
data[head:head+400] = headers
call = p.get_offset_from_rva(0x1360e)
assert data[call:call+5] == bytes.fromhex('e8ebf1feff')
data[call:call+5] = b'\xe8'+struct.pack('<i', start-(0x1360e+5))
data.extend(b'\0'*(start-len(data)))
data.extend(helper+b'\0'*(size-len(helper)))
struct.pack_into('<I', data, p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'), start+size)
struct.pack_into('<I', data, p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'), p.OPTIONAL_HEADER.SizeOfCode+size)
cp = p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum')
struct.pack_into('<I', data, cp, 0)
struct.pack_into('<I', data, cp, pefile.PE(data=bytes(data)).generate_checksum())
q = pefile.PE(data=bytes(data))
assert q.OPTIONAL_HEADER.CheckSum == q.generate_checksum()
allowed = set(range(head,head+400))|set(range(call,call+5))
for field in ['SizeOfImage','SizeOfCode','CheckSum']:
    off=p.OPTIONAL_HEADER.get_field_absolute_offset(field);allowed.update(range(off,off+4))
changed = [i for i,(a,b) in enumerate(zip(original,data)) if a != b]
assert set(changed) <= allowed
for section in p.sections:
    a,n=section.PointerToRawData,section.SizeOfRawData
    expected=bytearray(original[a:a+n])
    if a<=call<a+n:expected[call-a:call-a+5]=data[call:call+5]
    assert data[a:a+n] == expected
dest=k/'artifacts/atapi-candidate0105.sys'
assert not dest.exists()
dest.write_bytes(data)
instructions=[dict(rva=i.address,raw=i.bytes.hex(),op=i.mnemonic,args=i.op_str)
    for i in capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(helper,start)]
assert sum(len(bytes.fromhex(i['raw'])) for i in instructions)==len(helper)
r=dict(physical_access=False,source=str(source),source_sha256=sha(original),candidate_sha256=sha(data),
    helper_sha256=sha(helper),helper_rva=start,helper_bytes=len(helper),helper_instructions=instructions,
    existing_changed_offsets=changed,checksum_valid=True,all_old_rvas_preserved=True,
    only_old_code_change=dict(rva=0x1360e,before=original[call:call+5].hex(),after=data[call:call+5].hex()),
    sources={n:sha((k/n).read_bytes()) for n in ['dispatch.S','build-helper.sh','build.py']},
    restrictions='Private pinned NT5 binary only. WRITE(10), 512-byte sectors, <=2TiB LBA32; 48-bit-capable PIO multiple-write command39 only. Reject unsupported high addresses, malformed requests and LBA32 overflow. No physical qualification.',
    ordinary_qualified=False,dump_qualified=False)
(k/'build-review.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['candidate_sha256','helper_bytes','checksum_valid','only_old_code_change']},indent=2))

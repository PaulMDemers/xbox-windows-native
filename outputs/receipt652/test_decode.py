"""Validate C output against an independent Python layout/checksum oracle."""
import json
import struct
import sys
import zlib
from pathlib import Path
from decode import decode, GROUPS

blob = Path(sys.argv[1]).read_bytes()
attempt, candidate = bytes(range(1, 17)), bytes(range(0xa0, 0xc0))
expected = bytearray(1536)
expected[:8] = b'XWN652R1'
struct.pack_into('<II', expected, 8, 1, 768)
expected[16:32], expected[32:64] = attempt, candidate
struct.pack_into('<iI', expected, 64, -1, 2)
for index, (name, offset, count) in enumerate(GROUPS, 1):
    struct.pack_into('<' + 'I' * count, expected, offset,
                     *[index * 0x10000000 + i for i in range(count)])
expected[1024:1032] = b'XWN652C1'
struct.pack_into('<II', expected, 1032, 1, 1024)
expected[1040:1056], expected[1056:1088] = attempt, candidate
struct.pack_into('<I', expected, 1088, zlib.crc32(expected[:1024]))
struct.pack_into('<I', expected, 1532, zlib.crc32(expected[1024:1532]))
assert blob == bytes(expected)
decoded = decode(blob, attempt, candidate)
for index, (name, _, count) in enumerate(GROUPS, 1):
    assert decoded[name] == [index * 0x10000000 + i for i in range(count)]
checks = 6


def reject(b, a=attempt, c=candidate):
    global checks
    try:
        decode(b, a, c)
    except ValueError:
        checks += 1
    else:
        raise AssertionError('invalid record accepted')


for length in range(1536):
    reject(blob[:length])
reject(blob + b'\0')
for i in range(1536):
    for bit in range(8):
        b = bytearray(blob)
        b[i] ^= 1 << bit
        reject(bytes(b))
for a, c in [(b'\0'*16, candidate), (attempt, b'\0'*32),
             (attempt[:-1], candidate), (attempt, candidate[:-1]),
             (b'Z'*16, candidate), (attempt, b'Z'*32)]:
    reject(blob, a, c)
# Recompute checksums to distinguish semantic validation from integrity checks.
for offset in (0, 8, 12, 64, 68, 768, 1024, 1032, 1036, 1092):
    b = bytearray(blob)
    b[offset:offset+4] = b'\xfe'*4
    struct.pack_into('<I', b, 1088, zlib.crc32(b[:1024]))
    struct.pack_into('<I', b, 1532, zlib.crc32(b[1024:1532]))
    reject(bytes(b))
print(json.dumps(dict(passed=True, checks=checks,
                     scope='synthetic format and corruption oracle; no hardware')))

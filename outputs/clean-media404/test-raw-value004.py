import json, struct
from pathlib import Path
from raw_value004 import stored_value
data = bytearray(8192); at = 100; data[at:at+2] = b'vk'
count = 0
for length in range(5):
    struct.pack_into('<III', data, at+4, 0x80000000 | length, 0x04030201, 7)
    assert stored_value(data, at) == (7, bytes([1,2,3,4])[:length]); count += 1
struct.pack_into('<III', data, at+4, 3, 32, 0x404)
struct.pack_into('<i', data, 4128, -8); data[4132:4135] = b'abc'
assert stored_value(data, at) == (0x404, b'abc'); count += 1
for length, offset, size in [(0x80000005, 0, -8), (5,32,-8), (3,32,8), (3,9000,-8)]:
    struct.pack_into('<III', data, at+4, length, offset, 1); struct.pack_into('<i',data,4128,size)
    try:
        stored_value(data, at)
    except ValueError:
        count += 1
    else:
        raise AssertionError('Malformed value accepted')
with (Path(__file__).parent / 'raw-value-controls004.json').open('x') as f:
    json.dump(dict(checks=count, passed=True, scope='Synthetic declared lengths and invalid bounds; not guest evidence'), f, indent=2)
print(count)

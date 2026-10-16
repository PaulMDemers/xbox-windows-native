import ast
import hashlib
import json
import struct
from pathlib import Path
from review import verify_sections, call_target

K = Path(__file__).resolve().parent
elf = Path('E:/xwn374/build001/image-crom.elf').read_bytes()
payload = Path('E:/xwn374/build001/image-crom.bin').read_bytes()
review = json.loads((K/'source-review.json').read_text(encoding='utf-8'))
assert verify_sections(elf,payload) == review['sections']
negative = 0
for offset in [0, 0x420, 0x4f8, 0x538, 0x56d, 0x71b, 0x3434c, 0x4588f, len(payload)-1]:
    changed = bytearray(payload)
    changed[offset] ^= 1
    try:
        verify_sections(elf,changed)
    except AssertionError:
        negative += 1
    else:
        raise AssertionError('Changed deployed byte accepted')
for row in review['calls']:
    assert call_target(payload,row['address']) == row['target']
    altered = bytearray(payload)
    altered[row['address']-0x2600000+1] ^= 1
    assert call_target(altered,row['address']) != row['target']
    negative += 1
for file in K.glob('*.py'):
    ast.parse(file.read_text(encoding='utf-8'))
assert b'\xe9\x1b\x02\x00\x00' == payload[0x200:0x205]
for name,digest in review['source_files'].items():
    assert hashlib.sha256((Path('E:/xwn413/source')/name).read_bytes()).hexdigest() == digest
r = dict(passed=True, sections=3, direct_call_sites=4, mutation_rejections=negative,
         source_pins=6, scope='Host-only ELF/embedded-code and direct-call preflight; no runtime result')
with (K/'preflight001.json').open('x',encoding='utf-8') as f:
    json.dump(r,f,indent=2)
    f.write('\n')
print(json.dumps(r))

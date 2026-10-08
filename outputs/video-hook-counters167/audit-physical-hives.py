"""Read preserved physical hives and display bindings using the pinned offline runtime."""
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, '/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex

k = Path(__file__).resolve().parent
base=k;case=sys.argv[1];assert case in ['candidate001'];k=k/case
art = k/'artifacts/physical'
dest = k/'physical-hive-audit.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
assert read(k/'physical.json').get('collected_utc')
result = dict(physical_result=True, hives=[], bindings=[], physical_qualified=False)
for name in ['system', 'software']:
    p = art/('after-'+name)
    data = p.read_bytes()
    h = hivex.Hivex(str(p))
    todo = [h.root()]
    seen = set()
    values = 0
    while todo:
        n = todo.pop()
        assert n not in seen
        seen.add(n)
        h.node_name(n)
        for v in h.node_values(n):
            h.value_key(v)
            h.value_value(v)
            values += 1
        todo.extend(h.node_children(n))
    a, b = struct.unpack_from('<II', data, 4)
    checksum = 0
    for at in range(0, 508, 4):
        checksum ^= struct.unpack_from('<I', data, at)[0]
    if checksum == 0xffffffff:
        checksum = 0xfffffffe
    elif checksum == 0:
        checksum = 1
    result['hives'].append(dict(name=name, parsed=True, keys=len(seen), values=values,
        sha256=hashlib.sha256(data).hexdigest(), sequences_equal=a == b,
        checksum_valid=checksum == struct.unpack_from('<I', data, 508)[0]))
    if name == 'system':
        for expected in read(base.parent/'video-physical-review159/binding-edit.json')['changes']:
            n = h.root()
            for part in expected['path'].split('\\'):
                n = h.node_get_child(n, part)
                assert n
            v = h.node_get_value(n, expected['name'])
            typ, raw = h.value_value(v)
            result['bindings'].append(dict(path=expected['path'], type=typ, hex=raw.hex(),
                matched=typ == expected['type'] and raw.hex() == expected['after_hex' if case=='candidate001' else 'before_hex']))
result['passed'] = all(v['parsed'] and v['sequences_equal'] and v['checksum_valid'] for v in result['hives']) and all(v['matched'] for v in result['bindings'])
result['limits'] = 'Two preserved post-diagnostic hives, not every registry hive or full allocation audit.'
dest.write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
print(json.dumps(dict(passed=result['passed'], bindings=len(result['bindings']))))

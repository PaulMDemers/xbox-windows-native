"""Read actual cold ATAPI configuration; never change the hive or device policy."""
import hashlib
import json
import sys
from pathlib import Path

k = Path(__file__).resolve().parent
sys.path.insert(0, '/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex

p = k.parent/'dump-lba-trace/crash004/artifacts/before-configuration-system'
h = hivex.Hivex(str(p))
def node(path):
    n = h.root()
    for part in path.split('\\'):
        n = h.node_get_child(n, part)
        if not n:
            return 0
    return n
def values(n):
    result = {}
    for v in h.node_values(n):
        t, b = h.value_value(v)
        result[h.value_key(v)] = dict(type=t, raw=b.hex(), value=int.from_bytes(b, 'little')
            if t == 4 else b.decode('utf-16le').rstrip('\0') if t in [1, 2, 7] else b.hex())
    return result
cs = 'ControlSet%03d' % values(node('Select'))['Current']['value']
root = cs+'\\Services\\atapi'
pending = [(root, node(root))]
assert pending[0][1]
rows = []
while pending:
    path, n = pending.pop()
    assert len(rows) < 200
    rows.append(dict(path=path, values=values(n)))
    pending.extend((path+'\\'+h.node_name(child), child) for child in h.node_children(n))
dest = k/'registry-state.json'
assert not dest.exists()
dest.write_text(json.dumps(dict(scope=__doc__, hive_path=str(p),
    hive_sha256=hashlib.sha256(p.read_bytes()).hexdigest(), current_control_set=cs,
    keys=rows, physical_access=False, registry_modified=False), indent=2)+'\n')
print(json.dumps(rows, indent=2))

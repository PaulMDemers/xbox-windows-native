"""Independent raw-value agreement; unknown typed decoding remains a failure."""
import hashlib, json, struct, sys
from pathlib import Path
from Registry import Registry
sys.path.insert(0, '/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
from raw_value004 import stored_value

def audit(p):
    data = p.read_bytes()
    first, second = struct.unpack_from('<II', data, 4)
    checksum = 0
    for at in range(0, 508, 4):
        checksum ^= struct.unpack_from('<I', data, at)[0]
    checksum = 1 if checksum == 0 else 0xfffffffe if checksum == 0xffffffff else checksum
    r = Registry.Registry(str(p)); py = {}; pykeys = set(); errors = []
    todo = [(r.root(), '')]
    while todo:
        node, path = todo.pop()
        assert path not in pykeys; pykeys.add(path)
        for v in node.values():
            name = v.name() if v._vkrecord.has_name() else ''
            identity = (path, name)
            assert identity not in py
            stored_type, raw = stored_value(data, v._vkrecord.offset())
            assert stored_type == v.value_type()
            py[identity] = (v.value_type(), hashlib.sha256(raw).hexdigest(), len(raw))
            try:
                v.value()
            except Exception as e:
                errors.append(dict(key=path, value_name=name, type=v.value_type(),
                                   raw_sha256=hashlib.sha256(raw).hexdigest(), raw_bytes=len(raw),
                                   exception=type(e).__name__))
        todo.extend((n, path + '\\' + n.name()) for n in node.subkeys())
    h = hivex.Hivex(str(p)); hx = {}; hxkeys = set(); todo = [(h.root(), '')]; seen = set()
    while todo:
        n, path = todo.pop()
        assert n not in seen and path not in hxkeys; seen.add(n); hxkeys.add(path)
        for v in h.node_values(n):
            identity = (path, h.value_key(v)); assert identity not in hx
            typ, raw = h.value_value(v)
            hx[identity] = (typ, hashlib.sha256(raw).hexdigest(), len(raw))
        todo.extend((child, path + '\\' + h.node_name(child)) for child in h.node_children(n))
    assert pykeys == hxkeys and py == hx, 'Independent raw registry readers disagree'
    canonical = json.dumps([[list(k), list(v)] for k, v in sorted(py.items())], ensure_ascii=True).encode()
    return dict(name=p.name.lower(), sequences=[first, second],
                header_valid=data[:4] == b'regf' and checksum == struct.unpack_from('<I', data, 508)[0],
                clean=first == second, parsed_keys=len(pykeys), parsed_values=len(py),
                independent_raw_values_agree=True, raw_value_map_sha256=hashlib.sha256(canonical).hexdigest(),
                typed_decode_complete=not errors, typed_decode_errors=errors)

"""Read-only independent cells/references and first hivex refusal in closed194 SYSTEM."""
import datetime
import hashlib
import json
import struct
import sys
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
prior = k / 'observe001'
dest = k / 'system-forensics001.json'
assert not dest.exists() and json.loads((prior / 'closure.json').read_text())['closed']
sys.path.insert(0, '/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex

def inspect(p):
    data = p.read_bytes()
    r = dict(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
    a, b = struct.unpack_from('<II', data, 4)
    xor = 0
    for at in range(0, 508, 4):
        xor ^= struct.unpack_from('<I', data, at)[0]
    xor = 0xfffffffe if xor == 0xffffffff else 1 if xor == 0 else xor
    r.update(sequence_numbers=[a, b], checksum_valid=xor == struct.unpack_from('<I', data, 508)[0])
    cells = {}
    try:
        end = 4096 + struct.unpack_from('<I', data, 40)[0]
        assert end <= len(data)
        pos = 4096
        while pos < end:
            assert data[pos:pos + 4] == b'hbin'
            offset, size = struct.unpack_from('<II', data, pos + 4)
            assert offset == pos - 4096 and size >= 4096 and size % 4096 == 0 and pos + size <= end
            cell = pos + 32
            while cell < pos + size:
                signed = struct.unpack_from('<i', data, cell)[0]
                n = abs(signed)
                assert n >= 8 and n % 8 == 0 and cell + n <= pos + size
                cells[cell - 4096] = (cell + 4, n - 4, signed < 0)
                cell += n
            assert cell == pos + size
            pos += size
        r.update(cell_layout_valid=True, cells=len(cells))
    except Exception as exc:
        r.update(cell_layout_valid=False, cell_layout_error=repr(exc))
    failures = []
    def allocated(index, signature=None, context=''):
        row = cells.get(index)
        if row is None or not row[2] or signature and data[row[0]:row[0] + 2] != signature:
            failures.append(dict(context=context, index=hex(index), present=row is not None,
                                 allocated=None if row is None else row[2],
                                 actual_signature=None if row is None else data[row[0]:row[0] + 2].hex()))
            raise ValueError('Invalid referenced allocated cell')
        return row[:2]
    keys = set()
    seen_indexes = set()
    def children(index, path):
        assert index not in seen_indexes
        seen_indexes.add(index)
        at, size = allocated(index, context=path + ' subkey index')
        kind = data[at:at + 2]
        n = struct.unpack_from('<H', data, at + 2)[0]
        assert kind in [b'li', b'lf', b'lh', b'ri']
        stride = 8 if kind in [b'lf', b'lh'] else 4
        assert 4 + n * stride <= size
        entries = [struct.unpack_from('<I', data, at + 4 + i * stride)[0] for i in range(n)]
        return [v for entry in entries for v in children(entry, path)] if kind == b'ri' else entries
    def key(index, parent):
        assert index not in keys and len(keys) < 262144
        keys.add(index)
        at, size = allocated(index, b'nk', parent + ' key')
        assert size >= 76
        flags, name_length = struct.unpack_from('<H', data, at + 2)[0], struct.unpack_from('<H', data, at + 72)[0]
        assert 76 + name_length <= size
        name = data[at + 76:at + 76 + name_length].decode('cp1252' if flags & 32 else 'utf-16le')
        path = parent + '\\' + name
        count, value_count, values = (struct.unpack_from('<I', data, at + off)[0] for off in [20, 36, 40])
        if value_count:
            va, vs = allocated(values, context=path + ' value list')
            assert value_count <= 262144 and value_count * 4 <= vs
            for i in range(value_count):
                vi = struct.unpack_from('<I', data, va + i * 4)[0]
                vat, vsize = allocated(vi, b'vk', path + ' value[%d]' % i)
                assert vsize >= 20
                length, offset = struct.unpack_from('<II', data, vat + 4)
                if length & 0x80000000:
                    assert length & 0x7fffffff <= 4
                elif length:
                    da, ds = allocated(offset, context=path + ' value data[%d]' % i)
                    # NT5 small direct values. Large DB values are reported, not assumed invalid.
                    assert length <= ds or data[da:da + 2] == b'db'
        if count:
            entries = children(struct.unpack_from('<I', data, at + 28)[0], path)
            assert len(entries) == count
            for child in entries:
                key(child, path)
    try:
        key(struct.unpack_from('<I', data, 36)[0], '')
        r['independent_reference_walk_passed'] = True
    except Exception as exc:
        r.update(independent_reference_walk_passed=False, independent_error=repr(exc))
    r.update(keys_checked=len(keys), first_reference_failures=failures[:8])
    current = ''
    try:
        h = hivex.Hivex(str(p))
        todo = [('', h.root())]
        seen = set()
        while todo:
            current, n = todo.pop()
            assert n not in seen
            seen.add(n)
            for v in h.node_values(n):
                h.value_key(v)
                h.value_value(v)
            todo.extend((current + '\\' + h.node_name(c), c) for c in h.node_children(n))
        r['hivex_walk_passed'] = True
    except Exception as exc:
        r.update(hivex_walk_passed=False, hivex_error=repr(exc), hivex_first_failure_path=current)
    return r

rows = {phase: inspect(prior / 'artifacts' / (phase + '-system')) for phase in ['before', 'after']}
before = (prior / 'artifacts/before-system').read_bytes()
after = (prior / 'artifacts/after-system').read_bytes()
changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
result = dict(read_only=True, physical_access=False, guest_launch=False,
              utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), systems=rows,
              changed_bytes=len(changed), first_changed_offsets=changed[:32], last_changed_offsets=changed[-32:],
              prior_closed_audit_sha256=hashlib.sha256((prior / 'audit.json').read_bytes()).hexdigest(),
              source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              limits='Independent partial registry reference oracle, not a producer/root-cause determination '
                     'or permission to repair raw evidence, relaunch closed201 or deploy its unqualified helper.')
dest.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(rows, indent=2))

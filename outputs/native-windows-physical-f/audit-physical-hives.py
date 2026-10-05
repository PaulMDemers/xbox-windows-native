"""WSL read-only validation of already collected physical registry snapshots."""
import argparse, importlib.util, json, pathlib, struct

p = argparse.ArgumentParser()
p.add_argument('--cycle', required=True, type=int)
a = p.parse_args()
assert 1 <= a.cycle <= 999
k = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('hive_audit', k.parent / 'native-windows-fatx-paging/audit-hive.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
rows = []
out = k / f'physical-{a.cycle:03d}-hive-audit.json'
assert not out.exists()
for name in ['system', 'software', 'sam', 'security', 'default']:
    path = k / 'artifacts' / f'physical-{a.cycle:03d}-{name}'
    data = path.read_bytes()
    assert len(data) >= 4096 and data[:4] == b'regf'
    first, second = struct.unpack_from('<II', data, 4)
    assert first == second
    checksum = 0
    for value in struct.unpack_from('<127I', data):
        checksum ^= value
    checksum = 0xfffffffe if checksum == 0xffffffff else checksum or 1
    assert checksum == struct.unpack_from('<I', data, 508)[0]
    rows.append(dict(name=name, sequence1=first, sequence2=second,
                     checksum_valid=True, tree=m.audit_hive(path)))
out.write_text(json.dumps(rows, indent=2) + '\n')
print(json.dumps(rows, indent=2))

"""Read-only complete key/value comparison; detailed changes remain private."""
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, '/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
K = Path(__file__).resolve().parent
out = K / 'registry001.json'; assert not out.exists()
private = Path('/mnt/e/xwn422/registry-diff001.json'); assert not private.exists()
stage = json.loads((K.parent / 'loader-correspondence416/stage001.json').read_text())
capture = json.loads((K / 'capture001.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def walk(path):
    h = hivex.Hivex(str(path)); result = {}; stack = [(h.root(), '')]
    while stack:
        node, key = stack.pop()
        assert len(result) < 200000 and len(key) < 4096
        assert key not in result
        values = {}
        for v in h.node_values(node):
            name = h.value_key(v).lower(); kind, data = h.value_value(v)
            assert name not in values
            values[name] = [kind, data.hex()]
        result[key] = values
        for child in h.node_children(node):
            stack.append((child, key + '/' + h.node_name(child).lower()))
    return result

all_diffs = {}; summary = {}
for hive in ('system', 'software'):
    remote = '/E/winnt/system32/config/' + hive
    old = Path('/mnt/e/xwn415/demo/winnt/system32/config') / hive
    new = Path('/mnt/e/xwn422/before001') / hive
    assert sha(old) == stage['protected'][remote]
    assert sha(new) == capture['protected'][remote]
    before, after = walk(old), walk(new)
    differences = []
    for key in sorted(before.keys() | after.keys()):
        if before.get(key) == after.get(key): continue
        if key not in before or key not in after:
            differences.append(dict(key=key, before=before.get(key), after=after.get(key)))
        else:
            for name in sorted(before[key].keys() | after[key].keys()):
                a, b = before[key].get(name), after[key].get(name)
                if a != b: differences.append(dict(key=key, value=name, before=a, after=b))
    assert sha(old) == stage['protected'][remote] and sha(new) == capture['protected'][remote]
    all_diffs[hive] = differences
    summary[hive] = dict(old_keys=len(before), current_keys=len(after),
        value_or_key_changes=len(differences), old_sha256=sha(old), current_sha256=sha(new))
private.write_text(json.dumps(all_diffs, indent=2) + '\n')
r = dict(readonly=True, physical_writes=False, summary=summary,
    private_changes=str(private), private_changes_sha256=sha(private),
    scope='Complete decoded key/value tree; timestamps, hive free space and security descriptors are not compared')
out.write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps(summary, indent=2))
for hive, rows in all_diffs.items():
    for row in rows[:60]: print(hive, row['key'], row.get('value', '<key added/removed>'))

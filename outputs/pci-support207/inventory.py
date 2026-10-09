"""Read pinned physical189 evidence; never open a hive writable or touch a guest."""
import argparse, hashlib, json, re, struct, sys
from pathlib import Path

sys.path.insert(0, '/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def typed(value):
    typ, data = value
    result = {'type': typ, 'hex': data.hex()}
    if typ in (1, 2, 7):
        result['decoded'] = data.decode('utf-16le').rstrip('\0').split('\0') if typ == 7 else data.decode('utf-16le').rstrip('\0')
    elif typ == 4 and len(data) == 4:
        result['decoded'] = struct.unpack('<I', data)[0]
    return result

def snapshot(path):
    h = hivex.Hivex(str(path))
    values = {}
    todo = [('', h.root())]
    while todo:
        key, node = todo.pop()
        values[key] = {h.value_key(v): typed(h.value_value(v)) for v in h.node_values(node)}
        todo.extend((key + '\\' + h.node_name(c), c) for c in h.node_children(node))
    return values

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence-root', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Fresh output required'
    root = args.evidence_root
    manifest = root / 'outputs/device-durability189/physical.json'
    source = json.loads(manifest.read_text())
    result = {'scope': __doc__, 'source_manifest_sha256': sha(manifest), 'phases': {}, 'physical_access': False}
    logs = {}
    for phase in ('before', 'after'):
        pins = {}
        for name in ('system', 'setupapi.log'):
            row = source[phase][name]
            p = root / row['path']
            assert sha(p) == row['sha256'], p
            pins[name] = row
        values = snapshot(root / pins['system']['path'])
        select = values['\\Select']
        cs = 'ControlSet%03d' % select['Current']['decoded']
        devices = []
        for key, data in sorted(values.items()):
            if not key.startswith('\\' + cs + '\\Enum\\PCI\\') or len(key.split('\\')) != 6:
                continue
            row = {'instance': key.split('\\Enum\\')[1], 'values': data}
            driver = data.get('Driver', {}).get('decoded')
            service = data.get('Service', {}).get('decoded')
            row['driver_key'] = values.get('\\' + cs + '\\Control\\Class\\' + driver, {}) if driver else None
            row['service_key'] = values.get('\\' + cs + '\\Services\\' + service, {}) if service else None
            devices.append(row)
        logs[phase] = (root / pins['setupapi.log']['path']).read_bytes()
        result['phases'][phase] = {'pins': pins, 'select': select, 'current_control_set': cs, 'pci_instances': devices}
    assert logs['after'].startswith(logs['before']), 'SetupAPI history changed'
    tail = logs['after'][len(logs['before']):].decode('cp1252')
    result['setupapi_new_bytes'] = len(logs['after']) - len(logs['before'])
    result['setupapi_new_sections'] = [s.strip() for s in re.split(r'(?=\[\d{4}/)', tail) if s.strip()]
    result['limits'] = 'Persistent registry records include stale PC/emulator instances; presence and live ownership require runtime evidence. No device installation or qualification.'
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    for row in result['phases']['after']['pci_instances']:
        print(row['instance'], {k: v.get('decoded') for k, v in row['values'].items() if k in ('LocationInformation', 'Service', 'Driver', 'DeviceDesc')})
    print(tail)

if __name__ == '__main__':
    main()

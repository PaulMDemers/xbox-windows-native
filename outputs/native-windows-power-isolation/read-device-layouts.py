"""Record power/device layouts from the exact native kernel's public symbols."""
import hashlib, json, pathlib
out = pathlib.Path(__file__).resolve().parent
root = out.parents[1]
pdb = root / 'work/symbols/ntoskrnl-2195-7376.pdb'
expected = '29f5de2a8db7959875b8a615945bd6f16e50e5c5a9465dd8f71b37f37d671e9e'
assert hashlib.sha256(pdb.read_bytes()).hexdigest() == expected
parser = out.parent / 'native-windows-nt5-interrupts/read-pdb-layouts.py'
ns = {'__file__': str(parser)}
exec(parser.read_text().split('selected={}')[0], ns)
r = {'pdb_sha256': expected}
for name in ('_DRIVER_OBJECT', '_DEVICE_OBJECT', '_DEVOBJ_EXTENSION',
             '_DEVICE_NODE', '_KDEVICE_QUEUE', '_IRP', '_IO_STACK_LOCATION',
             '_DEVICE_OBJECT_POWER_EXTENSION'):
    item = ns['structs'][name]
    r[name] = {**item, 'fields': ns['fields'](item['field_list'])}
(out / 'native-device-layouts.json').write_text(json.dumps(r, indent=2) + '\n')
print('Exact native device layouts recorded')

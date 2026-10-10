"""Narrow, offline review of physical001 runtime registry differences; never writes hives."""
import hashlib
import importlib
import json
import struct
import sys
import uuid
from pathlib import Path

sys.dont_write_bytecode = True
k = Path(__file__).resolve().parent
sys.path.insert(0, str(k))
audit = importlib.import_module('audit-physical220')
repo = audit.repo
read = audit.read
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = read(k / 'physical001.json')
a = read(k / 'physical001-audit.json')
old = audit.configuration(audit.snapshot(repo / p['before']['system']['path']))
new = audit.configuration(audit.snapshot(repo / p['after']['system']['path']))
for ph in ('before', 'after'):
    for row in p[ph].values():
        if row:
            audit.data(row)
delta = [dict(path=key, before=old.get(key), after=new.get(key))
         for key in sorted(set(old) | set(new)) if old.get(key) != new.get(key)]
assert delta == a['configuration_delta']
assert len(delta) == 8
adapter = '{A9C365A2-852B-45F4-ABE6-3954C2DD03AC}'
times = dict(LeaseObtainedTime=(1791591289, 1791661544),
             T1=(1791634489, 1791704744), T2=(1791666889, 1791737144),
             LeaseTerminatesTime=(1791677689, 1791747944))
guids = ('f4806ef6e9f4b745be723ba029a3ca97', '37b813acb94c3443ac8d9a1b65a788da')
expected = {}
for cs in ('ControlSet001', 'ControlSet002'):
    root = '\\' + cs + '\\Services\\'
    expected[root + 'Dhcp\\Parameters'] = {adapter}
    expected[root + 'lanmanserver\\parameters'] = {'Guid'}
    expected[root + 'Tcpip\\Parameters\\Interfaces\\' + adapter] = set(times)
    expected[root + adapter + '\\Parameters\\Tcpip'] = set(times)
assert {d['path'] for d in delta} == set(expected)
reviewed = []
for d in delta:
    before, after = d['before'], d['after']
    changed = {n for n in set(before) | set(after) if before.get(n) != after.get(n)}
    assert changed == expected[d['path']]
    row = dict(path=d['path'], changed_values=sorted(changed))
    for name in changed:
        x, y = before[name], after[name]
        if name in times:
            for val, n in zip((x, y), times[name]):
                assert val == dict(type=4, hex=struct.pack('<I', n).hex(), decoded=n)
            assert y['decoded'] - x['decoded'] == 70255
            assert before['Lease']['decoded'] == after['Lease']['decoded'] == 86400
        elif name == 'Guid':
            assert [v['hex'] for v in (x, y)] == list(guids)
            assert x['type'] == y['type'] == 3
            assert all(uuid.UUID(bytes_le=bytes.fromhex(v['hex'])).version == 4 for v in (x, y))
        else:
            assert name == adapter and x['type'] == y['type'] == 3
            xb, yb = bytes.fromhex(x['hex']), bytes.fromhex(y['hex'])
            # Fixed observed cache offsets, not a blanket DHCP subtree exclusion.
            offsets = [16, 40, 72, 96, 120, 144, 168, 192, 216, 240]
            replacement = bytearray(xb)
            for offset in offsets:
                assert xb[offset:offset+4] == struct.pack('<I', times['LeaseTerminatesTime'][0])
                replacement[offset:offset+4] = struct.pack('<I', times['LeaseTerminatesTime'][1])
            assert bytes(replacement) == yb
            row['lease_expiry_cache_offsets'] = offsets
    reviewed.append(row)

# Independent physical USB trial, which did not run this PCI helper. Read only;
# its post-boot SYSTEM was separately retained before its baseline restoration.
usb = k.parents[4] / 'usb/repo/outputs/usb-hardware220'
up = read(usb / 'physical001.json')
control = dict(manifest_sha256=sha(usb / 'physical001.json'), phases={})
for ph in ('before', 'after'):
    pin = up[ph]['system']
    path = usb / pin['file']
    assert sha(path) == pin['sha256']
    values = audit.snapshot(path)
    observed = {cs: values['\\' + cs + '\\Services\\lanmanserver\\parameters']['Guid']
                for cs in ('ControlSet001', 'ControlSet002')}
    assert observed['ControlSet001'] == observed['ControlSet002']
    assert observed['ControlSet001']['type'] == 3
    assert uuid.UUID(bytes_le=bytes.fromhex(observed['ControlSet001']['hex'])).version == 4
    control['phases'][ph] = dict(system=pin, server_guid=observed)
assert control['phases']['before']['server_guid'] != control['phases']['after']['server_guid']
assert control['phases']['before']['server_guid']['ControlSet001']['hex'] == guids[0]
assert control['phases']['after']['server_guid']['ControlSet001']['hex'] != guids[1]

observation = read(k / 'physical001-user-observation.json')
assert observation['normal_windows_restart_reported']
assert a['normal_shutdown_event_count'] == 1
gates = ('hives_valid', 'incoming_protected_exact', 'helper_review_valid',
         'startup_restored', 'protected_exact', 'inventory_complete',
         'helpers_exit_zero', 'setupapi_history_preserved',
         'event_history_preserved', 'dashboard_return_recorded')
assert all(a[name] is True for name in gates)
assert p['helpers_exact'] and not p['startup_enabled']
result = dict(scope=__doc__, initial_audit_sha256=sha(k / 'physical001-audit.json'),
              source_sha256=sha(Path(__file__)), initial_configuration_unchanged=False,
              initial_baseline_gate=False, reviewed_keys=reviewed,
              changed_key_count=8, changed_value_count=20,
              independent_usb_control=control,
              interpretation='Exact lease timestamps/cache renewal and a new v4 server identity; the independent USB boot also changed this identity. Boot runtime interpretation, not an NT5 implementation proof.',
              other_selected_configuration_unchanged=True,
              baseline_restored=True, diagnostic_usable=True,
              baseline_scope='Original startup and protected files exact; all selected driver/device/service configuration unchanged except the 20 explicitly reviewed runtime values. Full hive byte equality is not claimed.',
              verified_gates={name: a[name] for name in gates},
              user_observation_sha256=sha(k / 'physical001-user-observation.json'),
              normal_restart_reported_and_event_correlated=True,
              physical_function_qualified=False, ordinary_qualified=False,
              full_allocation_audited=False,
              limits='One read-only identification run. Inherited Ftdisk49 remains a strict error. No SMBus/codec functionality, full storage durability or repeated-boot qualification.')
audit.save(k / 'physical001-restoration-review.json', result)
print(json.dumps({name: result[name] for name in ('baseline_restored', 'diagnostic_usable', 'changed_key_count', 'changed_value_count', 'independent_usb_control')}, indent=2))

"""Authorize a fresh snapshot only after reviewing all 32 actual value changes."""
import hashlib
import json
import re
from pathlib import Path
K = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = K / 'registry-review001.json'; assert not out.exists()
changes_path = Path('E:/xwn422/registry-diff001.json')
report = read(K / 'registry001.json'); assert sha(changes_path) == report['private_changes_sha256']
changes = read(changes_path)

def allowed(hive, row):
    if set(row) != {'key', 'value', 'before', 'after'}: return False
    if row['before'] is None or row['after'] is None: return False
    if row['before'][0] != row['after'][0]: return False
    key, value = row['key'], row['value']
    if hive == 'system':
        if not re.match(r'^/controlset00[12]/', key): return False
        tail = key[len('/controlset001/'):]
        if (tail, value) in [('control/print/providers', 'logontime'), ('control/windows', 'shutdowntime'), ('services/lanmanserver/parameters', 'guid')]: return True
        if tail == 'services/dhcp/parameters': return bool(re.fullmatch(r'\{[0-9a-f-]{36}\}', value))
        if re.fullmatch(r'services/(tcpip/parameters/interfaces/\{[0-9a-f-]{36}\}|\{[0-9a-f-]{36}\}/parameters/tcpip)', tail):
            return value in ('leaseobtainedtime', 'leaseterminatestime', 't1', 't2')
    if hive == 'software':
        if (key, value) in [('/microsoft/cryptography/rng', 'seed'), ('/microsoft/wbem/cimom', 'startup heap preallocation size')]: return True
        if key.startswith('/microsoft/windows nt/currentversion/profilelist/s-1-5-21-'): return value in ('profileloadtimehigh', 'profileloadtimelow')
        if key.startswith('/microsoft/windows/currentversion/syncmgr/'): return value == 'timestamp'
    return False

assert len(changes['system']) == 24 and len(changes['software']) == 8
assert all(allowed(hive, row) for hive, rows in changes.items() for row in rows)
negative_checks = 0
for hive, rows in changes.items():
    for row in rows:
        for replacement in [dict(row, key='/controlset001/services/xwnfatx'), dict(row, before=None), dict(row, after=None), dict(row, value='ImagePath')]:
            assert not allowed(hive, replacement)
            negative_checks += 1
r = dict(reviewed=True, baseline_refresh_approved=True, physical_writes=False,
    capture_sha256=sha(K / 'capture001.json'), registry_comparison_sha256=sha(K / 'registry001.json'),
    private_changes_sha256=sha(changes_path), system_changes=24, software_changes=8,
    no_keys_added_or_removed=True, no_value_types_changed=True, negative_checks=negative_checks,
    classification=['Print/logon/shutdown times', 'DHCP lease state', 'LanmanServer GUID',
                    'RNG seed', 'WBEM heap sizing', 'Profile load times', 'Synchronization timestamps'],
    unchanged_scope='All other decoded key/value data, including driver/start/display/pagefile/mount settings',
    limitation='Does not prove prior boot or full hive timestamp/security equivalence; original preflight failure retained')
out.write_text(json.dumps(r, indent=2) + '\n')
print('32 runtime-state changes reviewed; 128 mutations rejected; fresh exact hive baseline approved')

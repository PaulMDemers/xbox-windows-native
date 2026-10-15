"""Discriminating negative gates; synthetic inputs are not guest evidence."""
import copy, json
from pathlib import Path
from qualification import qualify
K = Path(__file__).resolve().parent
kernel = {'version': '5.0.2195.7376', 'sha256': 'kernel-model'}
probe = 'probe-model'
marker = dict(phase='setup-logon', version='5.0.2195', setup_in_progress='0', setup_type='0',
              copy='1', runonce='1', cd_readable='1', shutdown_privilege='1', shutdown_api_accepted='1')
base = dict(unchanged_by_audit=True, setup=dict(SystemSetupInProgress=0, SetupType=0),
            hives=[dict(name=n, header_valid=True, clean=True, parsed_keys=1) for n in ['system', 'software', 'sam', 'security', 'default']],
            versions={'ntoskrnl.exe': kernel}, files={'xwn404.exe': {'sha256': probe}},
            qcow_check={'check-errors': 0}, normal_shutdown_events=1, warnings_errors=[],
            markers={'xwn404-setup.txt': marker}, events={'system': [{'record': 1, 'event_id': 6006}], 'application': []})
final = copy.deepcopy(base)
final['markers']['xwn404-boot.txt'] = dict(marker, phase='disk-only-logon', cd_readable='0')
final['normal_shutdown_events'] = 2
assert qualify(base, final, kernel, probe)['clean_pc_install_scoped_passed']
mutations = [
    lambda r: r['markers']['xwn404-boot.txt'].update(cd_readable='1'),
    lambda r: r['markers']['xwn404-boot.txt'].update(shutdown_api_accepted='0'),
    lambda r: r['markers']['xwn404-boot.txt'].update(setup_in_progress='1'),
    lambda r: r['markers']['xwn404-setup.txt'].update(runonce='0'),
    lambda r: r['hives'][0].update(clean=False),
    lambda r: r['hives'][0].update(header_valid=False),
    lambda r: r['versions']['ntoskrnl.exe'].update(sha256='other'),
    lambda r: r['files']['xwn404.exe'].update(sha256='other'),
    lambda r: r['qcow_check'].update(corruptions=1),
    lambda r: r.update(qcow_check={}),
    lambda r: r.update(normal_shutdown_events=1),
    lambda r: r['events']['system'].clear(),
    lambda r: r.update(unchanged_by_audit=False),
]
for change in mutations:
    r = copy.deepcopy(final); change(r)
    assert not qualify(base, r, kernel, probe)['clean_pc_install_scoped_passed']
warning = copy.deepcopy(final); warning['warnings_errors'] = [{'source': 'retained-test-warning'}]
result = qualify(base, warning, kernel, probe)
assert result['clean_pc_install_scoped_passed'] and not result['strict_clean_pc_passed']
assert not result['fresh_xbox_assembly_qualified'] and not result['physical_qualified']
record = dict(synthetic_scope=True, scoped_failure_mutations=len(mutations), strict_warning_retained=True,
              no_xbox_or_physical_promotion=True, passed=True)
with (K / 'qualification-controls001.json').open('x') as f:
    json.dump(record, f, indent=2)
print(json.dumps(record))

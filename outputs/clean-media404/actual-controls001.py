"""Mutate copies of actual cold reports; never alter frozen disk or reports."""
import copy, hashlib, json
from pathlib import Path
from qualification002 import qualify
K = Path(__file__).resolve().parent
read = lambda n: json.loads((K / n).read_text())
first, final = read('cold-phase03.json'), read('cold-phase04.json')
kernel = next(r['kernel'] for r in read('media-structure001.json') if r['id'] == 'customized-sp4-oem-en')
probe = read('probe-build002.json')['binary_sha256']
baseline = qualify(first, final, kernel, probe)
assert baseline['clean_pc_install_scoped_passed'] and not baseline['strict_clean_pc_passed']
assert not baseline['typed_decode_complete'] and not baseline['automatic_runonce_handoff_passed']
changes = [lambda r: r['markers']['xwn404-boot.txt'].update(cd_readable='1'),
           lambda r: r['hives'][0].update(independent_raw_values_agree=False),
           lambda r: r['hives'][0].update(clean=False),
           lambda r: r.update(normal_shutdown_events=1),
           lambda r: r['versions']['ntoskrnl.exe'].update(sha256='changed'),
           lambda r: r['events']['system'].clear()]
for change in changes:
    altered = copy.deepcopy(final); change(altered)
    assert not qualify(first, altered, kernel, probe)['clean_pc_install_scoped_passed']
warning = copy.deepcopy(final); warning['warnings_errors'].append({'type': 2, 'source': 'negative-control'})
assert not qualify(first, warning, kernel, probe)['strict_events_passed']
with (K / 'actual-controls001.json').open('x') as f:
    json.dump(dict(actual_negative_mutations=len(changes)+1, passed=True,
                   typed_decode_and_automatic_handoff_failures_retained=True,
                   originals={n: hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['cold-phase03.json', 'cold-phase04.json']}), f, indent=2)
print('Seven actual-report mutations rejected; original failures retained.')

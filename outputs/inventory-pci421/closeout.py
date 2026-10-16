"""Read-only evidence review and new closeout records; no console access."""
import hashlib
import json
import pathlib
import re
import subprocess
import zipfile
K = pathlib.Path(__file__).resolve().parent
W = K.parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
def save(name, obj):
    p = K / name; assert not p.exists(); p.write_text(json.dumps(obj, indent=2) + '\n')
build = read(K / 'build001.json')
for n, h in build['sources'].items():
    assert sha((W / 'src/utilities/hardware-report' / n).read_bytes()) == h
    assert sha((pathlib.Path(build['output']) / n).read_bytes()) == h
stage = read(K / 'stage001.json')
for n, h in stage['inputs'].items(): assert sha((K / n).read_bytes()) == h, n
reference = W / 'work/reference-sources/reactos-xbox'
head = subprocess.check_output(['git', '-C', str(reference), 'rev-parse', 'HEAD']).decode().strip()
assert head == '7c35fc4ead884e1bd0640a9613f652c40bca8b2e'
rel = 'hal/halx86/legacy/bus/pcibus.c'
reference_bytes = (reference / rel).read_bytes()
assert b'Trying to get PCI config data from devices 0:0:1 and 0:0:2' in reference_bytes
save('source-review001.json', dict(reference_commit=head, reference_path=rel,
    reference_file_sha256=sha(reference_bytes), utility_sources=build['sources'],
    stage_inputs_exact=len(stage['inputs']), native_source_matches_current=True,
    scope='Hardware facts inform independently written MIT filter; no upstream function copied'))
physical = read(K / 'physical-collection001.json')
assert physical['completed'] and physical['protected_unchanged']
assert sha(pathlib.Path(physical['report_path']).read_bytes()) == physical['report_sha256']
archive = read(K / 'bundle001.json'); data = pathlib.Path(archive['archive']).read_bytes()
assert sha(data) == archive['sha256']
binary = []; sensitive = []
patterns = [rb'gh[pousr]_[A-Za-z0-9]{25,}', rb'-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----', rb'(?i)(?:productkey|product_key|hddkey|hdd_key)\s*[=:]\s*["\x27]?[A-Za-z0-9-]{12,}']
with zipfile.ZipFile(archive['archive']) as z:
    for info in z.infolist():
        if info.is_dir(): continue
        b = z.read(info)
        if b'\0' in b or b.startswith((b'MZ', b'XBEH')): binary.append(info.filename)
        if any(re.search(p, b) for p in patterns): sensitive.append(info.filename)
assert binary == ['E/Applications/XWNInfo/default.xbe'] and not sensitive
save('bundle-content-review001.json', dict(binary_members=binary,
    token_private_key_or_private_payload_matches=sensitive, sha256=archive['sha256'],
    scope='Payload classification and selected secret patterns, not a comprehensive privacy certification'))
smoke = read(K / 'smoke001.json')
assert smoke['report_scope_passed'] and smoke['allocation']['errors'] == 0 and smoke['allocation']['orphans'] == 0
assert read(K / 'closure001.json')['closed'] and not read(K / 'closure001.json')['fallback']
assert read(K / 'physical-return001.json')['returned']
save('final-review.json', dict(source_and_stage_inputs_exact=True,
    emulator_scope_passed=True, physical_inventory_scope_passed=True,
    physical_pci_response_records=len(physical['report']['pci']),
    physical_report_sha256=physical['report_sha256'],
    strict_emulator_disk_unchanged=smoke['only_E_changed'],
    physical_whole_disk_audited=False, other_revisions_qualified=False,
    windows_tested=False, loader416_activated=False, console_C_accessed=False,
    all_owned_sessions_closed=True, bundle_sha256=archive['sha256'],
    tests=dict(policy_asan_ubsan=524, report_validator_windows=5,
               report_validator_linux=5, bundle_windows_passed=9, bundle_windows_skipped=1)))
print('Exact source/stage/private report/archive checks passed; new closeout records written')

"""Create a private delivery index for verified independent profile archives."""
import hashlib
import json
import shutil
from pathlib import Path

root = Path('D:/xwn844')
repo = Path(__file__).resolve().parents[2]
receipt = repo / 'outputs/bundle-config844/registry-semantic-comparison.json'
assert hashlib.sha256(receipt.read_bytes()).hexdigest() == 'a889c873110434ad6021f6d74d4f1bd7ebf29c7b31e1fd038bf9835389ebace7'
profiles = [
    ('xbox16-720p-002', 'b711fe0f7d660f1eb921bbfef902c174bb45616eb6c522ee6971dee48a3ca81d',
     '1.6 fixed 720p: 843 desktop and preconnected mouse observed; shutdown stalled. Permanent-path launcher rebuilt and this archive not boot-tested.'),
    ('xbox10-720p-002', 'e1837395ac915fd1446bf115fc713a9e267df9c79667a2cff018f11cb8415915',
     '1.0 fixed 720p: selected boot and FATX components match historic physical evidence; targeted registry values match 642; this archive not boot-tested.'),
    ('xbox10-480p-001', '02dac3111407e5f5bae2bab94e534ba4fd83f8cbc8f8f79dbefb5bdf5cbab032',
     '1.0 720x480 progressive: selected boot and FATX components match 638/642 physical tests; targeted registry values match 642; this archive not boot-tested.'),
    ('xbox10-1080i-002', 'ef1a678f47a3ad9d429df4264acdac487f025ab390a41b071fc15360b881c738',
     '1.0 1080i: stock E source reconstruction; historical text gaps and motion/drag artifacts and field quality remain unresolved. This archive is not physically tested.')]
rows = []
for name, expected, qualification in profiles:
    p = root / name / (name + '.zip')
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    assert h.hexdigest() == expected
    issues = p.parent / 'KNOWN-ISSUES.txt'
    rows.append({'archive': p.relative_to(root).as_posix(), 'bytes': p.stat().st_size,
                 'sha256': expected, 'qualification': qualification,
                 'known_issues': issues.relative_to(root).as_posix(), 'known_issues_sha256': hashlib.sha256(issues.read_bytes()).hexdigest()})
destination = root / 'registry-semantic-comparison.json'
if not destination.exists():
    shutil.copyfile(receipt, destination)
assert destination.read_bytes() == receipt.read_bytes()
index = {'private': True, 'profiles': rows,
         'copying_instructions': {'path': 'COPYING.txt', 'sha256': hashlib.sha256((root / 'COPYING.txt').read_bytes()).hexdigest()},
         'registry_receipt': {'path': destination.name, 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()},
         'limits': ['Every archive is a newly assembled, unbooted candidate.',
                    'Windows and profile data are private; do not publish.',
                    'The 1.6 shutdown did not complete in 843.',
                    'Full hive equivalence and general compatibility are not established.',
                    'No 640x480 or 1024x576 E Windows package has been qualified by this index.']}
with (root / 'DELIVERY-002.json').open('x', encoding='utf-8') as f:
    json.dump(index, f, indent=2)
    f.write('\n')
print('Private delivery index written for', len(rows), 'verified packages')

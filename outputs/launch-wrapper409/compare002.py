"""Read-only comparison of the two closed physical allocation probes."""
import datetime
import hashlib
import json
from pathlib import Path

from decode002 import decode

K = Path(__file__).resolve().parent


def read(name):
    return json.loads((K / name).read_text(encoding='utf-8'))


def main():
    a = read('collection001.json')
    b = read('manual-collection002.json')
    raw_a = Path('E:/xwn409/physical001/report.bin').read_bytes()
    raw_b = Path('E:/xwn409/physical002/report.bin').read_bytes()
    for record, raw in ((a, raw_a), (b, raw_b)):
        assert record['completed'] and record['protected_exact']
        assert len(record['protected']) == 62 and all(record['protected'].values())
        assert hashlib.sha256(raw).hexdigest() == record['report_sha256']
    da = decode(raw_a, cookie=0x40900101)
    db = decode(raw_b, cookie=0x40900102)
    assert db == b['decoded']
    historical = read('interpretation002.json')
    assert all(historical[key] == value for key, value in da.items())
    assert da == db and da['outcome'] == 'allocation_prefix_completed'
    differences = [i for i, (x, y) in enumerate(zip(raw_a, raw_b)) if x != y]
    assert len(raw_a) == len(raw_b) == 80 and differences == [12, 72]
    assert a['decode_error'] and b['diagnostic_xbe_exact'] and b['owner_exact']
    pins = read('manual-stage002.json')['source_pins']
    for path, digest in pins.items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
    result = {
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'both_attempts_closed': True,
        'decoded_allocation_results_identical': True,
        'raw_byte_differences': differences,
        'raw_difference_meaning': 'Only the low byte of each attempt cookie differs.',
        'decoded': db,
        'protected_checks_per_attempt': 62,
        'manual_source_pins_exact': len(pins),
        'original_decoder_failure_preserved': True,
        'user_observation': read('manual-user-return002.json')['verbatim'],
        'console_C_accessed': False,
        'new_launch_requested': False,
        'historical_failure_cause_established': False,
        'paging_or_handoff_verified': False,
        'release_ready': False,
        'input_sha256': {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [Path(__file__), K / 'decode002.py',
                         K / 'collection001.json', K / 'manual-collection002.json',
                         K / 'manual-user-return002.json', K / 'interpretation002.json']
        },
    }
    with (K / 'pair-review002.json').open('x', encoding='utf-8', newline='\n') as out:
        json.dump(result, out, indent=2)
        out.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

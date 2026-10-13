"""Post-run summary of four physical calls, not twenty independent samples."""
import hashlib
import json
import statistics
import struct
import sys
from pathlib import Path

K = Path(__file__).resolve().parent
W = K.parents[1]
out = K / 'candidate001'
dest = out / 'timing-review.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
a = read(out / 'audit.json')
assert a['bandwidth_passed'] and a['bandwidth_identity']['passed']
assert a['diagnostic_workload_completed']
samples = a['bandwidth_samples']
assert len(samples) == 5 and all(v == samples[0] for v in samples)
records = samples[0]['records']
assert len(records) == 4
rows = []
for v in records:
    assert v['bytes'] == 921600 and v['ram_ms'] > 0 and v['scanout_ms'] > 0
    rows.append(dict(**v,
        ram_mib_per_second=v['bytes'] / (1024 * 1024) * 1000 / v['ram_ms'],
        scanout_mib_per_second=v['bytes'] / (1024 * 1024) * 1000 / v['scanout_ms'],
        scanout_to_ram_time_ratio=v['scanout_ms'] / v['ram_ms'],
        calibration_min_us=v['calibration_min'] * 1000000 / v['frequency'],
        calibration_max_us=v['calibration_max'] * 1000000 / v['frequency']))
sys.path.insert(0, str(W / 'outputs/bandwidth-runtime365'))
from joined_identity import join
root = K / 'artifacts/candidate001/E/xwnbandwidth368candidate001/sample0'
packet = root / 'bandwidth.bin'
memory = root / 'memory-after.bin'
b = packet.read_bytes()
m = memory.read_bytes()
assert join(b, m)['passed']
words = list(struct.unpack('<133392I', b))
negative_count = 0
for slot in range(4):
    for field in (4, 5, 6, 12):
        changed = words.copy()
        changed[16 + slot * 33344 + field] += 4096
        try:
            join(struct.pack('<133392I', *changed), m)
        except ValueError:
            negative_count += 1
        else:
            raise AssertionError((slot, field))
assert packet.read_bytes() == b and memory.read_bytes() == m
result = dict(
    physical_measurement=True, unique_upload_calls=4, repeated_packet_reads=5,
    records=rows, actual_identity_mutations_rejected=negative_count,
    median_ram_ms=statistics.median(v['ram_ms'] for v in rows),
    median_scanout_ms=statistics.median(v['scanout_ms'] for v in rows),
    median_paired_ratio=statistics.median(v['scanout_to_ram_time_ratio'] for v in rows),
    hashes={str(p.relative_to(W)): sha(p) for p in
        [Path(__file__), out / 'audit.json', packet, memory,
         W / 'outputs/bandwidth-runtime365/joined_identity.py',
         W / 'outputs/bandwidth364/decode.py']},
    strict_qualification_passed=a['strict_qualification_passed'],
    performance_improvement_proved=False,
    limits='Four instrumented existing upload calls with alternating order. '
           'Private destination pitch2560 differs from scanout pitch7680; allocation, '
           'verification and mapping capture occur outside timing but affect cache history. '
           'No overhead subtraction, statistical desktop FPS, cache-change causality, '
           'all-alias or transient ABA proof. Five packet reads contain the same four calls.')
dest.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ['unique_upload_calls', 'median_ram_ms',
    'median_scanout_ms', 'median_paired_ratio', 'actual_identity_mutations_rejected']}, indent=2))

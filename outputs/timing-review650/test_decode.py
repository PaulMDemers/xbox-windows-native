"""Independent known-value and overflow isolation checks for the offline decoder."""
import json
from decode import analyze, decode_crtc, load_profiles, next_endpoint

checks = 0


def check(value):
    global checks
    assert value
    checks += 1


profiles = load_profiles()
for mode, oracle in [(3, (104, 90, 525, 480, 488, 494, 2880)), (1, (205, 160, 750, 720, 724, 729, 5120))]:
    d = decode_crtc(profiles[mode]['CR'])
    check(tuple(d[k] for k in ('horizontal_total_chars', 'horizontal_display_chars',
        'vertical_total_lines', 'vertical_display_lines', 'vertical_retrace_start',
        'vertical_retrace_end', 'pitch_bytes')) == oracle)
    check(d['vertical_retrace_end'] < d['vertical_total_lines'])
    check(not d['scan_double'] and d['max_scan_line'] == 0 and d['sync_enabled'])

# One-bit fixtures isolate every extended vertical placement, especially the
# conflicting CR25 bit2/bit3 descriptions and missing physical CR41 fields.
base = dict.fromkeys(profiles[3]['CR'], 0)
mapping = [(7, 0, 'vertical_total_lines', 256), (7, 5, 'vertical_total_lines', 512),
    (0x25, 0, 'vertical_total_lines', 1024), (0x41, 0, 'vertical_total_lines', 2048),
    (7, 1, 'vertical_display_lines', 256), (7, 6, 'vertical_display_lines', 512),
    (0x25, 1, 'vertical_display_lines', 1024), (0x41, 2, 'vertical_display_lines', 2048),
    (7, 2, 'vertical_retrace_start', 256), (7, 7, 'vertical_retrace_start', 512),
    (0x25, 2, 'vertical_retrace_start', 1024), (0x41, 4, 'vertical_retrace_start', 2048),
    (7, 3, 'vertical_blank_start', 256), (9, 5, 'vertical_blank_start', 512),
    (0x25, 3, 'vertical_blank_start', 1024), (0x41, 6, 'vertical_blank_start', 2048),
    (0x2d, 0, 'horizontal_total_chars', 256), (0x2d, 1, 'horizontal_display_chars', 256),
    (0x2d, 2, 'horizontal_blank_start', 256), (0x2d, 3, 'horizontal_retrace_start', 256)]
decoded_base = decode_crtc(base)
for index, bit, field, delta in mapping:
    case = base.copy()
    case[index] = 1 << bit
    result = decode_crtc(case)
    check(result[field] == decoded_base[field] + delta)
    for other in ('vertical_total_lines', 'vertical_display_lines', 'vertical_retrace_start',
                  'vertical_blank_start', 'horizontal_total_chars', 'horizontal_display_chars',
                  'horizontal_blank_start', 'horizontal_retrace_start'):
        if other != field:
            check(result[other] == decoded_base[other])

# Full-value endpoint examples use actual start+length, not a second decoder.
for bits in (4, 5, 7, 8):
    for start in (0, 15, 31, 127, 255, 479, 488, 719, 724, 1023, 2047):
        for length in (1, 2, (1 << bits) - 1, 1 << bits):
            end = start + length
            check(next_endpoint(start, end % (1 << bits), bits) == end)

for index in (0x25, 0x41, 0x10, 0x11):
    case = profiles[3]['CR'].copy()
    del case[index]
    try:
        decode_crtc(case)
    except AssertionError:
        checks += 1
    else:
        raise AssertionError('Accepted missing register')
for invalid in (-1, 256, 0x10000):
    case = profiles[3]['CR'].copy()
    case[0x10] = invalid
    try:
        decode_crtc(case)
    except AssertionError:
        checks += 1
    else:
        raise AssertionError('Accepted invalid byte')

result = analyze()
check(result['retained_readback_comparison_count'] == 114)
check(len(result['unmasked_differences']) == 6)
check(result['physical_crtc41_not_captured'])
print(json.dumps(dict(passed=True, checks=checks, physical_access=False,
    scope='Offline counter decoding, synthetic overflow/boundary tests and retained-readback comparison')))

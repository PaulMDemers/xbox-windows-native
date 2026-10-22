"""Offline programmed-counter review; never accesses hardware or a guest runtime.

Bit placements follow Linux v6.12 nouveau/dispnv04/nvreg.h and crtc.c.
These are encoded CRTC counter values, not measured output timings or clocks.
"""
import ast
import hashlib
import json
import re
from pathlib import Path

KIT = Path(__file__).resolve().parent
ROOT = KIT.parents[1]


def load_profiles():
    path = ROOT / 'outputs/native480p633/xwn_hd_profile.c'
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == '37c8c8bd6d4eebe9f025d4dcef9a57a6638ac47034e7b924b101a08715d6cc32'
    text = data.decode('ascii')

    def array(name):
        match = re.search(r'\b' + re.escape(name) + r'\[\d+\]\s*=\s*(\{.*?\});', text, re.S)
        assert match, name
        body = re.sub(r'(?<=[0-9a-fA-F])[uU]\b', '', match[1])
        return ast.literal_eval(body.replace('{', '[').replace('}', ']'))

    indices = [array(n) for n in ('xwn_hd_crtc_indices', 'xwn_hd_mmio_offsets', 'xwn_hd_encoder_indices')]
    result = {}
    for mode, values in enumerate(array('profiles'), 1):
        groups = dict(zip(('CR', 'MM', 'EN'), (dict(zip(i, v, strict=True)) for i, v in zip(indices, values[5:], strict=True))))
        result[mode] = dict(geometry=values[:5], **groups)
    assert len(result) == 3
    return result


def next_endpoint(start, low, bits):
    """First following counter value with these low bits; equal means full span.

    This is a modulo-counter arithmetic convention, not a pulse measurement.
    Current profiles have nonzero differences, so equal-end ambiguity is unused.
    """
    span = 1 << bits
    assert 0 <= low < span and start >= 0
    return start + ((low - start) % span or span)


def decode_crtc(cr):
    required = set(range(0, 10)) | {0x10, 0x11, 0x12, 0x13, 0x15, 0x16, 0x17, 0x19, 0x25, 0x28, 0x2d, 0x39, 0x41}
    assert required <= cr.keys(), 'Missing registers must remain unknown, never default to zero'
    assert all(isinstance(v, int) and 0 <= v <= 255 for v in cr.values())

    def bit(index, source, target):
        return ((cr[index] >> source) & 1) << target

    vt = cr[6] | bit(7, 0, 8) | bit(7, 5, 9) | bit(0x25, 0, 10) | bit(0x41, 0, 11)
    vd = cr[0x12] | bit(7, 1, 8) | bit(7, 6, 9) | bit(0x25, 1, 10) | bit(0x41, 2, 11)
    vs = cr[0x10] | bit(7, 2, 8) | bit(7, 7, 9) | bit(0x25, 2, 10) | bit(0x41, 4, 11)
    vb = cr[0x15] | bit(7, 3, 8) | bit(9, 5, 9) | bit(0x25, 3, 10) | bit(0x41, 6, 11)
    ht = cr[0] | bit(0x2d, 0, 8)
    hd = cr[1] | bit(0x2d, 1, 8)
    hb = cr[2] | bit(0x2d, 2, 8)
    hs = cr[4] | bit(0x2d, 3, 8)
    hbe = (cr[3] & 31) | bit(5, 7, 5) | bit(0x25, 4, 6)
    ve = next_endpoint(vs, cr[0x11] & 15, 4)
    return dict(
        horizontal_total_chars=ht + 5, horizontal_display_chars=hd + 1,
        horizontal_blank_start=hb, horizontal_blank_end=next_endpoint(hb, hbe, 7),
        horizontal_retrace_start=hs, horizontal_retrace_end=next_endpoint(hs, cr[5] & 31, 5),
        vertical_total_lines=vt + 2, vertical_display_lines=vd + 1,
        vertical_blank_start=vb, vertical_blank_end=next_endpoint(vb, cr[0x16], 8),
        vertical_retrace_start=vs, vertical_retrace_end=ve, vertical_retrace_span=ve - vs,
        pitch_bytes=8 * (cr[0x13] | ((cr[0x19] & 0xe0) << 3)),
        scan_double=bool(cr[9] & 128), max_scan_line=cr[9] & 31,
        sync_enabled=bool(cr[0x17] & 128), interlace_register=cr[0x39],
        pixel_format=cr[0x28] & 3,
    )


def analyze():
    profiles = load_profiles()
    facts = json.loads((ROOT / 'outputs/native480p633/profile-facts.json').read_text())
    for group in ('CR', 'MM', 'EN'):
        assert profiles[3][group] == {int(k): v for k, v in facts['groups'][group].items()}
    old = json.loads((ROOT / 'outputs/hd-profile310/profile-facts.json').read_text())
    for group, index, name in [('CR', 'crtc_indices', 'crtc'), ('MM', 'mmio_offsets', 'mmio'), ('EN', 'encoder_indices', 'encoder')]:
        assert profiles[1][group] == dict(zip(old[index], old['profiles'][0][name], strict=True))
    physical = json.loads((ROOT / 'outputs/mode-switch631/physical-collection002.json').read_text())['decoded']['stages']
    comparisons = []
    differences = []
    for stage, mode in zip(physical, (3, 1, 3), strict=True):
        p = profiles[mode]
        for key, value in stage['crtc'].items():
            index = int(key)
            # Preserve established631/632 comparison masks. Other bits are not licensed writes.
            mask = {0x19: 0xe0, 0x2d: 1}.get(index, 255)
            assert p['CR'][index] & mask == value & mask
            comparisons.append(dict(mode=mode, kind='CR', index=index, mask=mask))
            if p['CR'][index] != value:
                differences.append(dict(mode=mode, index=index, programmed=p['CR'][index], readback=value, mask=mask))
        for index, value in enumerate(stage['fp']):
            offset = 0x680800 + 4 * index
            if offset in p['MM']:
                assert p['MM'][offset] == value
                comparisons.append(dict(mode=mode, kind='MM', offset=offset, mask=0xffffffff))
        assert p['MM'][0x680600] == stage['mmio'][str(0x680600)]
        comparisons.append(dict(mode=mode, kind='MM', offset=0x680600, mask=0xffffffff))
    modes = {}
    for mode in (3, 1):
        p = profiles[mode]
        cr = decode_crtc(p['CR'])
        mm = p['MM']
        modes[str(mode)] = dict(geometry=p['geometry'], programmed_crtc=cr,
            programmed_fp=dict(hdisplay_end=mm[0x680820], htotal=mm[0x680824], hcrtc=mm[0x680828],
                hsync_start=mm[0x68082c], hsync_end=mm[0x680830], hvalid_end=mm[0x680838],
                vdisplay_end=mm[0x680800], vtotal=mm[0x680804], vcrtc=mm[0x680808],
                vsync_start=mm[0x68080c], vsync_end=mm[0x680810], vvalid_end=mm[0x680818]),
            crtc_h_total_at_declared_8_dot_clock=cr['horizontal_total_chars'] * 8,
            fp_h_total_plus_one=mm[0x680824] + 1)
    return dict(passed=True, physical_access=False, guest_launch=False,
        scope='Offline programmed constants and retained stock631 readback only; no failing native readback',
        programming_facts_exact=True, retained_readback_comparison_count=len(comparisons),
        readback_masks_preserved=True, unmasked_differences=differences, modes=modes,
        physical_crtc41_not_captured=True, actual_clock_and_routing_unresolved=True)


if __name__ == '__main__':
    print(json.dumps(analyze(), indent=2))

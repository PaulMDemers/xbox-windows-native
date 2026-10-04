"""Decode a bounded trace without interpreting pending IRPs as completed ones."""
import argparse, hashlib, json, pathlib, struct

def decode(data):
    assert len(data) == 4096 and data[:16] == b'XWN-VID-TRACE01\n'
    count, dropped = struct.unpack_from('<II', data, 16)
    assert count <= 254
    labels = {1: 'armed', 2: 'AddDevice entry', 3: 'AddDevice return',
              4: 'PnP dispatch entry', 5: 'PnP dispatch return',
              6: 'unload', 7: 'START resource-list counts',
              8: 'PCI config bytes returned', 9: 'PCI config DWORD'}
    events, bridge, gpu = [], {}, {}
    for i in range(count):
        event, a, b, c = struct.unpack_from('<4I', data, 32 + 16*i)
        assert event in labels
        events.append({'event': labels[event], 'a': f'{a:08x}', 'b': f'{b:08x}', 'c': f'{c:08x}'})
        if event == 9:
            assert a < 64 and a % 4 == 0
            bridge[f'{a:02x}'] = f'{b:08x}'
            gpu[f'{a:02x}'] = f'{c:08x}'
    return {'sha256': hashlib.sha256(data).hexdigest(), 'records': count,
            'skipped_io_attempts': dropped, 'events': events,
            'bridge_00_1e_0_config': bridge, 'gpu_01_00_0_config': gpu}

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('input', type=pathlib.Path)
    p.add_argument('--output', type=pathlib.Path, required=True); a = p.parse_args()
    result = decode(a.input.read_bytes())
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

"""Read-only source closure for the 263 backend-retirement design review."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPSULE = Path('E:/Codex-archive/xbox-windows-native/pending263-build001/source')
DEST = Path('E:/Codex-archive/xbox-windows-native/retirement264-source001')
WSL = '/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet'
PINS = ROOT / 'outputs/surface-pending263/renderer-source-pins001.json'
FILES = [
    'hw/xbox/nv2a/pgraph/gl/' + x for x in
    ('renderer.c', 'renderer.h', 'surface.c', 'texture.c', 'vertex.c',
     'display.c', 'reports.c', 'shaders.c', 'draw.c')
] + [
    'hw/xbox/nv2a/pgraph/pgraph.c', 'hw/xbox/nv2a/pfifo.c',
    'hw/xbox/nv2a/nv2a.c', 'hw/xbox/nv2a/nv2a_int.h',
    'hw/xbox/nv2a/pcrtc.c', 'hw/xbox/nv2a/pvideo.c',
    'system/physmem.c', 'system/cpus.c', 'cpu-common.c',
    'ui/xemu.c', 'include/qemu/lru.h',
    'hw/xbox/nv2a/pgraph/thirdparty/gloffscreen/common.c',
    'hw/xbox/nv2a/pgraph/thirdparty/gloffscreen/sdl.c',
]

def main():
    global DEST, FILES
    supplement = sys.argv[1:] == ['--supplement']
    assert sys.argv[1:] in ([], ['--supplement'])
    if supplement:
        DEST = DEST.with_name('retirement264-source002')
        FILES = ['ui/xui/main.cc', 'ui/xemu-thumbnail.cc',
                 'ui/xemu-snapshots.c', 'ui/xemu-snapshots.h']
    pins = json.loads(PINS.read_text(encoding='utf-8'))
    assert not DEST.exists(), 'Never overwrite a captured source closure'
    # Read and verify every source before creating the destination.
    rows = []
    for name in FILES:
        assert name in pins, name
        source = CAPSULE / name
        if source.exists():
            data = source.read_bytes()
            origin = str(source)
        else:
            data = subprocess.check_output(
                ['wsl', '-d', 'Ubuntu', '-u', 'root', '--', 'cat', WSL + '/' + name],
                timeout=30)
            origin = WSL + '/' + name
        digest = hashlib.sha256(data).hexdigest()
        assert digest == pins[name], (name, digest, pins[name])
        rows.append((name, data, origin, digest))
    for name, data, _, _ in rows:
        path = DEST / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    result = dict(schema=1, scope='source review only; no emulator or hardware launch',
                  source_pin_manifest=str(PINS),
                  source_pin_manifest_sha256=hashlib.sha256(PINS.read_bytes()).hexdigest(),
                  destination=str(DEST), files=[dict(path=n, origin=o, sha256=h,
                  bytes=len(d)) for n, d, o, h in rows])
    out = HERE / ('source-review002.json' if supplement else 'source-review.json')
    with out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps(dict(verified_files=len(rows), destination=str(DEST))))

if __name__ == '__main__':
    main()

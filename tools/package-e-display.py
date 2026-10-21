"""SPDX-License-Identifier: MIT
Package the pinned 480p/720p E selectors for private testing. No console access.
Existing output archives are never replaced; no Windows or game files are included.
"""
import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--launcher-480p', type=Path, required=True)
    parser.add_argument('--launcher-720p', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    policy = json.loads((ROOT / 'tools/e-display-policy.json').read_text(encoding='utf-8-sig'))
    entries = {}
    for mode, path in [('480p', args.launcher_480p), ('720p', args.launcher_720p)]:
        data = path.read_bytes()
        pin = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        if pin != policy['profiles'][mode]:
            raise ValueError('Launcher does not match policy: ' + mode)
        entries['resolution/' + mode + '/default.xbe'] = data
    for name in ['tools/configure-e-display.py', 'tools/e-display-policy.json',
                 'docs/display-configuration.md', 'docs/display-selector-recovery.md']:
        entries[name] = (ROOT / name).read_bytes()
    entries['README.txt'] = (
        'Experimental E boot-mode selector; original Conexant console only.\r\n'
        'Run on the PC with Python 3; do not FTP this entire archive to Xbox.\r\n'
        'Read docs/display-selector-recovery.md before changing anything.\r\n'
        '720p remains default/recovery. 480p is 720x480, not 640x480.\r\n'
        'Boot-time selection only; no Windows live switching or automatic detection.\r\n'
        'No Windows, game, firmware, credentials or prior receipts included.\r\n'
    ).encode('ascii')
    manifest = {name: {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                for name, data in entries.items()}
    entries['manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    # This is a small archive, with no WSL allocation or backing-volume growth.
    needed = 2 * sum(len(data) for data in entries.values())
    if shutil.disk_usage(args.output.parent).free - needed < 20 * 1024**3:
        raise ValueError('Projected output volume free space below 20 GiB')
    with zipfile.ZipFile(args.output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    with zipfile.ZipFile(args.output) as archive:
        if archive.namelist() != list(entries) or any(archive.read(n) != b for n, b in entries.items()):
            raise ValueError('Archive readback mismatch; preserve failed archive')
    print(json.dumps({'output': str(args.output), 'bytes': args.output.stat().st_size,
                      'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      'entries_verified': len(entries), 'physical_access': False}, indent=2))


if __name__ == '__main__':
    main()

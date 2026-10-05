"""Create a deterministic file-only native driver/loader overlay, never deploy it.

Requires an existing configured Windows installation. Not a full OS installer.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

DESTINATIONS = {
    'freeldr.sys': 'E/Applications/XWNFBoot/freeldr.sys',
    'rosload.exe': 'E/Applications/XWNFBoot/rosload.exe',
    'halxboxnt5.dll': 'E/Applications/XWNFBoot/loader/halxboxnt5.dll',
    'xboxbvid.dll': 'E/Applications/XWNFBoot/loader/xboxbvid.dll',
    'xwnfatx.sys': 'F/winnt/system32/drivers/xwnfatx.sys',
    'xboxvnt5.sys': 'F/winnt/system32/drivers/xboxvnt5.sys',
    'nvnetnt5.sys': 'F/winnt/system32/drivers/nvnetnt5.sys',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native-build', type=Path, required=True)
    p.add_argument('--launcher-build', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    native = json.loads((a.native_build / 'build-report.json').read_text())
    launcher = json.loads((a.launcher_build / 'build-report.json').read_text())
    if native['status'] != 'compiled' or launcher['status'] != 'compiled':
        raise RuntimeError('Both builds must have completed')
    # This is the physical framebuffer compatibility view required by 0.1.0.
    # Earlier fresh builds intentionally remain recorded, but are not packaged.
    cache = (a.native_build / 'boot-CMakeCache.txt').read_text()
    if 'XBOX_NT5_FRAMEBUFFER_ONLY_PCI:BOOL=ON' not in cache:
        raise RuntimeError('Missing physical framebuffer PCI compatibility flag')
    rows = {x['name']: x for x in native['artifacts']}
    if set(rows) != set(DESTINATIONS) or len(rows) != len(native['artifacts']):
        raise RuntimeError('Native artifact inventory mismatch')
    payloads = {}
    for name, dest in DESTINATIONS.items():
        data = (a.native_build / 'artifacts' / name).read_bytes()
        if sha(data) != rows[name]['sha256'] or len(data) != rows[name]['bytes']:
            raise RuntimeError('Artifact changed: ' + name)
        payloads[dest] = data
    row = launcher['artifact']
    if row['name'] != 'default.xbe':
        raise RuntimeError('Unexpected launcher name')
    data = (a.launcher_build / 'default.xbe').read_bytes()
    if sha(data) != row['sha256'] or len(data) != row['bytes']:
        raise RuntimeError('Launcher changed')
    payloads['E/Applications/XWNFBoot/default.xbe'] = data
    manifest = {'schema': 1, 'kind': 'native-component-overlay', 'runtime_qualified': False,
                'source_tree': native['verified_source_tree'], 'launcher_tree': launcher['patched_tree'],
                'prerequisites': ['Existing owned configured Windows installation and XWNFBoot config',
                                  'Validated partition mapping and preserved rollback files'],
                'excluded': ['Windows files and registry', 'Firmware', 'Dashboard', 'Startup scripts', 'User data'],
                'files': [{'path': n, 'bytes': len(b), 'sha256': sha(b)} for n, b in sorted(payloads.items())]}
    manifest_bytes = (json.dumps(manifest, indent=2) + '\n').encode()
    a.output.mkdir(parents=True, exist_ok=False)
    archive = a.output / 'native-overlay.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_STORED) as z:
        for name, data in sorted({**payloads, 'manifest.json': manifest_bytes}.items()):
            info = zipfile.ZipInfo(name, (2000, 1, 1, 0, 0, 0))
            info.create_system = 3; info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    with zipfile.ZipFile(archive) as z:
        for name, data in {**payloads, 'manifest.json': manifest_bytes}.items():
            if z.read(name) != data:
                raise RuntimeError('Archive readback mismatch')
    (a.output / 'manifest.json').write_bytes(manifest_bytes)
    report = {'archive_sha256': sha(archive.read_bytes()), 'archive_bytes': archive.stat().st_size,
              'payload_files': len(payloads), 'readback_verified': True,
              'runtime_qualified': False, 'deployed': False}
    (a.output / 'package-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()

"""Build the held non-HD E candidate from pinned private F and stock-E archives."""
import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import tester_bundle as bundle
from stock_e import Package

sha = lambda b: hashlib.sha256(b).hexdigest()
F = Path('E:/Codex-archive/xbox-windows-native/0.1.0/xwn-0.1.0-physical-system.zip')
E = Path('E:/xwn343/bundle002/stock-e-1080i-001.zip')
DEST = Path('D:/xwn844/xbox10-1024x576-f-001')
F_SHA = '279c55837192e21ec938760bd10164b194488500f38b3d063fa60c13fc1cc25b'
E_SHA = 'e79771fbf5eaf10c3e30e80e0d04e622dfd443448e24fa4eb76deac01d1b3e83'
OVERLAYS = {
    'E/Applications/XWNEBoot/default.xbe': ('D:/xwn-bundle844/nonhd004/default.xbe', 'ef7f88dfa0991e81e3629e61a67d79026cffc63320afdc2290c142be336e6b21'),
    'E/Applications/XWNEBoot/freeldr.sys': ('D:/xwn-bundle844/nonhd004/freeldr.sys', '45140ea525ea2301766eb53b5b04ffc9828985c6929a93a304a31d4ed0437a24'),
    'E/Applications/XWNEBoot/rosload.exe': ('D:/xwn-bundle844/nonhd004/rosload.exe', '2f505cb96178c2c4a85d220db9e8e42c84fc588c51b97ea824e909c21d3e81df'),
    'E/Applications/XWNEBoot/loader/xboxbvid.dll': ('outputs/native-windows-bootvid-framebuffer/artifacts/xboxbvid.dll', '2196f646653c4c944d73fee4944ee3d056c82cf01903e4f435e67d63c03ed4b7'),
    'E/winnt/system32/config/system': ('D:/xwn-bundle844/nonhd-f-hive001/system', '6bb380dfe3887b99c4b19e866d83189dfd54ec95307cde562e2ca3f8c73e6a20'),
    'E/winnt/system32/drivers/xboxvnt5.sys': ('D:/xwn844/video0093.sys', '3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf'),
    'E/winnt/system32/drivers/xwnfatx.sys': ('outputs/native-windows-fatx-forensics/artifacts/xwnfatx-retired-write.sys', '0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336'),
    'E/winnt/system32/xwn-video-trace.bin': ('D:/xwn-bundle844/nonhd-hive001/xwn-video-trace.bin', '5806fe7ce339298b5a94a0e0ab1bdfb78922fc449effd5cea2f393f0d33fd00e'),
}
RECORDS = {
    'F-to-E registry conversion': ('outputs/bundle-boot844/nonhd/f-hive001.json', '094709af0e534bee2110796f0855ea31e28fac3f8d1d19a052636a64ab8e15d4'),
    'F source readback': ('outputs/bundle-boot844/nonhd/emu-f-derived001.json', '8e1d6064060f161c8980d27441a4583affdec6c7d3b78f220407fed073fa3008'),
    'empty-directory preparation': ('outputs/bundle-boot844/nonhd/emu-f-complete001.json', '63f8039bef76d80409a4b86c02b0e78415fd97c5e9ed8da80f4782a5da4d5cee'),
    'emulator desktop input observation': ('outputs/bundle-boot844/nonhd/emu-run013.json', 'c082cb90e62170218ac79924c06cfdfdc9297b93e016698f938716b306eea863'),
}


def main():
    global DEST
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fatx843', action='store_true', help='Build a separate fixed843 driver successor')
    args = parser.parse_args()
    if args.fatx843:
        DEST = Path('D:/xwn844/xbox10-1024x576-f-002')
        OVERLAYS['E/winnt/system32/drivers/xwnfatx.sys'] = (
            'C:/xwn843/driver003/xwnfatx.sys', '3b2179ecec681cd91bc910a6178956d660f7bac18aa69bf6eafdb9f483a9af2c')
    assert not DEST.exists(), 'Use a fresh output destination'
    assert shutil.disk_usage(DEST.parent).free >= 23 * 1024**3
    assert sha(F.read_bytes()) == F_SHA
    pkg = Package(E, ROOT / 'tools/stock-e-profile.json')
    assert pkg.archive_sha256 == E_SHA
    blobs = {}
    for target, (path, expected) in OVERLAYS.items():
        bundle.safe_path(target, 'windows-e-preview')
        data = Path(path).read_bytes()
        assert sha(data) == expected, target
        blobs[target.casefold()] = data
    for path, expected in RECORDS.values():
        assert sha((ROOT / path).read_bytes()) == expected
    DEST.mkdir()
    stage = DEST / 'stage'
    stage.mkdir()
    prefixes = ('f/winnt/', 'f/documents and settings/', 'f/program files/')
    with zipfile.ZipFile(F) as z:
        names = z.namelist()
        assert len(names) == len(set(names))
        fm = json.loads(z.read('BUNDLE-MANIFEST.json'))
        directory_count = 0
        for info in z.infolist():
            if not info.filename.casefold().startswith(prefixes):
                continue
            relative = 'E/' + info.filename[2:].rstrip('/')
            if info.is_dir():
                bundle.safe_path(relative + '/.directory-placeholder', 'windows-e-preview')
                (stage / relative).mkdir(parents=True, exist_ok=True)
                directory_count += 1
                continue
            bundle.safe_path(relative, 'windows-e-preview')
            meta = fm['/' + info.filename]
            data = z.read(info)
            assert len(data) == meta['bytes'] and sha(data) == meta['sha256']
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blobs.pop(relative.casefold(), data))
        assert directory_count == 317, 'Captured F directory inventory changed'
    for name in pkg.files:
        if not name.casefold().startswith('/e/applications/xwneboot/'):
            continue
        rel = name.lstrip('/')
        target = stage / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blobs.pop(rel.casefold(), pkg.read(name)))
    assert not blobs, 'Some required overlays have no captured destination'
    host = stage / 'host'
    host.mkdir()
    for name in ('tester_bundle.py', 'fatx_names.py'):
        shutil.copyfile(ROOT / 'tools' / name, host / name)
    source = stage / 'source'
    source.mkdir()
    receipt = {'source_F_archive_sha256': F_SHA, 'source_E_support_archive_sha256': E_SHA,
               'f_directory_count': directory_count,
               'overlays': {k: h for k, (_, h) in OVERLAYS.items()},
               'evidence': {k: h for k, (_, h) in RECORDS.items()},
               'qualification': 'Held; populated-root regression, physical E boot, shutdown and persistence remain unqualified.'}
    (source / 'lineage.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    (stage / 'README.txt').write_text(
        'HELD - PRIVATE XBOX 1.0 1024x576 E TEST CANDIDATE\n\n'
        'Do not deploy until independent populated-root repeat testing is reviewed. This E-based\n'
        'composition has not been tested on physical hardware. One composite-cable\n'
        'emulator boot reached a 1024x576 desktop with Start and mouse movement; shutdown\n'
        'and persistence were not tested. Historical physical cable type is unknown.\n'
        'The loader requires 64 MiB, a responding Conexant encoder and EEPROM widescreen.\n'
        'Composite was emulated; S-video and SCART are unqualified. HDTV and VGA are refused.\n'
        'Keep Windows/profile data private. Verify the archive and its SHA-256 before use.\n'
        'When separately cleared, extract to a PC and copy the CONTENTS of E to dashboard E;\n'
        'copy E/Applications/XWNEBoot/default.xbe last, verify a full binary FTP readback,\n'
        'then launch that XBE from the dashboard. Back up target data before replacement.\n', encoding='utf-8')
    manifest = bundle.collect(stage, 'windows-e-preview', 'e-1024x576')
    plan = DEST / 'plan.json'
    plan.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    archive = DEST / (DEST.name + '.zip')
    digest = bundle.build(stage, plan, archive, private_windows=True)
    tree = bundle.verify_tree(archive, stage)
    (DEST / (archive.name + '.sha256')).write_text(digest + '  ' + archive.name + '\n', encoding='ascii')
    print(json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size,
                      'sha256': digest, 'files': len(manifest['files']), 'tree': tree}, indent=2))


if __name__ == '__main__':
    main()

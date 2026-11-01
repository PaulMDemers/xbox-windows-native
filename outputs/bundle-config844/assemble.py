#!/usr/bin/env python3
"""Assemble one private, pinned stock-E Windows profile; never connect or launch."""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from stock_e import Package
import tester_bundle as bundle


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('config', type=Path)
    ap.add_argument('destination', type=Path, help='new private directory on output volume')
    a = ap.parse_args()
    c = json.loads(a.config.read_text(encoding='utf-8'))
    assert set(c) == {'profile', 'title', 'history', 'source_archive', 'source_sha256', 'overlays', 'source_records'}
    assert c['profile'] in ('e-720p', 'e-1080i', 'e-720x480', 'e-640x480', 'e-1024x576')
    assert isinstance(c['history'], str) and c['history']
    dest = a.destination.resolve()
    assert not dest.exists(), 'Use a new private output directory'
    # Allow for a complete stage, ZIP, temporary host use, plus a 20 GiB reserve.
    free = shutil.disk_usage(dest.parent).free
    assert free >= 20 * 1024**3 + 3 * 1024**3, 'Insufficient projected free space'
    pkg = Package(c['source_archive'], ROOT / 'tools/stock-e-profile.json')
    assert pkg.archive_sha256 == c['source_sha256'] == 'e79771fbf5eaf10c3e30e80e0d04e622dfd443448e24fa4eb76deac01d1b3e83'
    assert c['source_records'], 'Source and build receipts required'
    for record in c['source_records']:
        assert set(record) == {'description', 'source', 'sha256'}
        assert record['description'] and sha(Path(record['source']).read_bytes()) == record['sha256']
    # Resolve and check every replacement before writing the stage.
    overlays = {}
    for row in c['overlays']:
        assert set(row) == {'target', 'source', 'sha256'}
        name = row['target']
        bundle.safe_path(name, 'windows-e-preview')
        assert name.startswith('E/') and name.casefold() not in overlays
        p = Path(row['source'])
        assert p.is_file() and not p.is_symlink()
        data = p.read_bytes()
        assert sha(data) == row['sha256'], name
        overlays[name.casefold()] = (name, data, row['sha256'])
    assert all(k.startswith(('e/applications/xwneboot/', 'e/xwndemo372/')) or k in
               ('e/winnt/system32/drivers/xwnfatx.sys', 'e/winnt/system32/drivers/xboxvnt5.sys',
                'e/winnt/system32/config/system', 'e/winnt/system32/xwn-video-trace.bin')
               for k in overlays), 'Unreviewed overlay target'
    dest.mkdir()
    stage = dest / 'stage'
    stage.mkdir()
    for directory in pkg.dirs:
        (stage / directory.lstrip('/')).mkdir(parents=True, exist_ok=True)
    for name in pkg.files:
        rel = name.lstrip('/')
        out = stage / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        replacement = overlays.pop(rel.casefold(), None)
        out.write_bytes(replacement[1] if replacement else pkg.read(name))
    for name, data, _ in overlays.values():
        out = stage / name
        out.parent.mkdir(parents=True, exist_ok=True)
        assert not out.exists()
        out.write_bytes(data)
    host = stage / 'host'
    host.mkdir()
    for name in ('tester_bundle.py', 'fatx_names.py'):
        shutil.copyfile(ROOT / 'tools' / name, host / name)
    source = stage / 'source'
    source.mkdir()
    receipt = {'source_archive_sha256': pkg.archive_sha256,
               'source_manifest_sha256': pkg.policy['manifest_sha256'],
               'profile': c['profile'], 'title': c['title'], 'history': c['history'],
               'source_records': [{'description': x['description'], 'sha256': x['sha256']} for x in c['source_records']],
               'overlays': [{'target': x['target'], 'sha256': x['sha256']} for x in c['overlays']],
               'limitation': 'File integrity and historical observations do not establish a new boot or hardware qualification.'}
    (source / 'lineage.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    (stage / 'README.txt').write_text(
        c['title'] + '\n\n' + c['history'] + '\n\n'
        'Private Windows installation: keep this archive private. Verify the ZIP hash and run\n'
        'python host/tester_bundle.py verify ARCHIVE.zip on a PC. Extract into a fresh folder.\n'
        'Back up target E. Have at least 1.25 GiB free. Stop if WINNT, Documents and Settings,\n'
        'Program Files, Applications/XWNEBoot or xwndemo372 already exist on E.\n'
        'Using binary FTP, copy the CONTENTS of the extracted E folder to dashboard E:\\.\n'
        'Copy E/Applications/XWNEBoot/default.xbe last, after the other files. Download\n'
        'a readback into a fresh readback/E folder and check before uploading the launcher:\n'
        'python host/tester_bundle.py verify-tree ARCHIVE.zip --root readback --console-only --defer-launcher\n'
        'Then upload and read back default.xbe and repeat without --defer-launcher.\n'
        'Launch E:\\Applications\\XWNEBoot\\default.xbe from the dashboard.\n'
        'Connect the mouse before boot. Test one console and one package at a time.\n'
        'The E folder is the complete installation; host and source stay on the PC.\n'
        'Changing to another package requires restoring/replacing its complete E installation.\n'
        'This newly assembled package has not been boot-tested.\n', encoding='utf-8')
    manifest = bundle.collect(stage, 'windows-e-preview', c['profile'])
    plan = dest / 'plan.json'
    plan.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    archive = dest / (dest.name + '.zip')
    archive_hash = bundle.build(stage, plan, archive, private_windows=True)
    verified = bundle.verify_tree(archive, stage)
    (dest / (archive.name + '.sha256')).write_text(archive_hash + '  ' + archive.name + '\n', encoding='ascii')
    print(json.dumps({'archive': str(archive), 'sha256': archive_hash,
                      'files': len(manifest['files']), 'tree': verified,
                      'free_before': free, 'reserve': 20 * 1024**3}, indent=2))


if __name__ == '__main__':
    main()

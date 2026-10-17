# SPDX-License-Identifier: MIT
"""Read-only source pins and host-result input verification; unique outputs."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

kit = Path(__file__).resolve().parent
root = kit.parent.parent
for name in ('source-review001.json', 'final-review.json'):
    if (kit / name).exists():
        raise SystemExit('Consumed review ID')
sources = {
    'src/drivers/fatx/drivers/filesystems/vfatfs/vfat.h': ['Filename[42]', 'unsigned long FileSize'],
    'src/drivers/fatx/drivers/filesystems/vfatfs/dirwr.c': ['FATXAddEntry(', 'FATXDelEntryLocked(', 'vfatRenameEntry('],
    'src/drivers/fatx/drivers/filesystems/vfatfs/fcb.c': ['vfatDirFindFile(', 'RtlEqualUnicodeString'],
    'src/drivers/fatx/drivers/filesystems/vfatfs/finfo.c': ['VfatSetRenameInformation(', 'VfatRenameChildFCB(', 'UpdateFileSize('],
    'src/boot/loader/boot/freeldr/freeldr/lib/fs/fs.c': ['NtfsMount,', 'FileData[MAX_FDS]'],
    'src/boot/loader/boot/freeldr/freeldr/lib/fs/ntfs.c': ['NtfsMount(ULONG DeviceId)', 'ArcRead(DeviceId'],
    'src/boot/loader/boot/freeldr/freeldr/disk/part_brfr.c': ['Store , E:', 'System, C:'],
    'src/boot/loader/boot/freeldr/freeldr/include/xwnvolume.h': ['Windows NOT entered.'],
    'docs/installation.md': ['six', 'Six'],
    'docs/recovery-guide.md': ['whole', 'restore'],
    'tools/install-stock-e.py': [],
    'tools/fatx_names.py': ['42'],
}
rows = []
for name, anchors in sources.items():
    raw = (root / name).read_bytes()
    lines = raw.decode('utf-8-sig').splitlines()
    found = {a: [i+1 for i, line in enumerate(lines) if a in line] for a in anchors}
    # Documentation anchors are alternatives because wording/capitalization varies.
    if anchors:
        assert any(found.values()) if name.startswith('docs/') else all(found.values()), name
    rows.append(dict(path=name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), anchors=found))

# Actual complete materialized upstream source. This is not an overlay glob.
code = '''from pathlib import Path
import subprocess,hashlib,json
r=Path("/home/paul/xbox-windows-native/release-readiness403-fatx001/source")
tree="dc942ab4b23df76a2015c466dc37f97699938772"
rows=[]
for name in ("direntry.c","dirwr.c","fcb.c","finfo.c","vfat.h"):
 p="drivers/filesystems/vfatfs/"+name
 b=(r/p).read_bytes()
 original=subprocess.check_output(["git","-C",str(r),"show",tree+":"+p])
 assert b==original,p
 rows.append(dict(path=p,sha256=hashlib.sha256(b).hexdigest(),recorded_tree_exact=True))
print(json.dumps(dict(tree=tree,files=rows)))
'''
upstream = json.loads(subprocess.check_output(['wsl', '-d', 'Ubuntu', '--',
                                              'python3', '-B', '-c', code], text=True))
for row in upstream['files']:
    public = root / 'src/drivers/fatx' / row['path']
    if public.exists():
        assert hashlib.sha256(public.read_bytes()).hexdigest() == row['sha256']
        row['public_overlay_exact'] = True
    else:
        assert row['path'].endswith('/direntry.c')
        row['public_overlay_exact'] = None
        row['note'] = 'Inherited full upstream file, absent from partial public overlay'
source_result = dict(public_sources=rows, actual403_fatx=upstream,
                     boot_overlay_scope='Current pinned source review, not a new compiled loader result')
with (kit / 'source-review001.json').open('x', encoding='utf-8', newline='\n') as f:
    f.write(json.dumps(source_result, indent=2) + '\n')
tests = [json.loads((kit / name).read_text()) for name in ('tests001.json', 'tests002.json')]
for test in tests:
    assert test['passed'] is True
    for name, sha in test['inputs'].items():
        assert hashlib.sha256((kit / name).read_bytes()).hexdigest() == sha
result = dict(utc=datetime.now(timezone.utc).isoformat(), passed=True,
              scope='Architecture/source review and synthetic host model only',
              source_files_pinned=len(rows), upstream_files_exact=len(upstream['files']),
              host_checks=tests[0]['total'] + tests[1]['checks'],
              native_build=False, guest_launch=False, physical_access=False,
              long_name_storage_implemented=False, strict_release_qualified=False,
              owned_running_sessions=[],
              inputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(kit.iterdir()) if p.is_file()})
with (kit / 'final-review.json').open('x', encoding='utf-8', newline='\n') as f:
    f.write(json.dumps(result, indent=2) + '\n')
print(json.dumps({k:v for k,v in result.items() if k != 'inputs'}))

"""Fresh corrected utility bundle; retain verified SDK source/notices from 417b."""
import hashlib
import json
import pathlib
import posixpath
import re
import shutil
import struct
import sys
import zipfile
K = pathlib.Path(__file__).resolve().parent
W = K.parents[1]
sys.path.insert(0, str(W / 'tools'))
import tester_bundle as bundle
sha = lambda data: hashlib.sha256(data).hexdigest()
stage = W / 'work/tester421-utilities001'
archive = pathlib.Path('E:/xwn421/xwn-utilities-preview-421.zip')
old = pathlib.Path('E:/xwn417/xwn-utilities-preview-417b.zip')
assert not stage.exists() and not archive.exists() and not (K / 'bundle001.json').exists()
assert shutil.disk_usage('C:/').free - 40 * 1024**2 >= 20 * 1024**3
assert shutil.disk_usage('E:/').free - 16 * 1024**2 >= 20 * 1024**3
assert sha(old.read_bytes()) == '070b8c5b54669c6b88a3459e785705aae7cae70873eb61a76d3621f87525792a'
previous = bundle.verify(old)
build = json.loads((K / 'build001.json').read_text())
physical = json.loads((K / 'physical-collection001.json').read_text())
assert build['compiled'] and build['sdk_unchanged'] and physical['completed']
assert physical['protected_unchanged'] and physical['report']['schema'] == 2
native = pathlib.Path(build['output'])
def put(name, data):
    p = stage / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
with zipfile.ZipFile(old) as z:
    identity = json.loads(z.read('source/build-identity.json'))
    assert identity['sdk_commit'] == build['sdk_head']
    assert identity['sdk_library_sha256'] == {n:h for n,h in build['sdk_before'].items() if n.endswith('.lib')}
    for d in previous['directories']: (stage / d).mkdir(parents=True, exist_ok=True)
    for row in previous['files']:
        name = row['path']
        if name.startswith(('source/nxdk/', 'licenses/')) or name == 'source/nxdk-submodules.txt':
            data = z.read(name); assert sha(data) == row['sha256']; put(name, data)
for name in ('main.c', 'Makefile', 'pci_probe.h'):
    data = (native / name).read_bytes(); assert sha(data) == build['sources'][name]
    assert data == (W / 'src/utilities/hardware-report' / name).read_bytes()
    put('source/hardware-report/' + name, data)
xbe = (native / 'bin/default.xbe').read_bytes()
assert sha(xbe) == 'f9163c73c3baa556c80138e122dbc81fe9aec77bd7ec3d951ec9fd9ad0778d5d'
assert xbe[:4] == b'XBEH'
base = struct.unpack_from('<I', xbe, 0x104)[0]
count = struct.unpack_from('<I', xbe, 0x11c)[0]
at = struct.unpack_from('<I', xbe, 0x120)[0] - base
sections = []
for i in range(count):
    flags, va, size, raw, n, name, refs, head, tail = struct.unpack_from('<9I', xbe, at + 56*i)
    assert raw + n <= len(xbe) and n <= size
    label = xbe[name-base:xbe.index(b'\0', name-base)].decode()
    sections.append(dict(name=label, bytes=n, sha256=sha(xbe[raw:raw+n])))
pe = (native / 'main.exe').read_bytes(); peoff = struct.unpack_from('<I', pe, 60)[0]
assert pe[peoff:peoff+4] == b'PE\0\0' and struct.unpack_from('<II', pe, peoff+24+96) == (0, 0)
put('E/Applications/XWNInfo/default.xbe', xbe)
for name in ('tester_bundle.py', 'hardware_report.py', 'fatx_names.py'):
    put('host/' + name, (W / 'tools' / name).read_bytes())
for name in ('testers.md', 'tester-bundles.md', 'tester-report-template.md', 'tester-rollout.md'):
    text = (W / 'docs' / name).read_text(encoding='utf-8-sig')
    def link(m):
        if '://' in m[2] or m[2].startswith('#'): return m[0]
        return '[' + m[1] + '](https://github.com/PaulMDemers/xbox-windows-native/blob/main/' + posixpath.normpath('docs/' + m[2]) + ')'
    put('docs/' + name, re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text).encode())
identity.update(tool='xwn-hardware-report-2', source_sha256=build['sources'],
    xbe_sha256=sha(xbe), xbe_bytes=len(xbe), sections=sections,
    evidence='421: emulator report/cold E allocation passed; one development-console report and dashboard FTP return. Other revisions unqualified.',
    pci_scan_policy='xbox-safe-v1',
    source_evidence='https://github.com/PaulMDemers/xbox-windows-native/tree/main/outputs/inventory-pci421')
put('source/build-identity.json', (json.dumps(identity, indent=2) + '\n').encode())
put('README.txt', b'''XWN utilities preview 421 -- corrected PCI scanner

Replaces 417/417b, which can hang on a hazardous Xbox PCI configuration query.
One physical development-console run saved its report and returned to dashboard
FTP. Kernel 1.0.4034.1 / 64 MiB / Conexant response. Other revisions unqualified.
The manifest conservatively retains experimental-not-hardware-qualified status;
that denotes no general hardware qualification, not an absence of this one test.

1. Read docs/testers.md and docs/tester-report-template.md.
2. Verify: python host/tester_bundle.py verify PATH_TO_ZIP
   Compare the outer SHA-256 with the maintainer's separately supplied checksum.
3. FTP only E/Applications/XWNInfo to Xbox E:\\Applications\\XWNInfo.
   Do not overwrite an existing folder. Preserve an older kit before replacing it.
   Leave Xbox C and unrelated Apps alone. Keep source/docs/licenses on your PC.
4. Use UnleashX File Explorer: E:\\Applications\\XWNInfo\\default.xbe
5. After its automatic dashboard return, retrieve E:\\xwn-report-00.json
   (or the next unused number). Allow up to a minute; do not loop failed boots.
6. Check: python host/hardware_report.py xwn-report-00.json
   Send the JSON and completed tester report. Schema must be 2.

PCI entries are raw responses, not independent physical-device counts. Known
hazardous locations and GPU device aliases are explicitly left unprobed.
No Windows payload, firmware, EEPROM contents, keys or private recovery included.
This utility does not install or boot Windows. No flashing or partitioning.
''')
manifest = bundle.collect(stage, 'utilities')
plan = K / 'utilities-plan001.json'; assert not plan.exists()
plan.write_text(json.dumps(manifest, indent=2) + '\n')
h = bundle.build(stage, plan, archive)
tree = bundle.verify_tree(archive, stage)
(archive.parent / (archive.name + '.sha256')).write_text(h + '  ' + archive.name + '\n')
r = dict(archive=str(archive), sha256=h, bytes=archive.stat().st_size,
    files=len(manifest['files']), directories=len(manifest['directories']),
    xbe_sha256=sha(xbe), inherited_sdk_archive_sha256=sha(old.read_bytes()),
    readback_verified=True, tree_check=tree, windows_included=False, public_upload=False,
    physical_scope='One development console; no general revision qualification')
(K / 'bundle001.json').write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps(r, indent=2))

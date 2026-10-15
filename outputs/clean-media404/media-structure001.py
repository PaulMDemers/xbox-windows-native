"""Read supplied ISO structures and test complete cabinet decompression privately."""
import hashlib, io, json, subprocess, sys
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
sys.path.insert(0, str(W / 'work/python-packages'))
import pycdlib, pefile
P = Path('/mnt/c/xwn404/media-structure001')
P.mkdir(exist_ok=False)
seven = '/home/paul/xbox-windows-native/toolchains/7zip/root/usr/lib/7zip/7z'
sha = lambda b: hashlib.sha256(b).hexdigest()
rows = []
for media in json.loads((K / 'media-inventory001.json').read_text()):
    source = W / 'outputs' / media['filename']
    with source.open('rb') as f:
        assert hashlib.file_digest(f, 'sha256').hexdigest() == media['sha256']
    out = P / media['id']; out.mkdir()
    iso = pycdlib.PyCdlib(); iso.open(str(source))
    inventory = []; archives = []; kernel = None
    for dirname, dirs, names in iso.walk(iso_path='/'):
        for name in names:
            path = dirname.rstrip('/') + '/' + name
            b = io.BytesIO(); iso.get_file_from_iso_fp(b, iso_path=path); data = b.getvalue()
            inventory.append(dict(path=path, bytes=len(data), sha256=sha(data)))
            if path.upper().split(';')[0] in ['/I386/NTOSKRNL.EX_', '/I386/NTOSKRNL.EXE', '/I386/DRIVER.CAB', '/I386/SP4.CAB']:
                dest = out / name.split(';')[0]; dest.write_bytes(data)
                if dest.name.upper().endswith(('.CAB', '.EX_')):
                    with (out / (dest.name + '.test.log')).open('xb') as log:
                        result = subprocess.run([seven, 't', str(dest)], stdout=log, stderr=subprocess.STDOUT)
                    archives.append(dict(name=dest.name, sha256=sha(data), complete_decompression_passed=result.returncode == 0))
                    assert result.returncode == 0
                if dest.name.upper().startswith('NTOSKRNL'):
                    if dest.suffix.upper() == '.EX_':
                        with (out / 'kernel-extract.log').open('xb') as log:
                            subprocess.run([seven, 'x', '-y', '-o' + str(out / 'kernel'), str(dest)], check=True, stdout=log, stderr=subprocess.STDOUT)
                        candidates = [p for p in (out / 'kernel').rglob('*') if p.is_file()]
                        assert len(candidates) == 1
                        dest = candidates[0]
                    pe = pefile.PE(str(dest)); v = pe.VS_FIXEDFILEINFO[0]
                    kernel = dict(version='.'.join(map(str, [v.FileVersionMS >> 16, v.FileVersionMS & 65535,
                        v.FileVersionLS >> 16, v.FileVersionLS & 65535])), sha256=sha(dest.read_bytes()))
                    pe.close()
    inv = out / 'iso-files.json'; inv.write_text(json.dumps(inventory, indent=2) + '\n')
    rows.append(dict(id=media['id'], iso_sha256=media['sha256'], iso_files=len(inventory),
                     file_bytes_read=sum(r['bytes'] for r in inventory),
                     private_file_inventory=str(inv), file_inventory_sha256=sha(inv.read_bytes()),
                     volume_id=iso.pvd.volume_identifier.decode('ascii').strip(),
                     el_torito_present=iso.eltorito_boot_catalog is not None,
                     archives=archives, kernel=kernel,
                     scope='All ISO file bytes read; selected complete cabinets decompressed. Not all compressed-file members or setup executed.'))
    iso.close()
(K / 'media-structure001.json').write_text(json.dumps(rows, indent=2) + '\n')
probe = Path('/home/paul/xbox-windows-native/clean-media404-build002/PROBE.EXE')
pe = pefile.PE(str(probe))
imports = {e.dll.decode(): [v.name.decode() if v.name else '#' + str(v.ordinal) for v in e.imports] for e in pe.DIRECTORY_ENTRY_IMPORT}
assert {n.lower() for n in imports} == {'kernel32.dll', 'user32.dll', 'advapi32.dll'}
assert pe.FILE_HEADER.Machine == 0x14c and pe.OPTIONAL_HEADER.MajorSubsystemVersion == 5
(K / 'probe-review001.json').write_text(json.dumps(dict(binary_sha256=sha(probe.read_bytes()), imports=imports,
    subsystem=[pe.OPTIONAL_HEADER.MajorSubsystemVersion, pe.OPTIONAL_HEADER.MinorSubsystemVersion],
    source_review='Only witness/copy/RunOnce/shutdown; no device, network, media or Windows licensing modifications'), indent=2) + '\n')
print(json.dumps(rows))

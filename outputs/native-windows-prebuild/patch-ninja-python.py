"""Patch the private RosBE Ninja archive for Python 3.13+; retain provenance."""
import difflib
import hashlib
import io
import json
from pathlib import Path
import tarfile

root = Path('/home/paul/xbox-windows-native/toolchain-source/RosBE-Unix-2.2.1/sources')
archive = root / 'ninja.tar.bz2'
original = root / 'ninja.original.tar.bz2'
kit = Path(__file__).resolve().parent
if original.exists():
    provenance = json.loads((kit / 'ninja-archive-provenance.json').read_text())
    assert hashlib.sha256(original.read_bytes()).hexdigest() == provenance['original_sha256']
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == provenance['patched_sha256']
    raise SystemExit(0)
data = archive.read_bytes()
original.write_bytes(data)
temporary = root / 'ninja.patched.tar.bz2'
with tarfile.open(original, 'r:bz2') as src, tarfile.open(temporary, 'w:bz2') as dst:
    for member in src.getmembers():
        payload = src.extractfile(member).read() if member.isfile() else None
        if member.name == 'ninja/configure.py':
            before = payload.decode()
            assert 'import pipes' in before and 'pipes.quote' in before
            after = before.replace('import pipes', 'import shlex').replace('pipes.quote', 'shlex.quote')
            payload = after.encode()
            member.size = len(payload)
        dst.addfile(member, io.BytesIO(payload) if payload is not None else None)
(kit / 'patches/0004-ninja-python-shlex.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='a/ninja/configure.py', tofile='b/ninja/configure.py')))
temporary.replace(archive)
(kit / 'ninja-archive-provenance.json').write_text(json.dumps({
    'reason': 'Python 3.13 removed pipes; shlex.quote provides equivalent shell quoting.',
    'original_sha256': hashlib.sha256(data).hexdigest(),
    'patched_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
}, indent=2) + '\n')

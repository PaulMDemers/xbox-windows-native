"""SPDX-License-Identifier: MIT
Verify all manifest bytes and reject added files. This is not signature verification.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify(root=ROOT):
    root=Path(root).resolve()
    entries=json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))['files']
    names=[r['path'] for r in entries]
    if len(names)!=len(set(names)): raise ValueError('Duplicate manifest path')
    paths=list(root.rglob('*'))
    if any(p.is_symlink() for p in paths): raise ValueError('Symlinks are not package files')
    actual={p.relative_to(root).as_posix() for p in paths if p.is_file()}
    if actual != set(names)|{'MANIFEST.json'}: raise ValueError('Missing or additional file')
    for row in entries:
        path=(root/row['path']).resolve(strict=True)
        if not path.is_relative_to(root) or path.is_symlink(): raise ValueError('Unsafe path')
        data=path.read_bytes()
        if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:
            raise ValueError('Digest mismatch: '+row['path'])
    return {'verified_files':len(entries),'scope':'Manifest integrity only; no origin signature or license clearance'}


if __name__ == '__main__': print(json.dumps(verify(),indent=2))

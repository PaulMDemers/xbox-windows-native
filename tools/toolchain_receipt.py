# SPDX-License-Identifier: MIT
"""Inventory locally bootstrapped tools; a receipt is evidence, not a signature."""
import hashlib
import json
from pathlib import Path


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def inventory(prefix):
    prefix = Path(prefix).resolve()
    result = {}
    for p in sorted(prefix.rglob('*')):
        relative = p.relative_to(prefix).as_posix()
        if p.is_symlink():
            if not p.resolve().is_relative_to(prefix) or not p.exists():
                raise ValueError('External/broken toolchain link: ' + relative)
            result[relative] = {'link': str(p.readlink())}
        elif p.is_file():
            result[relative] = {'sha256': sha(p), 'mode': p.stat().st_mode & 0o777}
        elif not p.is_dir():
            raise ValueError('Unsupported toolchain entry: ' + relative)
    if not result:
        raise ValueError('Empty toolchain')
    return result


def validate_bootstrap(record, lock):
    if (record.get('status') != 'compiled' or
        record.get('archive_sha256') != lock['archives']['rosbe']['sha256'] or
        record.get('ninja_sha256') != lock['ninja_compatibility']['patched_sha256']):
        raise ValueError('Incomplete/unrecognized RosBE bootstrap')


def create(bootstrap, output, lock):
    bootstrap = Path(bootstrap).resolve()
    record = json.loads(bootstrap.read_text())
    validate_bootstrap(record, lock)
    prefix = bootstrap.parent / 'RosBE-2.2.1'
    entries = inventory(prefix)
    for name, expected in record['tool_sha256'].items():
        if sha(prefix / name) != expected:
            raise ValueError('Bootstrap tool changed: ' + name)
    result = {'schema': 1, 'bootstrap': record, 'bootstrap_sha256': sha(bootstrap),
              'files': entries, 'scope': 'Locally compiled toolchain; not historical binary identity'}
    with Path(output).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    return result


def verify(prefix, receipt, lock):
    record = json.loads(Path(receipt).read_text())
    if record.get('schema') != 1:
        raise ValueError('Unknown toolchain receipt')
    validate_bootstrap(record['bootstrap'], lock)
    if inventory(prefix) != record['files']:
        raise ValueError('Toolchain differs from the complete local receipt')
    return {'receipt_sha256': sha(receipt), 'files': len(record['files']),
            'scope': record['scope']}


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bootstrap', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    lock = json.loads((Path(__file__).resolve().parents[1] / 'upstream/dependencies.json').read_text())
    print(json.dumps({'files': len(create(a.bootstrap, a.output, lock)['files'])}))

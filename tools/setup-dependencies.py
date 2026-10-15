#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fetch pinned public sources and bootstrap RosBE in a new private directory."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def anonymous_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_CONFIG_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null',
               GIT_TERMINAL_PROMPT='0', GIT_ASKPASS='/bin/false')
    return env


def extract(archive, output):
    with tarfile.open(archive) as tf:
        # data filter rejects paths escaping the new root, devices and unsafe links.
        if not hasattr(tarfile, 'data_filter'):
            raise RuntimeError('Python with tarfile.data_filter is required (3.12+ recommended)')
        tf.extractall(output, filter='data')


def fetch(lock, output):
    output.mkdir(parents=True, exist_ok=False)
    record = {'sources': {}, 'archives': {}, 'anonymous': True}
    for name, row in lock['sources'].items():
        dest = output / name
        subprocess.run(['git', 'init', '--bare', '-q', str(dest)], check=True, env=anonymous_env())
        with (output / (name + '.log')).open('w') as log:
            subprocess.run(['git', '-c', 'credential.helper=', '-c', 'http.extraHeader=',
                            '-c', 'core.askPass=', '-C', str(dest), 'fetch', '--depth=1',
                            row['url'], row['commit']], env=anonymous_env(), stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=600)
        actual = subprocess.check_output(['git', '-C', str(dest), 'rev-parse', 'FETCH_HEAD'],
                                         env=anonymous_env(), text=True).strip()
        if actual != row['commit']:
            raise RuntimeError('Source commit mismatch: ' + name)
        record['sources'][name] = dict(row, resolved_commit=actual)
    for name, row in lock['archives'].items():
        dest = output / row['filename']
        count = 0
        with urllib.request.urlopen(row['url'], timeout=60) as remote, dest.open('xb') as f:
            if not remote.url.startswith('https://'):
                raise RuntimeError('Non-HTTPS redirect refused')
            while b := remote.read(1024 * 1024):
                count += len(b)
                if count > row['maximum_bytes']:
                    raise RuntimeError('Archive size bound exceeded')
                f.write(b)
        if sha(dest) != row['sha256']:
            raise RuntimeError('Archive hash mismatch: ' + name)
        record['archives'][name] = dict(row, bytes=count)
    (output / 'fetch.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


def bootstrap(lock, archive, output):
    if sha(archive) != lock['archives']['rosbe']['sha256']:
        raise RuntimeError('RosBE archive hash mismatch')
    from build_space import require_space
    space = require_space(output)
    for tool in ['as', 'bzip2', 'find', 'gcc', 'g++', 'grep', 'm4', 'makeinfo', 'python', 'tar', 'make', 'pkg-config', 'taskset']:
        if not shutil.which(tool):
            raise RuntimeError('Missing host prerequisite: ' + tool)
    subprocess.run(['pkg-config', '--exists', 'zlib'], check=True)
    output.mkdir(parents=True, exist_ok=False)
    extract(archive, output / 'source')
    source = output / 'source/RosBE-Unix-2.2.1'
    ninja = source / 'sources/ninja.tar.bz2'
    if sha(ninja) != lock['ninja_compatibility']['original_sha256']:
        raise RuntimeError('Unexpected embedded Ninja archive')
    original = ninja.with_name('ninja.original.tar.bz2')
    ninja.rename(original)
    changed = 0
    with tarfile.open(original, 'r:bz2') as src, tarfile.open(ninja, 'w:bz2') as dst:
        for member in src.getmembers():
            b = src.extractfile(member).read() if member.isfile() else None
            if member.name == 'ninja/configure.py':
                if b'import pipes' not in b or b'pipes.quote' not in b:
                    raise RuntimeError('Unexpected Ninja compatibility site')
                b = b.replace(b'import pipes', b'import shlex').replace(b'pipes.quote', b'shlex.quote')
                member.size = len(b)
                changed += 1
            dst.addfile(member, io.BytesIO(b) if b is not None else None)
    if changed != 1 or sha(ninja) != lock['ninja_compatibility']['patched_sha256']:
        raise RuntimeError('Ninja compatibility result mismatch')
    cpus = ','.join(str(n) for n in sorted(os.sched_getaffinity(0))[:4])
    prefix = output / 'RosBE-2.2.1'
    command = ['taskset', '-c', cpus, 'bash', str(source / 'RosBE-Builder.sh'), str(prefix)]
    record = {'archive_sha256': sha(archive), 'ninja_sha256': sha(ninja), 'space': space,
              'command': command, 'host_tools': {n: shutil.which(n) for n in ['gcc', 'g++', 'makeinfo', 'python']},
              'status': 'started'}
    receipt = output / 'bootstrap.json'
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    try:
        with (output / 'bootstrap.log').open('w') as log:
            subprocess.run(command, input='yes\n', text=True, stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=7200)
        record['tool_sha256'] = {name: sha(prefix / name) for name in
                                ['RosBE.sh', 'bin/cmake', 'bin/ninja', 'i386/bin/i686-w64-mingw32-gcc']}
        record['status'] = 'compiled'
    except Exception as e:
        record.update(status='failed', error=str(e))
        raise
    finally:
        receipt.write_text(json.dumps(record, indent=2) + '\n')
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['fetch', 'bootstrap'])
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--archive', type=Path)
    a = p.parse_args()
    output = a.output.resolve()
    if output.exists() or output.is_relative_to(ROOT):
        p.error('Choose a fresh output outside the repository')
    lock = json.loads((ROOT / 'upstream/dependencies.json').read_text())
    if a.action == 'bootstrap' and (not a.archive or os.name != 'posix'):
        p.error('bootstrap requires Linux/WSL and --archive')
    result = fetch(lock, output) if a.action == 'fetch' else bootstrap(lock, a.archive.resolve(), output)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

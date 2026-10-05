"""Build the physical-F Cromwell launcher in a fresh owned Linux checkout."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from build_space import require_space

ROOT = Path(__file__).resolve().parent.parent
BASE = '9fc54d0c7cbed7bc3c70373642d833684853011f'
PATCHES = {
    'outputs/native-windows-physical-loader/cromwell-base.patch': '69964e0a5f5557881486b4668ddd2e940ecbf1cc26110e1960366ca7ecf5e12e',
    'outputs/native-windows-physical-f/cromwell-f-launcher.patch': '1a47d42c371540549a8fb1f4de40404ca8436e4ad35f1e2c8236f82bc367fbb2',
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-cache', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--cc', default='/usr/bin/gcc-12', type=Path)
    a = p.parse_args()
    if sys.platform != 'linux' or os.environ.get('XWN_BUILD_LEASE') != 'held':
        p.error('Linux and the project build lease are required')
    for name, expected in PATCHES.items():
        if sha(ROOT / name) != expected:
            raise RuntimeError('Patch changed: ' + name)
    cache = a.source_cache.resolve(strict=True)
    cc = a.cc.resolve(strict=True)
    out = a.output.resolve()
    if out.is_relative_to(cache):
        raise RuntimeError('Output must be separate from source cache')
    space = require_space(out, minimum_gib=2)
    out.mkdir(parents=True, exist_ok=False)
    report = {'status': 'started', 'space_preflight': space, 'base_commit': BASE, 'patch_sha256': PATCHES,
              'compiler_sha256': sha(cc), 'commands': [],
              'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'Fresh launcher compilation only; no physical or emulator qualification'}
    try:
        with (out / 'build.log').open('w') as log:
            src = out / 'source'
            def run(argv, **kw):
                report['commands'].append([str(x) for x in argv])
                subprocess.run(argv, stdout=log, stderr=log, check=True, **kw)
            run(['git', 'init', '-q', str(src)])
            run(['git', '-C', str(src), 'fetch', '--depth=1', str(cache), BASE])
            run(['git', '-C', str(src), 'checkout', '--detach', 'FETCH_HEAD'])
            for name in PATCHES:
                run(['git', '-C', str(src), 'apply', '--index', str(ROOT / name)])
            report['patched_tree'] = subprocess.check_output(['git', '-C', str(src), 'write-tree'], text=True).strip()
            hosttools = out / 'host-tools'; hosttools.mkdir()
            (hosttools / 'gcc').symlink_to(cc)
            env = dict(os.environ, PATH=str(hosttools) + ':' + os.environ['PATH'])
            run(['make', 'all', 'CC=' + str(cc), 'GITREV=9fc54d0-xwn-fboot',
                 'EXTRA_CROM_CFLAGS=-DXWN_PHYSICAL_PREFLIGHT'], cwd=src, env=env)
            artifact = out / 'default.xbe'
            shutil.copyfile(src / 'xbe/xromwell.xbe', artifact)
            report['artifact'] = {'name': artifact.name, 'sha256': sha(artifact), 'bytes': artifact.stat().st_size}
            report['status'] = 'compiled'
    except Exception as exc:
        report.update(status='failed', error=str(exc))
        raise
    finally:
        report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'status': report['status'], 'report': str(out / 'build-report.json')}))


if __name__ == '__main__':
    main()

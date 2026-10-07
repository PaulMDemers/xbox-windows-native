"""Reconstruct selected open-source NT5 components in a fresh Linux directory.

No firmware/media download, packaging of Windows, deployment or guest launch.
Run under the host's build lease. A failed attempt is retained, never reused.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
from build_space import require_space

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-cache', type=Path, required=True)
    p.add_argument('--rosbe', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--profile', choices=['fatx', 'boot', 'video', 'support', 'all'], default='all')
    p.add_argument('--jobs', type=int, default=4)
    a = p.parse_args()
    if sys.platform != 'linux' or os.environ.get('XWN_BUILD_LEASE') != 'held':
        p.error('Run on Linux/WSL under the project build lease (XWN_BUILD_LEASE=held)')
    if not 1 <= a.jobs <= 32:
        p.error('--jobs must be between 1 and 32')
    lock_path = ROOT / 'outputs/fatx-dump-map/control-inputs.json'
    lock = json.loads(lock_path.read_text())
    for name, expected in lock['patch_sha256'].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or digest(path) != expected:
            raise RuntimeError('Patch input mismatch: ' + name)
    for name, expected in lock['tool_sha256'].items():
        if digest(a.rosbe / name) != expected:
            raise RuntimeError('Tool input mismatch: ' + name)
    manifest = ROOT / lock['manifest']
    # JSON metadata must survive LF/CRLF checkout differences. Patch bytes remain
    # exact (the repository deliberately marks patches as non-text).
    manifest_data = json.loads(manifest.read_text())
    manifest_hash = hashlib.sha256(json.dumps(manifest_data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if manifest_hash != lock['manifest_json_sha256']:
        raise RuntimeError('Manifest changed')
    cache = a.source_cache.resolve(strict=True)
    rosbe = a.rosbe.resolve(strict=True)
    out = a.output.resolve()
    if out.is_relative_to(cache) or out.is_relative_to(rosbe):
        raise RuntimeError('Output must not be inside a source cache or toolchain')
    space = require_space(out)
    out.mkdir(parents=True, exist_ok=False)
    report = {'status': 'started', 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'profile': a.profile, 'space_preflight': space, 'source_base': lock['base_commit'],
              'source_tree': lock['result_tree'], 'inputs_sha256': digest(lock_path),
              'tool_sha256': lock['tool_sha256'], 'commands': [], 'artifacts': [],
              'scope': 'fresh source and compilation only; no runtime qualification'}

    def run(argv, **kwargs):
        report['commands'].append([str(x) for x in argv])
        subprocess.run(argv, check=True, **kwargs)

    try:
        with (out / 'build.log').open('w') as log:
            src = out / 'source'
            # Fetch objects into an independent repo; no worktree, hardlinks or alternates.
            run(['git', 'init', '-q', str(src)], stdout=log, stderr=log)
            run(['git', '-C', str(src), 'fetch', '--depth=1', str(cache), lock['base_commit']], stdout=log, stderr=log)
            run(['git', '-C', str(src), 'checkout', '--detach', 'FETCH_HEAD'], stdout=log, stderr=log)
            run([sys.executable, str(ROOT / 'tools/apply-series.py'), '--source', str(src),
                 '--manifest', str(manifest)], stdout=log, stderr=log)
            tree = subprocess.check_output(['git', '-C', str(src), 'write-tree'], text=True).strip()
            if tree != lock['result_tree']:
                raise RuntimeError('Reconstructed tree mismatch')
            report['verified_source_tree'] = tree
            artifacts = out / 'artifacts'
            artifacts.mkdir()
            for name, profile in lock['profiles'].items():
                if a.profile not in ('all', name):
                    continue
                print('Building ' + name, flush=True)
                build = out / ('build-' + name)
                configure = ['cmake', '-S', str(src), '-B', str(build), '-G', 'Ninja',
                             '-DCMAKE_TOOLCHAIN_FILE=' + str(src / 'toolchain-gcc.cmake')]
                configure += ['-D' + key + '=' + value for key, value in profile['definitions'].items()]
                compile_command = ['cmake', '--build', str(build), '--target', *profile['targets'], '--', '-j' + str(a.jobs)]
                # Quoted shell commands feed RosBE; fail-fast prevents configure failure
                # being masked by its interactive shell reaching EOF successfully.
                script = 'set -e\n' + shlex.join(configure) + '\n' + shlex.join(compile_command) + '\n'
                (out / (name + '-commands.sh')).write_text(script)
                run([str(rosbe / 'RosBE.sh'), str(src), '0', 'i386'], input=script,
                    text=True, stdout=log, stderr=log)
                for rel, filename in profile['artifacts'].items():
                    source_file = build / rel
                    target = artifacts / filename
                    shutil.copyfile(source_file, target)
                    report['artifacts'].append({'name': filename, 'bytes': target.stat().st_size,
                                                'sha256': digest(target), 'profile': name})
                shutil.copyfile(build / 'CMakeCache.txt', out / (name + '-CMakeCache.txt'))
        report['status'] = 'compiled'
    except Exception as exc:
        report['status'] = 'failed'
        report['error'] = str(exc)
        raise
    finally:
        report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (out / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'status': report['status'], 'report': str(out / 'build-report.json')}), flush=True)


if __name__ == '__main__':
    main()

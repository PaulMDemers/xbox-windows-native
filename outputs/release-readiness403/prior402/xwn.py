#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Materialize and build the reviewed component profiles without touching a console."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'upstream/components.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(argv, **kwargs):
    return subprocess.check_output([str(x) for x in argv], **kwargs).decode().strip()


def child(root, name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
        raise ValueError('Unsafe relative path: ' + name)
    target = root.joinpath(*p.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('Path escapes root: ' + name)
    return target


def fresh(path, protected):
    path = Path(path).resolve()
    if path.exists():
        raise ValueError('Output already exists; choose a fresh directory: ' + str(path))
    for anchor in protected:
        if path.is_relative_to(Path(anchor).resolve()):
            raise ValueError('Output must be outside repository/cache/toolchain: ' + str(path))
    return path


def verify(profile, allow_modified=False):
    overlay = child(ROOT, profile['overlay'])
    expected = set()
    changed = []
    for entry in profile['files']:
        p = child(overlay, entry['path'])
        if entry['action'] == 'write':
            expected.add(p)
            if entry['mode'] not in ('100644', '100755') or not p.is_file() or p.is_symlink():
                raise ValueError('Missing/unsupported source: ' + str(p))
            if digest(p) != entry['sha256']:
                changed.append(entry['path'])
        elif entry['action'] != 'delete':
            raise ValueError('Unknown source action')
    extra = {p for p in overlay.rglob('*') if p.is_file()} - expected
    if extra:
        raise ValueError('Unlisted overlay files; update manifest: ' + str(sorted(extra)))
    if changed and not allow_modified:
        raise ValueError('Changed source; use --allow-modified for development: ' + str(changed))
    return changed


def materialize(profile, cache, output, allow_modified=False):
    changed = verify(profile, allow_modified)
    cache = Path(cache).resolve()
    output = fresh(output, [ROOT, cache])
    base = profile['base_commit']
    if run(['git', '-C', cache, 'rev-parse', base + '^{commit}']) != base:
        raise ValueError('Upstream commit unavailable')
    objects = Path(run(['git', '-C', cache, 'rev-parse', '--path-format=absolute', '--git-path', 'objects']))
    if '\n' in str(objects):
        raise ValueError('Unsupported cache path')
    output.mkdir(parents=True)
    source = output / 'source'
    subprocess.run(['git', 'init', '-q', str(source)], check=True)
    (source / '.git/objects/info/alternates').write_text(str(objects) + '\n')
    for key, value in [('core.autocrlf', 'false'), ('core.filemode', 'true')]:
        subprocess.run(['git', '-C', str(source), 'config', key, value], check=True)
    subprocess.run(['git', '-C', str(source), 'checkout', '-q', '--detach', base], check=True)
    overlay = child(ROOT, profile['overlay'])
    for entry in profile['files']:
        target = child(source, entry['path'])
        if entry['action'] == 'delete':
            if not target.is_file():
                raise ValueError('Deletion does not match upstream: ' + entry['path'])
            target.unlink()
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(child(overlay, entry['path']).read_bytes())
            target.chmod(0o755 if entry['mode'] == '100755' else 0o644)
    subprocess.run(['git', '-C', str(source), 'add', '-A'], check=True)
    tree = run(['git', '-C', source, 'write-tree'])
    if not changed and tree != profile['reference_tree']:
        raise ValueError('Reconstructed tree differs: ' + tree)
    # Materialize upstream checkout attributes, including the recorded CRLF INF.
    subprocess.run(['git', '-C', str(source), 'checkout-index', '-a', '-f'], check=True)
    for rule in profile.get('checkout_byte_rules', []):
        if rule['path'] not in changed and digest(child(source, rule['path'])) != rule['checked_out_sha256']:
            raise ValueError('Checkout-byte mismatch: ' + rule['path'])
    record = {'profile': profile['name'], 'base': base, 'tree': tree,
              'reference_match': tree == profile['reference_tree'], 'changed_sources': changed,
              'cache_dependency': str(objects), 'build_performed': False}
    (output / 'source.json').write_text(json.dumps(record, indent=2) + '\n')
    return source, record


def build(profile, source, output, rosbe, gcc12, manifest, jobs):
    from build_space import require_space
    space = require_space(output)
    env = os.environ.copy()
    builddir = output / 'build'
    pins = {}
    if profile['upstream'] == 'reactos':
        rosbe = Path(rosbe).resolve()
        for name, expected in manifest['rosbe_tool_pins'].items():
            actual = digest(child(rosbe, name))
            if actual != expected:
                raise ValueError('Toolchain identity mismatch: ' + name)
            pins[name] = actual
        cmake = rosbe / 'bin/cmake'
        configure = [str(cmake), '-S', str(source), '-B', str(builddir), '-G', 'Ninja',
                     '-DCMAKE_TOOLCHAIN_FILE=' + str(source / 'toolchain-gcc.cmake')]
        configure += ['-D' + key + '=' + str(value) for key, value in profile['build']['definitions'].items()]
        compile_cmd = [str(cmake), '--build', str(builddir), '--target'] + profile['build']['targets'] + ['--', '-j' + str(jobs)]
        command = [str(rosbe / 'RosBE.sh'), str(source), '0', 'i386']
        stdin = 'set -e\n' + shlex.join(configure) + '\n' + shlex.join(compile_cmd) + '\n'
    else:
        gcc12 = Path(gcc12).resolve()
        actual = digest(gcc12)
        if actual != profile['build']['compiler_sha256']:
            raise ValueError('GCC 12 identity mismatch')
        pins['gcc12'] = actual
        hostbin = output / 'host-bin'
        hostbin.mkdir()
        (hostbin / 'gcc').symlink_to(gcc12)
        env['PATH'] = str(hostbin) + os.pathsep + env['PATH']
        command = ['make', profile['build']['make_target'], 'CC=' + str(gcc12),
                   'GITREV=9fc54d0-xwn-eboot', 'EXTRA_CROM_CFLAGS=' + profile['build']['flags'],
                   'LDFLAGS-ROM=-s -S -T ' + str(source / 'scripts/ldscript-crom.ld') + ' -Map=' + str(output / 'image-crom.map')]
        stdin = None
        builddir = source
    (output / 'build-command.json').write_text(json.dumps({'command': command, 'stdin': stdin, 'tool_pins': pins, 'space': space}, indent=2) + '\n')
    with (output / 'build.log').open('w') as log:
        subprocess.run(command, input=stdin, text=True, cwd=source, env=env,
                       stdout=log, stderr=subprocess.STDOUT, check=True, timeout=1200)
    artifacts = output / 'artifacts'
    artifacts.mkdir()
    entries = []
    for name, renamed in profile['artifacts'].items():
        original = child(builddir, name)
        destination = child(artifacts, renamed)
        shutil.copyfile(original, destination)
        entries.append({'file': renamed, 'bytes': destination.stat().st_size, 'sha256': digest(destination)})
    result = {'profile': profile['name'], 'artifacts': entries, 'tool_pins': pins,
              'source': json.loads((output / 'source.json').read_text()),
              'scope': 'Compiler output only; no guest, deployment or binary reproducibility claim'}
    (output / 'build.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['list', 'verify', 'source', 'build'])
    parser.add_argument('--profile')
    parser.add_argument('--cache', type=Path, help='Existing upstream Git cache containing the pinned base commit')
    parser.add_argument('--output', type=Path, help='Fresh output directory outside this repository')
    parser.add_argument('--rosbe', type=Path)
    parser.add_argument('--gcc12', type=Path)
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--allow-modified', action='store_true')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    profiles = {p['name']: p for p in manifest['profiles']}
    if args.action == 'list':
        print('\n'.join(profiles))
        return
    if args.action == 'verify':
        selected = [profiles[args.profile]] if args.profile else profiles.values()
        print(json.dumps({p['name']: verify(p, args.allow_modified) for p in selected}, indent=2))
        return
    if args.profile not in profiles or not args.cache or not args.output:
        parser.error('source/build require --profile, --cache and --output')
    if sys.platform != 'linux':
        parser.error('source/build require Linux or WSL to preserve executable modes')
    profile = profiles[args.profile]
    if args.action == 'build':
        tool = args.rosbe if profile['upstream'] == 'reactos' else args.gcc12
        if not tool or args.jobs < 1 or args.jobs > 32:
            parser.error('build requires its toolchain (--rosbe or --gcc12) and 1..32 jobs')
        fresh(args.output, [ROOT, args.cache, tool if tool.is_dir() else tool.parent])
        from build_space import require_space
        require_space(args.output)
    source, record = materialize(profile, args.cache, args.output, args.allow_modified)
    if args.action == 'build':
        record = build(profile, source, args.output.resolve(), args.rosbe, args.gcc12, manifest, args.jobs)
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the original NT5 graphics ladder; never deploy or execute it."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from build_space import require_space

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src/samples/graphics-ladder/ladder.c'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rosbe', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--sample', choices=('ladder', 'present', 'sprites', 'keyprobe', 'lifecycle', 'discovery', 'triangle'), default='ladder')
    a = p.parse_args()
    if sys.platform != 'linux':
        p.error('Build under Linux/WSL with the documented RosBE toolchain')
    out, sdk = a.output.resolve(), a.rosbe.resolve()
    if out.exists() or out.is_relative_to(ROOT) or out.is_relative_to(sdk) or sdk.is_relative_to(out):
        p.error('Choose a fresh output outside the repository and toolchain')
    cc = sdk / 'i386/bin/i686-w64-mingw32-gcc'
    objdump = sdk / 'i386/bin/i686-w64-mingw32-objdump'
    for tool in (cc, objdump):
        if not tool.is_file():
            p.error(f'Missing tool: {tool}')
    space = require_space(out, 20 + 8/1024)
    out.mkdir(parents=True)
    source = SOURCE.with_name(a.sample + '.c')
    runner = a.sample + '.cmd' if a.sample != 'ladder' else 'run.cmd'
    copied = out / source.name
    shutil.copyfile(source, copied)
    shutil.copyfile(source.with_name(runner), out/runner)
    command = [str(cc), '-Os', '-Wall', '-Wextra', '-Werror', '-nostdlib',
               '-fno-stack-protector', '-fno-builtin', '-Wl,--entry,_mainCRTStartup@0',
               '-Wl,--subsystem,console:5.0', '-Wl,--major-os-version,5',
               '-Wl,--minor-os-version,0', '-Wl,-Map,' + str(out/(a.sample+'.map')),
               '-MD', '-MF', str(out/'headers.d'),
               '-o', str(out/(a.sample+'.exe')), str(copied), '-lkernel32', '-luser32', '-lgdi32']
    record = dict(schema=1, sample=a.sample, source_sha256=sha(copied), runner_sha256=sha(out/runner),
                  builder_sha256=sha(Path(__file__)), compiler=str(cc),
                  compiler_sha256=sha(cc), objdump_sha256=sha(objdump),
                  command=command, space=space, executable_run=False,
                  scope='compile and PE inspection only; NT5/physical runtime unqualified')
    try:
        with (out/'build.log').open('xb') as f:
            result = subprocess.run(command, stdout=f, stderr=subprocess.STDOUT, timeout=180)
        record['exit_code'] = result.returncode
        record['log_sha256'] = sha(out/'build.log')
        if result.returncode:
            raise RuntimeError('Compile failed; retained build.log and inputs')
        exe = out/(a.sample+'.exe')
        deps=(out/'headers.d').read_text().replace('\\\n','').split(': ',1)[1].split()
        record['headers'] = {name:sha(Path(name)) for name in sorted(set(deps)) if Path(name)!=copied}
        raw = subprocess.check_output([str(objdump), '-p', str(exe)], timeout=30)
        (out/'pe.txt').write_bytes(raw)
        record.update(executable_sha256=sha(exe), executable_bytes=exe.stat().st_size,
                      pe_sha256=sha(out/'pe.txt'))
    except Exception as exc:
        record['error'] = str(exc)
        raise
    finally:
        (out/'build.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()

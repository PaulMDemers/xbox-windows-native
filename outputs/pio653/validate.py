"""Single owned host validation. No VM, console, XBE or physical disk access."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

K = Path(__file__).resolve().parent
W = K.parents[1]
O = Path('/mnt/c/xwn653/host001')
assert sys.platform == 'linux' and os.environ.get('XWN_BUILD_LEASE') == 'held'
assert not O.exists() and not (K / 'host001.json').exists()
sys.path.insert(0, str(W / 'tools'))
from build_space import require_space

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         status='preflight', physical_access=False, guest_launch=False,
         native_candidate_built=False, commands=[])


def save():
    (K / 'host001.json').write_text(json.dumps(r, indent=2) + '\n')


save()
try:
    r['space'] = require_space(O, minimum_gib=20.02)
    cc = Path('/usr/bin/gcc-12').resolve()
    assert sha(cc) == 'e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
    r['compiler_sha256'] = sha(cc)
    r['source_pins'] = {p.name: sha(p) for p in K.iterdir() if p.suffix in ('.c', '.h', '.py')}
    r['receipt652_pins'] = {n: sha(K.parent/'receipt652'/n) for n in ('receipt.c','receipt.h')}
    O.mkdir(parents=True)
    (O / 'tmp').mkdir()
    env = dict(os.environ, TMPDIR=str(O / 'tmp'))

    def run(name, args):
        r['commands'].append(dict(name=name, args=[str(a) for a in args]))
        save()
        p = subprocess.run(args, capture_output=True, env=env, timeout=60)
        (O / (name + '.stdout')).write_bytes(p.stdout)
        (O / (name + '.stderr')).write_bytes(p.stderr)
        assert p.returncode == 0 and not p.stderr, (name, p.returncode, p.stderr.decode())
        return p.stdout.decode()

    base = [str(cc), '-std=c99', '-Wall', '-Wextra', '-Werror', '-O1', '-g', '-I'+str(K.parent/'receipt652')]
    run('compile-host', base + ['-fsanitize=address,undefined', '-fno-pie', '-no-pie',
                              str(K/'pio.c'), str(K/'test.c'), str(K.parent/'receipt652/receipt.c'), '-o', str(O/'test-host')])
    r['protocol'] = json.loads(run('protocol', [str(O/'test-host')]))
    run('compile-i386', base + ['-m32', '-ffreestanding', '-fno-builtin', '-fno-pic', '-fno-pie',
                               '-fno-stack-protector', '-c', str(K/'pio.c'), '-o', str(O/'pio-i386.o')])
    r['undefined_symbols'] = run('undefined', ['nm', '-u', str(O/'pio-i386.o')]).strip()
    assert not r['undefined_symbols']
    run('link', ['ld','-m','elf_i386','-Ttext=0x100000','-e','admit653',str(O/'pio-i386.o'),'-o',str(O/'pio.elf')])
    run('binary',['objcopy','-O','binary',str(O/'pio.elf'),str(O/'pio.bin')])
    run('symbols',['nm','-n',str(O/'pio.elf')])
    r['artifacts'] = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in O.iterdir() if p.is_file()}
    r['status'] = 'passed'
except BaseException as e:
    r.update(status='failed', failure=repr(e))
    raise
finally:
    r['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save()
print(json.dumps(dict(status=r['status'], protocol=r['protocol'])))

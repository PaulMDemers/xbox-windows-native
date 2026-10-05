"""One-command reconstruction and packaging of the native component overlay."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
from build_space import require_space

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--reactos-cache', type=Path, required=True)
p.add_argument('--cromwell-cache', type=Path, required=True)
p.add_argument('--rosbe', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--cc', type=Path, default=Path('/usr/bin/gcc-12'))
p.add_argument('--jobs', type=int, default=4)
a = p.parse_args()
if sys.platform != 'linux' or os.environ.get('XWN_BUILD_LEASE') != 'held':
    p.error('Run in Linux/WSL under the project build lease')
out = a.output.resolve()
for path in (a.reactos_cache, a.cromwell_cache, a.rosbe):
    if out.is_relative_to(path.resolve(strict=True)):
        p.error('Output must be separate from source caches and toolchain')
space = require_space(out)
out.mkdir(parents=True, exist_ok=False)
tools = Path(__file__).resolve().parent
commands = [[sys.executable, str(tools / 'rebuild-native.py'),
                '--source-cache', str(a.reactos_cache), '--rosbe', str(a.rosbe),
                '--output', str(out / 'native'), '--jobs', str(a.jobs)],
               [sys.executable, str(tools / 'rebuild-launcher.py'),
                '--source-cache', str(a.cromwell_cache), '--cc', str(a.cc),
                '--output', str(out / 'launcher')],
               [sys.executable, str(tools / 'package-native.py'),
                '--native-build', str(out / 'native'), '--launcher-build', str(out / 'launcher'),
                '--output', str(out / 'package')]]
report = dict(status='started', space_preflight=space, commands=commands,
              started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              scope='Compilation and packaging only; no deployment or runtime qualification')
try:
    for command in commands:
        report['current_step'] = Path(command[1]).name
        (out / 'pipeline-report.json').write_text(json.dumps(report, indent=2)+'\n')
        subprocess.run(command, check=True)
    report['status'] = 'packaged'
except Exception as exc:
    report.update(status='failed', error=str(exc))
    raise
finally:
    report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # Even a full/read-only output filesystem must not hide the original error.
    try:
        (out / 'pipeline-report.json').write_text(json.dumps(report, indent=2)+'\n')
    except OSError as exc:
        print('Could not save pipeline report: '+str(exc), file=sys.stderr)
    print(json.dumps(report), flush=True)

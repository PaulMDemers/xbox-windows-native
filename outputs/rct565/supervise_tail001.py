"""MIT. One bounded read-only tail collection; never retries or launches Xbox."""
import datetime
import json
import subprocess
import sys
from pathlib import Path

K = Path(__file__).resolve().parent
out = K / 'supervisor-tail001.json'
assert not out.exists()
utc = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
r = dict(started_utc=utc(), completed=False, closed=False, timeout_seconds=300,
         remote_writes=False, xbox_launches=0, deadline_reached=False)


def save():
    out.write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')


save()
p = subprocess.Popen([sys.executable, '-B', str(K / 'collect_tail001.py')], cwd=K.parents[1])
r['pid'] = p.pid
save()
try:
    try:
        code = p.wait(timeout=300)
    except subprocess.TimeoutExpired:
        r['deadline_reached'] = True
        p.terminate()
        code = p.wait(timeout=5)
    r.update(exit_code=code, completed=code == 0 and not r['deadline_reached'])
finally:
    if p.poll() is None:
        p.kill()
        p.wait(timeout=5)
    r.update(closed=p.poll() is not None, ended_utc=utc())
    save()
sys.exit(0 if r['completed'] else 1)

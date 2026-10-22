"""Fresh Windows loopback qualification. No LAN, console, or firewall edits."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn655/windows001')
assert sys.platform=='win32' and not B.exists() and not (K/'windows001.json').exists()
r=dict(status='preflight',physical_access=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save():(K/'windows001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    sys.path.insert(0,str(W/'tools'));from build_space import require_space
    r['space']=require_space(B,minimum_gib=20.05);B.mkdir(parents=True)
    host=json.loads((K/'host002.json').read_text());assert host['status']=='pass'
    for name in ('receiver.py','test_receiver.py'):
        assert sha(K/name)==host['source_pins']['outputs/udp655/'+name]
    fixture=Path('C:/xwn655/host002/encoder.stdout')
    assert sha(fixture)==host['outputs']['encoder.stdout']['sha256']
    r.update(python_sha256=sha(Path(sys.executable)),fixture_sha256=sha(fixture),script_sha256=sha(Path(__file__)))
    r['command']=[sys.executable,'-B',str(K/'test_receiver.py'),'--packets',str(fixture),'--output',str(B/'loopback001')]
    x=subprocess.run(r['command'],capture_output=True,timeout=30)
    (B/'stdout.txt').write_bytes(x.stdout);(B/'stderr.txt').write_bytes(x.stderr)
    r['exit_code']=x.returncode;assert x.returncode==0
    r['tests']=json.loads(x.stdout);r['status']='pass'
except BaseException as e:r.update(status='failed',failure=repr(e));raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(r['tests']))

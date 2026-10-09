"""One read-only HMP screendump of this owned running child; no stop/resume or UI input."""
import socket,json,datetime,hashlib,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'cancel001';run=ws/'work/runs/nt5-wizard201-cancel001'
dest=out/'live-screen.json';assert not dest.exists() and not (run/'cleanup.json').exists()
i=json.loads((run/'instance.json').read_text());assert i['taskId']=='windows-native-wizard201' and i['sourceSha256'].lower()=='685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890'
p=out/'artifacts/live.ppm';assert not p.exists()
s=socket.create_connection(('127.0.0.1',4594),timeout=5);s.settimeout(5)
try:
    before=s.recv(4096)
    cmd='screendump '+p.as_posix();s.sendall(cmd.encode('ascii')+b'\n')
    reply=b'';deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        reply+=s.recv(4096)
        if b'(qemu)' in reply:break
finally:s.close()
assert p.exists()
dest.write_text(json.dumps(dict(scope=__doc__,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),screenshot_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),ordinary_monitor_snapshot=True,debugger=False,physical_access=False),indent=2)+'\n')
print('Owned guest screen preserved; no pause or input')

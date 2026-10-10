"""Read-only screenshot of the journaled owned guest; no UI input or reset."""
import datetime,json,os,socket
from pathlib import Path
k=Path(__file__).resolve().parent;case=k/'emulator001';r=json.loads((case/'run.json').read_text())
assert not r['closed'] and r['launch_requested']
assert 'tcp:127.0.0.1:4764,server,nowait' in r['argv']
out=case/'artifacts/runtime/screen001.ppm';assert not out.exists()
with socket.create_connection(('127.0.0.1',4764),timeout=5) as s:
    def reply():
        data=b''
        while not data.endswith(b'(qemu) '):
            part=s.recv(65536)
            if not part:raise EOFError()
            data+=part
        return data.decode('utf-8','replace')
    reply();s.sendall(('screendump "'+out.as_posix()+'"\n').encode());response=reply()
assert out.exists()
(case/'screen001.json').write_text(json.dumps(dict(scope=__doc__,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pid=r['pid'],path=str(out),response=response,no_input=True),indent=2)+'\n')
print(out)

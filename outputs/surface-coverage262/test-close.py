"""Fake monitor transport exercises the actual helper; never touches an emulator."""
import importlib.util,json,socket,sys,tempfile
from pathlib import Path
from unittest.mock import patch
k=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('close262',k/'close-host.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));import monitor_capture
class Lock:
    closed=False
    def close(self):self.closed=True
class Monitor:
    def __init__(self,replies):self.replies=iter(replies);self.commands=[]
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def settimeout(self,t):assert 0<t<=5
    def sendall(self,b):self.commands.append(b.decode().strip())
    def recv(self,n):
        v=next(self.replies)
        if isinstance(v,Exception):raise v
        return v
rows=[]
cases=[('quit-eof',[b'(qemu) ',b'(qemu) ',b''],True),('quit-reset',[b'(qemu) ',b'(qemu) ',ConnectionResetError('test')],True),('early-eof',[b''],False),('unknown-stop',[b'(qemu) ',b'unknown command\n(qemu) '],False),('stop-timeout',[b'(qemu) ',socket.timeout('test')],False)]
for name,replies,expected in cases:
    with tempfile.TemporaryDirectory(prefix='xwn262-close-') as root:
        run=Path(root);(run/'instance.json').write_text('{}')
        sock=Monitor(replies);lock=Lock()
        with patch.object(m.socket,'create_connection',return_value=sock),patch.object(monitor_capture,'acquire_monitor_lock',return_value=lock):
            try:m.close(run,4594)
            except (AssertionError,socket.timeout):assert not expected
        r=json.loads((run/'host-close.json').read_text());assert r['protocol_passed']==expected and lock.closed
        if expected:assert sock.commands==['stop','quit'] and r['quit_sent']
        rows.append(dict(name=name,expected_success=expected,actual_success=r['protocol_passed'],lock_released=lock.closed,commands=sock.commands))
dest=k/'close-tests.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,synthetic_transport_only=True,physical_access=False,cases=rows),indent=2)+'\n')
print('262 actual close helper: 5 simulated success/failure paths pass')

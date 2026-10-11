"""Actual bounded receive/close protocol; explicit socket and lease adapters."""
import importlib.util,json,socket,sys,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'host-close-test001.json';assert not dest.exists()
spec=importlib.util.spec_from_file_location('close238',k/'close-host.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));import monitor_capture
checks=0
class Fake:
    def __init__(self,mode):self.mode=mode;self.commands=[];self.reads=0
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def settimeout(self,v):assert 0<v<=5
    def sendall(self,data):self.commands.append(data)
    def recv(self,n):
        assert n==65536;self.reads+=1
        if self.reads<=2:
            if self.reads==2 and self.mode=='early-eof':return b''
            if self.reads==2 and self.mode=='stop-error':return b'Error stop refused\n(qemu) '
            return b'(qemu) '
        if self.mode=='quit-reset':raise ConnectionResetError('expected quit reset')
        if self.mode=='oversize':return b'x'*65536
        if self.mode=='timeout':raise socket.timeout('bounded')
        return b''
class Lock:
    def close(self):pass
old_socket=m.socket.create_connection;old_lock=monitor_capture.acquire_monitor_lock
root=k/'artifacts/host-close-tests';root.mkdir(exist_ok=False)
try:
    for mode in ['quit-eof','quit-reset','early-eof','stop-error','oversize','timeout']:
        run=root/mode;run.mkdir();(run/'instance.json').write_text('{}',encoding='utf-8');fake=Fake(mode)
        m.socket.create_connection=lambda *args,**kwargs:fake
        monitor_capture.acquire_monitor_lock=lambda port:Lock()
        try:m.close(run,4594);passed=True
        except (AssertionError,socket.timeout):passed=False
        assert passed==(mode in ['quit-eof','quit-reset']);checks+=1
        result=json.loads((run/'host-close.json').read_text(encoding='utf-8'));assert result['protocol_passed']==passed;checks+=1
        if mode in ['early-eof','stop-error']:assert fake.commands==[b'stop\n'];checks+=1
        else:assert fake.commands==[b'stop\n',b'quit\n'];checks+=1
        if mode=='oversize':assert fake.reads==19;checks+=1
        try:m.close(run,4594)
        except AssertionError:checks+=1
        else:raise AssertionError('Repeated close permitted')
finally:m.socket.create_connection=old_socket;monitor_capture.acquire_monitor_lock=old_lock
dest.write_text(json.dumps(dict(passed=True,checks=checks,source_sha256=hashlib.sha256((k/'close-host.py').read_bytes()).hexdigest(),physical_access=False,guest_launch=False,actual_protocol_executed=True),indent=2)+'\n',encoding='utf-8')
print('238 closure checks',checks)

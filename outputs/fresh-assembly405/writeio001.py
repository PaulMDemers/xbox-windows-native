"""Private regular QCOW2 writer over a private Unix socket; no device nodes."""
import socket, struct, subprocess, tempfile, time
from pathlib import Path
class WriteIO:
    def __init__(self,path,expected_size,allowed_root):
        p=Path(path); root=Path(allowed_root).resolve()
        assert p.is_file() and not p.is_symlink() and p.resolve().parent==root
        self.tmp=tempfile.TemporaryDirectory(prefix='xwn405-write-')
        self.process=None;self.sock=None;self.pos=0;self.handle=0
        try:
            name=str(Path(self.tmp.name)/'nbd.sock')
            self.process=subprocess.Popen(['qemu-nbd','--format=qcow2','--socket='+name,str(p)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            for _ in range(100):
                if Path(name).exists():break
                if self.process.poll() is not None:raise RuntimeError(self.process.stderr.read().decode())
                time.sleep(.05)
            self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(30);self.sock.connect(name)
            assert self.recv(16)==b'NBDMAGICIHAVEOPT'
            flags=struct.unpack('>H',self.recv(2))[0];assert flags&1
            nozero=bool(flags&2);self.sock.sendall(struct.pack('>I',3 if nozero else 1))
            self.sock.sendall(struct.pack('>QII',0x49484156454f5054,1,0))
            self.size,transmission=struct.unpack('>QH',self.recv(10));assert self.size==expected_size and not transmission&2 and transmission&4
            if not nozero:assert self.recv(124)==bytes(124)
        except BaseException:self.close();raise
    def recv(self,n):
        b=bytearray()
        while len(b)<n:
            part=self.sock.recv(n-len(b))
            if not part:raise EOFError('Private writer disconnected')
            b.extend(part)
        return bytes(b)
    def request(self,kind,offset,n,payload=b''):
        assert kind in [0,1,3] and 0<=n<=8*1024**2 and 0<=offset<=self.size and offset+n<=self.size
        assert offset%512==0 and n%512==0
        assert len(payload)==(n if kind==1 else 0)
        self.handle+=1
        self.sock.sendall(struct.pack('>IHHQQI',0x25609513,0,kind,self.handle,offset,n)+payload)
        magic,error,handle=struct.unpack('>IIQ',self.recv(16))
        assert magic==0x67446698 and handle==self.handle and error==0,(magic,error,handle)
        return self.recv(n) if kind==0 else b''
    def seek(self,pos,whence=0):
        assert whence==0 and 0<=pos<=self.size;self.pos=pos;return pos
    def read(self,n):
        b=self.request(0,self.pos,n);self.pos+=n;return b
    def write(self,b):
        self.request(1,self.pos,len(b),b);self.pos+=len(b);return len(b)
    def flush(self):self.request(3,0,0)
    def close(self):
        if self.sock:self.sock.close();self.sock=None
        if self.process:
            try:self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:self.process.terminate();self.process.wait(timeout=5)
            assert self.process.returncode==0, self.process.stderr.read().decode()
            self.process.stderr.close();self.process=None
        self.tmp.cleanup()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()

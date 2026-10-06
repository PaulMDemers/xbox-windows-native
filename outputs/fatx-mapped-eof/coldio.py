"""Owned read-only qemu-nbd Unix socket; no kernel device attachment or write command."""
import socket,struct,subprocess,tempfile,time
from pathlib import Path
class ColdIO:
    def __init__(self,path):
        self.tmp=tempfile.TemporaryDirectory(prefix='xwn-cold-');self.process=None;self.sock=None
        self.pos=0;self.handle=0;self.read_bytes=0
        try:
            name=str(Path(self.tmp.name)/'nbd.sock')
            self.process=subprocess.Popen(['qemu-nbd','--read-only','--format=qcow2','--socket='+name,str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            for _ in range(100):
                if Path(name).exists():break
                if self.process.poll() is not None:raise RuntimeError(self.process.stderr.read().decode())
                time.sleep(.05)
            self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(30);self.sock.connect(name)
            assert self.recv(16)==b'NBDMAGICIHAVEOPT'
            flags=struct.unpack('>H',self.recv(2))[0];assert flags&1
            nozero=bool(flags&2);self.sock.sendall(struct.pack('>I',3 if nozero else 1))
            self.sock.sendall(struct.pack('>QII',0x49484156454f5054,1,0)) # EXPORT_NAME, empty export
            self.size,transmission=struct.unpack('>QH',self.recv(10));assert transmission&2,'Export must be read-only'
            if not nozero:assert self.recv(124)==bytes(124)
        except BaseException:self.close();raise
    def recv(self,n):
        b=bytearray()
        while len(b)<n:
            part=self.sock.recv(n-len(b))
            if not part:raise EOFError('Read-only NBD disconnected')
            b.extend(part)
        return bytes(b)
    def seek(self,pos,whence=0):
        assert whence==0 and 0<=pos<=self.size;self.pos=pos;return pos
    def read(self,n):
        assert 0<=n<=32*1024*1024 and self.pos+n<=self.size
        if not n:return b''
        self.handle+=1
        self.sock.sendall(struct.pack('>IHHQQI',0x25609513,0,0,self.handle,self.pos,n)) # Only NBD_CMD_READ
        magic,error,handle=struct.unpack('>IIQ',self.recv(16))
        assert magic==0x67446698 and handle==self.handle and error==0,(magic,error,handle)
        b=self.recv(n);self.pos+=n;self.read_bytes+=n;return b
    def close(self):
        if self.sock:self.sock.close();self.sock=None
        if self.process:
            try:self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:self.process.terminate();self.process.wait(timeout=5)
            self.process.stderr.close();self.process=None
        self.tmp.cleanup()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()

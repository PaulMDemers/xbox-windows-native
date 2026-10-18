"""Bounded read-only GDB and HMP transport for the owned standalone control."""
import socket,time

class Remote:
    def __init__(self,port):
        self.s=socket.create_connection(('127.0.0.1',port),timeout=5)
    def exact(self,n):
        b=bytearray()
        while len(b)<n:
            p=self.s.recv(n-len(b))
            if not p:raise EOFError('GDB disconnected')
            b.extend(p)
        return bytes(b)
    def recv(self,seconds=5):
        end=time.monotonic()+seconds
        while True:
            self.s.settimeout(max(.001,end-time.monotonic()))
            c=self.exact(1)
            if c not in (b'$',b'%'):continue
            data=bytearray()
            while True:
                self.s.settimeout(max(.001,end-time.monotonic()))
                c=self.exact(1)
                if c==b'#':break
                data+=c
                assert len(data)<=65536,'GDB packet capacity'
            check=self.exact(2);assert int(check,16)==sum(data)%256
            self.s.sendall(b'+')
            if data.startswith(b'O') and len(data)>2 and all(c in b'0123456789abcdefABCDEF' for c in data[1:]):continue
            return data.decode('ascii')
    def send(self,text):
        b=text.encode('ascii');self.s.settimeout(5)
        self.s.sendall(b'$'+b+b'#'+f'{sum(b)%256:02x}'.encode())
    def ask(self,text):
        self.send(text)
        for _ in range(4):
            reply=self.recv()
            if text!='?' and reply.startswith(('T','S')):
                self.async_stops=getattr(self,'async_stops',[])+[reply]
                continue
            return reply
        raise RuntimeError('Too many asynchronous stop replies')
    def read(self,address,size):
        assert 0<size<=131072 and 0<=address<=0xffffffff-size+1
        result=bytearray()
        for offset in range(0,size,1024):
            n=min(1024,size-offset);reply=self.ask(f'm{address+offset:x},{n:x}')
            assert not reply.startswith('E'),(hex(address+offset),n,reply)
            data=bytes.fromhex(reply);assert len(data)==n;result+=data
        return bytes(result)
    def interrupt(self):self.s.sendall(b'\x03');return self.recv()

def monitor(port,text,quit=False):
    end=time.monotonic()+10
    with socket.create_connection(('127.0.0.1',port),timeout=5) as s:
        def receive(eof=False):
            data=bytearray()
            while not data.endswith(b'(qemu) '):
                s.settimeout(max(.001,end-time.monotonic()))
                try:p=s.recv(65536)
                except ConnectionResetError:
                    if eof:return bytes(data)
                    raise
                if not p:
                    if eof:return bytes(data)
                    raise EOFError('HMP disconnected')
                data+=p;assert len(data)<=1048576
            return bytes(data)
        receive();s.sendall((text+'\n').encode());return receive(quit).decode('utf-8','replace')

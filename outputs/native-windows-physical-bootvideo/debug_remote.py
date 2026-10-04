import socket,struct
class Remote:
    def __init__(self,port):
        self.s=socket.create_connection(('127.0.0.1',port),timeout=20)
        self.s.settimeout(20)
    def recv(self):
        while True:
            c=self.s.recv(1)
            if not c:raise EOFError('Debugger disconnected')
            if c!=b'$':continue
            b=bytearray()
            while True:
                c=self.s.recv(1)
                if not c:raise EOFError('Incomplete debugger packet')
                if c==b'#':break
                b+=c
            checksum=self.s.recv(2)
            assert int(checksum,16)==sum(b)%256
            self.s.sendall(b'+')
            if b.startswith(b'O') and b!=b'OK':continue
            return b.decode()
    def send(self,s):
        b=s.encode();self.s.sendall(b'$'+b+b'#'+f'{sum(b)%256:02x}'.encode())
    def ask(self,s):self.send(s);return self.recv()
    def bp(self,addr,on=True):assert self.ask(f'{"Z" if on else "z"}0,{addr:x},1')=='OK'
    def regs(self):
        raw=bytes.fromhex(self.ask('g'))
        values=struct.unpack_from('<10I',raw)
        return {k:values[i] for i,k in enumerate(['eax','ecx','edx','ebx','esp','ebp','esi','edi','eip','eflags'])}
    def read(self,addr,size):return bytes.fromhex(self.ask(f'm{addr:x},{size:x}'))

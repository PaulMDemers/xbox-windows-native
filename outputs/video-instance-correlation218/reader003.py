"""Bounded read-only CPU RAM reader adapted from closed217; no MMIO/write/BP API."""
import socket
class Reader:
 def __init__(self):self.s=socket.create_connection(('127.0.0.1',4595),timeout=5);self.s.settimeout(5)
 def recv(self):
  while True:
   c=self.s.recv(1)
   if not c:raise EOFError()
   if c!=b'$':continue
   b=bytearray()
   while True:
    c=self.s.recv(1)
    if not c:raise EOFError()
    if c==b'#':break
    b+=c
   h=self.s.recv(2);assert len(h)==2 and int(h,16)==sum(b)%256
   self.s.sendall(b'+');return b.decode('ascii')
 def ask(self,text):
  b=text.encode('ascii');self.s.sendall(b'$'+b+b'#'+f'{sum(b)%256:02x}'.encode());return self.recv()
 def interrupt(self):self.s.sendall(b'\x03');return self.recv()
 def read(self,a,n,allow_unmapped=False):
  assert (((0x80000000<=a and a+n<=0x84000000) or (0xd0000000<=a and a+n<=0xe0000000)) or (a==0x11000 and n==64)) and 0<n<=4096
  answer=self.ask(f'm{a:x},{n:x}')
  if answer.startswith('E') and allow_unmapped:return None,answer
  assert not answer.startswith('E'),answer
  data=bytes.fromhex(answer);assert len(data)==n;return data

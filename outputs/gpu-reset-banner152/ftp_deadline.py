"""Bound the whole FTP greeting/login exchange, including multiline replies."""
import ftplib,socket,time
class DeadlineFTP(ftplib.FTP):
    def __init__(self,deadline):
        super().__init__();self.deadline=deadline
    def budget(self):
        remaining=self.deadline-time.monotonic()
        if remaining<=0:raise socket.timeout('FTP exchange deadline expired')
        if self.sock:self.sock.settimeout(remaining)
        return remaining
    def getline(self):
        self.budget();return super().getline()
    def putline(self,line):
        self.budget();return super().putline(line)

"""Exercise fragmented greetings and real deadline expiry through local sockets."""
import hashlib,json,socket,threading,time
from pathlib import Path
from ftp_deadline import DeadlineFTP
def exchange(chunks,delay,budget,should_pass):
    client,server=socket.socketpair();f=DeadlineFTP(time.monotonic()+budget)
    f.sock=client;f.file=client.makefile('r',encoding='utf-8');st=time.monotonic()
    def writer():
        try:
            for chunk in chunks:time.sleep(delay);server.sendall(chunk)
        except (BrokenPipeError,ConnectionResetError,OSError):pass
        finally:server.close()
    worker=threading.Thread(target=writer);worker.start()
    try:
        try:reply=f.getresp();passed=True
        except socket.timeout:passed=False;reply=None
        elapsed=time.monotonic()-st;assert passed==should_pass
        if passed:assert reply.endswith('220 Ready')
        else:assert elapsed<budget+.2
    finally:f.close();worker.join(1);assert not worker.is_alive()
    return dict(passed=passed,elapsed_seconds=elapsed,deadline_seconds=budget,worker_joined=True)
results=[exchange([b'220-First\r\n',b'\r\n',b'220 Ready\r\n'],.01,1,True),
         exchange([b'220-First\r\n']*4+[b'220 Ready\r\n'],.10,.25,False)]
p=Path(__file__).with_name('deadline-tests.json');assert not p.exists()
p.write_text(json.dumps(dict(passed=True,results=results,test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
print('Complete greeting accepted; drip-fed greeting stopped at absolute deadline')

"""One bounded host responder for the owned guest's exact network witness."""
import datetime, hashlib, json, socket, time
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'emu005/network-host.json'
assert not out.exists()
r=dict(started=datetime.datetime.now(datetime.timezone.utc).isoformat(),port=5459,accepted_witnesses=0,rounds=0,passed=False,attempts=[])
def exact(s,n):
    b=b''
    while len(b)<n:
        p=s.recv(n-len(b))
        if not p:raise EOFError('Short guest payload')
        b+=p
    return b
try:
    deadline=time.monotonic()+480
    while time.monotonic()<deadline:
        try:
            s=socket.create_connection(('127.0.0.1',5459),timeout=2);s.settimeout(5)
            header=exact(s,12)
        except (OSError,EOFError) as e:
            r['attempts'].append(type(e).__name__)
            try:s.close()
            except NameError:pass
            time.sleep(2);continue
        assert header==b'XWN405-NET1\n';r['accepted_witnesses']=1
        with s:
            tx=hashlib.sha256();rx=hashlib.sha256()
            for n in range(32):
                b=exact(s,4096);assert b==bytes((97+n*13+i*7)&255 for i in range(4096))
                tx.update(b);reply=bytes(v^0xa5 for v in b);s.sendall(reply);rx.update(reply);r['rounds']+=1
            assert s.recv(1)==b'';s.shutdown(socket.SHUT_WR)
        r.update(passed=True,bytes_each_direction=131072,guest_to_host_sha256=tx.hexdigest(),host_to_guest_sha256=rx.hexdigest());break
    else:raise TimeoutError('No guest network witness within owned deadline')
except Exception as e:r['error']=repr(e)
finally:
    with out.open('x') as f:json.dump(r,f,indent=2)
print(json.dumps({k:v for k,v in r.items() if k!='attempts'}))

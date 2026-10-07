"""One local host responder, exactly two guest exchanges, then exit."""
import datetime,hashlib,json,socket,sys
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['control001','candidate001'];out=k/case
path=out/'network-host.json';assert out.exists() and not path.exists()
r=dict(case=case,physical_access=False,bind='127.0.0.1:4597',connections=[],complete=False)
def save():write_json(path,r)
try:
    with socket.socket() as server:
        server.bind(('127.0.0.1',4597));server.listen(1);server.settimeout(300);r['listening']=True;save();print('Local responder ready',flush=True)
        for phase in [0,1]:
            conn,peer=server.accept();row=dict(phase=phase,peer=list(peer),rounds=0,received=0,sent=0);r['connections'].append(row);save()
            with conn:
                conn.settimeout(5);received=hashlib.sha256();sent=hashlib.sha256()
                for index in range(32):
                    data=b''
                    while len(data)<4096:
                        chunk=conn.recv(4096-len(data));assert chunk,'Early EOF';data+=chunk
                    assert data==bytes((phase*97+index*13+i*7)&255 for i in range(4096))
                    reply=bytes(v^0xa5 for v in data);conn.sendall(reply);received.update(data);sent.update(reply)
                    row.update(rounds=index+1,received=(index+1)*4096,sent=(index+1)*4096)
                assert conn.recv(1)==b'';conn.shutdown(socket.SHUT_WR)
                row.update(received_sha256=received.hexdigest(),sent_sha256=sent.hexdigest(),peer_send_closed=True)
            save()
    r['complete']=True;save();print('Both exact network exchanges completed',flush=True)
except BaseException as exc:r['error']=repr(exc);save();raise

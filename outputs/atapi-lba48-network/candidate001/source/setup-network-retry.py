"""New kit after outbound networking was rejected by the isolated backend."""
from pathlib import Path
import json
old=Path(__file__).resolve().parent;k=old.parent/'nvnet-shutdown-network';assert not k.exists();k.mkdir();(k/'artifacts').mkdir()
files=['probe.c','network.inc','Build.ps1','common.py','prepare.py','preflight.py','Run.ps1','supervise.py','audit.py','configuration.py','check-oracle.py','review.py','record-closure.py','verify-evidence.py','atomic_json.py','network-server.py','hal-review.json','fatx-review.json','nvnet-review.json','0104-nvnet-resident-shutdown-helper.patch','inputs.json','control-inputs.json','manifest.json','prepare-source.py','finalize-source.py','setup-runtime.py','build.py','build-control.py','review-nvnet.py','nvnet-build-candidate001.json','nvnet-build-control001.json']
for n in files:
    s=(old/n).read_text()
    if n.endswith(('.py','.ps1')) and n not in ['build.py','build-control.py','review-nvnet.py','prepare-source.py','finalize-source.py','setup-runtime.py']:
        s=s.replace('nvnet-shutdown-resident','nvnet-shutdown-network')
    if n=='Run.ps1':s=s.replace('../native-windows-nt5-kernel/Invoke-Diagnostic.ps1','Invoke-Network.ps1')
    if n=='preflight.py':s=s.replace("'network-server.py']","'network-server.py','Invoke-Network.ps1','setup-network-retry.py']")
    (k/n).write_text(s)
for n in ['nvnet-control001.sys','nvnet-candidate001.sys']:(k/'artifacts'/n).write_bytes((old/'artifacts'/n).read_bytes())
s=(old.parent/'native-windows-nt5-kernel/Invoke-Diagnostic.ps1').read_text()
needle='hostfwd=tcp:127.0.0.1:${FtpPort}-:21';assert s.count(needle)==1
s=s.replace(needle,needle+',hostfwd=tcp:127.0.0.1:4597-:4597')
(k/'Invoke-Network.ps1').write_text(s)
(k/'setup-network-retry.py').write_bytes(Path(__file__).read_bytes())
p=k/'network.inc';s=p.read_text();start=s.index('    s=socket(');end=s.index('    for(round=0;',start)
s=s[:start]+'''    {
        SOCKET listener=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);
        if(listener==INVALID_SOCKET)fatal("FAIL_SOCKET");
        address.sin_family=AF_INET;address.sin_port=htons(4597);address.sin_addr.s_addr=INADDR_ANY;
        error=1;if(setsockopt(listener,SOL_SOCKET,SO_REUSEADDR,(char*)&error,sizeof(error)))fatal("FAIL_REUSE");
        if(bind(listener,(struct sockaddr*)&address,sizeof(address))||listen(listener,1))fatal("FAIL_LISTEN");
        FD_ZERO(&writes);FD_SET(listener,&writes);timeout.tv_sec=30;timeout.tv_usec=0;
        if(select(0,&writes,NULL,NULL,&timeout)!=1)fatal("FAIL_ACCEPT_WAIT");
        s=accept(listener,NULL,NULL);if(s==INVALID_SOCKET)fatal("FAIL_ACCEPT");
        if(closesocket(listener))fatal("FAIL_LISTENER_CLOSE");
    }
    if(setsockopt(s,SOL_SOCKET,SO_RCVTIMEO,(char*)&ms,sizeof(ms))||setsockopt(s,SOL_SOCKET,SO_SNDTIMEO,(char*)&ms,sizeof(ms)))fatal("FAIL_SOCKET_TIMEOUT");
'''+s[end:]
s=s.replace('u_long nonblocking=1;','').replace('fd_set writes,errors;','fd_set writes;').replace('int error,errorSize,n,offset;','int error,n,offset;')
s=s.replace('if(shutdown(s,SD_SEND))fatal("FAIL_SOCKET_SHUTDOWN");\n    if(recv(s,(char*)rx,1,0)!=0)', 'if(shutdown(s,SD_SEND))fatal("FAIL_SOCKET_SHUTDOWN");\n    if(recv(s,(char*)rx,1,0)!=0)')
p.write_text(s)
# Guest still sends deterministic requests; the host now initiates each connection.
p=k/'network-server.py';s=p.read_text().replace('import datetime,hashlib,json,socket,sys','import datetime,hashlib,json,socket,sys,time')
start=s.index('    with socket.socket() as server:');end=s.index("            with conn:",start)
s=s[:start]+'''    for phase in [0,1]:
            deadline=time.monotonic()+300;row=dict(phase=phase,rounds=0,received=0,sent=0);r['connections'].append(row);save()
            while True:
                conn=socket.socket();conn.settimeout(3)
                try:
                    conn.connect(('127.0.0.1',4597));first=conn.recv(4096)
                    if not first:raise ConnectionError('Guest listener not ready')
                    break
                except (OSError,ConnectionError):
                    conn.close()
                    if time.monotonic()>=deadline:raise TimeoutError('No guest TCP listener')
                    time.sleep(1)
            row['peer']=['127.0.0.1',4597];save()
'''+s[end:]
s=s.replace("data=b''", "data=first if index==0 else b''")
s=s.replace("bind='127.0.0.1:4597'", "endpoint='127.0.0.1:4597',network_restricted=True")
s=s.replace('One local host responder, exactly two guest exchanges, then exit.','Connect through the explicit loopback-only forward; verify two guest exchanges.')
p.write_text(s)
print('New isolated-forward kit only; no guest launch')

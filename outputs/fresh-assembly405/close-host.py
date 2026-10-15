"""Bounded owned HMP stop/quit; process exit is verified separately by runner."""
import argparse,datetime,json,socket,sys,time
from pathlib import Path

def receive(s,deadline,allow_eof,record):
    data=b''
    while not data.endswith(b'(qemu) '):
        remaining=deadline-time.monotonic()
        assert remaining>0,'Total monitor deadline'
        s.settimeout(min(5,remaining))
        try:part=s.recv(65536)
        except ConnectionResetError as exc:
            if not allow_eof:raise
            record['quit_monitor_reset']=repr(exc)
            return data.decode('utf-8','replace')
        if not part:
            assert allow_eof,'Unexpected monitor EOF before quit'
            record['quit_monitor_eof']=True
            return data.decode('utf-8','replace')
        data+=part
        assert len(data)<=1048576,'Bounded monitor reply'
    return data.decode('utf-8','replace')

def close(run,port):
    assert port==5456 and (run/'instance.json').exists() and not (run/'host-close.json').exists()
    dest=run/'host-close.json';r=dict(physical_access=False,method='HMP stop then quit',actions=[],quit_sent=False)
    def save():
        tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');tmp.replace(dest)
    k=Path(__file__).resolve().parent
    sys.path.insert(0,str(k.parent/'native-windows-prebuild'))
    from monitor_capture import acquire_monitor_lock
    lock=None
    try:
        lock=acquire_monitor_lock(port);deadline=time.monotonic()+10
        with socket.create_connection(('127.0.0.1',port),timeout=5) as s:
            r['banner']=receive(s,deadline,False,r);save()
            for command in ['stop','quit']:
                row=dict(command=command,requested_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
                r['actions'].append(row);save();s.sendall((command+'\n').encode('ascii'))
                if command=='quit':r['quit_sent']=True;save()
                row['reply']=receive(s,deadline,command=='quit',r);save()
                assert 'Error' not in row['reply'] and 'unknown command' not in row['reply']
        r['protocol_passed']=True
    except BaseException as exc:r.update(protocol_passed=False,error=repr(exc));raise
    finally:
        if lock:lock.close()
        save()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('-Run',type=Path,required=True);parser.add_argument('-Port',type=int,required=True)
    args=parser.parse_args();close(args.Run,args.Port)

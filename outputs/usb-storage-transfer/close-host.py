"""Owned emu002 control: pause guest then request orderly emulator process exit."""
import datetime,json,socket,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case=='emu002'
run=k.parents[1]/('work/runs/nt5storxfer-'+case)
assert (run/'observe.json').exists() and not (run/'cleanup.json').exists()
instance=json.loads((run/'instance.json').read_text());port=instance['monitor_port']
assert port==5134 and instance['physical_access'] is False
out=run/'host-close.json';assert not out.exists()
r=dict(physical_access=False,guest_normal_restart=False,method='HMP stop then quit',actions=[])
def save():out.write_text(json.dumps(r,indent=2)+'\n')
def receive(s,allow_eof=False):
    data=b''
    while not data.endswith(b'(qemu) '):
        try:part=s.recv(65536)
        except ConnectionResetError as error:
            if not allow_eof:raise
            r['quit_monitor_reset']=repr(error)
            return data.decode('utf-8','replace')
        if not part:
            if allow_eof:return data.decode('utf-8','replace')
            raise RuntimeError('Unexpected monitor EOF')
        data+=part
        assert len(data)<=1048576
    return data.decode('utf-8','replace')
save()
try:
    with socket.create_connection(('127.0.0.1',port),timeout=5) as s:
        receive(s)
        for command in ['stop','quit']:
            row=dict(command=command,requested_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
            r['actions'].append(row);save();s.sendall((command+'\n').encode())
            row['reply']=receive(s,allow_eof=command=='quit');save()
    r['quit_sent']=True
except BaseException as error:r['error']=repr(error);raise
finally:save()

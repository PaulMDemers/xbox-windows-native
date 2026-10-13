"""One bounded emulator-only capacity launch, collect a fresh report, signal stop."""
import ftplib,hashlib,io,json,time
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'capacity-emu001';record=out/'launch.json'
assert not record.exists();r=dict(physical_access=False,launch_requested=False,completed=False)
save=lambda:record.write_text(json.dumps(r,indent=2)+'\n')
save();deadline=time.monotonic()+150
while time.monotonic()<deadline:
    f=ftplib.FTP()
    try:
        f.connect('127.0.0.1',5112,timeout=2);f.login('xbox','xbox')
        if not r['launch_requested']:
            b=io.BytesIO();f.retrbinary('RETR /E/Applications/XWNCapacity333/default.xbe',b.write)
            build=json.loads((K/'capacity-build001.json').read_text())
            assert hashlib.sha256(b.getvalue()).hexdigest()==build['outputs']['default.xbe']['sha256']
            r.update(launch_requested=True,command=r'SITE EXEC E:\Applications\XWNCapacity333\default.xbe');save()
            try:r['launch_reply']=f.sendcmd(r['command'])
            except (OSError,EOFError) as e:r['launch_reply_uncertain']=type(e).__name__
            save()
        else:
            b=io.BytesIO();f.retrbinary('RETR /E/Applications/XWNCapacity333/capacity.txt',b.write)
            data=b.getvalue();assert len(data)<1024 and data.endswith(b'COMPLETE 333\r\n')
            (out/'capacity.txt').write_bytes(data);r.update(completed=True,report_sha256=hashlib.sha256(data).hexdigest());save();break
    except (OSError,EOFError,ftplib.Error) as e:r['last_poll_error']=type(e).__name__;save()
    finally:f.close()
    time.sleep(2)
Path('E:/xwn333/runs/nt5-capacity333-emu001/capture-complete.signal').write_text('capacity observer closed\n')
r['observer_closed']=True;save();print(json.dumps(r,indent=2))

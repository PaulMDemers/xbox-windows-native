"""MIT. Bounded read-only dashboard/result observation; never launch or mutate."""
import ftplib,hashlib,importlib.util,json,os,time
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('scene549observe',K/'controller.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
c.verify();assert c.read(K/'launch001.json')['requested']
out=K/'observation001.json';assert not out.exists() and not (K/'collection001.json').exists()
r=dict(started_utc=c.m.utc(),pid=os.getpid(),closed=False,completed=False,observations=[],remote_writes=[],launches=0,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),console_state='unknown',normal_restart_proved=False)
c.m.write_json(out,r);deadline=time.monotonic()+240
try:
    while time.monotonic()<deadline:
        time.sleep(min(6,max(0,deadline-time.monotonic())))
        if time.monotonic()>=deadline:break
        row=dict(utc=c.m.utc(),dashboard=False)
        try:
            with c.m.connect(timeout=3) as f:
                row['dashboard']=True
                if 'xwn549' in {n.lower() for n in c.m.names(f,'/E')}:
                    rows=c.m.names(f,c.RESULT);row['result_names']=sorted(rows)
                    row['runner_receipt_listed']='runner.txt' in rows
                else:row['runner_receipt_listed']=False
            r['console_state']='authenticated dashboard'
        except (OSError,EOFError,ftplib.Error) as e:
            row['error_type']=type(e).__name__;r['console_state']='dashboard unavailable; screen state unknown'
        r['observations'].append(row);c.m.write_json(out,r)
        if row.get('runner_receipt_listed'):
            r.update(completed=True,result='dashboard_with_runner_receipt');break
    else:pass
    if not r['completed']:r.update(completed=True,result='observation_deadline_screen_confirmation_needed')
finally:
    r.update(closed=True,ended_utc=c.m.utc());c.m.write_json(out,r)
print(json.dumps({n:r.get(n) for n in ['completed','closed','result','console_state']}))

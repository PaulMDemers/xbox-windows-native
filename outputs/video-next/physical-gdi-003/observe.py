"""Observe only the recorded launch; collect once after dashboard returns."""
import datetime,ftplib,json,os,subprocess,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent
trial=json.loads((k/'trial.json').read_text());assert trial['launch_attempted'] and not trial.get('collected_utc')
out=k/'observation.json';assert not out.exists()
r=dict(launch_utc=trial['launch_utc'],offline_observed=False,launches_issued=0)
deadline=time.monotonic()+240
while time.monotonic()<deadline:
    time.sleep(8)
    f=ftplib.FTP()
    try:
        f.connect(os.environ['XWN_FTP_HOST'],timeout=3)
        f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
        if r['offline_observed']:
            f.quit();f.close()
            r.update(dashboard_return=True,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
            out.write_text(json.dumps(r,indent=2)+'\n')
            subprocess.run([sys.executable,str(k/'trial.py'),'collect'],check=True)
            print('Physical run collected; review required',flush=True)
            break
    except ftplib.all_errors:
        r['offline_observed']=True
    finally:f.close()
else:
    r.update(dashboard_return=False,observation='No confirmed offline-to-online transition before deadline; not a crash inference')
    out.write_text(json.dumps(r,indent=2)+'\n');print(r['observation'],flush=True)

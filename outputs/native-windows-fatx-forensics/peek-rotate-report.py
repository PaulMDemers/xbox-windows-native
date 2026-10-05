"""Inspect resident probe text; absence is inconclusive because log pages may not be resident."""
import pathlib,sys,json,argparse,hashlib,time
k=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(k.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--port',type=int,default=4594);p.add_argument('--marker',default='ROTATE-BEGIN');a=p.parse_args()
assert a.run.startswith(('nt5-physical-f-cache-','nt5-physical-f-hives-','nt5-physical-f-high-allocation-')) and a.run.replace('-','').isalnum()
run=k.parents[1]/'work/runs'/a.run;raw=run/'rotate-report.ram';assert run.is_dir() and not raw.exists()
with acquire_monitor_lock(a.port):
    running='VM status: running' in command(a.port,'info status');command(a.port,'stop')
    try:
        command(a.port,'pmemsave 0 62914560 '+json.dumps(raw.resolve().as_posix()))
        b=raw.read_bytes();start=0;reports=[]
        while True:
            at=b.find(a.marker.encode('ascii'),start)
            if at<0:break
            value=b[at:at+4096].split(b'\0')[0].decode('ascii',errors='replace').rstrip()
            if value not in reports:reports.append(value)
            start=at+1
        label=hashlib.sha256(a.marker.encode('ascii')).hexdigest()[:12]
        (run/('live-rotate-report-'+label+'-'+str(time.time_ns())+'.json')).write_text(json.dumps(reports,indent=2)+'\n')
        print(json.dumps([x[:1000] for x in reports],indent=2))
    finally:
        try:
            raw.unlink(missing_ok=True)
        except OSError as e:
            print('Partial dump retained:',repr(e))
        finally:
            if running:command(a.port,'cont')

"""Read the pre-created report after the second physical cycle."""
import pathlib,ftplib,io,json,os,hashlib,datetime
k=pathlib.Path(__file__).resolve().parent;p=k/'physical-cycle-002.json';r=json.loads(p.read_text());assert r['launch_attempted']
def get(f,name):
 b=io.BytesIO();f.retrbinary('RETR '+name,b.write);return b.getvalue()
with ftplib.FTP() as f:
 f.connect(r['host'],timeout=10);f.login('xbox',os.environ['XWN_FTP_PASSWORD']);f.cwd('/F');b=get(f,'xwn-report-v2.txt')
 r.update(dashboard_available=True,collected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report_sha256=hashlib.sha256(b).hexdigest(),report=b.decode('ascii').rstrip())
 r['report_changed']=r['report_sha256']!=r['report_seed_sha256'];r['native_probe_passed']=False
 p.write_text(json.dumps(r,indent=2)+'\n');print(r['report'])
 assert len(b)==4096 and b.startswith(b'XWN-V2-STARTED\r\n'),'No completed native report'
 if b'XWN-V2-PASS\r\n' in b and b'Failures: 0\r\n' in b:
  data=get(f,'xwn-create-v2.bin');assert data==bytes(((i*37+(i>>8)+0x5a)&255)^0xa5 for i in range(65537))
  r.update(native_probe_passed=True,payload_bytes=len(data),payload_sha256=hashlib.sha256(data).hexdigest())
 p.write_text(json.dumps(r,indent=2)+'\n')
 if not r['native_probe_passed']:raise SystemExit('Native diagnostic returned a failure; inspect its stage/error code.')

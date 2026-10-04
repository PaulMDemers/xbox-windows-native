"""Read and verify the cycle009 report and payload after dashboard return."""
import pathlib,ftplib,io,json,os,hashlib,datetime
k=pathlib.Path(__file__).resolve().parent;p=k/'physical-cycle-009.json';r=json.loads(p.read_text())
assert r['launch_attempted'] and r.get('trace_collected')
def get(f,name):
 b=io.BytesIO();f.retrbinary('RETR '+name,b.write);return b.getvalue()
with ftplib.FTP() as f:
 f.connect(r['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
 f.cwd('/E/Applications/XWNFBoot/loader');assert hashlib.sha256(get(f,'halxboxnt5.dll')).hexdigest()==r['hal_sha256']
 f.cwd('/F');b=get(f,'xwn-report-v2.txt')
 r.update(dashboard_available=True,collected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report_sha256=hashlib.sha256(b).hexdigest(),report=b.decode('ascii').rstrip(),native_probe_passed=False)
 p.write_text(json.dumps(r,indent=2)+'\n');print(r['report'])
 assert len(b)==4096 and b.startswith(b'XWN-V2-STARTED\r\n'),'No completed native report'
 if b'XWN-V2-PASS\r\n' in b and b'Failures: 0\r\n' in b:
  data=get(f,'xwn-create-v2.bin');assert data==bytes(((i*37+(i>>8)+0x5a)&255)^0xa5 for i in range(65537))
  r.update(native_probe_passed=True,payload_bytes=len(data),payload_sha256=hashlib.sha256(data).hexdigest(),status='physical_user_mode_probe_pass_payload_readback_verified_dashboard_available')
 p.write_text(json.dumps(r,indent=2)+'\n')
 if not r['native_probe_passed']:raise SystemExit('Native diagnostic returned a failure; inspect its stage/error code.')

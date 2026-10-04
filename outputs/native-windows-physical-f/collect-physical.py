"""Retrieve fresh physical native Windows evidence after automatic restart."""
import pathlib,ftplib,io,json,hashlib,os,datetime
k=pathlib.Path(__file__).resolve().parent;record=k/'physical-cycle-001.json';r=json.loads(record.read_text());assert r['launch_attempted']
def get(f,name):
 b=io.BytesIO();f.retrbinary('RETR '+name,b.write);return b.getvalue()
with ftplib.FTP() as f:
 f.connect(r['host'],timeout=10);f.login('xbox',os.environ['XWN_FTP_PASSWORD']);f.cwd('/F')
 r.update(dashboard_available=True,last_collection_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 try:log=get(f,'xwn-physical.log')
 except ftplib.error_perm as e:
  r.update(report_missing=str(e).startswith('550'),collection_error=str(e));record.write_text(json.dumps(r,indent=2)+'\n');raise
 (k/'physical-native-result.txt').write_bytes(log)
 r.update(retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),dashboard_available=True,log_sha256=hashlib.sha256(log).hexdigest(),report=log.decode('ascii'))
 record.write_text(json.dumps(r,indent=2)+'\n');print(r['report'])
 assert b'XWN-PHYSICAL-PASS\r\n' in log and b'Failures: 0\r\n' in log
 data=get(f,'xwn-physical-write.bin');assert data==bytes(((i*37+(i>>8)+0x5a)&255)^0xa5 for i in range(65537))
 r.update(native_storage_passed=True,write_payload_sha256=hashlib.sha256(data).hexdigest(),write_payload_bytes=len(data),fresh_native_report_retrieved=True)
 record.write_text(json.dumps(r,indent=2)+'\n')

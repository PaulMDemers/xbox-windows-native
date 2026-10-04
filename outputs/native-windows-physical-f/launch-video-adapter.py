"""Readback-verify a diagnostic miniport replacement and launch exactly once."""
import pathlib,ftplib,io,json,os,hashlib,datetime
k=pathlib.Path(__file__).resolve().parent;record=k/'physical-cycle-005.json';assert not record.exists(),'One-shot launch record already exists'
r={'host':'192.168.50.242','scope':'Physical adapter-resource checkpoint; intentional halt after successful discovery','launch_attempted':False}
new=(k/'artifacts/xboxvnt5-adapter.sys').read_bytes();digest=hashlib.sha256(new).hexdigest()
tests=json.loads((k/'video-adapter-test.json').read_text());assert tests['all_imports_resolve'] and tests['sha256']==digest
validation=json.loads((k/'video-adapter-emulator.json').read_text());assert validation['passed'] and validation['miniport_sha256']==digest
expected=json.loads((k/'physical-cycle-004.json').read_text())['miniport_sha256']
seed=b'XWN-V2-PENDING-20261004\r\n'.ljust(4096,b' ')
def get(f,name,optional=False):
 b=io.BytesIO()
 try:f.retrbinary('RETR '+name,b.write)
 except ftplib.error_perm as e:
  if optional and str(e).startswith('550'):return None
  raise
 return b.getvalue()
with ftplib.FTP() as f:
 f.connect(r['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD']);f.cwd('/F')
 assert get(f,'xwn-report-v2.txt')==seed and get(f,'xwn-create-v2.bin',True) is None
 f.cwd('/F/winnt/system32/drivers');old=get(f,'xboxvnt5.sys');assert hashlib.sha256(old).hexdigest()==expected
 assert get(f,'xboxvnt5.xwn-v4',True) is None and get(f,'xboxvnt5.xwn-v5',True) is None
 f.storbinary('STOR xboxvnt5.xwn-v5',io.BytesIO(new),blocksize=1024);assert get(f,'xboxvnt5.xwn-v5')==new
 f.rename('xboxvnt5.sys','xboxvnt5.xwn-v4');f.rename('xboxvnt5.xwn-v5','xboxvnt5.sys');assert get(f,'xboxvnt5.sys')==new
 r.update(original_miniport_sha256=expected,miniport_sha256=digest,backup='/F/winnt/system32/drivers/xboxvnt5.xwn-v4',probe_report_seed_unchanged=True,emulator_run=validation['run'])
 f.cwd('/E/Applications/XWNFBoot');previous=json.loads((k/'physical-cycle-001.json').read_text())
 for name,key in [('default.xbe','launcher_sha256'),('freeldr.sys','loader_sha256')]:assert hashlib.sha256(get(f,name)).hexdigest()==previous[key]
 r.update(launch_attempted=True,launch_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=previous['command'],status='awaiting_physical_adapter_checkpoint')
 record.write_text(json.dumps(r,indent=2)+'\n')
 try:r['reply']=f.sendcmd(r['command'])
 except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
 record.write_text(json.dumps(r,indent=2)+'\n');print(r)

from pathlib import Path
import ftplib,io,hashlib,json,datetime,os
kit=Path(__file__).resolve().parent;old=kit.parent/'native-windows-physical-loader/package';remote='/E/Applications/XWNLoader'
r={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':'192.168.50.242','destination':remote,'launched':False,'files':[]}
sha=lambda b:hashlib.sha256(b).hexdigest()
def get(f,path):
 b=io.BytesIO();f.retrbinary('RETR '+path,b.write);return b.getvalue()
def absent(f,path):
 try:get(f,path)
 except ftplib.error_perm as e:
  if str(e).startswith('550'):return
  raise
 raise RuntimeError('Expected absent destination: '+path)
with ftplib.FTP() as f:
 f.connect(r['host'],21,timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD']);f.cwd(remote)
 assert get(f,'default.xbe')==(old/'default.xbe').read_bytes()
 original_loader=get(f,'freeldr.sys');original_readme=get(f,'README.txt')
 assert original_loader==(old/'freeldr.sys').read_bytes();assert original_readme==(old/'README.txt').read_bytes()
 for name in ['freeldr-xwn40.sys','README-xwn40.txt','rosload.exe','probe.bin','freeldr.ini']:absent(f,name)
 for name in ['rosload.exe','probe.bin','freeldr.ini','README.txt','freeldr.sys']:
  temporary=name+'.xwn-new';absent(f,temporary);data=(kit/'package'/name).read_bytes()
  print('Uploading '+name,flush=True);f.storbinary('STOR '+temporary,io.BytesIO(data));assert get(f,temporary)==data
  r['files'].append({'name':name,'bytes':len(data),'sha256':sha(data),'staging_readback_equal':True})
 for name in ['rosload.exe','probe.bin','freeldr.ini']:f.rename(name+'.xwn-new',name)
 f.rename('README.txt','README-xwn40.txt');f.rename('README.txt.xwn-new','README.txt')
 assert get(f,'freeldr.sys')==original_loader
 f.rename('freeldr.sys','freeldr-xwn40.sys')
 try:f.rename('freeldr.sys.xwn-new','freeldr.sys')
 except Exception:
  f.rename('freeldr-xwn40.sys','freeldr.sys');raise
 for item in r['files']:
  assert sha(get(f,item['name']))==item['sha256'];item['final_readback_equal']=True
 assert get(f,'freeldr-xwn40.sys')==original_loader
 assert get(f,'README-xwn40.txt')==original_readme
 assert get(f,'default.xbe')==(old/'default.xbe').read_bytes()
r['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();r['previous_loader_retained']='freeldr-xwn40.sys';r['launcher_unchanged']=True
(kit/'ftp-upload.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

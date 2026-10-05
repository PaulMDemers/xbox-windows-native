"""Restore only the four detached Windows files, after physical metadata validation."""
import argparse,datetime,ftplib,hashlib,io,json,os,pathlib,socket
k=pathlib.Path(__file__).resolve().parent;p=k.parent/'native-windows-physical-f'
assert json.loads((k/'physical-repair-validation.json').read_text())['passed']
parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');a=parser.parse_args()
record=k/'restoration.json';assert a.resume or not record.exists(),'Inspect existing restoration before retry'
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
class FTP(ftplib.FTP):
 def ntransfercmd(self,*args,**kwargs):
  s,n=super().ntransfercmd(*args,**kwargs);s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return s,n
def get(f,path):
 b=io.BytesIO();f.retrbinary('RETR '+path,b.write,blocksize=65536);return b.getvalue()
paths=['winnt/system32/drivers/xwnfatx.sys','winnt/system32/wbem/repository/cim.rep','winnt/system32/wbem/repository/$winmgmt.cfg','documents and settings/all users/start menu/programs/accessories/system tools/system information.lnk']
manifest={v['path'].lower():v for v in json.loads((p/'package-manifest.json').read_text())['files']}
files=[]
for path in paths:
 source=k.parent/'native-windows-fatx-forensics/artifacts/xwnfatx-retired-write.sys' if path.endswith('/xwnfatx.sys') else p/'package/F'/path
 data=source.read_bytes();wanted='0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336' if path.endswith('/xwnfatx.sys') else manifest['f/'+path]['sha256']
 assert sha(data)==wanted;files.append((path,data,wanted))
r=json.loads(record.read_text()) if a.resume else dict(scope=__doc__,started_utc=utc(),files=[],complete=False,windows_launched=False)
assert not r['complete'] and not r['windows_launched']
def save():record.write_text(json.dumps(r,indent=2)+'\n')
with FTP() as f:
 f.connect('192.168.50.242',timeout=30);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
 assert json.loads(get(f,'/F/xwn-deploy-v1.json'))==json.loads((p/'physical-cache-preflight.json').read_text())['ownership_marker']
 cycle=json.loads((p/'physical-cycle-013.json').read_text());startup='/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
 assert sha(get(f,startup))==cycle['current_startup_sha256']
 for path,data,wanted in files:
  current=get(f,'/F/'+path)
  assert data.startswith(current) if a.resume else current==b'','Unexpected destination bytes'
 # Check preserved hardware-specific baseline before any restoration.
 for path,wanted in [('/F/winnt/system32/drivers/xboxvnt5.sys',cycle['miniport_sha256']),('/E/Applications/XWNFBoot/loader/halxboxnt5.dll','a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648')]:assert sha(get(f,path))==wanted
 save()
 for path,data,wanted in files:
  current=get(f,'/F/'+path);assert data.startswith(current);at=len(current)
  r['in_progress']=path;save()
  while at<len(data):
   chunk=data[at:at+32768];f.storbinary(('STOR ' if at==0 else 'APPE ')+'/F/'+path,io.BytesIO(chunk),blocksize=1024);at+=len(chunk)
  actual=get(f,'/F/'+path);assert actual==data
  if not any(v['path']==path for v in r['files']):r['files'].append(dict(path=path,bytes=len(data),sha256=wanted,readback_verified=True))
  save();print('Restored and verified',path,flush=True)
 assert sha(get(f,startup))==cycle['current_startup_sha256'];r.pop('in_progress');r.update(complete=True,completed_utc=utc(),startup_unchanged=True);save()
print('Four detached Windows files restored and byte-verified; Windows remains disabled')

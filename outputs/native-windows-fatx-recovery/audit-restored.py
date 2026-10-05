"""Read-only audit of restored Windows binaries and registry copies; never launches Windows."""
import argparse,datetime,ftplib,hashlib,io,json,os,pathlib,socket,struct,subprocess
k=pathlib.Path(__file__).resolve().parent;p=k.parent/'native-windows-physical-f';out=k/'restored-audit.json'
parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');parser.add_argument('--phase',choices=['restored','posttrial','postsoak','postlong'],default='restored');a=parser.parse_args()
out=k/(a.phase+'-audit.json')
if a.phase in ('posttrial','postsoak','postlong'):
 trial=json.loads((k/({'posttrial':'physical-trial.json','postsoak':'physical-soak.json','postlong':'physical-long.json'}[a.phase])).read_text());assert trial.get('collected_utc') and not trial['startup_restart_enabled']
restore=json.loads((k/'restoration.json').read_text());assert restore['complete']
manifest=json.loads((p/'package-manifest.json').read_text())['files'];ext={'.exe','.dll','.sys','.nls','.fon','.ttf','.cpl','.ocx'}
items=[v for v in manifest if v['path'].startswith('F/') and pathlib.PurePosixPath(v['path']).suffix.lower() in ext]
cycle=json.loads((p/'physical-cycle-013.json').read_text());overrides={'f/winnt/system32/drivers/xwnfatx.sys':'0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336','f/winnt/system32/drivers/xboxvnt5.sys':cycle['miniport_sha256']}
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
class FTP(ftplib.FTP):
 def ntransfercmd(self,*args,**kwargs):
  s,n=super().ntransfercmd(*args,**kwargs);s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return s,n
def get(f,path):
 b=io.BytesIO();f.retrbinary('RETR '+path,b.write,blocksize=65536);return b.getvalue()
r=dict(scope=__doc__,started_utc=utc(),checked=0,expected_count=len(items),bytes=0,mismatches=[],hives=[],complete=False)
if a.resume:
 r=json.loads(out.read_text());assert not r['complete'] and r['expected_count']==len(items);r.pop('error',None)
else:assert not out.exists()
def save():out.write_text(json.dumps(r,indent=2)+'\n')
try:
 with FTP() as f:
  f.connect('192.168.50.242',timeout=30);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
  assert json.loads(get(f,'/F/xwn-deploy-v1.json'))==json.loads((p/'physical-cache-preflight.json').read_text())['ownership_marker']
  assert sha(get(f,'/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'))==cycle['current_startup_sha256']
  for v in items[r['checked']:]:
   data=get(f,'/'+v['path']);expected=overrides.get(v['path'].lower(),v['sha256'])
   if sha(data)!=expected:r['mismatches'].append(dict(path=v['path'],expected=expected,actual=sha(data),bytes=len(data)))
   r['checked']+=1;r['bytes']+=len(data)
   if r['checked']%100==0:save();print(r['checked'],'checked;',len(r['mismatches']),'mismatches',flush=True)
  hivepaths={'F/winnt/system32/config/'+n for n in ['system','software','sam','security','default']}
  hivepaths.update(v['path'] for v in manifest if v['path'].startswith('F/') and pathlib.PurePosixPath(v['path']).name.lower() in ['ntuser.dat','usrclass.dat'])
  folder=k/'artifacts'/(a.phase+'-hives');folder.mkdir(exist_ok=True)
  for name in sorted(hivepaths):
   if any(h['path']==name for h in r['hives']):continue
   data=get(f,'/'+name);assert len(data)>=4096 and data[:4]==b'regf';seq1,seq2=struct.unpack_from('<II',data,4);assert seq1==seq2
   checksum=0
   for value in struct.unpack_from('<127I',data):checksum^=value
   checksum=0xfffffffe if checksum==0xffffffff else checksum or 1;assert checksum==struct.unpack_from('<I',data,508)[0]
   target=folder/name.replace('/','__');
   if target.exists():assert target.read_bytes()==data
   else:target.write_bytes(data)
   linux='/mnt/c/'+str(target.resolve()).replace('\\','/')[3:]
   cmd=['wsl','-d','Ubuntu','--','env','LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu','python3','/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-fatx-paging/audit-hive.py',linux]
   tree=json.loads(subprocess.check_output(cmd));r['hives'].append(dict(path=name,bytes=len(data),sha256=sha(data),matching_sequences=True,checksum_valid=True,tree=tree));save()
  r.update(complete=True,passed=not r['mismatches'],completed_utc=utc());save()
except Exception as e:r['error']=repr(e);save();raise
print('Audit complete',r['checked'],'binaries',len(r['hives']),'hives; passed',r['passed'])

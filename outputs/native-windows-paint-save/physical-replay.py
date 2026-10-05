"""One hardware BMP replay with unchanged drivers; collect disables startup first."""
import argparse,datetime,ftplib,hashlib,io,json,os,pathlib,socket
k=pathlib.Path(__file__).resolve().parent
recovery=k.parent/'native-windows-fatx-recovery';physical=k.parent/'native-windows-physical-f'
record=k/'physical-replay.json';folder=k/'artifacts/physical-replay'
startup='/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
trace='/F/winnt/system32/xwn-video-trace.bin'
sha=lambda b:hashlib.sha256(b).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
previous=json.loads((recovery/'physical-paint.json').read_text())
checks={
 '/F/winnt/system32/drivers/xwnfatx.sys':previous['filesystem_sha256'],
 '/F/winnt/system32/drivers/xboxvnt5.sys':previous['miniport_sha256'],
 previous['miniport_backup']:previous['previous_miniport_sha256'],
 '/E/Applications/XWNFBoot/loader/halxboxnt5.dll':previous['hal_sha256']}
initial=json.loads((physical/'physical-cycle-001.json').read_text())
checks.update({'/E/Applications/XWNFBoot/'+name:initial[key] for name,key in
 [('default.xbe','launcher_sha256'),('freeldr.sys','loader_sha256')]})
logs={'trace.bin':trace,'system.evt':'/F/winnt/system32/config/sysevent.evt',
      'application.evt':'/F/winnt/system32/config/appevent.evt',
      'user-partial.bmp':'/F/Documents and Settings/win2k/Desktop/untitled.bmp'}
class FTP(ftplib.FTP):
 def ntransfercmd(self,*args,**kwargs):
  s,n=super().ntransfercmd(*args,**kwargs);s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return s,n
def get(f,path,optional=False):
 b=io.BytesIO()
 def receive(data):
  assert b.tell()+len(data)<=16*1024*1024;b.write(data)
 try:f.retrbinary('RETR '+path,receive,blocksize=65536)
 except ftplib.error_perm as e:
  if optional and str(e).startswith('550'):return None
  raise
 return b.getvalue()
def put(f,path,data):
 for at in range(0,max(1,len(data)),32768):
  f.storbinary(('STOR ' if at==0 else 'APPE ')+path,io.BytesIO(data[at:at+32768]),blocksize=1024)
 assert get(f,path)==data,path
def preserve(name,data):
 p=folder/name
 if p.exists():assert p.read_bytes()==data,'Preserved evidence differs: '+name
 else:p.write_bytes(data)
 return dict(bytes=len(data),sha256=sha(data))
def save():record.write_text(json.dumps(r,indent=2)+'\n')
def verify(f):
 for path,expected in checks.items():assert sha(get(f,path))==expected,path

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['launch','collect']);a=p.parse_args()
 folder.mkdir(parents=True,exist_ok=True)
 with FTP() as f:
  f.connect('192.168.50.242',timeout=30);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
  assert json.loads(get(f,'/F/xwn-deploy-v1.json'))==json.loads((physical/'physical-cache-preflight.json').read_text())['ownership_marker']
  if a.action=='launch':
   assert not record.exists(),'Never repeat an existing hardware launch record'
   assert json.loads((recovery/'postpaint-audit.json').read_text())['passed']
   assert json.loads((recovery/'physical-paint-allocation.json').read_text())['allocation_consistent']
   qualification=json.loads((k/'nt5-paint-runner-001-save-audit.json').read_text());assert qualification['passed']
   assert qualification['runner_log']=='ATTEMPT_ONCE\r\nREPLAY_EXIT_ZERO\r\nNORMAL_RESTART_REQUEST\r\n'
   events=json.loads((k/'nt5-paint-runner-001-system-events.json').read_text())['records'];assert events[-1]['event_id']==6006
   verify(f);baseline=get(f,startup);assert sha(baseline)==previous['startup_sha256']
   f.cwd('/F');assert 'xwnpaint' not in [n.replace('\\','/').rstrip('/').split('/')[-1].lower() for n in f.nlst()]
   fixture=json.loads((k/'runner-fixture.json').read_text());payloads={}
   for item in fixture['helpers']:
    name=pathlib.PurePosixPath(item['path']).name;data=(k/'artifacts'/name).read_bytes();assert sha(data)==item['sha256'];payloads[name]=data
   image=(k/'artifacts/images/scribble.bmp').read_bytes();assert sha(image)=='ad7bfd3fa51af5ae5a666f13888b755bf0cd17a4bbe4c1dbb4e81742d2b148d8';payloads['scribble.bmp']=image
   script=b'@echo off\r\nC:\\xwnpaint\\runner.exe\r\nexit\r\n';assert sha(script)==fixture['startup_sha256']
   r=dict(scope=__doc__,created_utc=utc(),launch_attempted=False,startup_restart_enabled=False,
    startup_sha256=sha(script),previous_startup_sha256=sha(baseline),expected_drivers=checks,
    filesystem_sha256=previous['filesystem_sha256'],miniport_sha256=previous['miniport_sha256'],
    preserved={},payloads={name:dict(bytes=len(data),sha256=sha(data)) for name,data in payloads.items()})
   r['preserved']['startup.cmd']=preserve('before-startup.cmd',baseline)
   for name,path in logs.items():r['preserved'][name]=preserve('before-'+name,get(f,path))
   save()
   try:
    f.mkd('/F/xwnpaint')
    for name,data in payloads.items():put(f,'/F/xwnpaint/'+name,data)
    put(f,trace,b'XWN-VID-TRACE01\n'+bytes(4080));put(f,startup,script)
    r['startup_restart_enabled']=True;save();verify(f)
    r.update(launch_attempted=True,launch_utc=utc(),command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe');save()
    try:r['reply']=f.sendcmd(r['command'])
    except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
    save();print('Single hardware replay launched:',r.get('reply',r.get('uncertain_reply')))
   except Exception as e:
    r['error']=repr(e);save()
    if not r['launch_attempted']:
     put(f,startup,baseline);r['startup_restart_enabled']=False;save()
    raise
  else:
   r=json.loads(record.read_text());assert r['launch_attempted'] and not r.get('collected_utc')
   baseline=(folder/'before-startup.cmd').read_bytes();assert sha(baseline)==r['previous_startup_sha256']
   current=get(f,startup);assert sha(current) in (r['startup_sha256'],r['previous_startup_sha256'])
   if current!=baseline:put(f,startup,baseline)
   r['startup_restart_enabled']=False;save()
   try:
    r['collected']={}
    for name,path in {**logs,'attempt.log':'/F/xwnpaint/attempt.log','replay.log':'/F/xwnpaint/replay.log',
                     **{f'replay{i:02d}.bmp':f'/F/xwnpaint/replay{i:02d}.bmp' for i in range(16)}}.items():
     data=get(f,path,optional=name.startswith('replay') or name=='attempt.log')
     r['collected'][name]=None if data is None else preserve('after-'+name,data);save()
    r['driver_checks']={path:sha(get(f,path))==expected for path,expected in checks.items()}
    r['payload_checks']={name:sha(get(f,'/F/xwnpaint/'+name))==info['sha256'] for name,info in r['payloads'].items()}
    def text(name):
     return (folder/('after-'+name)).read_bytes().decode('ascii',errors='replace') if r['collected'][name] else ''
    r['runner_log']=text('attempt.log');r['replay_log']=text('replay.log')
    expected=r['payloads']['scribble.bmp']['sha256']
    r['all_images_match']=all(r['collected'][f'replay{i:02d}.bmp'] and r['collected'][f'replay{i:02d}.bmp']['sha256']==expected for i in range(16))
    r['user_partial_unchanged']=r['collected']['user-partial.bmp']==r['preserved']['user-partial.bmp']
    r['workload_passed']=(r['all_images_match'] and r['replay_log'].count('CASE_PASS ')==16 and '\nPASS 16 ' in r['replay_log']
      and r['runner_log']=='ATTEMPT_ONCE\r\nREPLAY_EXIT_ZERO\r\nNORMAL_RESTART_REQUEST\r\n' and 'FAIL_' not in r['replay_log']
      and all(r['driver_checks'].values()) and all(r['payload_checks'].values()) and r['user_partial_unchanged'])
    r.update(collected_utc=utc(),qualification_pending='Event review and full allocation/binary/hive checks');save()
    print('Collected; startup disabled; bounded workload passed:',r['workload_passed'])
   except Exception as e:r['collection_error']=repr(e);save();raise

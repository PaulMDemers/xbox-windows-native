"""Launch/collect the validated E-only read-only hardware preflight; never writes F: or boots Windows."""
import argparse,datetime,ftplib,hashlib,io,json,os,pathlib,sys
k=pathlib.Path(__file__).resolve().parent;p=k.parent/'native-windows-physical-f';research=k.parent/'native-windows-fatx-forensics'
parser=argparse.ArgumentParser();parser.add_argument('action',choices=['check','launch','collect']);a=parser.parse_args()
record=k/'physical-preflight.json';remote='/E/Applications/XWNFatCheck'
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def get(f,path,limit=200*1024*1024):
 result=io.BytesIO()
 def receive(b):
  if result.tell()+len(b)>limit:raise ValueError('Unexpected transfer size')
  result.write(b)
 f.retrbinary('RETR '+path,receive);return result.getvalue()
def save():record.write_text(json.dumps(r,indent=2)+'\n')
validation=json.loads((k/'validation.json').read_text());assert validation['emulator_snapshot_passed'] and not validation['top_overlay_F_extents']
assert json.loads((k/'analyzer-tests.json').read_text())['passed']
xbe=(k/'artifacts/default.xbe').read_bytes();assert sha(xbe)==validation['xbe_sha256']
# The next experiment starts with metadata collection, not a damaged Windows boot.
for run in ['nt5-physical-f-high-allocation-r14','nt5-physical-f-high-allocation-r15']:
 q=json.loads((research/(run+'-qualification.json')).read_text());assert q['passed'] and q['lifetime']['passed']
 assert q['filesystem_sha256']=='0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336'
assert q['lifetime']['reboot_verified'] and q['lifetime']['long_soak_completed']
assert sha((research/'artifacts/xwnfatx-retired-write.sys').read_bytes())==q['filesystem_sha256']
assert json.loads((research/'retired-replay.json').read_text())['passed']
cycle=json.loads((p/'physical-cycle-013.json').read_text());assert not cycle['startup_restart_enabled']
if a.action=='check':
 already_launched=record.exists()
 r=dict(checked_utc=utc(),next_readonly_hardware_test_ready=not already_launched,windows_boot_ready=False,
        candidate_sha256=q['filesystem_sha256'],preflight_xbe_sha256=sha(xbe),
        qualifications=['nt5-physical-f-high-allocation-r14','nt5-physical-f-high-allocation-r15'],
        hardware_access_performed=already_launched,
        next_step=('Inspect the existing capture and rehearse scoped metadata repair before Windows restoration.' if already_launched else 'Collect full F metadata, assess ownership, then scope Windows-only restoration before boot.'))
 (k/'readiness.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));sys.exit(0)
with ftplib.FTP() as f:
 f.connect('192.168.50.242',timeout=30);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
 marker=json.loads((p/'physical-cache-preflight.json').read_text())['ownership_marker'];assert json.loads(get(f,'/F/xwn-deploy-v1.json',65536))==marker
 startup='/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
 assert sha(get(f,startup,65536))==cycle['current_startup_sha256']
 if a.action=='launch':
  assert not record.exists(),'Existing launch record: collect or inspect, never blindly relaunch'
  f.cwd('/E/Applications');assert 'xwnfatcheck' not in [n.replace('\\','/').rstrip('/').split('/')[-1].lower() for n in f.nlst()]
  r=dict(scope=__doc__,host=f.host,remote_directory=remote,xbe_sha256=sha(xbe),created_utc=utc(),launch_attempted=False,source_access='Partition6 GENERIC_READ only',output_partition='E')
  save();f.mkd(remote)
  owner=json.dumps(dict(project='xbox-windows-native',purpose='full-F-readonly-preflight',xbe_sha256=sha(xbe))).encode()
  for name,data in [('owner.json',owner),('default.xbe',xbe)]:
   f.storbinary('STOR '+remote+'/'+name,io.BytesIO(data));assert get(f,remote+'/'+name)==data
  r.update(launch_attempted=True,launch_utc=utc(),command=r'SITE EXEC E:\Applications\XWNFatCheck\default.xbe');save()
  try:r['reply']=f.sendcmd(r['command'])
  except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
  save();print('Read-only preflight launch recorded; collect after dashboard returns.')
 else:
  r=json.loads(record.read_text());assert r['launch_attempted'] and not r.get('collected_utc');assert sha(get(f,remote+'/default.xbe'))==r['xbe_sha256']
  assert json.loads(get(f,remote+'/owner.json',65536))==dict(project='xbox-windows-native',purpose='full-F-readonly-preflight',xbe_sha256=r['xbe_sha256'])
  out=k/'artifacts/physical-001';out.mkdir(exist_ok=True);r['files']=[]
  for name in ['snapshot.txt','fat-metadata.bin','directories.bin']:
   data=get(f,remote+'/'+name);target=out/name
   if target.exists():assert target.read_bytes()==data,'Preserve differing evidence'
   else:target.write_bytes(data)
   r['files'].append(dict(name=name,bytes=len(data),sha256=sha(data)))
  report=(out/'snapshot.txt').read_text();r.update(report=report,collected_utc=utc(),snapshot_completed='SNAPSHOT_COMPLETE success=1 ' in report);save();print(report)

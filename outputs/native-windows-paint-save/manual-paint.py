"""One manual Paint repeatability boot; no driver or startup changes, no reboot timer."""
import argparse,importlib,json,os,struct
m=importlib.import_module('physical-replay');k=m.k
record=k/'physical-paint-repeat.json';m.folder=k/'artifacts/physical-paint-repeat'
load=lambda p:json.loads(p.read_text())
paths={f'paint-repeat-{i:02d}.bmp':f'/F/Documents and Settings/win2k/Desktop/paint-repeat-{i:02d}.bmp' for i in range(1,4)}
def save():record.write_text(json.dumps(r,indent=2)+'\n')
def bitmap(data):
 result=dict(bytes=len(data),sha256=m.sha(data),complete_24bit_bmp=False)
 if len(data)>=54 and data[:2]==b'BM':
  size=struct.unpack_from('<I',data,2)[0];offset=struct.unpack_from('<I',data,10)[0]
  header,width,height,planes,bpp,compression=struct.unpack_from('<IiiHHI',data,14)
  result.update(declared_bytes=size,pixel_offset=offset,width=width,height=height,bpp=bpp,compression=compression)
  if header==40 and width>0 and height!=0 and planes==1 and bpp==24 and compression==0:
   stride=(width*3+3)&~3
   result['complete_24bit_bmp']=offset>=54 and size==len(data)==offset+stride*abs(height)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['launch','collect']);a=p.parse_args()
 m.folder.mkdir(parents=True,exist_ok=True)
 with m.FTP() as f:
  f.connect('192.168.50.242',timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
  assert json.loads(m.get(f,'/F/xwn-deploy-v1.json'))==load(m.physical/'physical-cache-preflight.json')['ownership_marker']
  if a.action=='launch':
   assert not record.exists(),'Existing record: never relaunch blindly'
   assert load(k/'physical-matched-qualification.json')['passed']
   prior=load(k/'physical-matched.json');assert not prior['startup_restart_enabled']
   m.verify(f);startup=m.get(f,m.startup);assert m.sha(startup)==prior['previous_startup_sha256']
   for path in paths.values():assert m.get(f,path,optional=True) is None,'Choose fresh filenames; never overwrite user files'
   r=dict(scope=__doc__,created_utc=m.utc(),launch_attempted=False,startup_restart_enabled=False,startup_paint_enabled=False,
          startup_sha256=m.sha(startup),expected_drivers=m.checks,
          filesystem_sha256=prior['filesystem_sha256'],miniport_sha256=prior['miniport_sha256'],
          expected_user_paths=paths,preserved={},manual_observation='Awaiting user draw/save/reopen observations')
   r['preserved']['startup.cmd']=m.preserve('before-startup.cmd',startup)
   for name,path in m.logs.items():r['preserved'][name]=m.preserve('before-'+name,m.get(f,path))
   save()
   try:
    m.put(f,m.trace,b'XWN-VID-TRACE01\n'+bytes(4080))
    assert m.get(f,m.startup)==startup;m.verify(f)
    r.update(launch_attempted=True,launch_utc=m.utc(),command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe');save()
    try:r['reply']=f.sendcmd(r['command'])
    except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
    save();print('Manual desktop launch accepted:',r.get('reply',r.get('uncertain_reply')))
   except Exception as e:r['error']=repr(e);save();raise
  else:
   r=load(record);assert r['launch_attempted'] and not r.get('collected_utc')
   assert m.sha(m.get(f,m.startup))==r['startup_sha256']
   try:
    r['collected']={};r['saved_bitmaps']={}
    for name,path in {**m.logs,**r['expected_user_paths']}.items():
     data=m.get(f,path,optional=name in r['expected_user_paths'])
     r['collected'][name]=None if data is None else m.preserve('after-'+name,data)
     if name in r['expected_user_paths']:r['saved_bitmaps'][name]=None if data is None else bitmap(data)
     save()
    r['driver_checks']={path:m.sha(m.get(f,path))==expected for path,expected in r['expected_drivers'].items()}
    r['user_partial_unchanged']=r['collected']['user-partial.bmp']==r['preserved']['user-partial.bmp']
    r.update(collected_utc=m.utc(),qualification_pending='User observations, event review and independent allocation/binary/hive checks')
    save();print('Evidence collected; no automatic pass inferred from file presence.')
   except Exception as e:r['collection_error']=repr(e);save();raise

"""Read-only audit of a stopped, owned NTFS regression fixture."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,struct,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
assert re.fullmatch(r'nt5-ntfs-shutdown-[0-9]+',a.run)
ws=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
root=Path('/home/paul/xbox-windows-native');runtime=root/'toolchains/offline-disk/root'
run=ws/'work/runs'/a.run;source=run/'hdd.qcow2';temp=root/'fixtures'/('audit-'+a.run)
assert (run/'cleanup.json').exists() and not temp.exists();temp.mkdir()
env=dict(os.environ,LD_LIBRARY_PATH=str(runtime/'usr/lib/x86_64-linux-gnu'))
def sha(path):
 with path.open('rb') as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
r={'scope':'Read-only NTFS regression audit; selected immutable files and reachable registry trees, not a complete filesystem consistency proof',
   'source_sha256':sha(source),'immutable_files':[],'registry_trees':[],'logs':{}}
try:
 raw=temp/'disk.raw';part=temp/'windows.ntfs'
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('rb') as fp,part.open('xb') as dst:
  m=fp.read(512);assert m[450]==7;start,count=struct.unpack_from('<II',m,454)
  assert start==16777216 and count*512<=4*1024**3;fp.seek(start*512);left=count*512
  while left:
   data=fp.read(min(left,4*1024**2));assert data
   if data.strip(b'\0'):dst.write(data)
   else:dst.seek(len(data),1)
   left-=len(data)
  dst.truncate(count*512)
 def cat(path):
  canonical=expected.get(path.lower(),{}).get('path',path)
  return subprocess.check_output([str(runtime/'usr/bin/ntfscat'),str(part),canonical],env=env)
 volume=subprocess.check_output([str(runtime/'usr/bin/ntfscat'),'-a','0x70','-i','3',str(part)],env=env)
 assert len(volume)==12
 r['volume_information']={'major':volume[8],'minor':volume[9],'flags':struct.unpack_from('<H',volume,10)[0]}
 check=subprocess.run([str(runtime/'usr/bin/ntfsfix'),'-n',str(part)],env=env,capture_output=True,text=True)
 r['ntfsfix_read_only']={'arguments':['-n'],'exit_code':check.returncode,'stdout':check.stdout,'stderr':check.stderr}
 expected={f['path'].lower():f for f in json.loads((ws/'outputs/native-windows-fatx-runtime/fatx-boot-disk-001.json').read_text())['files']}
 names=['/WINNT/explorer.exe']
 names+=['/WINNT/system32/'+n for n in ['ntoskrnl.exe','ntdll.dll','kernel32.dll','user32.dll','gdi32.dll','winlogon.exe','csrss.exe','smss.exe','services.exe','lsass.exe','shell32.dll','advapi32.dll','win32k.sys']]
 names+=['/WINNT/system32/drivers/'+n for n in ['ntfs.sys','atapi.sys','disk.sys','classpnp.sys','pci.sys','pciide.sys','partmgr.sys','ftdisk.sys','openhci.sys','usbhub.sys','hidclass.sys','kbdclass.sys','mouclass.sys','ndis.sys','tcpip.sys']]
 for name in names:
  try:
   actual=hashlib.sha256(cat(name)).hexdigest();expected_sha=expected[name.lower()]['sha256']
   r['immutable_files'].append({'path':name,'sha256':actual,'passed':actual==expected_sha})
  except Exception as ex:r['immutable_files'].append({'path':name,'passed':False,'error':repr(ex)})
 hives=['/WINNT/system32/config/'+n for n in ['system','software','sam','security','default']]
 hives+=['/Documents and Settings/Win2k/NTUSER.DAT','/Documents and Settings/Win2k/Local Settings/Application Data/Microsoft/Windows/UsrClass.dat']
 for name in hives:
  try:
   data=cat(name);copy=temp/'hive-copy';copy.write_bytes(data)
   result=json.loads(subprocess.check_output([sys.executable,str(ws/'outputs/native-windows-fatx-paging/audit-hive.py'),str(copy)],env=env))
   result['path']=name;result['header_sequences']=list(struct.unpack_from('<II',data,4));r['registry_trees'].append(result);copy.unlink()
  except Exception as ex:r['registry_trees'].append({'path':name,'passed':False,'error':repr(ex)})
 logs=run/'guest-logs';logs.mkdir(exist_ok=True)
 for name in ['xwn-check.log','xwn-sound-stress.log','xwn-cycle.log','xwn-ipconfig.txt','xwn-renew.txt','xwn-ping-after.txt']:
  try:
   data=cat('/'+name);(logs/name).write_bytes(data);r['logs'][name]={'sha256':hashlib.sha256(data).hexdigest(),'text':data.decode('ascii',errors='replace')}
  except Exception as ex:r['logs'][name]={'error':repr(ex)}
 text=r['logs'].get('xwn-check.log',{}).get('text','')
 r['endurance_passed']=all(s in text for s in ['4 MiB write/flush/reopen/read comparison passed','GUI response passed','8 MiB memory retention passed across 20 intervals','Failures: 0'])
 r['passed']=all(f['passed'] for f in r['immutable_files']) and all(h['passed'] for h in r['registry_trees']) and r['endurance_passed'] and check.returncode==0
 assert sha(source)==r['source_sha256'];r['source_preserved']=True
finally:
 assert temp.resolve().parent==(root/'fixtures').resolve();shutil.rmtree(temp);r['temporary_raw_removed']=True
 (run/'cold-integrity.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))

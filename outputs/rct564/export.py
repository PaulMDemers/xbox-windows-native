"""MIT. Read-only full game export before this fixture is closed; private assets."""
import hashlib,json,struct,sys,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn564/pc001')
sys.path.insert(0,str(K.parent/'crypto-persistence423'));from ntfs_read002 import Reader,sha
sys.path.insert(0,str(W/'tools'));from build_space import require_space
from fatx_names import check_path
sys.path.insert(0,str(W/'work/python-packages'));from Registry import Registry
read=lambda p:json.loads(p.read_text())
out=K/'transfer001.json';assert not out.exists();r=read(K/'ntfs-phase1.json');cold=read(K/'ntfs-cold1-002.json')
assert r['closed'] and r['exit_code']==0 and not r['deadline'] and not r.get('host_quit')
assert cold['complete'] and cold['normal_shutdown_delta']==1 and sha(P/'disk.qcow2')==cold['disk_sha256']
assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in cold['hives'])
manifest=read(P/'cold1-002/manifest.json');rows=[v for n,v in manifest.items() if n.startswith('xwn565-kit/game/')]
assert 400<len(rows)<1000;total=sum(v['bytes'] for v in rows);assert total<400*1024**2
dest=P.parent/'transfer001';assert not dest.exists();require_space(dest,20+total/1024**3+.125);dest.mkdir()
files={};directories={'game','game/Saved Games'}
with Reader(P/'disk.qcow2') as reader:
 for row in rows:
  relative=row['path'].split('/',1)[1];check_path(relative,437);assert row['bytes']<=64*1024**2
  assert relative.lower() not in {n.lower() for n in files};b=reader.read(row['path']);assert hashlib.sha256(b).hexdigest()==row['sha256']
  p=dest/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);assert sha(p)==row['sha256']
  files[relative]=dict(path=str(p),bytes=len(b),sha256=row['sha256'])
  parts=relative.split('/')[:-1]
  directories.update('/'.join(parts[:i]) for i in range(1,len(parts)+1))
 for name in ['runner.txt','registry.bin']:
  b=reader.read('xwn565/'+name);p=dest/name;p.write_bytes(b)
assert sha(P/'disk.qcow2')==cold['disk_sha256']
log=(dest/'runner.txt').read_text();assert 'registry_restored=1\n' in log and 'restart_requested=1\n' in log and 'game_exit=0\n' in log and 'forced_terminate=' not in log
data=(dest/'registry.bin').read_bytes();assert len(data)==1048
reg=Registry.Registry(str(P/'cold1-002/files/WINNT/system32/config/software'));key=reg.open('Fish Technology Group\\RollerCoaster Tycoon Setup')
restored={}
for i,name in enumerate(['Path','Language']):
 exists,kind,size=struct.unpack_from('<III',data,i*524);raw=data[i*524+12:i*524+12+size];assert exists==1
 value=raw.rstrip(b'\0').decode('cp1252') if kind==1 else struct.unpack('<I',raw)[0]
 assert key.value(name).value()==value;restored[name]=value
assert restored==dict(Path='C:\\xwn565-kit\\game',Language=0)
exe=next(v for n,v in files.items() if n.lower()=='game/rct.exe')
assert exe['sha256']=='bdfebd64383b231de0252fe0726523d1c45aa2c4da919c2d7ed8bfb7aaa05c76'
result=dict(passed=True,files=files,directories=sorted(directories,key=lambda s:(s.count('/'),s.lower())),total_bytes=total,private_root=str(dest),runner_log=log,restored_registry=restored,source_disk_sha256=cold['disk_sha256'],game_without_original_disc=True,scope='Exact private transfer preparation and PC helper result; no Xbox qualification',physical_access=False)
out.write_text(json.dumps(result,indent=2)+'\n');print('Exported',len(files),'files',total,'bytes; registry restored and game exited normally')

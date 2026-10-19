"""MIT. Reconstruct missing original-disc Data files, without changing installed assets."""
import hashlib,io,json,sys,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pycdlib
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
media=read(K.parent/'rct559/media001.json')[1];original=Path(media['path']);assert sha(original.read_bytes())==media['sha256']
installed=read(Path('C:/xwn564/pc001/cold1-002/manifest.json'))
rec=read(K.parent/'rct564/receipt001.json');cfg=Path(rec['files']['xwn565-kit/game/Data/Game.cfg']['path'].replace('/mnt/c/','C:/'));assert sha(cfg.read_bytes())==rec['files']['xwn565-kit/game/Data/Game.cfg']['sha256']
exe=Path('C:/xwn565/runner-build004/run565.exe');build=read(K.parent/'rct565/runner-build004.json');assert build['status']=='compiled' and sha(exe.read_bytes())==build['rows'][0]['sha256']
out=K/'media001.json';dest=Path('C:/xwn566/helper-media001.iso');assert not dest.exists() and not out.exists()
src=pycdlib.PyCdlib();src.open(str(original));iso=pycdlib.PyCdlib();iso.new(interchange_level=3,vol_ident='XWN566HELPER');iso.add_directory('/DATA');buffers=[];added=[];same=[]
for row in media['files']:
 if not row['path'].lower().startswith('/data/'):continue
 fp=io.BytesIO();src.get_file_from_iso_fp(fp,joliet_path=row['path']);b=fp.getvalue();assert len(b)==row['bytes']
 existing=installed.get('xwn565-kit/game'+row['path'].lower())
 if existing:
  assert existing['sha256']==sha(b),row['path'];same.append(row['path']);continue
 name=row['path'].rsplit('/',1)[1].upper();fp=io.BytesIO(b);buffers.append(fp);iso.add_fp(fp,len(b),iso_path='/DATA/'+name+';1');added.append(dict(original=row['path'],name=name,bytes=len(b),sha256=sha(b)))
batch=b'@echo off\r\ncopy /Y D:\\DATA\\* C:\\xwn565-kit\\game\\Data\\\r\nif errorlevel 1 goto fail\r\ncopy /Y D:\\GAME.CFG C:\\xwn565-kit\\game\\Data\\Game.cfg\r\nif errorlevel 1 goto fail\r\necho COPY COMPLETE\r\nexit\r\n:fail\r\necho COPY FAILED\r\npause\r\n'
for name,b in [('RUN565.EXE',exe.read_bytes()),('GAME.CFG',cfg.read_bytes()),('PREP.CMD',batch)]:
 fp=io.BytesIO(b);buffers.append(fp);iso.add_fp(fp,len(b),iso_path='/'+name+';1')
assert shutil.disk_usage('C:/').free-sum(r['bytes'] for r in added)-16*1024**2>=20.125*1024**3
iso.write(str(dest));iso.close();src.close()
out.write_text(json.dumps(dict(path=str(dest),sha256=sha(dest.read_bytes()),bytes=dest.stat().st_size,original_iso_sha256=media['sha256'],added=added,existing_exact=same,config_sha256=sha(cfg.read_bytes()),runner_sha256=sha(exe.read_bytes()),copy_script=batch.decode(),scope='Only original disc data absent from full installation; no game executable modification'),indent=2)+'\n')
print('Missing disc data:',len(added),'files,',sum(r['bytes'] for r in added),'bytes; unchanged existing:',len(same))

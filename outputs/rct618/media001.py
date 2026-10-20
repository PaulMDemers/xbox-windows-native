"""Small supplementary CD; original retail CD supplies independently mapped files."""
import hashlib,io,json,sys,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pycdlib
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
m=json.loads((K.parent/'rct577/disc-mapping001.json').read_text())
b=json.loads((K/'build001.json').read_text());assert b['status']=='compiled'
p=Path('C:/xwn618/helper001.iso');assert not p.exists() and not (K/'media001.json').exists()
assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
iso=pycdlib.PyCdlib();iso.new(interchange_level=3,joliet=3,vol_ident='XWN618COPY')
dirs={'': ''};files={};counter=0
def add(name,path):
 global counter
 parent=''
 for part in name.split('/')[:-1]:
  child=parent+'/'+part
  if child not in dirs:
   counter+=1;internal=dirs[parent]+'/D'+str(counter);iso.add_directory(iso_path=internal,joliet_path=child);dirs[child]=internal
  parent=child
 counter+=1;internal=dirs[parent]+'/F'+str(counter)+'.BIN;1'
 iso.add_file(str(path),iso_path=internal,joliet_path='/'+name);files[name]=dict(bytes=path.stat().st_size,sha256=sha(path))
for name,v in sorted(m['supplemental_files'].items()):
 path=Path(v['private_path']);assert sha(path)==v['sha256'];add(name,path)
extra=json.loads((K/'source001.json').read_text())['save'];saved=Path(extra['path']);assert sha(saved)==extra['sha256'];add('game/Saved Games/XWN593.SV4',saved)
for row in b['rows']:
 path=Path(row['path'].replace('/mnt/c/','C:/'));assert sha(path)==row['sha256'];add(path.name.upper(),path)
retail=Path(m['source_iso']['path']);assert sha(retail)==m['source_iso']['sha256']
original=pycdlib.PyCdlib();original.open(str(retail))
lines=['@echo off','if exist C:\\xwn618-kit goto fail','if not exist D:\\VERIFY618.EXE goto fail','mkdir C:\\xwn618-kit','xcopy D:\\game C:\\xwn618-kit\\game\\ /E /I /Y','if errorlevel 1 goto fail']
for name,v in sorted(m['mapped_files'].items()):
 f=io.BytesIO();original.get_file_from_iso_fp(f,joliet_path=v['source']);assert hashlib.sha256(f.getvalue()).hexdigest()==v['sha256']
 dst='C:\\xwn618-kit\\'+name.replace('/','\\');src='E:'+v['source'].replace('/','\\')
 parent=dst.rsplit('\\',1)[0];lines+=['if not exist "'+parent+'" mkdir "'+parent+'"','copy "'+src+'" "'+dst+'"','if errorlevel 1 goto fail']
original.close()
lines+=['copy D:\\RUN618.EXE C:\\xwn618-kit\\RUN618.EXE','if errorlevel 1 goto fail','copy D:\\TRACE618.EXE C:\\xwn618-kit\\TRACE618.EXE','if errorlevel 1 goto fail','copy D:\\VERIFY618.EXE C:\\xwn618-kit\\VERIFY618.EXE','if errorlevel 1 goto fail','attrib -R C:\\xwn618-kit\\*.* /S','C:\\xwn618-kit\\VERIFY618.EXE','if errorlevel 1 goto fail','echo COPY VERIFIED - EJECT BOTH CDS BEFORE RUNNING','exit',':fail','echo XWN618 COPY FAILED - DO NOT RUN GAME','pause']
batch=('\r\n'.join(lines)+'\r\n').encode('ascii');fp=io.BytesIO(batch);iso.add_fp(fp,len(batch),iso_path='/PREP.CMD;1',joliet_path='/PREP.CMD');iso.write(str(p));iso.close()
r=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,files=files,copy_script=batch.decode(),retail_sha256=sha(retail),physical_access=False)
(K/'media001.json').write_text(json.dumps(r,indent=2)+'\n');print('Small media',p.stat().st_size)

"""MIT. Private helper ISO from independently pinned retail export, not a runtime."""
import hashlib, io, json, shutil, sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages')); import pycdlib
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
rows=json.loads((K.parent/'rct565/package001.json').read_text())['files']
game={n:r for n,r in rows.items() if n.startswith('game/')}
dest=Path('C:/xwn569/helper001.iso'); out=K/'media001.json'
assert not dest.exists() and not out.exists()
exe=Path('C:/xwn569/runner-build002/run569.exe')
build=json.loads((K/'runner-build002.json').read_text())
assert build['status']=='compiled' and sha(exe)==build['rows'][0]['sha256']
need=sum(r['bytes'] for r in game.values())+16*1024**2
assert shutil.disk_usage('C:/').free-need>=21*1024**3
for n,r in game.items(): assert sha(r['path'])==r['sha256'],n
iso=pycdlib.PyCdlib(); iso.new(interchange_level=3,joliet=3,vol_ident='XWN569INPUT')
dirs={'game'}
for n in game:
    p=Path(n).parent
    while p.as_posix()!='.': dirs.add(p.as_posix()); p=p.parent
mapped={}
for i,n in enumerate(sorted(dirs,key=lambda x:(x.count('/'),x))):
    parent=Path(n).parent.as_posix()
    prefix=mapped[parent] if parent!='.' else ''
    mapped[n]=prefix+f'/D{i:04d}'
    iso.add_directory(mapped[n],joliet_path='/'+n)
for i,(n,r) in enumerate(sorted(game.items())):
    iso.add_file(r['path'],iso_path=mapped[Path(n).parent.as_posix()]+f'/F{i:05d}.DAT;1',joliet_path='/'+n)
batch=(r'''@echo off
if exist C:\xwn569-kit goto fail
mkdir C:\xwn569-kit
xcopy D:\game C:\xwn569-kit\game\ /E /I /Y
if errorlevel 1 goto fail
copy /Y D:\RUN569.EXE C:\xwn569-kit\RUN569.EXE
if errorlevel 1 goto fail
C:\xwn569-kit\RUN569.EXE /pc800
exit
:fail
echo XWN569 COPY FAILED - preserve this control
pause
''').replace('\n','\r\n').encode('ascii')
fp=io.BytesIO(batch)
iso.add_fp(fp,len(batch),iso_path='/PREP.CMD;1',joliet_path='/PREP.CMD')
iso.add_file(str(exe),iso_path='/RUN569.EXE;1',joliet_path='/RUN569.EXE')
iso.write(str(dest));iso.close()
out.write_bytes((json.dumps(dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha(dest),source_package_sha256=sha(K.parent/'rct565/package001.json'),game_files=len(game),game_bytes=sum(r['bytes'] for r in game.values()),runner_sha256=sha(exe),copy_script=batch.decode(),physical_access=False),indent=2)+'\n').encode())
print('Private helper ISO created',dest.stat().st_size)

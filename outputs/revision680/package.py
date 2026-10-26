"""Record retained build iterations and assemble a local-only watched-test kit."""
import datetime,hashlib,json,shutil,subprocess,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('C:/xwn680/package001')
assert not O.exists() and not (K/'builds001.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert shutil.disk_usage('C:/').free > 20.01*1024**3
r={'physical_access':False,'deployed':False,'selected_build':'build003','builds':{},'sdk':{}}
for name in ['build001','build002','build003']:
    p=Path('C:/xwn680')/name
    assert 'CXBE' in (p/'build.log').read_text(encoding='utf-16' if (p/'build.log').read_bytes().startswith(b'\xff\xfe') else 'utf-8')
    r['builds'][name]={n:{'sha256':sha(p/n),'bytes':(p/n).stat().st_size} for n in ['main.c','pattern.h','Makefile','main.obj','main.exe','build.log','bin/default.xbe']}
for name in ['main.c','pattern.h','Makefile']:
    assert sha(W/'src/utilities/video-baseline'/name)==r['builds']['build003'][name]['sha256']
r['build_changes']={'build001':'initial successful compile','build002':'added observed geometry guard before drawing','build003':'added start-record reference to subsequent checkpoints'}
r['sdk']['commit']=subprocess.check_output(['git','-C','C:/nxdk','rev-parse','HEAD'],text=True).strip()
r['sdk']['files']={str(p.relative_to('C:/nxdk')).replace('\\','/'):sha(p) for p in [Path('C:/nxdk/Makefile'),Path('C:/nxdk/lib/hal/video.c'),Path('C:/nxdk/lib/hal/video.h'),*Path('C:/nxdk/lib').rglob('*.lib')]}
r['sdk']['scope']='Shared prebuilt nxdk; all discovered library archives pinned as a superset, not claimed rebuilt here. Existing untracked submodule files were not changed.'
O.mkdir();dest=O/'XWNVideo680';dest.mkdir()
shutil.copyfile('C:/xwn680/build003/bin/default.xbe',dest/'default.xbe')
shutil.copyfile(W/'src/utilities/video-baseline/README.md',O/'README.md')
(O/'SHA256SUMS.txt').write_text(sha(dest/'default.xbe')+'  XWNVideo680/default.xbe\n'+sha(O/'README.md')+'  README.md\n')
z=O/'xwn-video-baseline680.zip'
with zipfile.ZipFile(z,'x',zipfile.ZIP_DEFLATED) as f:
    for p in [dest/'default.xbe',O/'README.md',O/'SHA256SUMS.txt']:f.write(p,p.relative_to(O))
with zipfile.ZipFile(z) as f:
    assert f.testzip() is None
    assert f.read('XWNVideo680/default.xbe')==(dest/'default.xbe').read_bytes()
r['package']={'path':str(z),'sha256':sha(z),'bytes':z.stat().st_size,'members':['XWNVideo680/default.xbe','README.md','SHA256SUMS.txt']}
r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(K/'builds001.json').write_text(json.dumps(r,indent=2)+'\n')
print('Packaged verified local watched-test utility:',z)

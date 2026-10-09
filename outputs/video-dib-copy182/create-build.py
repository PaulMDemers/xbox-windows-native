"""Pin original sources into a reproducible114 patch and fresh paired builder."""
import hashlib,json,subprocess,shutil
from pathlib import Path
k=Path(__file__).resolve().parent; ws=k.parents[1];d=ws/'work/dib182-patch'
assert not d.exists()
orig=k.parent/'video-clip-upload/display';t=d/'win32ss/drivers/displays/framebuf';t.mkdir(parents=True)
for p in orig.iterdir():
 if p.is_file():shutil.copyfile(p,t/p.name)
def git(*args):return subprocess.run(['git','-C',str(d),*args],check=True)
git('init','-q');git('config','core.autocrlf','false');git('add','.')
git('-c','user.name=XWN','-c','user.email=xwn@local','commit','-qm','Pinned112')
for p in (k/'display').iterdir():
 if p.is_file():shutil.copyfile(p,t/p.name)
git('add','.')
patch=subprocess.check_output(['git','-C',str(d),'diff','--cached','--binary'])
(k/'0114-bounded-dib-copy.patch').write_bytes(patch)
r=json.loads((k/'source-review.json').read_text());r['patch_sha256']=hashlib.sha256(patch).hexdigest()
(k/'source-review.json').write_text(json.dumps(r,indent=2)+'\n')
s=(k.parent/'video-body-timing170/build.py').read_text().replace('0113-body-timing.patch','0114-bounded-dib-copy.patch').replace("defs['XWN_BODY_PROFILE']=enabled","defs['XWN_DIB_FASTPATH']=enabled")
(k/'build.py').write_bytes(s.encode())
s=(k.parent/'video-body-timing170/Build.ps1').read_text().replace('video-body-timing170-001','video-dib-copy182-001')
(k/'Build.ps1').write_bytes(s.encode())
a=ws/'.gitattributes';a.write_bytes(a.read_bytes()+b'\n/outputs/video-dib-copy182/** -text whitespace=cr-at-eol\n/outputs/video-dib-copy182/0114-bounded-dib-copy.patch whitespace=cr-at-eol,-blank-at-eol\n')
print('Patch and fresh matched build commands ready')

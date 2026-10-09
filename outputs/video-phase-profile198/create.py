"""Combine pinned113 observation with unchanged115 REP-copy control; no guest access."""
import ast, hashlib, json, shutil, subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
old=k.parent/'video-word-store184';timer=k.parent/'video-body-timing170'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (k/'source-review.json').exists()
assert read(old/'driver-review.json')['passed'] and read(timer/'driver-review.json')['passed']
for base,record in [(old,read(old/'source-review.json')),(timer,read(timer/'source-review.json'))]:
    for n,h in record['source_files'].items():assert sha(base/'display'/n)==h,n
d=k/'display';shutil.copytree(old/'display',d)
shutil.copyfile(timer/'display/profile_math.h',d/'profile_math.h')
def update(name,before,after):
    p=d/name;s=p.read_text();assert s.count(before)==1,(name,before)
    p.write_bytes(s.replace(before,after).encode())
update('framebuf.h','typedef struct _PDEV','#include "profile_math.h"\ntypedef struct _PDEV')
update('framebuf.h','   ULONG ShadowUploads;','   XWN_PROFILE Profile;\n   ULONG ShadowUploads;')
update('framebuf.h','#endif /* _FRAMEBUF_PCH_ */','VOID XwnProfileInit(PPDEV);\nLONGLONG XwnProfileStart(VOID);\nVOID XwnProfileEnd(PPDEV,ULONG,LONGLONG);\nVOID XwnProfileSnapshot(PPDEV,ULONG *);\n#endif /* _FRAMEBUF_PCH_ */')
update('CMakeLists.txt','    ownership.c','    ownership.c\n    profile_math.h')
cm=(timer/'display/CMakeLists.txt').read_text();cm=cm[cm.index('option(XWN_BODY_PROFILE'):]
with (d/'CMakeLists.txt').open('a',newline='\n') as f:f.write('\n'+cm)
update('enable.c','   memcpy(pdi, &DevInfo, min(sizeof(DEVINFO), cjDevInfo));','   XwnProfileInit(ppdev);\n   memcpy(pdi, &DevInfo, min(sizeof(DEVINFO), cjDevInfo));')
update('enable.c','   if (Escape == 0x58574431 && OutBytes == 32)','   if (Escape == 0x58574433 && OutBytes == sizeof(Data))\n   {\n      XwnProfileSnapshot(p,Data);memcpy(Out,Data,sizeof(Data));return 1;\n   }\n   if (Escape == 0x58574431 && OutBytes == 32)')
own=(timer/'display/ownership.c').read_text();own=own[own.index('/* Separate elapsed diagnostic.'):]
with (d/'ownership.c').open('a',newline='\n') as f:f.write('\n'+own)
update('shadow.c',' LONG y; ULONG bytes,fast=0,slow=0;',' LONG y; ULONG bytes,fast=0,slow=0; LONGLONG begin;')
update('shadow.c',' for(y=r->top;y<r->bottom;y++) {',' begin=XwnProfileStart();\n for(y=r->top;y<r->bottom;y++) {')
update('shadow.c',' XwnRowRecord(p,fast,slow,bytes);',' XwnProfileEnd(p,2,begin);\n XwnRowRecord(p,fast,slow,bytes);')
update('shadow.c','VOID XwnUpload(PPDEV p, const RECTL *rect, const CLIPOBJ *clip)','static VOID XwnUploadInternal(PPDEV p, const RECTL *rect, const CLIPOBJ *clip)')
update('shadow.c','ULONG XwnCheckScanout(PPDEV p)','VOID XwnUpload(PPDEV p, const RECTL *rect, const CLIPOBJ *clip)\n{\n LONGLONG begin=XwnProfileStart();\n XwnUploadInternal(p,rect,clip);\n XwnProfileEnd(p,3,begin);\n}\nULONG XwnCheckScanout(PPDEV p)')
p=d/'shadow.c';s=p.read_text()
for name,kind in [('XwnBitBlt',0),('XwnCopyBits',1)]:
    start=s.index('BOOL APIENTRY '+name);end=s.index('\nBOOL APIENTRY ',start+1);part=s[start:end]
    assert part.count(' PPDEV p=NULL; BOOL ok;')==1
    part=part.replace(' PPDEV p=NULL; BOOL ok;',' PPDEV p=NULL; BOOL ok; LONGLONG begin;')
    part=part.replace(' ok=Eng',' begin=XwnProfileStart();\n ok=Eng',1)
    part=part.replace(' if (XwnOwner(',f' XwnProfileEnd(p,{kind},begin);\n if (XwnOwner(',1)
    s=s[:start]+part+s[end:]
p.write_bytes(s.encode())
for p in d.iterdir():
    if p.is_file():p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
patchdir=ws/'work/phase198-patch';assert not patchdir.exists();target=patchdir/'win32ss/drivers/displays/framebuf';target.mkdir(parents=True)
for p in (old/'display').iterdir():
    if p.is_file():shutil.copyfile(p,target/p.name)
def git(*args):return subprocess.run(['git','-C',str(patchdir),*args],check=True)
git('init','-q');git('config','core.autocrlf','false');git('add','.');git('-c','user.name=XWN','-c','user.email=xwn@local','commit','-qm','Pinned115')
for p in d.iterdir():
    if p.is_file():shutil.copyfile(p,target/p.name)
git('add','.');patch=subprocess.check_output(['git','-C',str(patchdir),'diff','--cached','--binary']);(k/'0116-phase-observation.patch').write_bytes(patch)
r=dict(parent_tree=read(old/'build-report.json')['source_tree'],original_files=read(old/'source-review.json')['source_files'],source_files={p.name:sha(p) for p in d.iterdir() if p.is_file()},patch_sha256=sha(k/'0116-phase-observation.patch'),prior_driver_review_sha256=sha(old/'driver-review.json'),prior_timer_review_sha256=sha(timer/'driver-review.json'),clock_source_reused_exact=True,profile_math_sha256=sha(d/'profile_math.h'),scalar_stores_enabled=False,profile_escape='0x58574433/version113/128bytes',row_escape='0x58574435/version115/128bytes',diagnostic_overhead_added=True,render_copy_clip_mode_cache_lifetime_unchanged=True,physical_access=False,guest_launch=False)
(k/'source-review.json').write_text(json.dumps(r,indent=2)+'\n')
build=(old/'build.py').read_text().replace("profile=read(k/'source-review.json');", "profile=read(k/'source-review.json');oldprofile=read(k.parent/'video-word-store184/source-review.json');")
build=build.replace("==profile['parent_tree']","==oldprofile['parent_tree']",1)
build=build.replace("assert sha(k/'0115-scalar-row-stores.patch')==profile['patch_sha256']","assert sha(k.parent/'video-word-store184/0115-scalar-row-stores.patch')==oldprofile['patch_sha256']")
build=build.replace("str(k/'0115-scalar-row-stores.patch')","str(k.parent/'video-word-store184/0115-scalar-row-stores.patch')")
before="  r['source_tree']=subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()"
after="  assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==profile['parent_tree']\n  assert sha(k/'0116-phase-observation.patch')==profile['patch_sha256']\n  run(['git','-C',str(src),'apply','--index',str(k/'0116-phase-observation.patch')],stdout=log,stderr=log)\n"+before
assert build.count(before)==1;build=build.replace(before,after)
build=build.replace("defs['XWN_UC_STORES']=enabled","defs['XWN_UC_STORES']='OFF';defs['XWN_BODY_PROFILE']=enabled")
ast.parse(build);(k/'build.py').write_bytes(build.encode())
(k/'Build.ps1').write_bytes((old/'Build.ps1').read_text().replace('video-word-store184-001','video-phase-profile198-001').encode())
for n in ['math-tests.c','host-tests.py']:shutil.copyfile(timer/n,k/n)
host=(k/'host-tests.py').read_text().replace('profile170-math','phase198-math');(k/'host-tests.py').write_bytes(host.encode())
with (ws/'.gitattributes').open('ab') as f:f.write(b'\n/outputs/video-phase-profile198/** -text whitespace=cr-at-eol\n/outputs/video-phase-profile198/*.patch whitespace=cr-at-eol,-blank-at-eol\n')
print('New phase198 source and fresh matched compiler commands; no guest or physical access')

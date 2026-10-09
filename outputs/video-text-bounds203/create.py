"""New117 conservative text upload from pinned198; no guest or physical access."""
import hashlib,json,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-phase-profile198'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (k/'source-review.json').exists()
assert read(old/'driver-review.json')['passed'] and read(k.parent/'video-unattended202/raw-review-candidate001.json')['passed']
prior=read(old/'source-review.json')
for name,digest in prior['source_files'].items():assert sha(old/'display'/name)==digest
d=k/'display';shutil.copytree(old/'display',d);shutil.copyfile(k/'text_bounds.h',d/'text_bounds.h')
def replace(name,before,after):
    p=d/name;s=p.read_text();assert s.count(before)==1,(name,before);p.write_bytes(s.replace(before,after).encode())
replace('framebuf.h','#include "profile_math.h"','#include "profile_math.h"\n#include "text_bounds.h"')
replace('framebuf.h','   XWN_PROFILE Profile;','   XWN_PROFILE Profile;\n   XWT_STATS TextStats;')
replace('framebuf.h','#endif /* _FRAMEBUF_PCH_ */','VOID XwnTextRecord(PPDEV,ULONG,ULONG,const XWT_RECT *,const XWT_COPY *);\nVOID XwnTextSnapshot(PPDEV,ULONG *);\n#endif /* _FRAMEBUF_PCH_ */')
replace('CMakeLists.txt','    profile_math.h','    profile_math.h\n    text_bounds.h')
with (d/'CMakeLists.txt').open('a') as f:f.write('''
option(XWN_TEXT_BOUNDS "Conservative string/opaque text upload bounds" OFF)
if(XWN_TEXT_BOUNDS)
 target_compile_definitions(xwnown PRIVATE XWN_TEXT_BOUNDS=1)
else()
 target_compile_definitions(xwnown PRIVATE XWN_TEXT_BOUNDS=0)
endif()
''')
replace('enable.c','   if (Escape == 0x58574435','   if (Escape == 0x58574436 && OutBytes == sizeof(Data))\n   {\n      XwnTextSnapshot(p,Data);memcpy(Out,Data,sizeof(Data));return 1;\n   }\n   if (Escape == 0x58574435')
replace('shadow.c','static VOID XwnUploadBox(PPDEV p, const RECTL *r)','static VOID XwnUploadBox(PPDEV p, const RECTL *r, XWT_COPY *account)')
replace('shadow.c',' p->ShadowBytes+=(ULONGLONG)bytes*(r->bottom-r->top);',' p->ShadowBytes+=(ULONGLONG)bytes*(r->bottom-r->top);\n if(account) XwtCopy(account,(ULONGLONG)bytes*(r->bottom-r->top));')
replace('shadow.c','static VOID XwnUploadInternal(PPDEV p, const RECTL *rect, const CLIPOBJ *clip)','static VOID XwnUploadInternal(PPDEV p, const RECTL *rect, const CLIPOBJ *clip, XWT_COPY *account)')
p=d/'shadow.c';s=p.read_text().replace('XwnUploadBox(p,&part);','XwnUploadBox(p,&part,account);').replace('XwnUploadBox(p,&r);','XwnUploadBox(p,&r,account);').replace('XwnUploadInternal(p,rect,clip);','XwnUploadInternal(p,rect,clip,NULL);')
before=''' PPDEV p=NULL; BOOL ok;
 if ((TRUE) && !XwnSelectOwner(&p, pso)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[2] != 0xffffffff) ++p->ShadowCalls[2];
 ok=EngTextOut((TRUE ? XwnSub(p, pso) : NULL), pstro, pfo, pco, prclExtra, prclOpaque, pboFore, pboOpaque, pptlOrg, mix);
 if (XwnOwner(pso)) XwnUpload(p, NULL, pco);
 return ok;'''
after=''' PPDEV p=NULL; BOOL ok; ULONG reason; LONGLONG begin;
 XWT_RECT string={0,0,0,0},opaque={0,0,0,0},bound={0,0,0,0};
 RECTL rect; const RECTL *chosen=NULL; XWT_COPY copied={0,0,0}; ULONG glyphs=0;
 if ((TRUE) && !XwnSelectOwner(&p, pso)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[2] != 0xffffffff) ++p->ShadowCalls[2];
 /* Snapshot metadata before Eng can consume an enumeration. No glyph walk. */
 if(pstro) {glyphs=pstro->cGlyphs;string.left=pstro->rclBkGround.left;
  string.top=pstro->rclBkGround.top;string.right=pstro->rclBkGround.right;string.bottom=pstro->rclBkGround.bottom;}
 if(prclOpaque) {opaque.left=prclOpaque->left;opaque.top=prclOpaque->top;
  opaque.right=prclOpaque->right;opaque.bottom=prclOpaque->bottom;}
 reason=XwtBounds(pstro!=NULL,glyphs,&string,prclOpaque?&opaque:NULL,prclExtra!=NULL,&bound);
 ok=EngTextOut((TRUE ? XwnSub(p, pso) : NULL), pstro, pfo, pco, prclExtra, prclOpaque, pboFore, pboOpaque, pptlOrg, mix);
 if (XwnOwner(pso)) {
  if(!ok) reason=XWT_ENGINE_FAILED;
  if(XWN_TEXT_BOUNDS && reason==XWT_BOUNDED) {
   rect.left=bound.left;rect.top=bound.top;rect.right=bound.right;rect.bottom=bound.bottom;chosen=&rect;
  }
  begin=XwnProfileStart();
  if(!(XWN_TEXT_BOUNDS && reason==XWT_EMPTY)) XwnUploadInternal(p,chosen,pco,&copied);
  XwnProfileEnd(p,3,begin);
  XwnTextRecord(p,reason,glyphs,&bound,&copied);
 }
 return ok;'''
assert s.count(before)==1;s=s.replace(before,after);p.write_bytes(s.encode())
with (d/'ownership.c').open('a') as f:f.write('''
/* Actual per-call copied bytes, published only after copy, lock never spans Eng/copy. */
VOID XwnTextRecord(PPDEV p,ULONG reason,ULONG glyphs,const XWT_RECT *bound,const XWT_COPY *copied)
{
 EngAcquireSemaphore(XwnOwnerLock);
 XwtRecord(&p->TextStats,XWN_TEXT_BOUNDS,reason,glyphs,bound,copied);
 EngReleaseSemaphore(XwnOwnerLock);
}
VOID XwnTextSnapshot(PPDEV p,ULONG *out)
{
 ULONG i;XWT_STATS *s=&p->TextStats;
 RtlZeroMemory(out,128);EngAcquireSemaphore(XwnOwnerLock);
 out[0]=0x54585758;out[1]=117;out[2]=128;out[3]=XWN_TEXT_BOUNDS;
 out[4]=s->calls;out[5]=s->bounded;out[6]=s->fallback;out[7]=s->empty;
 out[8]=s->boxes;out[9]=(ULONG)s->bytes;out[10]=(ULONG)(s->bytes>>32);
 out[11]=s->overflow;
 for(i=0;i<7;i++)out[12+i]=s->reasons[i];
 out[19]=s->last_glyphs;out[20]=s->last_reason;out[21]=s->last_mode;
 out[22]=s->last.left;out[23]=s->last.top;out[24]=s->last.right;out[25]=s->last.bottom;
 out[26]=s->copied.boxes;out[27]=(ULONG)s->copied.bytes;out[28]=(ULONG)(s->copied.bytes>>32);
 out[29]=s->copied.overflow;
 EngReleaseSemaphore(XwnOwnerLock);
}
''')
for p in d.iterdir():
    if p.is_file():p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
patchdir=ws/'work/text203-patch';assert not patchdir.exists();target=patchdir/'win32ss/drivers/displays/framebuf';target.mkdir(parents=True)
for p in (old/'display').iterdir():
    if p.is_file():shutil.copyfile(p,target/p.name)
def git(*args):return subprocess.run(['git','-C',str(patchdir),*args],check=True)
git('init','-q');git('config','core.autocrlf','false');git('add','.');git('-c','user.name=XWN','-c','user.email=xwn@local','commit','-qm','Pinned116')
for p in d.iterdir():
    if p.is_file():shutil.copyfile(p,target/p.name)
git('add','.');(k/'0117-text-upload-bounds.patch').write_bytes(subprocess.check_output(['git','-C',str(patchdir),'diff','--cached','--binary']))
r=dict(parent_tree=read(old/'build-report.json')['source_tree'],source_files={p.name:sha(p) for p in d.iterdir() if p.is_file()},patch_sha256=sha(k/'0117-text-upload-bounds.patch'),prerequisite_review_sha256=sha(old/'driver-review.json'),bounds_snapshot_before_eng=True,no_glyph_or_extra_enumeration=True,extra_pointer_falls_back=True,engine_failure_falls_back=True,ownership_mode_cache_clip_unchanged=True,physical_access=False,guest_launch=False)
(k/'source-review.json').write_text(json.dumps(r,indent=2)+'\n')
build=(old/'build.py').read_text().replace("profile=read(k/'source-review.json');","profile=read(k.parent/'video-phase-profile198/source-review.json');newprofile=read(k/'source-review.json');")
build=build.replace("sha(k/'0116-phase-observation.patch')","sha(k.parent/'video-phase-profile198/0116-phase-observation.patch')").replace("str(k/'0116-phase-observation.patch')","str(k.parent/'video-phase-profile198/0116-phase-observation.patch')")
needle="  for name,enabled in [('control001','OFF'),('candidate001','ON')]:"
insert="  assert r['source_tree']==newprofile['parent_tree']\n  run(['git','-C',str(src),'apply','--index',str(k/'0117-text-upload-bounds.patch')],stdout=log,stderr=log)\n  r['source_tree']=subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()\n  r['text_patch_sha256']=sha(k/'0117-text-upload-bounds.patch');assert r['text_patch_sha256']==newprofile['patch_sha256']\n  for n,h in newprofile['source_files'].items():assert sha(src/'win32ss/drivers/displays/framebuf'/n)==h\n"+needle
assert build.count(needle)==1;build=build.replace(needle,insert).replace("defs['XWN_BODY_PROFILE']=enabled","defs['XWN_BODY_PROFILE']='OFF';defs['XWN_TEXT_BOUNDS']=enabled")
(k/'build.py').write_bytes(build.encode());(k/'Build.ps1').write_bytes((old/'Build.ps1').read_bytes().replace(b'video-phase-profile198-001',b'video-text-bounds203-001'))
print('Conservative117 source/paired boundsOFF-ON build commands prepared, no guest launch')

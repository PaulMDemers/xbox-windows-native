"""Create reviewed119 observation patch from pinned118; no render/cache change."""
import ast,difflib,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-text-clip205'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (k/'display').exists() and not (k/'source-review.json').exists()
review=json.loads((old/'source-review.json').read_text());dest=k/'display';dest.mkdir()
for n,h in review['source_files'].items():
 assert sha(old/'display'/n)==h;shutil.copyfile(old/'display'/n,dest/n)
def edit(name,before,after,count=1):
 p=dest/name;s=p.read_text();assert s.count(before)==count,(name,before,s.count(before));p.write_text(s.replace(before,after),newline='\n')
shutil.copyfile(k/'upload_account.h',dest/'upload_account.h')
edit('framebuf.h','#include "text_bounds.h"','#include "text_bounds.h"\n#include "upload_account.h"')
edit('framebuf.h','   XWN_PROFILE Profile;','   XWN_PROFILE Profile;\n   XWA_STATS UploadStats;')
edit('framebuf.h','VOID XwnUpload(PPDEV p, const RECTL *rect, const CLIPOBJ *clip);','VOID XwnUpload(PPDEV p, const RECTL *rect, const CLIPOBJ *clip, ULONG kind);\nVOID XwnUploadRecord(PPDEV,ULONG,ULONG,const XWA_COPY *);\nVOID XwnUploadSnapshot(PPDEV,ULONG *);')
edit('shadow.c','XWT_COPY *account)','XWT_COPY *account, XWA_COPY *producer)',2)
edit('shadow.c',' if(account) XwtCopy(account,(ULONGLONG)bytes*(r->bottom-r->top));',' if(account) XwtCopy(account,(ULONGLONG)bytes*(r->bottom-r->top));\n if(producer) XwaBox(producer,(ULONGLONG)bytes*(r->bottom-r->top));')
edit('shadow.c','XwnUploadBox(p,&part,account);','XwnUploadBox(p,&part,account,producer);')
edit('shadow.c','XwnUploadBox(p,&r,account);','XwnUploadBox(p,&r,account,producer);',2)
edit('shadow.c','fallback:\n','fallback:\n if(producer) XwaFallback(producer);\n')
edit('shadow.c','VOID XwnUpload(PPDEV p, const RECTL *rect, const CLIPOBJ *clip)\n{\n LONGLONG begin=XwnProfileStart();\n XwnUploadInternal(p,rect,clip,NULL);\n XwnProfileEnd(p,3,begin);\n}', 'VOID XwnUpload(PPDEV p, const RECTL *rect, const CLIPOBJ *clip, ULONG kind)\n{\n XWA_COPY copied={0,0,0,0};\n LONGLONG begin=XwnProfileStart();\n XwnUploadInternal(p,rect,clip,NULL,&copied);\n XwnProfileEnd(p,3,begin);\n XwnUploadRecord(p,kind,rect!=NULL,&copied);\n}')
functions=['BitBlt','CopyBits','TextOut','StrokePath','FillPath','StrokeAndFillPath','LineTo','Paint','StretchBlt','StretchBltROP','PlgBlt','AlphaBlend','GradientFill','TransparentBlt']
p=dest/'shadow.c';s=p.read_text()
for kind,name in enumerate(functions):
 start=s.index('BOOL APIENTRY Xwn'+name+'(');end=s.find('\nBOOL APIENTRY ',start+1);end=len(s) if end<0 else end
 chunk=s[start:end]
 if kind==2:
  chunk=chunk.replace('XWT_COPY copied={0,0,0};','XWT_COPY copied={0,0,0}; XWA_COPY producer={0,0,0,0};')
  chunk=chunk.replace('XwnUploadInternal(p,chosen,pco,&copied);','XwnUploadInternal(p,chosen,pco,&copied,&producer);')
  needle='  XwnProfileEnd(p,3,begin);';assert chunk.count(needle)==1
  chunk=chunk.replace(needle,needle+'\n  XwnUploadRecord(p,2,chosen!=NULL,&producer);')
 else:
  assert chunk.count('XwnUpload(p,')==1,name
  # The only upload terminates at pco); including the multi-line LineTo call.
  assert chunk.count('pco);')>=1
  a=chunk.index('XwnUpload(p,');b=chunk.index('pco);',a)
  chunk=chunk[:b]+f'pco,{kind});'+chunk[b+5:]
 s=s[:start]+chunk+s[end:]
p.write_text(s,newline='\n')
edit('surface.c','XwnUpload(ppdev,NULL,NULL);','XwnUpload(ppdev,NULL,NULL,14);',2)
edit('enable.c','   if (Escape == 0x58574437', '   if (Escape == 0x58574438 && OutBytes == XWA_WORDS*4)\n   {\n      ULONG Upload[XWA_WORDS];XwnUploadSnapshot(p,Upload);memcpy(Out,Upload,sizeof(Upload));return 1;\n   }\n   if (Escape == 0x58574437')
p=dest/'ownership.c';p.write_text(p.read_text()+'''
/* Publish one completed upload; no membership lock spans Eng or framebuffer IO. */
VOID XwnUploadRecord(PPDEV p,ULONG kind,ULONG has_rect,const XWA_COPY *copied)
{
#if XWN_UPLOAD_ACCOUNTING
 EngAcquireSemaphore(XwnOwnerLock);
 XwaRecord(&p->UploadStats,kind,has_rect,copied);
 EngReleaseSemaphore(XwnOwnerLock);
#else
 (void)p;(void)kind;(void)has_rect;(void)copied;
#endif
}
VOID XwnUploadSnapshot(PPDEV p,ULONG *out)
{
 EngAcquireSemaphore(XwnOwnerLock);
 XwaSnapshot(&p->UploadStats,out);
 EngReleaseSemaphore(XwnOwnerLock);
}
''',newline='\n')
p=dest/'CMakeLists.txt';p.write_text(p.read_text()+'''
option(XWN_UPLOAD_ACCOUNTING "Diagnostic completed upload bytes by DDI" OFF)
if(XWN_UPLOAD_ACCOUNTING)
 target_compile_definitions(xwnown PRIVATE XWN_UPLOAD_ACCOUNTING=1)
else()
 target_compile_definitions(xwnown PRIVATE XWN_UPLOAD_ACCOUNTING=0)
endif()
''',newline='\n')
parts=[];changes=[]
for p in sorted(dest.iterdir()):
 original=old/'display'/p.name
 a=original.read_text() if original.exists() else ''
 b=p.read_text()
 if a==b:continue
 changes.append(p.name)
 path='win32ss/drivers/displays/framebuf/'+p.name
 parts.extend(difflib.unified_diff(a.splitlines(keepends=True),b.splitlines(keepends=True),fromfile='a/'+path if original.exists() else '/dev/null',tofile='b/'+path))
(k/'0119-upload-producer-accounting.patch').write_text(''.join(parts),newline='\n')
# Adapt the frozen208 reconstruction, retaining all original patch/tool guards.
b=(k.parent/'video-scalar208/build.py').read_text()
needle="  for name,enabled in [('control001','OFF'),('candidate001','ON')]:"
assert b.count(needle)==1
b=b.replace(needle,"  account=read(k/'source-review.json');assert r['source_tree']==account['parent_tree']\n  assert sha(k/'0119-upload-producer-accounting.patch')==account['patch_sha256']\n  run(['git','-C',str(src),'apply','--index',str(k/'0119-upload-producer-accounting.patch')],stdout=log,stderr=log)\n  r['source_tree']=subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()\n  r['accounting_patch_sha256']=account['patch_sha256']\n  for n,h in account['source_files'].items():assert sha(src/'win32ss/drivers/displays/framebuf'/n)==h\n"+needle)
b=b.replace("defs['XWN_UC_STORES']=enabled;defs['XWN_BODY_PROFILE']='OFF';defs['XWN_TEXT_BOUNDS']='OFF'", "defs['XWN_UC_STORES']='OFF';defs['XWN_BODY_PROFILE']='OFF';defs['XWN_TEXT_BOUNDS']='ON';defs['XWN_UPLOAD_ACCOUNTING']=enabled")
ast.parse(b);(k/'build.py').write_text(b,newline='\n')
b=(k.parent/'video-scalar208/Build.ps1').read_text().replace('video-scalar208-001','video-upload-accounting210-001');(k/'Build.ps1').write_text(b,newline='\n')
r=dict(parent_tree='4e335dc7a23b4fc058db597a1dded0c098af3cb1',patch_sha256=sha(k/'0119-upload-producer-accounting.patch'),
 source_files={p.name:sha(p) for p in sorted(dest.iterdir())},original_files=review['source_files'],changed_files=changes,
 kinds=functions+['SurfaceLifecycle'],packet_words=158,packet_bytes=632,
 physical_access=False,guest_launch=False,rendering_changed=False,clipping_changed=False,ownership_or_cache_changed=False,
 limits='Completed-copy accounting only, one protected publication per upload; NULL-request bytes are not proof of redundancy. Original pixels/global counters still required.')
(k/'source-review.json').write_text(json.dumps(r,indent=2)+'\n')
print('Fresh119 source observation patch created; no build/launch')

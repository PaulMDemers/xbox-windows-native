"""New118 input-clip telemetry from frozen117; no further drawing optimization."""
import hashlib,json,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-text-bounds203'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert not (k/'source-review.json').exists();prior=read(old/'source-review.json');compiled=read(old/'build-review.json');assert compiled['passed']
for name,digest in prior['source_files'].items():assert sha(old/'display'/name)==digest
d=k/'display';shutil.copytree(old/'display',d)
def change(name,before,after):
 p=d/name;s=p.read_text();assert s.count(before)==1,(name,before);p.write_bytes(s.replace(before,after).encode())
change('framebuf.h','   XWT_STATS TextStats;', '   XWT_STATS TextStats;\n   RECTL TextInputClip;\n   ULONG TextHasClip,TextComplexity;')
change('framebuf.h','VOID XwnTextRecord(PPDEV,ULONG,ULONG,const XWT_RECT *,const XWT_COPY *);', 'VOID XwnTextRecord(PPDEV,ULONG,ULONG,const XWT_RECT *,const XWT_COPY *,const RECTL *,ULONG);\nVOID XwnTextExtended(PPDEV,ULONG *);')
change('shadow.c','RECTL rect; const RECTL *chosen=NULL;', 'RECTL rect,inputClip={0,0,0,0}; ULONG complexity=0; const RECTL *chosen=NULL;')
change('shadow.c','reason=XwtBounds(pstro!=NULL', 'if(pco) {inputClip=pco->rclBounds;complexity=pco->iDComplexity;}\n reason=XwtBounds(pstro!=NULL')
change('shadow.c','XwnTextRecord(p,reason,glyphs,&bound,&copied);','XwnTextRecord(p,reason,glyphs,&bound,&copied,pco?&inputClip:NULL,complexity);')
change('ownership.c','VOID XwnTextRecord(PPDEV p,ULONG reason,ULONG glyphs,const XWT_RECT *bound,const XWT_COPY *copied)', 'VOID XwnTextRecord(PPDEV p,ULONG reason,ULONG glyphs,const XWT_RECT *bound,const XWT_COPY *copied,const RECTL *clip,ULONG complexity)')
change('ownership.c','XwtRecord(&p->TextStats,XWN_TEXT_BOUNDS,reason,glyphs,bound,copied);', 'XwtRecord(&p->TextStats,XWN_TEXT_BOUNDS,reason,glyphs,bound,copied);\n p->TextHasClip=clip!=NULL;p->TextComplexity=complexity;\n if(clip)p->TextInputClip=*clip;else RtlZeroMemory(&p->TextInputClip,sizeof(p->TextInputClip));')
s=(d/'ownership.c').read_text();start=s.index('VOID XwnTextSnapshot(');extended=s[start:]
extended=extended.replace('VOID XwnTextSnapshot(', 'VOID XwnTextExtended(').replace('RtlZeroMemory(out,128)', 'RtlZeroMemory(out,160)').replace('out[1]=117;out[2]=128','out[1]=118;out[2]=160')
extended=extended.replace(' EngReleaseSemaphore(XwnOwnerLock);', ''' out[32]=p->TextInputClip.left;out[33]=p->TextInputClip.top;out[34]=p->TextInputClip.right;out[35]=p->TextInputClip.bottom;
 out[36]=p->TextComplexity;out[37]=p->TextHasClip;
 EngReleaseSemaphore(XwnOwnerLock);''')
assert 'out[37]' in extended
(d/'ownership.c').write_bytes((s+'\n/* Atomic118 snapshot: actual input clip plus the same117 last-call accounting. */\n'+extended).encode())
change('enable.c','   if (Escape == 0x58574436', '''   if (Escape == 0x58574437 && OutBytes == 160)
   {
      ULONG Extended[40];XwnTextExtended(p,Extended);memcpy(Out,Extended,160);return 1;
   }
   if (Escape == 0x58574436''')
tmp=ws/'work/text205-patch';assert not tmp.exists();tmp.mkdir();rel='win32ss/drivers/displays/framebuf'
subprocess.run(['git','init','-q',str(tmp)],check=True);shutil.copytree(old/'display',tmp/rel)
subprocess.run(['git','-C',str(tmp),'add','.'],check=True)
subprocess.run(['git','-C',str(tmp),'-c','user.name=Codex','-c','user.email=codex@local','commit','-qm','frozen117 display'],check=True)
shutil.copytree(d,tmp/rel,dirs_exist_ok=True);subprocess.run(['git','-C',str(tmp),'add','.'],check=True)
patch=k/'0118-text-input-clip.patch';patch.write_bytes(subprocess.check_output(['git','-C',str(tmp),'diff','--cached','--binary','--no-ext-diff']))
report=dict(parent_tree=compiled['source_tree'],source_files={p.name:sha(p) for p in d.iterdir()},patch_sha256=sha(patch),
 actual_clip_before_eng=True,atomic_last_call_snapshot=True,rendering_and_upload_algorithms_unchanged_from117=True,guest_launch=False,physical_access=False)
(k/'source-review.json').write_text(json.dumps(report,indent=2)+'\n')
s=(old/'build.py').read_text();s=s.replace("newprofile=read(k/'source-review.json')", "newprofile=read(k.parent/'video-text-bounds203/source-review.json');clipprofile=read(k/'source-review.json')")
s=s.replace("str(k/'0117-text-upload-bounds.patch')", "str(k.parent/'video-text-bounds203/0117-text-upload-bounds.patch')").replace("sha(k/'0117-text-upload-bounds.patch')", "sha(k.parent/'video-text-bounds203/0117-text-upload-bounds.patch')")
line="  for n,h in newprofile['source_files'].items():assert sha(src/'win32ss/drivers/displays/framebuf'/n)==h"
assert s.count(line)==1
s=s.replace(line,line+'''
  assert r['source_tree']==clipprofile['parent_tree']
  run(['git','-C',str(src),'apply','--index',str(k/'0118-text-input-clip.patch')],stdout=log,stderr=log)
  r['source_tree']=subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()
  r['clip_patch_sha256']=sha(k/'0118-text-input-clip.patch');assert r['clip_patch_sha256']==clipprofile['patch_sha256']
  for n,h in clipprofile['source_files'].items():assert sha(src/'win32ss/drivers/displays/framebuf'/n)==h''')
(k/'build.py').write_text(s)
(k/'Build.ps1').write_text((old/'Build.ps1').read_text().replace('video-text-bounds203-001','video-text-clip205-001'))
print('New118 atomic input-clip telemetry prepared; no build/launch')

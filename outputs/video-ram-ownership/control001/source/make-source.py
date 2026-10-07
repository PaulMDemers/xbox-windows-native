"""Fresh ownership-only 0109 patch on pinned RAM0108; never mutate old kits."""
from pathlib import Path
import difflib, hashlib, json, re
k=Path(__file__).resolve().parent
parent=k.parent/'video-ram-primary'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=read(parent/'patch-review.json')
out=k/'display';out.mkdir(exist_ok=False)
original={}
for n,h in review['source_files'].items():
 p=parent/'display'/n;assert sha(p)==h
 original[n]=p.read_text();(out/n).write_text(original[n],newline='\n')
def edit(n,a,b):
 p=out/n;s=p.read_text();assert a in s,(n,a);p.write_text(s.replace(a,b),newline='\n')
edit('CMakeLists.txt','xwnram','xwnown')
edit('CMakeLists.txt','shadow.c','shadow.c\n    ownership.c')
edit('framebuf.h','#endif /* _FRAMEBUF_PCH_ */','''BOOL XwnOwnershipInit(VOID);
VOID APIENTRY XwnOwnershipDisable(VOID);
BOOL XwnRegisterPrimary(PPDEV p);
VOID XwnUnregisterPrimary(PPDEV p);
PPDEV XwnOwner(SURFOBJ *s);
BOOL XwnSelectOwner(PPDEV *selected, SURFOBJ *s);
#endif /* _FRAMEBUF_PCH_ */''')
edit('enable.c','   p = (PPDEV)Surface->dhpdev;','   p = XwnOwner(Surface);\n   if (!p) return 0;')
edit('enable.c','Data[1]=108','Data[1]=109')
edit('enable.c','   {INDEX_DrvEscape,','   {INDEX_DrvDisableDriver, (PFN)XwnOwnershipDisable},\n   {INDEX_DrvEscape,')
edit('enable.c','      pded->c =','      if (!XwnOwnershipInit()) return FALSE;\n      pded->c =')
edit('surface.c','   ppdev->hSurfEng = hSurface;','''   ppdev->hSurfEng = hSurface;
   if (!XwnRegisterPrimary(ppdev))
   {
      EngDeleteSurface(hSurface);
      ppdev->hSurfEng = NULL;
      goto FailMapping;
   }''')
edit('surface.c','   if (ppdev->hSurfEng) EngDeleteSurface(ppdev->hSurfEng);','   XwnUnregisterPrimary(ppdev);\n   if (ppdev->hSurfEng) EngDeleteSurface(ppdev->hSurfEng);')
p=out/'shadow.c';s=p.read_text();a=s.index('static PPDEV XwnOwner(');b=s.index('static SURFOBJ *XwnSub',a);s=s[:a]+s[b:]
s=s.replace('s && s->hsurf==p->hSurfEng','XwnOwner(s)==p')
s,n=re.subn(r' if \(!p && (.+)\) p=XwnOwner\((\w+)\);',r' if ((\1) && !XwnSelectOwner(&p, \2)) return FALSE;',s)
assert n==25,n
p.write_text(s,newline='\n')
(out/'ownership.c').write_text((k/'ownership.c').read_text(),newline='\n')
patch=''
for p in sorted(out.iterdir()):
 before=original.get(p.name,'');after=p.read_text()
 if before!=after:patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/win32ss/drivers/displays/framebuf/'+p.name if p.name in original else '/dev/null',tofile='b/win32ss/drivers/displays/framebuf/'+p.name))
(k/'0109-ram-ownership.patch').write_text(patch,newline='\n')
r=dict(parent_tree='0cb24809fa673421024b4a409d7a9fc08d40d8d0',original_files=review['source_files'],source_files={p.name:sha(p) for p in out.iterdir()},patch_sha256=sha(k/'0109-ram-ownership.patch'),physical_access=False)
(k/'patch-review.json').write_text(json.dumps(r,indent=2)+'\n')

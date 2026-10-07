"""Prepare new host/build/runtime tools from closed, pinned RAM0108 kit."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-ram-primary'
for name in ['build.py','Build.ps1','verify-source.py','review.py','Build-Probe.ps1','probe.c','atomic_json.py','audit.py','configuration.py','cold-map.py','preflight.py','Run.ps1','supervise.py','record-closure.py','common.py','prepare.py','verify-pair.py']:
 s=(old/name).read_text().replace('video-ram-primary','video-ram-ownership').replace('nt5-vram-','nt5-vown-').replace('xwnram114','xwnown116').replace('0108-ram-primary.patch','0109-ram-ownership.patch')
 if name=='build.py':
  anchor="  assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==review['parent_tree']"
  s=s.replace(anchor,"  run(['git','-C',str(src),'apply','--index',str(k.parent/'video-ram-primary/0108-ram-primary.patch')],stdout=log,stderr=log)\n"+anchor).replace('xwnram','xwnown')
 if name in ['review.py','preflight.py']:s=s.replace('xwnram.dll','xwnown.dll')
 if name=='prepare.py':
  s=s.replace('xwnram.dll','xwnown.dll').replace('xwndir.dll','xwnram.dll')
  s=s.replace('video-direct-ddi/candidate001/artifacts/xwnram.dll','video-ram-primary/candidate001/artifacts/xwnram.dll')
  s=s.replace('019f5267a66cf0a018731d1a3db9f9c8ef737da5a7fbeb6965c1aa96948d0d68','51d98cf9ee2d2f42c360d96152877491b32773471ef8a0680d40264b49f6efc5')
  s=s.replace("('xwnram' if case=='candidate001' else 'xwndir')","('xwnown' if case=='candidate001' else 'xwnram')")
  s=s.replace('Direct0107 control, private RAM0108 candidate','RAM0108 control, ownership0109 candidate').replace('Both xwndir and xwnram payloads','Both xwnram and xwnown payloads')
 if name=='configuration.py':s=s.replace("('xwnram' if case=='candidate001' else 'xwndir')","('xwnown' if case=='candidate001' else 'xwnram')")
 if name=='verify-pair.py':s=s.replace("('control001','xwndir'),('candidate001','xwnram')","('control001','xwnram'),('candidate001','xwnown')")
 if name=='probe.c':
  s=s.replace('114,3,3','116,3,3').replace('ExpectedShadow=expected','ExpectedShadow=1').replace('(expected?108:107)','(expected?109:108)').replace('data[7]!=expected','data[7]!=1').replace('d[1]!=108','(d[1]!=108&&d[1]!=109)')
 if name=='common.py':
  s=s.replace('[114,3,3]','[116,3,3]').replace('108 if candidate else 107,int(candidate)','109 if candidate else 108,1').replace("take('SHADOW_COHERENCE',[int(candidate),0,int(candidate)])","take('SHADOW_COHERENCE',[1,0,1])").replace('        if candidate:\n','        if True:\n')
 if name=='audit.py':s=s.replace('Matched direct0107/control or RAM0108/candidate','Matched RAM0108/control or ownership0109/candidate')
 (k/name).write_text(s,newline='\n')
# Preserve the old meaningful rendering/failure cases, augment with exact ownership.
import shutil
shutil.copytree(old/'tests',k/'tests',dirs_exist_ok=True)
h=k/'tests/framebuf.h';s=h.read_text().replace('*DHSURF;','*DHSURF,*HDEV,*HSEMAPHORE;').replace('HSURF hsurf;} SURFOBJ;','HSURF hsurf; HDEV hdev;} SURFOBJ;')
s=s.replace('#define STYPE_DEVICE 1','#define STYPE_DEVICE 1\n#define STYPE_BITMAP 0')
s=s.replace('#endif','''HSEMAPHORE EngCreateSemaphore(void);
VOID EngDeleteSemaphore(HSEMAPHORE);
VOID EngAcquireSemaphore(HSEMAPHORE);
VOID EngReleaseSemaphore(HSEMAPHORE);
BOOL XwnOwnershipInit(VOID);
VOID APIENTRY XwnOwnershipDisable(VOID);
BOOL XwnRegisterPrimary(PPDEV);
VOID XwnUnregisterPrimary(PPDEV);
PPDEV XwnOwner(SURFOBJ*);
BOOL XwnSelectOwner(PPDEV*,SURFOBJ*);
#endif''');h.write_text(s,newline='\n')
s=(old/'tests-body.c').read_text().replace('#include "shadow.c"','#include "shadow.c"\n#include "ownership.c"\n#include "semaphore-shim.inc"')
s=s.replace('Fault=fault;Active=p;','p->hDevEng=p;Fault=fault;Active=p;').replace('Primary.iType=STYPE_DEVICE;','Primary.hdev=p;Primary.iType=STYPE_DEVICE;')
s=s.replace(' for(f=0;f<=10;f++){',' assert(XwnOwnershipInit());\n for(f=0;f<=10;f++){')
s=s.replace(' printf("{',' XwnOwnershipDisable();\n printf("{')
# Unregistration must precede EngDeleteSurface and all foreign Eng calls.
s=s.replace(' if(s==&BitmapToken)assert(!Active->ShadowObject);',' if(s==&BitmapToken)assert(!Active->ShadowObject);\n if(s==&PrimaryToken)assert(!XwnOwner(&Primary));')
s=s.replace(' cleanup(&p);\n printf',' cleanup(&p);\n printf')
(k/'tests-body.c').write_text(s,newline='\n')
s=(k/'tests/engine-stubs.inc').read_text().replace('\n{\n','\n{\n assert(SemDepth==0); assert(XwnOwner(&Primary)==Active);\n')
(k/'tests/engine-stubs.inc').write_text(s,newline='\n')
s=(old/'host-tests.py').read_text().replace('video-ram-primary-host002','video-ram-ownership-host001').replace("k/'display/shadow.c',","k/'display/shadow.c',k/'display/ownership.c',").replace("'-g',","'-g','-pthread',")
(k/'host-tests.py').write_text(s,newline='\n')

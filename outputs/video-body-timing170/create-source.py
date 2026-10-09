"""Narrow113 profiling diagnostic on reviewed112; no build or guest access."""
import ast,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-clip-upload';d=k/'display';assert not d.exists();shutil.copytree(old/'display',d)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=json.loads((old/'patch-review.json').read_text())
for n,h in parent['source_files'].items():assert sha(d/n)==h,n
shutil.copyfile(k/'profile_math.h',d/'profile_math.h')
def update(name,old,new):
 p=d/name;text=p.read_text();assert text.count(old)==1,(name,old);p.write_bytes(text.replace(old,new).encode())
update('framebuf.h','#pragma once','#pragma once\n#include "profile_math.h"') if '#pragma once' in (d/'framebuf.h').read_text() else update('framebuf.h','typedef struct _PDEV','\n#include "profile_math.h"\ntypedef struct _PDEV')
update('framebuf.h','   ULONG ShadowUploads;','   XWN_PROFILE Profile;\n   ULONG ShadowUploads;')
with (d/'framebuf.h').open('a') as f:f.write('\nVOID XwnProfileInit(PPDEV);\nLONGLONG XwnProfileStart(VOID);\nVOID XwnProfileEnd(PPDEV,ULONG,LONGLONG);\nVOID XwnProfileSnapshot(PPDEV,ULONG *);\n')
update('CMakeLists.txt','    ownership.c','    ownership.c\n    profile_math.h')
with (d/'CMakeLists.txt').open('a') as f:f.write('\noption(XWN_BODY_PROFILE "Diagnostic elapsed engine/upload bodies" OFF)\nif(XWN_BODY_PROFILE)\n target_compile_definitions(xwnown PRIVATE XWN_BODY_PROFILE=1)\nelse()\n target_compile_definitions(xwnown PRIVATE XWN_BODY_PROFILE=0)\nendif()\n')
update('enable.c','   memcpy(pdi, &DevInfo, min(sizeof(DEVINFO), cjDevInfo));','   XwnProfileInit(ppdev);\n   memcpy(pdi, &DevInfo, min(sizeof(DEVINFO), cjDevInfo));')
update('enable.c','   if (Escape == 0x58574431 && OutBytes == 32)','   if (Escape == 0x58574433 && OutBytes == sizeof(Data))\n   {\n      XwnProfileSnapshot(p,Data);memcpy(Out,Data,sizeof(Data));return 1;\n   }\n   if (Escape == 0x58574431 && OutBytes == 32)')
with (d/'ownership.c').open('a') as f:f.write(r'''
/* Separate elapsed diagnostic. Never hold membership lock across an Eng render
 * call, clock query or framebuffer copy. It only protects64bit accounting and
 * snapshots; it remains no replacement for GDI's submitted-PDEV lifetime. */
VOID XwnProfileInit(PPDEV p)
{
    ULONG i; LONGLONG a,b;
    p->Profile.Enabled=XWN_BODY_PROFILE;
    p->Profile.Minimum=~(ULONGLONG)0;
    EngQueryPerformanceFrequency(&p->Profile.Frequency);
    if (p->Profile.Frequency<=0) ++p->Profile.Errors;
    for(i=0;i<128;i++) {
        a=b=-1;EngQueryPerformanceCounter(&a);EngQueryPerformanceCounter(&b);
        XwnProfileCalibration(&p->Profile,a,b);
    }
}
LONGLONG XwnProfileStart(VOID)
{
#if XWN_BODY_PROFILE
    LONGLONG tick=-1;EngQueryPerformanceCounter(&tick);return tick;
#else
    return 0;
#endif
}
VOID XwnProfileEnd(PPDEV p, ULONG kind, LONGLONG begin)
{
    LONGLONG end=XwnProfileStart();
    EngAcquireSemaphore(XwnOwnerLock);
    XwnProfileAccumulate(&p->Profile,kind,begin,end);
    EngReleaseSemaphore(XwnOwnerLock);
}
VOID XwnProfileSnapshot(PPDEV p, ULONG *out)
{
    ULONG i,at;
    RtlZeroMemory(out,128);
    EngAcquireSemaphore(XwnOwnerLock);
    out[0]=0x544d5758;out[1]=113;out[2]=128;out[3]=p->Profile.Enabled;
    out[4]=(ULONG)p->Profile.Frequency;out[5]=(ULONG)((ULONGLONG)p->Profile.Frequency>>32);
    out[6]=p->Profile.Samples;
    out[7]=(ULONG)p->Profile.Minimum;out[8]=(ULONG)(p->Profile.Minimum>>32);
    out[9]=(ULONG)p->Profile.Maximum;out[10]=(ULONG)(p->Profile.Maximum>>32);
    out[11]=p->Profile.Errors;out[12]=p->Profile.Overflows;
    for(i=0;i<4;i++) {
        at=14+i*3;out[at]=p->Profile.Count[i];
        out[at+1]=(ULONG)p->Profile.Ticks[i];out[at+2]=(ULONG)(p->Profile.Ticks[i]>>32);
    }
    out[26]=p->Profile.Reads;
    EngReleaseSemaphore(XwnOwnerLock);
}
''')
update('shadow.c',' LONG y; ULONG bytes;',' LONG y; ULONG bytes; LONGLONG begin;')
update('shadow.c',' for(y=r->top;y<r->bottom;y++) memcpy',' begin=XwnProfileStart();\n for(y=r->top;y<r->bottom;y++) memcpy')
update('shadow.c',' if(p->ShadowUploads!=0xffffffff)',' XwnProfileEnd(p,2,begin);\n if(p->ShadowUploads!=0xffffffff)')
update('shadow.c','VOID XwnUpload(PPDEV p, const RECTL *rect, const CLIPOBJ *clip)','static VOID XwnUploadInternal(PPDEV p, const RECTL *rect, const CLIPOBJ *clip)')
update('shadow.c','ULONG XwnCheckScanout(PPDEV p)','VOID XwnUpload(PPDEV p, const RECTL *rect, const CLIPOBJ *clip)\n{\n LONGLONG begin=XwnProfileStart();\n XwnUploadInternal(p,rect,clip);\n XwnProfileEnd(p,3,begin);\n}\nULONG XwnCheckScanout(PPDEV p)')
# Only two selected engine calls, leaving return/failure/upload semantics exact.
text=(d/'shadow.c').read_text()
for name,kind in [('XwnBitBlt',0),('XwnCopyBits',1)]:
 start=text.index('BOOL APIENTRY '+name);end=text.index('\nBOOL APIENTRY ',start+1)
 piece=text[start:end];assert piece.count(' PPDEV p=NULL; BOOL ok;')==1
 piece=piece.replace(' PPDEV p=NULL; BOOL ok;',' PPDEV p=NULL; BOOL ok; LONGLONG begin;')
 piece=piece.replace(' ok=Eng',' begin=XwnProfileStart();\n ok=Eng',1)
 piece=piece.replace(' if (XwnOwner(',f' XwnProfileEnd(p,{kind},begin);\n if (XwnOwner(',1)
 text=text[:start]+piece+text[end:]
(d/'shadow.c').write_bytes(text.encode())
for p in d.iterdir():
    if p.is_file():p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
r=dict(parent_tree=json.loads((old/'build-report.json').read_text())['source_tree'],original_files=parent['source_files'],
 source_files={p.name:sha(p) for p in d.iterdir() if p.is_file()},driver_semantics_changed=False,
 diagnostic_overhead_added=True,private_profile_escape=hex(0x58574433),profile_version=113,
 lock_scope='Existing membership lock, only accounting/snapshot, never render/clock/copy; lifetime still GDI',physical_access=False)
(k/'source-review.json').write_text(json.dumps(r,indent=2)+'\n');print('Fresh113 timing source; original112 semantics retained, calibration unverified')

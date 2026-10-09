"""Original115 UC scalar row-copy experiment on112, not unpromoted114."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-clip-upload';d=k/'display';assert not d.exists();shutil.copytree(old/'display',d)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();parent=json.loads((old/'patch-review.json').read_text())
for n,h in parent['source_files'].items():assert sha(d/n)==h,n
shutil.copyfile(k/'row_store.h',d/'row_store.h')
def update(name,before,after):
 p=d/name;s=p.read_text();assert s.count(before)==1,(name,before);p.write_bytes(s.replace(before,after).encode())
update('framebuf.h','   ULONG ShadowUploads;','   ULONG RowBoxes, RowFast, RowSlow;\n   ULONGLONG RowBytes, RowFastBytes;\n   ULONG ShadowUploads;')
update('framebuf.h','#endif /* _FRAMEBUF_PCH_ */','VOID XwnRowRecord(PPDEV p, ULONG fast, ULONG slow, ULONG bytes);\nVOID XwnRowSnapshot(PPDEV p, ULONG *out);\n#endif /* _FRAMEBUF_PCH_ */')
update('CMakeLists.txt','    ownership.c','    ownership.c\n    row_store.h')
with (d/'CMakeLists.txt').open('a') as f:f.write('''
option(XWN_UC_STORES "Bounded aligned scalar32bit scanout stores" OFF)
if(XWN_UC_STORES)
 target_compile_definitions(xwnown PRIVATE XWN_UC_STORES=1)
else()
 target_compile_definitions(xwnown PRIVATE XWN_UC_STORES=0)
endif()
''')
update('enable.c','   if (Escape == 0x58574431 && OutBytes == 32)','''   if (Escape == 0x58574435 && OutBytes == sizeof(Data))
   {
      XwnRowSnapshot(p,Data);memcpy(Out,Data,sizeof(Data));return 1;
   }
   if (Escape == 0x58574431 && OutBytes == 32)''')
with (d/'ownership.c').open('a') as f:f.write('''
/* Accounting only: never hold membership lock across render/copy. */
VOID XwnRowRecord(PPDEV p, ULONG fast, ULONG slow, ULONG bytes)
{
    ULONGLONG total=(ULONGLONG)bytes*(fast+slow), quick=(ULONGLONG)bytes*fast;
    EngAcquireSemaphore(XwnOwnerLock);
    if(p->RowBoxes!=0xffffffff)++p->RowBoxes;
    p->RowFast=0xffffffff-p->RowFast<fast?0xffffffff:p->RowFast+fast;
    p->RowSlow=0xffffffff-p->RowSlow<slow?0xffffffff:p->RowSlow+slow;
    p->RowBytes=(~(ULONGLONG)0)-p->RowBytes<total?~(ULONGLONG)0:p->RowBytes+total;
    p->RowFastBytes=(~(ULONGLONG)0)-p->RowFastBytes<quick?~(ULONGLONG)0:p->RowFastBytes+quick;
    EngReleaseSemaphore(XwnOwnerLock);
}
VOID XwnRowSnapshot(PPDEV p, ULONG *out)
{
    RtlZeroMemory(out,128);EngAcquireSemaphore(XwnOwnerLock);
    out[0]=0x57525758;out[1]=115;out[2]=128;out[3]=XWN_UC_STORES;
    out[4]=p->RowBoxes;out[5]=p->RowFast;out[6]=p->RowSlow;
    out[7]=(ULONG)p->RowBytes;out[8]=(ULONG)(p->RowBytes>>32);
    out[9]=(ULONG)p->RowFastBytes;out[10]=(ULONG)(p->RowFastBytes>>32);
    EngReleaseSemaphore(XwnOwnerLock);
}
''')
update('shadow.c','#include "framebuf.h"','#include "framebuf.h"\n#include "row_store.h"')
update('shadow.c',' LONG y; ULONG bytes;',' LONG y; ULONG bytes,fast=0,slow=0;')
before=' for(y=r->top;y<r->bottom;y++) memcpy((BYTE*)p->ScreenPtr+y*p->ScreenDelta+r->left*4,(BYTE*)p->ShadowBits+y*p->ScreenDelta+r->left*4,bytes);'
after=''' for(y=r->top;y<r->bottom;y++) {
  if(XwCopyRow((BYTE*)p->ScreenPtr+y*p->ScreenDelta+r->left*4,
               (BYTE*)p->ShadowBits+y*p->ScreenDelta+r->left*4,bytes,XWN_UC_STORES))++fast;
  else ++slow;
 }
 XwnRowRecord(p,fast,slow,bytes);'''
update('shadow.c',before,after)
for p in d.iterdir():
 if p.is_file():p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
r=dict(parent_tree=json.loads((old/'build-report.json').read_text())['source_tree'],original_files=parent['source_files'],source_files={p.name:sha(p) for p in d.iterdir() if p.is_file()},private_escape='0x58574435',escape_version=115,identity112_retained=True,cache_mode_engine_unchanged=True,physical_access=False,runtime_qualified=False)
(k/'source-review.json').write_text(json.dumps(r,indent=2)+'\n');print('Original115 scalar word-row source on112; no build/runtime qualification')

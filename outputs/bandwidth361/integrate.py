def integrate(src,kit):
 root=src/'win32ss/drivers/displays/framebuf'
 def replace(n,a,b):
  p=root/n;s=p.read_text();assert s.count(a)==1,(n,a);p.write_text(s.replace(a,b))
 assert (root/'capture.h').read_bytes()==(kit/'capture.h').read_bytes()
 for n in ['bandwidth.h','bandwidth.c']:(root/n).write_bytes((kit/n).read_bytes())
 replace('CMakeLists.txt','    memory_warm.c','    memory_warm.c\n    bandwidth.c')
 p=root/'framebuf.h';s=p.read_text();at=s.index('typedef struct')
 s=s[:at]+'#include "bandwidth.h"\n'+s[at:]
 assert s.count('} PDEV, *PPDEV;')==1
 s=s.replace('} PDEV, *PPDEV;','    B361_STATE Bandwidth;\n} PDEV, *PPDEV;')
 s+='\nBOOL XwnBandwidthReserve(PPDEV,B361_CONTEXT*);\nVOID XwnBandwidthPublish(PPDEV,B361_CONTEXT*);\nVOID XwnBandwidthSnapshot(PPDEV,ULONG*);\nVOID XwnBandwidthBegin(PPDEV,const RECTL*,B361_CONTEXT*);\nVOID XwnBandwidthEnd(PPDEV,B361_CONTEXT*,LONGLONG,LONGLONG);\n';p.write_text(s)
 p=root/'ownership.c';s=p.read_text();s+=r"""
BOOL XwnBandwidthReserve(PPDEV p,B361_CONTEXT*c)
{
 BOOL ok=FALSE;EngAcquireSemaphore(XwnOwnerLock);
 if(p->Bandwidth.issued<B361_SLOTS){c->slot=p->Bandwidth.issued++;
  c->record=p->Bandwidth.words[c->slot];c->active=1;ok=TRUE;}
 EngReleaseSemaphore(XwnOwnerLock);return ok;
}
VOID XwnBandwidthPublish(PPDEV p,B361_CONTEXT*c)
{
 EngAcquireSemaphore(XwnOwnerLock);p->Bandwidth.published|=1u<<c->slot;
 EngReleaseSemaphore(XwnOwnerLock);
}
VOID XwnBandwidthSnapshot(PPDEV p,ULONG*out)
{
 ULONG i;RtlZeroMemory(out,B361_BYTES);EngAcquireSemaphore(XwnOwnerLock);
 out[0]=0x42575758;out[1]=361;out[2]=B361_BYTES;
 out[3]=p->Bandwidth.issued;out[4]=p->Bandwidth.published;
 for(i=0;i<B361_SLOTS;i++)if(p->Bandwidth.published&(1u<<i))
  memcpy(out+16+i*B361_PACKET,p->Bandwidth.words[i],4*B361_PACKET);
 EngReleaseSemaphore(XwnOwnerLock);
}
""";p.write_text(s)
 replace('enable.c','   if (Escape == 0x5857443b)',
 '   if (Escape == 0x5857443c && OutBytes == B361_BYTES) {XwnBandwidthSnapshot(p,Out);return 1;}\n   if (Escape == 0x5857443b)')
 replace('shadow.c','#include "row_store.h"','#include "row_store.h"\n#include <pseh/pseh2.h>')
 replace('shadow.c','LONG y; ULONG bytes,fast=0,slow=0; LONGLONG begin;',
 'LONG y; ULONG bytes,fast=0,slow=0; LONGLONG begin,finish; B361_CONTEXT bandwidth;')
 replace('shadow.c',' begin=XwnProfileStart();\n for(y=r->top;',
 ' XwnBandwidthBegin(p,r,&bandwidth);\n begin=XwnProfileStart();finish=-1;\n _SEH2_TRY {\n for(y=r->top;')
 replace('shadow.c',' XwnProfileEnd(p,2,begin);',
 ' finish=XwnProfileStart();\n } _SEH2_FINALLY {\n XwnProfileEnd(p,2,begin);\n XwnBandwidthEnd(p,&bandwidth,begin,finish);\n } _SEH2_END;')

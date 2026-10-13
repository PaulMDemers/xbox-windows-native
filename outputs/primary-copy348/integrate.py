"""Exact-anchor patch in a fresh private source tree only."""
from pathlib import Path
def integrate(src,kit):
    root=src/'win32ss/drivers/displays/framebuf'
    def replace(name,old,new):
        p=root/name;s=p.read_text();assert s.count(old)==1,(name,old[:70]);p.write_text(s.replace(old,new))
    for name in ['primary_plan.h','primary_copy.c']:(root/name).write_bytes((kit/name).read_bytes())
    replace('CMakeLists.txt','    shadow.c\n','    shadow.c\n    primary_copy.c\n')
    with (root/'CMakeLists.txt').open('a') as f:f.write('''
option(XWN_PRIMARY_COPY "Bounded same-primary RAM overlap copy" OFF)
if(XWN_PRIMARY_COPY)
 target_compile_definitions(xwnown PRIVATE XWN_PRIMARY_COPY=1)
else()
 target_compile_definitions(xwnown PRIVATE XWN_PRIMARY_COPY=0)
endif()
''')
    replace('framebuf.h','   ULONG ShadowUploads;','   ULONG PrimaryStats[12];\n   ULONG ShadowUploads;')
    replace('framebuf.h','#endif /* _FRAMEBUF_PCH_ */','''int XwnTryPrimaryCopy(PPDEV,SURFOBJ *,SURFOBJ *,CLIPOBJ *,XLATEOBJ *,RECTL *,POINTL *,ULONGLONG *);
VOID XwnPrimaryRecord(PPDEV,int,ULONGLONG);
VOID XwnPrimarySnapshot(PPDEV,ULONG *);
#endif /* _FRAMEBUF_PCH_ */''')
    replace('shadow.c',' PPDEV p=NULL; BOOL ok; LONGLONG begin;\n if ((TRUE) && !XwnSelectOwner(&p, psoDest))',
            ' PPDEV p=NULL; BOOL ok; LONGLONG begin; int fast; ULONGLONG bytes;\n if ((TRUE) && !XwnSelectOwner(&p, psoDest))')
    original=' ok=EngCopyBits((TRUE ? XwnSub(p, psoDest) : NULL), (TRUE ? XwnSub(p, psoSrc) : NULL), pco, pxlo, prclDest, pptlSrc);'
    replace('shadow.c',original,''' fast=XwnTryPrimaryCopy(p,psoDest,psoSrc,pco,pxlo,prclDest,pptlSrc,&bytes);
 if(fast>=0)ok=TRUE;
 else
'''+original)
    replace('shadow.c',' XwnProfileEnd(p,1,begin);',' XwnProfileEnd(p,1,begin);\n XwnPrimaryRecord(p,fast,bytes);')
    replace('enable.c','   if (Escape == 0x58574437 && OutBytes == 160)', '''   if (Escape == 0x58574438 && OutBytes == sizeof(Data))
   {
      XwnPrimarySnapshot(p,Data);memcpy(Out,Data,sizeof(Data));return 1;
   }
   if (Escape == 0x58574437 && OutBytes == 160)''')
    with (root/'ownership.c').open('a') as f:f.write('''
/* Separate348 accounting outside the selected CopyBits body. */
static VOID XwnPrimaryIncrement(PPDEV p,ULONG index)
{
 if(p->PrimaryStats[index]==0xffffffff)p->PrimaryStats[7]=1;
 else ++p->PrimaryStats[index];
}
VOID XwnPrimaryRecord(PPDEV p,int result,ULONGLONG bytes)
{
 ULONGLONG old;
 EngAcquireSemaphore(XwnOwnerLock);
 XwnPrimaryIncrement(p,0);
 if(result!=-1)XwnPrimaryIncrement(p,1);
 if(result==1)XwnPrimaryIncrement(p,2);
 if(result==0)XwnPrimaryIncrement(p,3);
 if(result<0)XwnPrimaryIncrement(p,4);
 if(result==1) {
  old=((ULONGLONG)p->PrimaryStats[6]<<32)|p->PrimaryStats[5];
  if(~(ULONGLONG)0-old<bytes){old=~(ULONGLONG)0;p->PrimaryStats[7]=1;}
  else old+=bytes;
  p->PrimaryStats[5]=(ULONG)old;p->PrimaryStats[6]=(ULONG)(old>>32);
 }
 EngReleaseSemaphore(XwnOwnerLock);
}
VOID XwnPrimarySnapshot(PPDEV p,ULONG *out)
{
 ULONG i;RtlZeroMemory(out,128);
 EngAcquireSemaphore(XwnOwnerLock);
 out[0]=0x50435758;out[1]=348;out[2]=128;out[3]=XWN_PRIMARY_COPY;
 for(i=0;i<8;i++)out[4+i]=p->PrimaryStats[i];
 EngReleaseSemaphore(XwnOwnerLock);
}
''')

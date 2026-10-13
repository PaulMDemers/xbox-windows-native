"""Exact348 child, instrumentation only; old348 packet byte layout retained."""
from pathlib import Path
def integrate(src,kit):
 root=src/'win32ss/drivers/displays/framebuf'
 def replace(n,a,b):
  p=root/n;s=p.read_text();assert s.count(a)==1,(n,a);p.write_text(s.replace(a,b))
 for n in ['primary_copy.c','primary_plan.h']:assert (root/n).read_bytes()==(kit/n).read_bytes()
 (root/'eligible.h').write_bytes((kit/'eligible.h').read_bytes())
 replace('ownership.c','/* Separate348 accounting outside the selected CopyBits body. */','#include "eligible.h"\n/* Separate348 accounting outside the selected CopyBits body. */')
 replace('ownership.c',' XwnPrimaryIncrement(p,0);',' XwnEligibleRecord(p->PrimaryStats,result,bytes);\n XwnPrimaryIncrement(p,0);')
 with (root/'ownership.c').open('a') as f:f.write('''
VOID XwnEligibleSnapshot(PPDEV p,ULONG *out)
{
 ULONG i;RtlZeroMemory(out,128);
 EngAcquireSemaphore(XwnOwnerLock);
 out[0]=0x50435758;out[1]=351;out[2]=128;out[3]=XWN_PRIMARY_COPY;
 for(i=0;i<11;i++)out[4+i]=p->PrimaryStats[i];
 EngReleaseSemaphore(XwnOwnerLock);
}
''')
 replace('framebuf.h','VOID XwnPrimarySnapshot(PPDEV,ULONG *);','VOID XwnPrimarySnapshot(PPDEV,ULONG *);\nVOID XwnEligibleSnapshot(PPDEV,ULONG *);')
 replace('enable.c','   if (Escape == 0x58574438 && OutBytes == sizeof(Data))','''   if (Escape == 0x58574439 && OutBytes == sizeof(Data))
   {
      XwnEligibleSnapshot(p,Data);memcpy(Out,Data,sizeof(Data));return 1;
   }
   if (Escape == 0x58574438 && OutBytes == sizeof(Data))''')

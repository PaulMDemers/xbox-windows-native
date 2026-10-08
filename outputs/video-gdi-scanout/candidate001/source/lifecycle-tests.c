/* Include the same actual-source harness; augment its normal 46 cases. */
#define main original_main
#include "tests-body.c"
#undef main
#include <sys/mman.h>
int main(void) {
 PDEV p,owners[32];SURFOBJ surfaces[32],foreign;unsigned i;
 RECTL r={0,0,1024,576};ULONG calls,uploads;
 void *guard=mmap(NULL,4096,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);assert(guard!=MAP_FAILED);
 assert(original_main()==0);assert(XwnOwnershipInit());
 for(i=0;i<32;i++) {
  memset(&owners[i],0,sizeof(PDEV));memset(&surfaces[i],0,sizeof(SURFOBJ));
  owners[i].hSurfEng=&owners[i];owners[i].hDevEng=&owners[i];owners[i].ShadowObject=&surfaces[i];
  surfaces[i].iType=STYPE_DEVICE;surfaces[i].dhpdev=&owners[i];surfaces[i].dhsurf=&owners[i];surfaces[i].hsurf=&owners[i];surfaces[i].hdev=&owners[i];
  assert(XwnRegisterPrimary(&owners[i]));
 }
 fresh(&p,0);assert(!DrvEnableSurface(&p));cleanup(&p);
 assert(Maps==1&&Unmaps==1&&Devices==1&&Bitmaps==1&&Deletes==2&&Allocations==1&&Frees==1&&Locks==1&&Unlocks==1);
 for(i=0;i<32;i++)assert(XwnOwner(&surfaces[i])==&owners[i]);
 for(i=1;i<32;i++)XwnUnregisterPrimary(&owners[i]);
 fresh(&p,0);assert(DrvEnableSurface(&p));
 foreign=Primary;foreign.dhpdev=guard;foreign.dhsurf=guard;
 calls=p.ShadowCalls[1];uploads=p.ShadowUploads;
 assert(!XwnCopyBits(&Primary,&foreign,NULL,NULL,&r,NULL));
 assert(!XwnCopyBits(&foreign,&Primary,NULL,NULL,&r,NULL));
 assert(!XwnCopyBits(&Primary,&surfaces[0],NULL,NULL,&r,NULL));
 assert(!XwnCopyBits(&surfaces[0],&Primary,NULL,NULL,&r,NULL));
 assert(calls==p.ShadowCalls[1]&&uploads==p.ShadowUploads);
 /* A bitmap that happens to reuse the primary handle is not substituted. */
 EngineResult=TRUE;WritePixel=FALSE;Other=Primary;Other.iType=STYPE_BITMAP;
 ExpectedDest=&Other;ExpectedOther=&Shadow;assert(XwnCopyBits(&Other,&Primary,NULL,NULL,&r,NULL));
 assert(p.ShadowUploads==uploads);
 cleanup(&p);assert(!XwnOwner(&Primary));assert(XwnOwner(&surfaces[0])==&owners[0]);
 XwnUnregisterPrimary(&owners[0]);XwnOwnershipDisable();assert(!munmap(guard,4096));
 puts("{\"passed\":true,\"additional_cases\":7,\"full_registry_surface_unwind\":true,\"foreign_and_mixed_rejected_before_Eng\":true,\"bitmap_handle_collision_preserved\":true}");return 0;
}

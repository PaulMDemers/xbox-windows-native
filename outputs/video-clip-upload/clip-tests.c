/* Actual uploader with an explicitly synthetic counted-enumeration API. */
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include "framebuf.h"
static RECTL Items[40];
static unsigned Count,Mode,Starts,Enums,Position;
static CLIPOBJ *ExpectedClip;
ULONG CLIPOBJ_cEnumStart(CLIPOBJ *c,BOOL all,ULONG type,ULONG direction,ULONG limit){
 assert(c==ExpectedClip&&!all&&type==CT_RECTANGLES&&direction==CD_ANY&&!limit);
 Starts++;Position=0;return 0xffffffff;
}
BOOL CLIPOBJ_bEnum(CLIPOBJ *c,ULONG size,ULONG *out){
 unsigned n,i;RECTL *rects=(RECTL*)(out+1);
 assert(c==ExpectedClip&&size==4+32*sizeof(RECTL));Enums++;
 if(Mode==6||(Mode==9&&Enums==2)){*out=33;return TRUE;}
 if(Mode==8||(Mode==5&&Enums==1)){*out=0;return TRUE;}
 n=Count-Position;if(n>32)n=32;*out=n;
 for(i=0;i<n;i++)rects[i]=Items[Position++];
 return Mode==9||Position<Count;
}
#include "shadow.c"
static int inside(const RECTL *r,int x,int y){return !r||(x>=r->left&&x<r->right&&y>=r->top&&y<r->bottom);}
int main(void){
 ULONG screen[64*48+32],ram[64*48+32];PDEV p;CLIPOBJ clip;
 RECTL bounds[]={{0,0,64,48},{4,5,54,40},{INT_MIN,INT_MIN,INT_MAX,INT_MAX},{70,0,80,10},{10,10,10,10}};
 unsigned mode,b,active,i,x,y,tests=0;
 for(mode=0;mode<12;mode++)for(b=0;b<6;b++)for(active=0;active<2;active++){
  const RECTL *rect=b?&bounds[b-1]:NULL;unsigned expected_uploads=0;ULONGLONG bytes=0;
  int any=0,fallback=mode==6||mode==7||mode==8||mode==9;
  Mode=mode;Starts=Enums=Position=0;Count=2;
  Items[0]=(RECTL){2,3,6,9};Items[1]=(RECTL){50,35,60,44};
  if(mode==1){Count=40;for(i=0;i<40;i++)Items[i]=(RECTL){1+(int)(i%8)*8,1+(int)(i/8)*8,3+(int)(i%8)*8,3+(int)(i/8)*8};}
  if(mode==2){Items[0]=(RECTL){2,3,16,19};Items[1]=(RECTL){8,10,26,25};}
  if(mode==3){Items[0]=(RECTL){INT_MIN,INT_MIN,10,12};Items[1]=(RECTL){55,40,INT_MAX,INT_MAX};}
  if(mode==4)Count=0;
  if(mode==7){Count=1;Items[0]=(RECTL){8,9,3,4};}
  for(i=0;i<64*48+32;i++){screen[i]=0x11223344;ram[i]=0xaabbccdd;}
  memset(&p,0,sizeof(p));memset(&clip,0,sizeof(clip));
  clip.rclBounds=(RECTL){1,2,63,47};clip.iDComplexity=mode==10?1:DC_COMPLEX;ExpectedClip=mode==11?NULL:&clip;
  p.ScreenPtr=screen+16;p.ShadowBits=ram+16;p.ScreenWidth=64;p.ScreenHeight=48;p.ScreenDelta=256;p.ShadowActive=active;
  XwnUpload(&p,rect,ExpectedClip);
  for(y=0;y<48;y++)for(x=0;x<64;x++){
   int area=active&&inside(rect,(int)x,(int)y)&&(!ExpectedClip||inside(&clip.rclBounds,(int)x,(int)y));
   int hit=0;any|=area;
   if(area){if(fallback||mode>=10)hit=1;else for(i=0;i<Count;i++)hit|=inside(&Items[i],(int)x,(int)y);}
   assert(screen[16+y*64+x]==(hit?0xaabbccdd:0x11223344));
  }
  /* Independently total each actual copy's pixel membership, including fallback. */
  for(i=0;i<Count+1;i++){
   unsigned pixels=0;int copy=0;
   if(mode>=10||fallback){if(i==Count)copy=1;else if(mode==9)copy=1;}
   else if(i<Count)copy=1;
   if(!copy)continue;
   for(y=0;y<48;y++)for(x=0;x<64;x++)
    if(active&&inside(rect,(int)x,(int)y)&&(!ExpectedClip||inside(&clip.rclBounds,(int)x,(int)y))&&(i==Count||inside(&Items[i],(int)x,(int)y)))pixels++;
   if(pixels){expected_uploads++;bytes+=(ULONGLONG)pixels*4;}
  }
  assert(p.ShadowUploads==expected_uploads&&p.ShadowBytes==bytes);
  if(any&&mode<10){assert(Starts==1);assert(Enums==(mode==8?256:mode==1||mode==5||mode==9?2:1));}
  else assert(!Starts&&!Enums);
  for(i=0;i<16;i++)assert(screen[i]==0x11223344&&screen[16+64*48+i]==0x11223344);
  tests++;
 }
 printf("{\"passed\":true,\"cases\":%u,\"sanitizers\":\"ASan/UBSan\"}\n",tests);
 return 0;
}

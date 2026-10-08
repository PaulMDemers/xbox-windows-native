/* Host API shim exercises the actual changed shadow.c, not a copy of its math. */
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include "framebuf.h"
static PDEV Device;
static SURFOBJ Primary,Shadow;
static RECTL *ExpectedBounds;
static CLIPOBJ *ExpectedClip;
static int EngineCalls,EngineResult;
PPDEV XwnOwner(SURFOBJ *s){return s==&Primary?&Device:NULL;}
BOOL XwnSelectOwner(PPDEV *p,SURFOBJ *s){if(s!=&Primary)return FALSE;*p=&Device;return TRUE;}
BOOL EngLineTo(SURFOBJ *s,CLIPOBJ *c,BRUSHOBJ *b,LONG x1,LONG y1,LONG x2,LONG y2,RECTL *r,MIX mix){
 assert(s==&Shadow&&c==ExpectedClip&&r==ExpectedBounds&&b==NULL);
 assert(x1==10&&y1==11&&x2==42&&y2==11&&mix==0x0d0d);EngineCalls++;return EngineResult;
}
#include "shadow.c"
int main(void){
 RECTL rects[]={{10,11,43,12},{10,11,11,44},{-5,-7,9,10},{INT_MIN,INT_MIN,INT_MAX,INT_MAX},{70,0,90,20},{-20,-20,-1,-1},{20,20,20,21},{20,20,19,19},{0,0,64,48}};
 RECTL clips[]={{0,0,64,48},{12,8,23,29},{0,0,0,0},{20,20,10,10},{INT_MIN,INT_MIN,INT_MAX,INT_MAX}};
 ULONG screen[64*48+32],ram[64*48+32];unsigned r,c,active,result,x,y,i;unsigned tests=0;
 for(r=0;r<=sizeof(rects)/sizeof(rects[0]);r++)for(c=0;c<=sizeof(clips)/sizeof(clips[0]);c++)for(active=0;active<2;active++)for(result=0;result<2;result++){
  CLIPOBJ clip;RECTL *bounds=r?&rects[r-1]:NULL;
  for(i=0;i<64*48+32;i++){screen[i]=0x11223344;ram[i]=0xaabbccdd;}
  memset(&Device,0,sizeof(Device));Device.ScreenPtr=screen+16;Device.ShadowBits=ram+16;Device.ScreenWidth=64;Device.ScreenHeight=48;Device.ScreenDelta=256;Device.ShadowActive=active;Device.ShadowObject=&Shadow;
  if(c)clip.rclBounds=clips[c-1];ExpectedClip=c?&clip:NULL;ExpectedBounds=bounds;EngineCalls=0;EngineResult=result;
  assert(XwnLineTo(&Primary,ExpectedClip,NULL,10,11,42,11,bounds,0x0d0d)==(active?(int)result:FALSE));assert(EngineCalls==(int)active);
  unsigned count=0;int valid=bounds&&bounds->left<bounds->right&&bounds->top<bounds->bottom;
  for(y=0;y<48;y++)for(x=0;x<64;x++){
   int hit=active&&(!valid||((LONG)x>=bounds->left&&(LONG)x<bounds->right&&(LONG)y>=bounds->top&&(LONG)y<bounds->bottom))&&(!c||((LONG)x>=clip.rclBounds.left&&(LONG)x<clip.rclBounds.right&&(LONG)y>=clip.rclBounds.top&&(LONG)y<clip.rclBounds.bottom));
   assert(screen[16+y*64+x]==(hit?0xaabbccdd:0x11223344));count+=hit;
  }
  assert(Device.ShadowBytes==(ULONGLONG)count*4&&Device.ShadowUploads==(count!=0));assert(Device.ShadowCalls[6]==active);
  for(i=0;i<16;i++){assert(screen[i]==0x11223344&&screen[16+64*48+i]==0x11223344);}
  tests++;
 }
 assert(!XwnLineTo(&Shadow,NULL,NULL,10,11,42,11,NULL,0x0d0d));tests++;
 printf("{\"passed\":true,\"cases\":%u,\"sanitizers\":\"ASan/UBSan\"}\n",tests);
 return 0;
}

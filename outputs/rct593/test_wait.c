/* MIT. Exercise the actual wait policy with controlled probe observations. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
typedef uint32_t DWORD;typedef unsigned char BYTE;typedef int BOOL;
#define TRUE 1
#define FALSE 0
static DWORD ticks,base;static int mode,calls;static DWORD elapsed,stable,polls;static int fatal,timedout,success;
static DWORD GetTickCount(void){return ticks;}
static void Sleep(DWORD ms){ticks+=ms;}
static void number(const char *n,DWORD v){
 if(!strcmp(n,"saved_wait_elapsed_ms"))elapsed=v;
 if(!strcmp(n,"saved_stable_ms"))stable=v;
 if(!strcmp(n,"saved_wait_polls"))polls=v;
 if(!strcmp(n,"saved_wait_fatal"))fatal=(int)v;
 if(!strcmp(n,"saved_wait_timeout"))timedout=(int)v;
 if(!strcmp(n,"save_phase_file_observed"))success=(int)v;
}
#include "save_wait_policy.h"
static int saved_probe(SAVED_SAMPLE *s,DWORD start){
 DWORD t=ticks-start;calls++;s->bytes=300000;memset(s->sha1,1,20);
 if(mode==1&&t<2000)return 0; /* delayed creation */
 if(mode==2&&t<1000)return 0; /* sharing lock */
 if(mode==3&&t<1500){s->bytes=100+t;s->sha1[0]=(BYTE)calls;}
 if(mode==4&&t<1500)s->sha1[0]=(BYTE)calls; /* same length, changing data */
 if(mode==5)return 0;
 if(mode==6)return -1;
 if(mode==7&&t==750)return 0; /* reset continuity */
 if(mode==8){ticks+=31000;return 1;} /* probe consumed deadline */
 if(mode==9){ticks+=100;s->sha1[0]=(BYTE)calls;return 1;} /* never stable */
 return 1;
}
int main(void){
 for(mode=0;mode<11;mode++){
  base=mode==10?UINT32_MAX-500:0;ticks=base;calls=fatal=timedout=success=0;elapsed=stable=polls=0;
  int ok=wait_saved_file();
  if(mode==5||mode==8||mode==9){assert(!ok&&!success&&timedout);assert(elapsed>=30000);}
  else if(mode==6){assert(!ok&&fatal&&!success&&calls==1);}
  else {assert(ok&&success&&!timedout&&!fatal&&stable>=1000&&polls>=5);}
  if(mode==1)assert(elapsed==3000);
  if(mode==2)assert(elapsed==2000);
  if(mode==3||mode==4)assert(elapsed>=2500);
  if(mode==7)assert(elapsed>=2000);
  if(mode==10)assert(elapsed==1000); /* unsigned tick wrap */
  printf("case=%d passed calls=%d elapsed=%u\n",mode,calls,elapsed);
 }
 return 0;
}

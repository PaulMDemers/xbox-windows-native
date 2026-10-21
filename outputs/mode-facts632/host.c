/* Host tests: DIGEST_MODEL exercises deeper branches using synthetic memory.
 * It is never enabled in main.c or the XBE build. */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "sha256.h"
#ifdef DIGEST_MODEL
static void digest_model(const uint8_t *p,size_t n,uint8_t out[32]) {
 static const uint8_t h[32]={0x0f,0x8d,0xa8,0xf4,0x64,0xbe,0x4b,0x26,0xe3,0x2e,0x60,0xb7,0x76,0x54,0x84,0x89,0x8b,0x02,0x93,0x85,0x0d,0x8a,0x9f,0x39,0x96,0xca,0x44,0xa7,0x42,0x13,0x9c,0xcd};
 assert(p && n==1181);for(unsigned i=0;i<32;i++)out[i]=h[i];
}
#define sha632 digest_model
#endif
#include "facts.h"
#ifdef DIGEST_MODEL
#undef sha632
#endif
#include "memory.h"
static uint8_t image[623712];static unsigned calls,deny;
static int validity(void *o,uint32_t a){return a!=(uint32_t)(uintptr_t)o;}
static int reader(void *o,uint32_t a,void *dest,unsigned n) {
 (void)o;calls++;if(calls==deny || !range632(a,n,validity,0))return 0;
 memcpy(dest,image+a,n);return 1;
}
int main(int argc,char **argv) {
 assert(argc>=2);
 if(!strcmp(argv[1],"sha")) {
  uint8_t d[32];size_t n=fread(image,1,sizeof(image),stdin);sha632(image,n,d);
  for(unsigned i=0;i<32;i++)printf("%02x",d[i]);puts("");return 0;
 }
 if(!strcmp(argv[1],"range")) {
  assert(range632(0,4096,validity,0));assert(range632(4090,20,validity,0));assert(range632(623711,1,validity,0));
  assert(!range632(0,0,validity,0));assert(!range632(0,4097,validity,0));assert(!range632(623711,2,validity,0));
  assert(!range632(0xffffffffu,20,validity,0));assert(!range632(0,20,0,0));
  assert(!range632(4090,20,validity,(void*)(uintptr_t)0x80010fff));
  assert(!range632(4090,20,validity,(void*)(uintptr_t)0x80011000));
  assert(!range632(4090,20,validity,(void*)(uintptr_t)0x8001100d));
  puts("range11");return 0;
 }
 assert(argc==4);assert(fread(image,1,sizeof(image),stdin)==sizeof(image));deny=(unsigned)strtoul(argv[2],0,0);
 Profile632 p,before;memset(&p,0xa5,sizeof(p));before=p;
 unsigned build=(unsigned)strtoul(argv[3],0,0);
 int error=facts632(reader,0,1,0,build,1,0x8003130c,&p);
 if(error)assert(!memcmp(&p,&before,sizeof(p)));
 printf("error=%d reads=%u\n",error,calls);
 if(!error) {
  for(unsigned i=0;i<35;i++)printf("CR %u %u\n",i,p.crtc[i]);
  for(unsigned i=0;i<28;i++)printf("MM %u %u\n",i,p.mmio[i]);
  for(unsigned i=0;i<14;i++)printf("EN %u %u\n",i,p.encoder[i]);
 }
 return 0;
}

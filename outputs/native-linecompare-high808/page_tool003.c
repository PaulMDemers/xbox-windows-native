/* SPDX-License-Identifier: MIT; host-only construction and negative tests. */
#include "page.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "payload_meta.h"
int main(int argc,char **argv)
{
 assert(argc==6);uint8_t code[2304],payload[24256],guard[32768+128],original[sizeof(guard)];
 FILE *f=fopen(argv[1],"rb");assert(f&&fread(code,1,sizeof(code),f)==sizeof(code)&&fgetc(f)==EOF);fclose(f);
 f=fopen(argv[2],"rb");assert(f&&fread(payload,1,sizeof(payload),f)==sizeof(payload)&&fgetc(f)==EOF);fclose(f);
 uint32_t base=strtoul(argv[4],0,0),fb=strtoul(argv[5],0,0);uint8_t *out=guard+64;
 memset(guard,0x5a,sizeof(guard));memcpy(original,guard,sizeof(guard));
 struct reloc705 rel[15];memcpy(rel,payload_reloc,sizeof(rel));
 uint32_t meta[5];memcpy(meta,bridge_meta,sizeof(meta));unsigned n=0;
 assert(!page705(out,code,meta,payload,15359,rel,15,base,fb));++n;
 assert(!page705(out,code,meta,payload,24256,rel,13,base,fb));++n;
 for(unsigned i=0;i<5;++i){uint32_t old=meta[i];meta[i]=0xffffffff;assert(!page705(out,code,meta,payload,24256,rel,15,base,fb));meta[i]=old;++n;}
 const uint32_t badbase[]={0,0x1000001,0x1ff9000,0xfffff000};
 for(unsigned i=0;i<4;++i){assert(!page705(out,code,meta,payload,24256,rel,15,badbase[i],fb));++n;}
 const uint32_t badfb[]={0,0x1fff000,0x2600000,0x3fff000,0xfffff000};
 for(unsigned i=0;i<5;++i){assert(!page705(out,code,meta,payload,24256,rel,15,base,badfb[i]));++n;}
 for(unsigned i=0;i<15;++i){rel[i].value^=1;assert(!page705(out,code,meta,payload,24256,rel,15,base,fb));rel[i].value^=1;++n;}
 assert(!page705(out,code,meta,payload,24256,rel,0,base,fb));++n;
 assert(!memcmp(guard,original,sizeof(guard)));
 assert(page705(out,code,meta,payload,24256,rel,15,base,fb));
 assert(!memcmp(guard,original,64)&&!memcmp(guard+32832,original+32832,64));
 f=fopen(argv[3],"wb");assert(f&&fwrite(out,1,32768,f)==32768);fclose(f);
 printf("PASS page construction and%u output-preserving rejections\n",n);return 0;
}

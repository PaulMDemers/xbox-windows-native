/* SPDX-License-Identifier: MIT; host-only page builder / input rejection test. */
#include "page.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc,char **argv){
 assert(argc==9);unsigned char code[4096],page[4096],unchanged[4096];
 FILE *f=fopen(argv[1],"rb");assert(f && fread(code,1,4096,f)==4096 && fgetc(f)==EOF);fclose(f);
 uint32_t end=strtoul(argv[3],0,0),flat=strtoul(argv[4],0,0),fault=strtoul(argv[5],0,0),base=strtoul(argv[6],0,0),fb=strtoul(argv[7],0,0);
 memset(page,0xa5,sizeof(page));memcpy(unchanged,page,4096);
 assert(!page701(page,code,4095,end,flat,fault,base,fb));assert(!memcmp(page,unchanged,4096));
 assert(!page701(page,code,4096,1217,flat,fault,base,fb));
 assert(!page701(page,code,4096,end,end,fault,base,fb));
 assert(!page701(page,code,4096,end,flat,end,base,fb));
 assert(!page701(page,code,4096,end,flat,fault,base+1,fb));
 assert(!page701(page,code,4096,end,flat,fault,base,0xfffff000));
 assert(!page701(page,code,4096,end,flat,fault,base,base));
 assert(!memcmp(page,unchanged,4096));
 assert(page701(page,code,4096,end,flat,fault,base,fb));
 assert(!memcmp(page,code,end));
 f=fopen(argv[2],"wb");assert(f && fwrite(page,1,4096,f)==4096);fclose(f);
 printf("PASS %s page builder and7 refusal cases\n",argv[8]);return 0;
}

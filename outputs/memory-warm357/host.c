#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "capture.h"
typedef struct {unsigned reads,msrs,cpus,fail,change,absent,large,user,pae,features,count,cs;} MODEL;
static int reg(void *p,unsigned n,uint32_t *v){MODEL*m=p;*v=n==0?0x80010033:n==1?0x123000:n==2?(m->pae?0x20:0x10):m->cs;return 1;}
static int cpuid(void *p,uint32_t leaf,uint32_t *v){MODEL*m=p;memset(v,0,16);
 if(!leaf){v[0]=2;v[1]=0x756e6547;v[3]=0x49656e69;v[2]=0x6c65746e;}
 if(leaf==1){m->cpus++;v[0]=0x68a;v[3]=m->features;}
 return 1;
}
static int msr(void*p,uint32_t n,uint32_t*v){MODEL*m=p;m->msrs++;v[0]=v[1]=0;
 if(n==0xfe)v[0]=m->count|0x500;
 if(n==0x277){v[0]=0x00070406;v[1]=0x00070406;}
 if(n==0x2ff)v[0]=0x800;
 if(n==0x200)v[0]=6;
 if(n==0x201){v[0]=0xfc000800;v[1]=15;}
 return 1;
}
static int readword(void*p,uint32_t a,uint32_t*v){MODEL*m=p;uint32_t va;m->reads++;
 if(m->reads==m->fail)return 0;
 if(a==0xc0300c00)*v=0x123003;
 else if(a>=0xc0300000&&a<0xc0301000)*v=m->absent?0:0x200003|(m->large?0x80:0)|(m->user?4:0);
 else{assert(!m->absent&&!m->large&&!m->user);assert(a>=0xc0000000&&a<0xc0400000);
  va=(a-0xc0000000)<<10;
  *v=va>=0xfb000000?0x0370001b+(va-0xfb000000):0x01000003+(va-0xe1000000);
 }
 if(m->reads==m->change)*v^=0x1000;
 return 1;
}
int main(int argc,char**argv){
 M354_VIEW v={0x80001000,0x80002000,0x80003000,0xe1000123,0xfb000000,1920,1080,7680,32};
 MODEL model;M354_IO io={reg,cpuid,msr,readword,&model};unsigned checks=0,offset,n;
 uint32_t *allocation=malloc(M354_BYTES+8),*o=allocation+1;assert(allocation);
 #define RESET() do{memset(&model,0,sizeof(model));model.features=0x11020;model.count=8;allocation[0]=allocation[M354_WORDS+1]=0x12345678;}while(0)
 #define CHECK(x) do{assert(x);checks++;}while(0)
 for(offset=0;offset<4096;offset+=17){RESET();v.shadow=0xe1000000+offset;m354_capture(&v,&io,o);
  CHECK(!o[3]);CHECK(o[14]==4050+(offset!=0));CHECK(model.cpus==2);
  CHECK(!memcmp(o+16,o+96,80*4));CHECK(allocation[0]==0x12345678&&allocation[M354_WORDS+1]==0x12345678);
 }
 v.shadow=0xe1000123;
 for(n=1;n<16210;n+=31){RESET();model.fail=n;m354_capture(&v,&io,o);CHECK(o[3]==M354_READ);CHECK(model.reads==n);}
 for(n=8110;n<16206;n+=31){RESET();model.change=n;m354_capture(&v,&io,o);CHECK(o[3]&M354_CHANGED);}
 RESET();model.absent=1;m354_capture(&v,&io,o);CHECK(o[3]==M354_PAGE&&model.reads==2);
 RESET();model.large=1;m354_capture(&v,&io,o);CHECK(o[3]==M354_PAGE&&model.reads==2);
 RESET();model.user=1;m354_capture(&v,&io,o);CHECK(o[3]==M354_PAGE&&model.reads==2);
 RESET();model.pae=1;m354_capture(&v,&io,o);CHECK(o[3]==M354_CPU&&!model.reads&&!model.msrs);
 RESET();model.cs=3;m354_capture(&v,&io,o);CHECK(o[3]==M354_CPU&&!model.reads&&!model.msrs);
 RESET();model.features=0;m354_capture(&v,&io,o);CHECK(o[3]==M354_CPU&&!model.reads&&!model.msrs);
 RESET();model.count=9;m354_capture(&v,&io,o);CHECK(o[3]==M354_CPU&&!model.reads&&model.msrs==3);
 RESET();v.screen=v.shadow;m354_capture(&v,&io,o);CHECK(o[3]==M354_INPUT&&!model.reads);
 v.screen=0xfb000000;RESET();v.shadow=0xfffff000;m354_capture(&v,&io,o);CHECK(o[3]==M354_INPUT&&!model.reads);
 v.shadow=0xe1000123;RESET();model.change=1;m354_capture(&v,&io,o);CHECK(o[3]==M354_SELF);
 RESET();m354_capture(&v,&io,o);CHECK(!o[3]);
 if(argc==2){FILE*f=fopen(argv[1],"wb");assert(f);assert(fwrite(o,1,M354_BYTES,f)==M354_BYTES);assert(!fclose(f));}
 printf("{\"checks\":%u,\"rows\":%u,\"model_only\":true}\n",checks,o[14]);free(allocation);return 0;
}

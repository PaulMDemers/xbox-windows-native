/* SPDX-License-Identifier: MIT. No Xbox APIs, kernel, device or mapping model. */
#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
uint32_t saved_esp,seed_flags,expected_flags,seeds[7],observed[9];
extern void invoke510(void);
extern unsigned char capture510_begin[],capture510_end[];
static uint32_t random_word(uint32_t *s) { *s=*s*1664525u+1013904223u;return *s; }
static int check(void) {
 uint32_t e[9]={seeds[0],seeds[1],seeds[2],saved_esp-4,seeds[3],seeds[4],seeds[5],seeds[6],expected_flags};
 return !memcmp(e,observed,sizeof(e));
}
int main(int argc,char **argv) {
 assert(argc==2);unsigned char stub[5];FILE *f=fopen(argv[1],"rb");assert(f);
 assert(fread(stub,1,5,f)==5 && fgetc(f)==EOF && !fclose(f));assert(stub[0]==0xe9);
 int32_t rel;memcpy(&rel,stub+1,4);assert((int64_t)0x11105+rel==0x94aff);
 void *low=mmap((void *)0x11000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
 void *high=mmap((void *)0x94000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
 assert(low==(void *)0x11000 && high==(void *)0x94000);
 size_t cap=(size_t)(capture510_end-capture510_begin);assert(cap>0 && cap<100);
 memcpy((void *)0x11100,stub,5);memcpy((void *)0x94aff,capture510_begin,cap);
 assert(!mprotect(low,4096,PROT_READ|PROT_EXEC) && !mprotect(high,4096,PROT_READ|PROT_EXEC));
 uint32_t random=0x51012345u;unsigned checks=0;unsigned bits[7]={0,2,4,6,7,10,11};
 for(unsigned i=0;i<4096;i++) {
  for(unsigned j=0;j<7;j++)seeds[j]=random_word(&random);
  seed_flags=0x202;for(unsigned j=0;j<7;j++)if(i&(1u<<j))seed_flags|=1u<<bits[j];
  memset(observed,0,sizeof(observed));invoke510();assert(check());checks++;
 }
 /* Executed negative controls: flag modification and one extra stack push. */
 unsigned refused=0;
 for(unsigned mode=0;mode<2;mode++) {
  assert(!mprotect(low,4096,PROT_READ|PROT_WRITE));
  unsigned char bad[6]={mode?0x50:0xf8,0xe9,0,0,0,0};rel=0x94aff-0x11106;memcpy(bad+2,&rel,4);
  memcpy((void *)0x11100,bad,6);assert(!mprotect(low,4096,PROT_READ|PROT_EXEC));
  seed_flags=0x603;invoke510();assert(!check());refused++;
 }
 assert(!munmap(low,4096) && !munmap(high,4096));
 printf("{\"passed\":true,\"actual_jump_cases\":%u,\"executed_negative_controls\":%u,\"capture_bytes\":%zu,\"xbox_APIs_executed\":false}\n",checks,refused,cap);
 return 0;
}

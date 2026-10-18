#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/prctl.h>
#include <sys/mman.h>
#include <setjmp.h>
#include <ucontext.h>
static sigjmp_buf done;
static unsigned expected_result;
static uint32_t *record;
extern void enter_stub(void);
static int mode,stage,active,starts,writes,reads,tscs,cli_seen,config_step;
static unsigned idle_reads,completion_reads;
static uint64_t clock_value;
static unsigned sticky;

static unsigned status(void) {
    reads++;
    assert(cli_seen);
    if(!active) {
        idle_reads++;
        if(mode==38)return 0x8;
        if(mode==40)return 0x808;
        if(mode==47)return 0x8;
        if(idle_reads<4) {
            if(mode==32)return 0x8;
            if(mode==36)return 0x808;
            if(mode==37)return 0x818;
        }
        if(mode==2 || mode==14 || (mode==6 && starts==1))return 0x800;
        if(mode==4 || mode==21)return 0x20;
        if(mode==16)return 0x400;
        if(mode==20 && idle_reads<4)return 0x800;
        return sticky;
    }
    completion_reads++;
    if(mode==39)return 0x8;
    if(mode==41)return 0x818;
    if(mode>=42 && mode<=46) {
        static const unsigned errors[]={0x809,0x80a,0x80c,0x828,0x848};
        return errors[mode-42];
    }
    if(mode==48)return 0x808;
    if(completion_reads<4) {
        if(mode==33)return 0x8;
        if(mode==32 || mode==34 || mode==49 || mode==50)return 0x808;
        if(mode==35)return 0x818;
    }
    if(mode==3 || (mode==7 && starts==2))return 0;
    if(mode==15)return 0x800;
    if(mode==5 || (mode==8 && starts==2))return 0x20;
    if(mode==17)return 0x400;
    if(mode==18)return 0x30;
    if(mode==19 && completion_reads<4)return 0x800;
    if(mode==31 && completion_reads<4)return 0x810;
    active=0;sticky=0x10;return sticky;
}
static void output(unsigned port,unsigned value,unsigned width) {
    writes++;assert(cli_seen && !active && !(record[8]&0x808));
    if(port==0xc000) {
        assert(width==2 && value==0x10 && sticky==0x10);
        sticky=0;return;
    }
    if(config_step==0)assert(port==0xc004 && width==1 && value==0x20);
    if(config_step==1)assert(port==0xc008 && width==1 && value==(starts==0?8u:7u));
    if(config_step==2)assert(port==0xc006 && width==2 && value==(starts==0?(stage==1?0xffu:0xa5u):1u));
    if(config_step==3) {
        assert(port==0xc002 && width==1 && value==0x1a && starts<2);
        starts++;active=1;config_step=0;completion_reads=0;idle_reads=0;return;
    }
    config_step++;
}
static uint64_t tick(void) {
    tscs++;
    if(tscs==1)return clock_value=1000;
    if(mode==47 && tscs>=4)return 64001000;
    if(mode==48 && completion_reads>=2)return 64001000;
    if(mode==13 || mode==29)return 999;
    if(mode==30)return UINT64_C(0x1000003e8);
    if(mode==9 || (mode==10 && starts==1) || (mode==11 && starts==1 && !active) || (mode==12 && starts==2))return 64001000;
    if(mode==14 || mode==15)return clock_value;
    return clock_value+=100;
}
static void trap(int sig,siginfo_t *info,void *v) {
    (void)info;assert(sig==SIGSEGV);
    ucontext_t *u=v;greg_t *g=u->uc_mcontext.gregs;
    if((uint32_t)g[REG_EIP]==0x26000f5) {
        assert(record[5]==1 && expected_result==1);
        assert((uint32_t)g[REG_EAX]==0x11111111 && (uint32_t)g[REG_EBX]==0x22222222);
        assert((uint32_t)g[REG_ECX]==0x33333333 && (uint32_t)g[REG_EDX]==0x44444444);
        assert((uint32_t)g[REG_ESI]==0x55555555 && (uint32_t)g[REG_EDI]==0x66666666);
        assert((uint32_t)g[REG_EBP]==0x77777777 && (uint32_t)g[REG_ESP]==0x2800000);
        assert(((uint32_t)g[REG_EFL]&0xed5)==0xed5);
        siglongjmp(done,1);
    }
    unsigned char *p=(void *)(uintptr_t)g[REG_EIP];
    unsigned port=(unsigned)g[REG_EDX]&0xffff;
    if(p[0]==0xfa) {cli_seen++;g[REG_EIP]++;return;}
    if(p[0]==0xf4) {assert(record[5]==expected_result && expected_result!=1);siglongjmp(done,2);}
    if(p[0]==0x0f && p[1]==0x31) {
        uint64_t t=tick();g[REG_EAX]=(uint32_t)t;g[REG_EDX]=(uint32_t)(t>>32);g[REG_EIP]+=2;return;
    }
    if(p[0]==0x66 && p[1]==0xed) {
        assert(port==0xc000);g[REG_EAX]=(g[REG_EAX]&0xffff0000u)|status();g[REG_EIP]+=2;return;
    }
    if(p[0]==0x66 && p[1]==0xef) {output(port,(unsigned)g[REG_EAX]&0xffff,2);g[REG_EIP]+=2;return;}
    if(p[0]==0xee) {output(port,(unsigned)g[REG_EAX]&0xff,1);g[REG_EIP]++;return;}
    fprintf(stderr,"unexpected stub fault %p %02x mode%d\n",(void*)p,p[0],mode);abort();
}
int main(int argc,char **argv) {
    assert(argc==2);FILE *f=fopen(argv[1],"rb");assert(f);
    unsigned char blob[4096];size_t n=fread(blob,1,sizeof(blob),f);assert(n>100 && n<4096 && feof(f));fclose(f);
    assert(mmap((void*)0x2680000,4096,7,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x2680000);
    assert(mmap((void*)0x27f0000,65536,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x27f0000);
    assert(mmap((void*)0x2600000,4096,0,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x2600000);
    stack_t ss={0};ss.ss_size=65536;ss.ss_sp=malloc(ss.ss_size);assert(ss.ss_sp);assert(!sigaltstack(&ss,NULL));
    struct sigaction sa={0};sa.sa_sigaction=trap;sa.sa_flags=SA_SIGINFO|SA_ONSTACK;
    assert(!sigaction(SIGSEGV,&sa,NULL));assert(!prctl(PR_SET_TSC,PR_TSC_SIGSEGV,0,0,0));
    static const unsigned results[51]={1,1,3,4,5,5,3,4,5,6,6,6,6,7,3,4,5,5,5,1,1,5,1,2,2,2,2,2,2,7,6,1,1,1,1,1,1,1,3,4,3,4,5,5,5,5,5,6,6,1,1};
    unsigned cases=0;
    for(mode=0;mode<51;mode++) {
        if(mode>=23 && mode<=28)continue;
        memcpy((void*)0x2680000,blob,n);memset((void*)0x27f0000,0xa7,65536);
        record=(void*)40370216;expected_result=results[mode];stage=2;
        active=starts=writes=reads=tscs=cli_seen=config_step=0;idle_reads=completion_reads=0;sticky=mode==1?0x10:0;
        int stopped=sigsetjmp(done,1);if(!stopped)enter_stub();
        assert(stopped==(expected_result==1?1:2));
        assert(record[5]==expected_result && record[22]==1 && record[3]==2 && record[4]==0xa5);
        assert(record[9]<=4096 && record[19]<=10 && record[23]==0);
        for(unsigned i=0;i<65000;i++)assert(*((unsigned char*)0x27f0000+i)==0xa7);
        char name[40];snprintf(name,sizeof(name),"stub%02d.bin",mode);FILE *o=fopen(name,"wbx");assert(o);assert(fwrite(record,1,96,o)==96);fclose(o);
        cases++;
    }
    printf("PASS %u actual post-stack stub cases; port/CLI/TSC modeled; original stack installation and success register preservation verified\n",cases);
    return 0;
}

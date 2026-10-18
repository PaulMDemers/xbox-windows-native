/* SPDX-License-Identifier: MIT
 * Execute actual 32-bit marker; model IN/OUT/CLI/RDTSC via Linux signal traps.
 * No real hardware I/O, privileged interrupt change, or Xbox qualification.
 */
#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <signal.h>
#include <sys/prctl.h>
#include <ucontext.h>

uint32_t *test_record,expected_esp,before_flags,after_flags,after_regs[8];
extern void invoke_test(void);
static uint32_t r[24];
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
    writes++;assert(cli_seen && !active && !(r[8]&0x808));
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
    unsigned char *p=(void *)(uintptr_t)g[REG_EIP];
    unsigned port=(unsigned)g[REG_EDX]&0xffff;
    if(p[0]==0xfa) {cli_seen++;g[REG_EIP]++;return;}
    if(p[0]==0x0f && p[1]==0x31) {
        uint64_t t=tick();g[REG_EAX]=(uint32_t)t;g[REG_EDX]=(uint32_t)(t>>32);g[REG_EIP]+=2;return;
    }
    if(p[0]==0x66 && p[1]==0xed) {
        assert(port==0xc000);g[REG_EAX]=(g[REG_EAX]&0xffff0000u)|status();g[REG_EIP]+=2;return;
    }
    if(p[0]==0x66 && p[1]==0xef) {output(port,(unsigned)g[REG_EAX]&0xffff,2);g[REG_EIP]+=2;return;}
    if(p[0]==0xee) {output(port,(unsigned)g[REG_EAX]&0xff,1);g[REG_EIP]++;return;}
    fprintf(stderr,"Unexpected fault opcode %02x %02x at %p mode%d\n",p[0],p[1],(void*)p,mode);assert(0);
}
int main(void) {
    struct sigaction sa={0};sa.sa_sigaction=trap;sa.sa_flags=SA_SIGINFO;
    assert(sigaction(SIGSEGV,&sa,NULL)==0);
    assert(prctl(PR_SET_TSC,PR_TSC_SIGSEGV,0,0,0)==0);
    static const unsigned expected[51]={1,1,3,4,5,5,3,4,5,6,6,6,6,7,3,4,5,5,5,1,1,5,1,2,2,2,2,2,2,7,6,1,1,1,1,1,1,1,3,4,3,4,5,5,5,5,5,6,6,1,1};
    for(mode=0;mode<51;mode++) {
        memset(r,0,sizeof(r));r[0]=0x354b524d;r[1]=1;r[2]=96;
        stage=mode==22||mode==28||mode==49?2:1;r[3]=stage;r[4]=stage==1?0xff:0xa5;
        if(mode==23)r[0]^=1;
        if(mode==24)r[1]=2;
        if(mode==25)r[2]=95;
        if(mode==26)r[3]=3;
        if(mode==27||mode==28)r[4]^=1;
        test_record=r;active=starts=writes=reads=tscs=cli_seen=config_step=0;
        idle_reads=completion_reads=0;sticky=mode==1?0x10:0;
        invoke_test();
        assert(after_regs[0]==0x66666666 && after_regs[1]==0x55555555 && after_regs[2]==0x77777777);
        assert(after_regs[3]==expected_esp && after_regs[4]==0x22222222 && after_regs[5]==0x44444444 && after_regs[6]==0x33333333 && after_regs[7]==0x11111111);
        assert(((after_flags^before_flags)&0xed5)==0);
        assert(r[5]==expected[mode] && r[22]==1 && r[9]<=4096 && starts<=2 && writes<=10);
        assert(r[19]==(unsigned)writes && r[9]==(unsigned)reads && r[21]==(unsigned)tscs);
        if(r[5]==1)assert(r[6]==2 && r[7]==3 && starts==2 && !active && !config_step);
        if(r[5]==2)assert(!starts && !writes && !reads && !tscs && !cli_seen);
        if(mode==2||mode==4||mode==9||mode==13||mode==14||mode==16||mode==21||mode==29||mode==30)assert(!writes && !starts);
        if(mode==6||mode==7||mode==8||mode==11||mode==12)assert(r[6]==1);
        if(mode==38 || mode==40)assert(!writes && r[9]==4096);
        if(mode==39 || mode==41)assert(writes==4 && r[9]==4096 && r[6]==0);
        if(mode>=42 && mode<=46)assert(r[5]==5 && writes==4 && !r[6]);
        if(mode==47)assert(!writes && r[5]==6);
        if(mode==48)assert(writes==4 && r[5]==6);
        char name[40];snprintf(name,sizeof(name),"case%02d.bin",mode);
        FILE *f=fopen(name,"wb");assert(f);assert(fwrite(r,1,sizeof(r),f)==sizeof(r));assert(fclose(f)==0);
        uint32_t saved[24];memcpy(saved,r,sizeof(r));int old_writes=writes,old_reads=reads,old_tscs=tscs,old_cli=cli_seen;
        invoke_test();
        assert(!memcmp(saved,r,sizeof(r)) && writes==old_writes && reads==old_reads && tscs==old_tscs && cli_seen==old_cli);
    }
    assert(prctl(PR_SET_TSC,PR_TSC_ENABLE,0,0,0)==0);
    puts("PASS 51 actual x86 marker cases; registers/flags/stack preserved; hardware I/O and TSC MODELED");
    return 0;
}

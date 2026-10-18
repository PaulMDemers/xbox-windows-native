/* SPDX-License-Identifier: MIT
 * Execute the actual assembled x86 wrapper. Kernel/file effects are modeled;
 * this is not Xbox execution, allocation success or physical boot qualification.
 */
#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <setjmp.h>
#include <signal.h>
#include <ucontext.h>
#include <sys/prctl.h>

#include "symbols.h"
#define API __attribute__((stdcall))
static sigjmp_buf done;
static int new_success;
static int case_id;
static int wmode,wc,ww,wf,wcl;
static unsigned char witness[256];
static unsigned witness_size;
static void save_witness(void) {
    char name[48];snprintf(name,sizeof(name),"witness%03d.bin",case_id);
    FILE *f=fopen(name,"wbx");assert(f);assert(fwrite(witness,1,witness_size,f)==witness_size);fclose(f);
}
static int fmode,fc,fw,ff,fcl;
static unsigned char frozen_marker[96];
static unsigned marker_io_at_snapshot;
static unsigned char fallback[192];
static unsigned fallback_size;
static volatile sig_atomic_t handoffs;
static int pmode, allocs, physcalls, virtuals, creates, writes, flushes, closes;
static unsigned char output[256];
static uint32_t output_size;
static unsigned char *image;
static size_t image_size;
static void clear_df(void) { __asm__ volatile("cld" ::: "cc"); }
static uint32_t API alloc(uint32_t size,uint32_t low,uint32_t high,uint32_t align,uint32_t prot) {
    clear_df(); allocs++; assert(prot==4);
    if(allocs==1) {
        assert(size==0x100000 && low==0x200000 && high==0x1ffffff && align==0);
        return pmode==1 ? 0 : 0x80400000;
    }
    assert(allocs==2 && size==4096 && low==0x1000000 && high==0x2000000 && align==16);
    return pmode==2 ? 0 : 0x81000000;
}
static uint32_t API physical(uint32_t va) {
    clear_df(); physcalls++; assert(va==0x80400000 || va==0x81000000 || va==0x1000000);
    if(physcalls==3) {
        assert(va==0x1000000);
        if(pmode==16)*(unsigned char*)0x80400000^=1;
        if(pmode==17)*((unsigned char*)0x81000000+500)^=1;
        if(pmode==18)*((unsigned char*)0x1000000+500)^=1;
        if(pmode==19)*((unsigned char*)0x81000000+74)^=1;
        if(pmode==20)*((unsigned char*)0x1000000+74)^=1;
        return 0x3000000;
    }
    uint32_t pa=va&0x7fffffff;
    if(pmode==15 && physcalls==2)pa+=4096;
    if(pmode==4 && physcalls==1) __asm__ volatile("std" ::: "cc");
    return pa;
}
static uint32_t API virtual_alloc(uint32_t *base,uint32_t zero,uint32_t *size,uint32_t type,uint32_t prot) {
    clear_df(); virtuals++;
    assert(*base==(pmode==15?0x1001000:0x1000000) && zero==0 && *size==4096 && type==0x3000 && prot==4);
    if(pmode==13)*base+=4096;
    if(pmode==14)*size=8192;
    return pmode==3 ? 0xc0000017u : pmode==44 ? 0x103 : 0;
}
static uint32_t API create(uint32_t *handle,uint32_t access,uint32_t *oa,uint32_t *iosb,
                           void *allocation,uint32_t attrs,uint32_t share,uint32_t disposition,uint32_t options) {
    clear_df();
    assert(access==0x40100000 && !allocation && attrs==0x80 && share==0 && disposition==2 && options==0x62);
    assert(oa[0]==0 && oa[2]==0x40);
    uint16_t *name=(void*)oa[1];uint32_t *ptr=(void*)((char*)name+4);
    const char *fall="\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot487a\\refusal.bin";
    if(!strcmp((char*)*ptr,fall)) {
        memcpy(frozen_marker,(void*)MARKER_ADDRESS,96);
        marker_io_at_snapshot=*(uint32_t *)(frozen_marker+76);
        if(case_id==84)memset((void*)MARKER_ADDRESS,0xa7,96);
        fc++;assert(fc==1 && name[0]==strlen(fall) && name[1]==name[0]+1);
        if(fmode==45)return 0xc0000035u;
        if(fmode==54)return 0x103;
        *handle=0x4781;
        if(fmode==50)return 0;
        iosb[0]=0;iosb[1]=2;return 0;
    }
    const char *wp="\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot487a\\handoff.bin";
    if(!strcmp((char*)*ptr,wp)) {
        wc++;assert(wc==1 && closes==1 && flushes==2 && output_size==176);
        assert(name[0]==strlen(wp) && name[1]==name[0]+1);
        assert(*(uint32_t*)(MARKER_ADDRESS+20)==1);
        if(wmode==1)return 0xc0000035u;
        if(wmode==2)return 0x103;
        *handle=wmode==6?0:0x4872;
        if(wmode==25)return 0xc0000185u;
        if(wmode==26)return 0x103;
        if(wmode==4)return 0;
        iosb[0]=wmode==3?0xc0000185u:0;iosb[1]=wmode==5?1:2;return 0;
    }
    creates++;
    const char *expected="\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot487a\\report.bin";
    assert(name[0]==strlen(expected) && name[1]==name[0]+1 && strcmp((char*)*ptr,expected)==0);
    if(pmode==5)return 0xc0000035u; /* existing report */
    if(pmode==21)return 0x103;
    *handle=pmode==25?0:0x4780;
    if(pmode==23)return 0;
    iosb[0]=pmode==22?0xc0000185u:0;iosb[1]=pmode==24?1:2;return 0;
}
static uint32_t API write_file(uint32_t handle,uint32_t event,uint32_t apc,uint32_t ctx,
                              uint32_t *iosb,const void *buf,uint32_t bytes,uint32_t offset) {
    clear_df();
    if(handle==0x4781) {
        fw++;assert(fw==1 && bytes==192 && !event && !apc && !ctx && !offset);
        if(fmode==47)return 0xc0000185u;
        fallback_size=fmode==46?191:192;memcpy(fallback,buf,fallback_size);
        iosb[0]=fmode==51?0xc0000185u:0;iosb[1]=fallback_size;
        return fmode==53?0x103:0;
    }
    if(handle==0x4872) {
        ww++;assert(ww==1 && bytes==256 && !event && !apc && !ctx && !offset);
        if(wmode==7)return 0xc0000185u;
        witness_size=wmode==11?255:256;memcpy(witness,buf,witness_size);
        if(wmode==10)return 0;
        iosb[0]=wmode==9?0xc0000185u:0;iosb[1]=wmode==27?257:witness_size;
        return wmode==8?0x103:0;
    }
    writes++;
    assert(handle==0x4780 && !event && !apc && !ctx && !offset);
    assert((writes==1 && bytes==160)||(writes==2 && bytes==16));
    if((pmode==10 && writes==1)||(pmode==11 && writes==2))return 0xc0000185u;
    uint32_t actual=bytes-((pmode==6 && writes==1)||(pmode==7 && writes==2));
    assert(output_size+actual<=sizeof(output));memcpy(output+output_size,buf,actual);output_size+=actual;
    if((pmode==28 && writes==1)||(pmode==40 && writes==2))return 0;
    iosb[0]=((pmode==27 && writes==1)||(pmode==39 && writes==2))?0xc0000185u:0;
    iosb[1]=actual;
    return ((pmode==26 && writes==1)||(pmode==38 && writes==2))?0x103:0;
}
static uint32_t API flush(uint32_t handle,uint32_t *iosb) {
    clear_df();
    if(handle==0x4781) {
        ff++;assert(ff==1);iosb[0]=0;iosb[1]=0;
        return fmode==48?0xc0000185u:fmode==52?0x103:0;
    }
    if(handle==0x4872) {
        wf++;assert(wf==1);
        if(wmode==15)return 0;
        iosb[0]=wmode==14?0xc0000185u:0;iosb[1]=0;
        return wmode==12?0xc0000185u:wmode==13?0x103:0;
    }
    flushes++;assert(handle==0x4780);
    if((pmode==31 && flushes==1)||(pmode==43 && flushes==2))return 0;
    iosb[0]=((pmode==30 && flushes==1)||(pmode==42 && flushes==2))?0xc0000185u:0;
    iosb[1]=0;
    if((pmode==29 && flushes==1)||(pmode==41 && flushes==2))return 0x103;
    return ((pmode==8 && flushes==1)||(pmode==9 && flushes==2)) ? 0xc0000185u : 0;
}
static uint32_t API close_file(uint32_t handle) {
    clear_df();
    if(handle==0x4781) {fcl++;assert(fcl==1);return fmode==49?0xc0000185u:0;}
    if(handle==0x4872) {
        wcl++;assert(wcl==1);
        if(wmode==18 || wmode==23)*(unsigned char*)0x80400000^=1;
        if(wmode==19)*((unsigned char*)0x81000000+500)^=1;
        if(wmode==20)*((unsigned char*)0x1000000+500)^=1;
        if(wmode==21)*((unsigned char*)0x81000000+74)^=1;
        if(wmode==22)*((unsigned char*)0x1000000+74)^=1;
        if(wmode==28)*((unsigned char*)0x80400000+524861)^=1;
        if(wmode==23 || wmode==24)__asm__ volatile("std" ::: "cc");
        return wmode==16?0xc0000185u:wmode==17?0x103:0;
    }
    closes++;assert(handle==0x4780);
    if(pmode==33)*(unsigned char*)0x80400000^=1;
    if(pmode==34)*((unsigned char*)0x81000000+500)^=1;
    if(pmode==35)*((unsigned char*)0x1000000+500)^=1;
    if(pmode==36)*((unsigned char*)0x81000000+74)^=1;
    if(pmode==37)*((unsigned char*)0x1000000+74)^=1;
    return pmode==32?0xc0000185u:0;
}
static void API reboot(uint32_t type) {clear_df();assert(type==1);siglongjmp(done,1);}

static int mode,stage,active,starts,port_writes,port_reads,tscs,cli_seen,config_step;
static unsigned idle_port_reads,completion_port_reads;
static uint64_t clock_value;
static unsigned sticky;

static unsigned status(void) {
    port_reads++;
    assert(cli_seen);
    if(!active) {
        idle_port_reads++;
        if(mode==38)return 0x8;
        if(mode==40)return 0x808;
        if(mode==47)return 0x8;
        if(idle_port_reads<4) {
            if(mode==32)return 0x8;
            if(mode==36)return 0x808;
            if(mode==37)return 0x818;
        }
        if(mode==2 || mode==14 || (mode==6 && starts==1))return 0x800;
        if(mode==4 || mode==21)return 0x20;
        if(mode==16)return 0x400;
        if(mode==20 && idle_port_reads<4)return 0x800;
        return sticky;
    }
    completion_port_reads++;
    if(mode==39)return 0x8;
    if(mode==41)return 0x818;
    if(mode>=42 && mode<=46) {
        static const unsigned errors[]={0x809,0x80a,0x80c,0x828,0x848};
        return errors[mode-42];
    }
    if(mode==48)return 0x808;
    if(completion_port_reads<4) {
        if(mode==33)return 0x8;
        if(mode==32 || mode==34 || mode==49 || mode==50)return 0x808;
        if(mode==35)return 0x818;
    }
    if(mode==3 || (mode==7 && starts==2))return 0;
    if(mode==15)return 0x800;
    if(mode==5 || (mode==8 && starts==2))return 0x20;
    if(mode==17)return 0x400;
    if(mode==18)return 0x30;
    if(mode==19 && completion_port_reads<4)return 0x800;
    if(mode==31 && completion_port_reads<4)return 0x810;
    active=0;sticky=0x10;return sticky;
}
static void output_port(unsigned port,unsigned value,unsigned width) {
    port_writes++;assert(cli_seen && !active && !(((uint32_t*)MARKER_ADDRESS)[8]&0x808));
    if(port==0xc000) {
        assert(width==2 && value==0x10 && sticky==0x10);
        sticky=0;return;
    }
    if(config_step==0)assert(port==0xc004 && width==1 && value==0x20);
    if(config_step==1)assert(port==0xc008 && width==1 && value==(starts==0?8u:7u));
    if(config_step==2)assert(port==0xc006 && width==2 && value==(starts==0?(stage==1?0xffu:0xa5u):1u));
    if(config_step==3) {
        assert(port==0xc002 && width==1 && value==0x1a && starts<2);
        starts++;active=1;config_step=0;completion_port_reads=0;idle_port_reads=0;return;
    }
    config_step++;
}
static uint64_t tick(void) {
    tscs++;
    if(tscs==1)return clock_value=1000;
    if(mode==47 && tscs>=4)return 64001000;
    if(mode==48 && completion_port_reads>=2)return 64001000;
    if(mode==13 || mode==29)return 999;
    if(mode==30)return UINT64_C(0x1000003e8);
    if(mode==9 || (mode==10 && starts==1) || (mode==11 && starts==1 && !active) || (mode==12 && starts==2))return 64001000;
    if(mode==14 || mode==15)return clock_value;
    return clock_value+=100;
}
static void trap(int sig,siginfo_t *info,void *opaque) {
    (void)info;ucontext_t *u=opaque;
    assert(sig==SIGSEGV && u->uc_mcontext.gregs[REG_TRAPNO]==13);
    greg_t *g=u->uc_mcontext.gregs;
    unsigned char *p=(void *)(uintptr_t)g[REG_EIP];
    unsigned port=(unsigned)g[REG_EDX]&0xffff;
    if((uint32_t)g[REG_EIP]!=0x1000000) {
        if(p[0]==0xfa) {cli_seen++;g[REG_EIP]++;return;}
        if(p[0]==0x0f && p[1]==0x31) {
            uint64_t t=tick();g[REG_EAX]=(uint32_t)t;g[REG_EDX]=(uint32_t)(t>>32);g[REG_EIP]+=2;return;
        }
        if(p[0]==0x66 && p[1]==0xed) {
            assert(port==0xc000);g[REG_EAX]=(g[REG_EAX]&0xffff0000u)|status();g[REG_EIP]+=2;return;
        }
        if(p[0]==0x66 && p[1]==0xef) {output_port(port,(unsigned)g[REG_EAX]&0xffff,2);g[REG_EIP]+=2;return;}
        if(p[0]==0xee) {output_port(port,(unsigned)g[REG_EAX]&0xff,1);g[REG_EIP]++;return;}
        fprintf(stderr,"unexpected integration fault %p %02x %02x\n",(void*)p,p[0],p[1]);abort();
    }
    assert(*(unsigned char*)0x1000000==0xfa); /* CLI trapped BEFORE execution */
    assert(output_size==176 && (pmode==0 || pmode==12));
    uint32_t *r=(void*)output;
    int regs[]={REG_EDI,REG_ESI,REG_EBP,REG_ESP,REG_EBX,REG_EDX,REG_ECX,REG_EAX};
    for(unsigned i=0;i<8;i++)assert((uint32_t)u->uc_mcontext.gregs[regs[i]]==r[32+i]+(i==3?4:0));
    assert(((uint32_t)u->uc_mcontext.gregs[REG_EFL]&0xed5)==(r[28]&0xed5));
    assert(wc==1 && ww==1 && wf==1 && wcl==1 && witness_size==256);
    assert(!memcmp(witness+160,r+32,32));assert(*(uint32_t*)(witness+192)==r[28]);
    assert(!memcmp(witness+64,(void*)MARKER_ADDRESS,96));
    handoffs++;siglongjmp(done,2);
}
int main(int argc,char **argv) {
    assert(argc==2 && sizeof(void*)==4);
    FILE *f=fopen(argv[1],"rb");assert(f);assert(!fseek(f,0,SEEK_END));image_size=ftell(f);rewind(f);
    image=malloc(image_size);assert(image && fread(image,1,image_size,f)==image_size);fclose(f);
    assert(mmap((void*)0x10000,0xa0000,7,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x10000);
    assert(mmap((void*)0x80400000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x80400000);
    assert(mmap((void*)0x81000000,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x81000000);
    assert(mmap((void*)0x1000000,4096,7,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x1000000);
    void *hooks[]={alloc,physical,virtual_alloc,create,write_file,flush,close_file,reboot};
    struct sigaction sa={0};sa.sa_sigaction=trap;sa.sa_flags=SA_SIGINFO;
    assert(!sigemptyset(&sa.sa_mask));assert(!sigaction(SIGSEGV,&sa,0));
    assert(prctl(PR_SET_TSC,PR_TSC_SIGSEGV,0,0,0)==0);
    unsigned cases=0;
    for(case_id=0;case_id<132;case_id++) {
        fmode=case_id>=74 && case_id<84?45+case_id-74:case_id;
        pmode=case_id>=55?0:case_id>=45?32:case_id;fc=fw=ff=fcl=0;fallback_size=0;memset(fallback,0,sizeof(fallback));
        static const int modes[]={2,4,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,29,30};
        mode=case_id>=85?32+case_id-85:case_id>=74?8:case_id>=55?modes[case_id-55]:0;stage=1;
        new_success=case_id>=85 && (mode<=37 || mode>=49);
        wmode=case_id>=104?case_id-103:0;wc=ww=wf=wcl=0;witness_size=0;memset(witness,0,sizeof(witness));
        if(case_id>=104){pmode=0;fmode=0;mode=0;new_success=0;}
        active=starts=port_writes=port_reads=tscs=cli_seen=config_step=0;
        idle_port_reads=completion_port_reads=0;sticky=0;
        allocs=physcalls=virtuals=creates=writes=flushes=closes=0;output_size=0;handoffs=0;
        memset(output,0,sizeof(output));memcpy((void*)0x10000,image,image_size);
        memset((void*)0x80400000,0x5a,0x100000);
        memset((void*)0x81000000,0xa5,4096);memset((void*)0x1000000,0xa5,4096);
        for(unsigned i=0;i<8;i++)((uint32_t*)0x11000)[i]=(uint32_t)hooks[i];
        if(!sigsetjmp(done,1)) {
            if(pmode==12)__asm__ volatile("std" ::: "cc");
            ((void(*)(void))0x11100)();abort();
        }
        if(case_id>=104) {
            clear_df();
            assert(creates==1 && writes==2 && flushes==2 && closes==1 && wc==1);
            unsigned reason=wmode<=6 || wmode==25 || wmode==26?13:
                wmode<=11 || wmode==27?14:wmode<=15?15:wmode<=17?16:
                wmode==18 || wmode==23 || wmode==28?17:wmode==19 || wmode==21?18:19;
            int success=wmode==24;
            assert(handoffs==success && fc==!success);
            assert(wcl==!(wmode==1 || wmode==2 || wmode==6));
            if(!success) {
                assert(fallback_size==192 && fcl==1);
                const uint32_t *q=(void*)fallback;
                assert(q[4]==reason && q[8]==((wmode==1 || wmode==2 || wmode==6)?0:0x4872));
                assert(q[9]==(reason<16?0:reason==16?1:2));
                assert(q[5]==(wmode==1?0xc0000035u:wmode==2||wmode==8||wmode==13||wmode==17||wmode==26?0x103u:
                    wmode==7||wmode==12||wmode==16||wmode==25?0xc0000185u:reason==18||reason==19?0:q[5]));
                if(wmode==3 || wmode==9 || wmode==14)assert(q[6]==0xc0000185u);
                if(wmode==4 || wmode==10 || wmode==15)assert(q[6]==0xeeeeeeee);
                if(wmode==11)assert(q[7]==255);
                if(wmode==27)assert(q[7]==257);
            }
            save_witness();
            char fn[48];snprintf(fn,sizeof(fn),"newrefusal%03d.bin",case_id);
            FILE *nf=fopen(fn,"wbx");assert(nf);assert(fwrite(fallback,1,fallback_size,nf)==fallback_size);fclose(nf);
            printf("witness case=%d mode=%d handoffs=%d reason=%u calls=%d/%d/%d/%d bytes=%u\n",case_id,wmode,handoffs,success?0:reason,wc,ww,wf,wcl,witness_size);
            cases++;continue;
        }
        save_witness();
        assert(creates==1);
        if(pmode==5 || pmode==21 || pmode==25)assert(writes==0 && closes==0 && output_size==0);
        else assert(closes==1);
        if(output_size>=160) {
            uint32_t *r=(void*)output;
            assert(r[0]==0x33383458 && r[1]==2 && r[2]==160 && r[3]==0x48700101);
            assert(r[5]==(pmode==1?1:pmode==2?2:(pmode==3 || pmode==44)?3:pmode==4?5:pmode>=13&&pmode<=15?7:6));
            assert(r[12]==524862);
            if(pmode==12)assert(r[4]&0x400);
            if(pmode==4)assert(r[13]&0x400);
            if(pmode==3)assert(r[10]==0xc0000017u);
            if(r[5]==6)assert(r[10]==0 && r[11]==4096 && r[14]==0x1000000);
        }
        assert(allocs==(pmode==1 || pmode==4?1:2));
        assert(virtuals==!(pmode==1 || pmode==2 || pmode==4));
        if(pmode==1 || pmode==4)assert(*(unsigned char*)0x80400000==0x5a);
        else if(pmode!=16 && pmode!=33)assert(!memcmp((void*)0x80400000,image+12288,524862));
        unsigned expected=176;
        if(pmode==5 || pmode==10 || (pmode>=21 && pmode<=25))expected=0;
        else if(pmode==6)expected=159;
        else if(pmode==7)expected=175;
        else if(pmode==8 || pmode==11 || (pmode>=26 && pmode<=31))expected=160;
        assert(output_size==expected);
        assert(handoffs==((pmode==0 || pmode==12) && (case_id<55 || new_success)));
        if(output_size==176) {
            uint32_t *r=(void*)output;
            assert(r[40]==0x454e4f44 && r[41]==2 && r[42]==0x48700101 && r[43]==160);
            if(r[5]==6) {
                assert(r[16]==1024 && r[18]==80 && r[19]==74 && r[20]==224);
                assert(r[21]==0x3000000 && r[27]==1 && r[30]==1);
                assert(r[24]==(pmode!=16));
                assert(r[25]==(pmode!=17 && pmode!=19));
                assert(r[26]==(pmode!=18 && pmode!=20));
                assert(r[31]==!(pmode>=16 && pmode<=20));
                assert(r[22]==(0x1000050u^(pmode==20)));
                assert(r[23]==(0x1000050u^(pmode==19)));
                assert(r[32]==0x1000400 && r[33]==0x400000 && r[36]==0x8100004a);
                assert(r[37]==0x1000000 && r[38]==0x1000000-r[17] && r[39]==0x1000050);
            } else {
                for(unsigned i=30;i<40;i++)assert(!r[i]);
            }
            if(r[5]==7)assert(r[29]==(pmode==13?2:pmode==14?1:3));
        }
        for(unsigned j=1024;j<4096;j++) {
            assert(*((unsigned char*)0x81000000+j)==0xa5);
            assert(*((unsigned char*)0x1000000+j)==0xa5);
        }
        printf("case %d actual_x86=1 phase=%u allocs=%d virtuals=%d bytes=%u flushes=%d closed=%d handoffs=%d\n",pmode,output_size>=128?((uint32_t*)output)[5]:0,allocs,virtuals,output_size,flushes,closes,handoffs);
        assert(fc==!((pmode==0 || pmode==12) && (case_id<55 || new_success)));
        if(fc) {
            unsigned expected_f=fmode==45||fmode==47||fmode==50||fmode==54?0:fmode==46?191:192;
            assert(fallback_size==expected_f);
            assert(fcl==!(fmode==45 || fmode==54));
            if(fallback_size==192) {
                const uint32_t *q=(void*)fallback;
                unsigned reason=case_id>=55?12:pmode==5 || (pmode>=21 && pmode<=25)?1:
                    pmode==6 || pmode==10 || (pmode>=26 && pmode<=28)?2:
                    pmode==8 || (pmode>=29 && pmode<=31)?3:
                    pmode==7 || pmode==11 || (pmode>=38 && pmode<=40)?4:
                    pmode==9 || (pmode>=41 && pmode<=43)?5:pmode==32?6:
                    pmode==1 || pmode==2 || pmode==3 || pmode==4 || (pmode>=13 && pmode<=15) || pmode==44?7:
                    pmode>=16 && pmode<=20?8:pmode==33?9:pmode==34||pmode==36?10:11;
                assert(q[0]==0x33383452 && q[1]==2 && q[2]==192 && q[3]==0x48700101);
                assert(q[4]==reason && q[19]==0);
                assert(q[44]==0x454e4f44 && q[45]==2 && q[46]==0x48700101 && q[47]==192);
                assert(q[9]==(reason<6?0:reason==6?1:2));
                if(reason>=6)assert(q[18]==0xeeeeeeee);
                else assert(q[18]==(q[8]?0:0xeeeeeeee));
                if(pmode==32)assert(q[5]==0xc0000185u);
                if(case_id>=55)assert(q[5]==((uint32_t*)frozen_marker)[5] && q[9]==2);
                assert(!memcmp(fallback+80,frozen_marker,96));
                if(reason==2 || reason==3 || reason==4 || reason==5)assert(q[8]==0x4780);
                if(pmode==27 || pmode==30 || pmode==39 || pmode==42)assert(q[6]==0xc0000185u);
                if(pmode==28 || pmode==31 || pmode==40 || pmode==43)assert(q[6]==0xeeeeeeee);
            }
        } else assert(!fw && !ff && !fcl && !fallback_size);
        const uint32_t *marker=case_id==84?(void*)frozen_marker:(void*)MARKER_ADDRESS;
        if(handoffs)assert(marker[5]==1 && marker[6]==2 && marker[7]==3 && marker[22]==1);
        else if(case_id>=55) {
            assert(marker[5]>=3 && marker[5]<=7 && marker[22]==1);
            assert(marker[19]==(unsigned)port_writes && marker_io_at_snapshot==(unsigned)port_writes);
            if(case_id==84)assert(*(uint32_t*)MARKER_ADDRESS==0xa7a7a7a7u);
        }
        else assert(marker[22]==0 && !cli_seen && !port_reads && !port_writes);
        char name[40];snprintf(name,sizeof(name),"case%02d.bin",case_id);
        FILE *capture=fopen(name,"wbx");assert(capture);assert(fwrite(output,1,output_size,capture)==output_size);fclose(capture);
        snprintf(name,sizeof(name),"refusal%02d.bin",case_id);
        FILE *ref=fopen(name,"wbx");assert(ref);assert(fwrite(fallback,1,fallback_size,ref)==fallback_size);fclose(ref);
        printf("fallback case=%d creates=%d writes=%d flushes=%d closes=%d bytes=%u\n",case_id,fc,fw,ff,fcl,fallback_size);
        snprintf(name,sizeof(name),"marker%02d.bin",case_id);
        FILE *mr=fopen(name,"wbx");assert(mr);assert(fwrite(marker,1,96,mr)==96);fclose(mr);
        cases++;
    }
    printf("PASS %u actual-wrapper cases; kernel/file/SMBus/TSC effects modeled; loader CLI trapped before execution\n",cases);
    free(image);return 0;
}

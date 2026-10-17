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

#define API __attribute__((stdcall))
static sigjmp_buf done;
static volatile sig_atomic_t handoffs;
static int mode, allocs, physcalls, virtuals, creates, writes, flushes, closes;
static unsigned char output[256];
static uint32_t output_size;
static unsigned char *image;
static size_t image_size;
static void clear_df(void) { __asm__ volatile("cld" ::: "cc"); }
static uint32_t API alloc(uint32_t size,uint32_t low,uint32_t high,uint32_t align,uint32_t prot) {
    clear_df(); allocs++; assert(prot==4);
    if(allocs==1) {
        assert(size==0x100000 && low==0x200000 && high==0x1ffffff && align==0);
        return mode==1 ? 0 : 0x80400000;
    }
    assert(allocs==2 && size==4096 && low==0x1000000 && high==0x2000000 && align==16);
    return mode==2 ? 0 : 0x81000000;
}
static uint32_t API physical(uint32_t va) {
    clear_df(); physcalls++; assert(va==0x80400000 || va==0x81000000 || va==0x1000000);
    if(physcalls==3) {
        assert(va==0x1000000);
        if(mode==16)*(unsigned char*)0x80400000^=1;
        if(mode==17)*((unsigned char*)0x81000000+500)^=1;
        if(mode==18)*((unsigned char*)0x1000000+500)^=1;
        if(mode==19)*((unsigned char*)0x81000000+74)^=1;
        if(mode==20)*((unsigned char*)0x1000000+74)^=1;
        return 0x3000000;
    }
    uint32_t pa=va&0x7fffffff;
    if(mode==15 && physcalls==2)pa+=4096;
    if(mode==4 && physcalls==1) __asm__ volatile("std" ::: "cc");
    return pa;
}
static uint32_t API virtual_alloc(uint32_t *base,uint32_t zero,uint32_t *size,uint32_t type,uint32_t prot) {
    clear_df(); virtuals++;
    assert(*base==(mode==15?0x1001000:0x1000000) && zero==0 && *size==4096 && type==0x3000 && prot==4);
    if(mode==13)*base+=4096;
    if(mode==14)*size=8192;
    return mode==3 ? 0xc0000017u : mode==44 ? 0x103 : 0;
}
static uint32_t API create(uint32_t *handle,uint32_t access,uint32_t *oa,uint32_t *iosb,
                           void *allocation,uint32_t attrs,uint32_t share,uint32_t disposition,uint32_t options) {
    clear_df(); creates++;
    assert(access==0x40100000 && !allocation && attrs==0x80 && share==0 && disposition==2 && options==0x62);
    assert(oa[0]==0 && oa[2]==0x40);
    uint16_t *name=(void*)oa[1];uint32_t *ptr=(void*)((char*)name+4);
    const char *expected="\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot461a\\report.bin";
    assert(name[0]==strlen(expected) && name[1]==name[0]+1 && strcmp((char*)*ptr,expected)==0);
    if(mode==5)return 0xc0000035u; /* existing report */
    if(mode==21)return 0x103;
    *handle=mode==25?0:0x4610;
    if(mode==23)return 0;
    iosb[0]=mode==22?0xc0000185u:0;iosb[1]=mode==24?1:2;return 0;
}
static uint32_t API write_file(uint32_t handle,uint32_t event,uint32_t apc,uint32_t ctx,
                              uint32_t *iosb,const void *buf,uint32_t bytes,uint32_t offset) {
    clear_df();writes++;
    assert(handle==0x4610 && !event && !apc && !ctx && !offset);
    assert((writes==1 && bytes==160)||(writes==2 && bytes==16));
    if((mode==10 && writes==1)||(mode==11 && writes==2))return 0xc0000185u;
    uint32_t actual=bytes-((mode==6 && writes==1)||(mode==7 && writes==2));
    assert(output_size+actual<=sizeof(output));memcpy(output+output_size,buf,actual);output_size+=actual;
    if((mode==28 && writes==1)||(mode==40 && writes==2))return 0;
    iosb[0]=((mode==27 && writes==1)||(mode==39 && writes==2))?0xc0000185u:0;
    iosb[1]=actual;
    return ((mode==26 && writes==1)||(mode==38 && writes==2))?0x103:0;
}
static uint32_t API flush(uint32_t handle,uint32_t *iosb) {
    clear_df();flushes++;assert(handle==0x4610);
    if((mode==31 && flushes==1)||(mode==43 && flushes==2))return 0;
    iosb[0]=((mode==30 && flushes==1)||(mode==42 && flushes==2))?0xc0000185u:0;
    iosb[1]=0;
    if((mode==29 && flushes==1)||(mode==41 && flushes==2))return 0x103;
    return ((mode==8 && flushes==1)||(mode==9 && flushes==2)) ? 0xc0000185u : 0;
}
static uint32_t API close_file(uint32_t handle) {
    clear_df();closes++;assert(handle==0x4610);
    if(mode==33)*(unsigned char*)0x80400000^=1;
    if(mode==34)*((unsigned char*)0x81000000+500)^=1;
    if(mode==35)*((unsigned char*)0x1000000+500)^=1;
    if(mode==36)*((unsigned char*)0x81000000+74)^=1;
    if(mode==37)*((unsigned char*)0x1000000+74)^=1;
    return mode==32?0xc0000185u:0;
}
static void API reboot(uint32_t type) {clear_df();assert(type==1);siglongjmp(done,1);}

static void trap(int sig,siginfo_t *info,void *opaque) {
    (void)info;ucontext_t *u=opaque;
    assert(sig==SIGSEGV && u->uc_mcontext.gregs[REG_TRAPNO]==13);
    assert((uint32_t)u->uc_mcontext.gregs[REG_EIP]==0x1000000);
    assert(*(unsigned char*)0x1000000==0xfa); /* CLI trapped BEFORE execution */
    assert(output_size==176 && (mode==0 || mode==12));
    uint32_t *r=(void*)output;
    int regs[]={REG_EDI,REG_ESI,REG_EBP,REG_ESP,REG_EBX,REG_EDX,REG_ECX,REG_EAX};
    for(unsigned i=0;i<8;i++)assert((uint32_t)u->uc_mcontext.gregs[regs[i]]==r[32+i]+(i==3?4:0));
    assert(((uint32_t)u->uc_mcontext.gregs[REG_EFL]&0xed5)==(r[28]&0xed5));
    handoffs++;siglongjmp(done,2);
}
int main(int argc,char **argv) {
    assert(argc==2 && sizeof(void*)==4);
    FILE *f=fopen(argv[1],"rb");assert(f);assert(!fseek(f,0,SEEK_END));image_size=ftell(f);rewind(f);
    image=malloc(image_size);assert(image && fread(image,1,image_size,f)==image_size);fclose(f);
    assert(mmap((void*)0x10000,0x60000,7,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x10000);
    assert(mmap((void*)0x80400000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x80400000);
    assert(mmap((void*)0x81000000,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x81000000);
    assert(mmap((void*)0x1000000,4096,7,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x1000000);
    void *hooks[]={alloc,physical,virtual_alloc,create,write_file,flush,close_file,reboot};
    struct sigaction sa={0};sa.sa_sigaction=trap;sa.sa_flags=SA_SIGINFO;
    assert(!sigemptyset(&sa.sa_mask));assert(!sigaction(SIGSEGV,&sa,0));
    unsigned cases=0;
    for(mode=0;mode<45;mode++) {
        allocs=physcalls=virtuals=creates=writes=flushes=closes=0;output_size=0;handoffs=0;
        memset(output,0,sizeof(output));memcpy((void*)0x10000,image,image_size);
        memset((void*)0x80400000,0x5a,0x100000);
        memset((void*)0x81000000,0xa5,4096);memset((void*)0x1000000,0xa5,4096);
        for(unsigned i=0;i<8;i++)((uint32_t*)0x11000)[i]=(uint32_t)hooks[i];
        if(!sigsetjmp(done,1)) {
            if(mode==12)__asm__ volatile("std" ::: "cc");
            ((void(*)(void))0x11100)();abort();
        }
        assert(creates==1);
        if(mode==5 || mode==21 || mode==25)assert(writes==0 && closes==0 && output_size==0);
        else assert(closes==1);
        if(output_size>=160) {
            uint32_t *r=(void*)output;
            assert(r[0]==0x31363458 && r[1]==2 && r[2]==160 && r[3]==0x46100101);
            assert(r[5]==(mode==1?1:mode==2?2:(mode==3 || mode==44)?3:mode==4?5:mode>=13&&mode<=15?7:6));
            assert(r[12]==288316);
            if(mode==12)assert(r[4]&0x400);
            if(mode==4)assert(r[13]&0x400);
            if(mode==3)assert(r[10]==0xc0000017u);
            if(r[5]==6)assert(r[10]==0 && r[11]==4096 && r[14]==0x1000000);
        }
        assert(allocs==(mode==1 || mode==4?1:2));
        assert(virtuals==!(mode==1 || mode==2 || mode==4));
        if(mode==1 || mode==4)assert(*(unsigned char*)0x80400000==0x5a);
        else if(mode!=16 && mode!=33)assert(!memcmp((void*)0x80400000,image+12288,288316));
        unsigned expected=176;
        if(mode==5 || mode==10 || (mode>=21 && mode<=25))expected=0;
        else if(mode==6)expected=159;
        else if(mode==7)expected=175;
        else if(mode==8 || mode==11 || (mode>=26 && mode<=31))expected=160;
        assert(output_size==expected);
        assert(handoffs==(mode==0 || mode==12));
        if(output_size==176) {
            uint32_t *r=(void*)output;
            assert(r[40]==0x454e4f44 && r[41]==2 && r[42]==0x46100101 && r[43]==160);
            if(r[5]==6) {
                assert(r[16]==1024 && r[18]==80 && r[19]==74 && r[20]==224);
                assert(r[21]==0x3000000 && r[27]==1 && r[30]==1);
                assert(r[24]==(mode!=16));
                assert(r[25]==(mode!=17 && mode!=19));
                assert(r[26]==(mode!=18 && mode!=20));
                assert(r[31]==!(mode>=16 && mode<=20));
                assert(r[22]==(0x1000050u^(mode==20)));
                assert(r[23]==(0x1000050u^(mode==19)));
                assert(r[32]==0x1000400 && r[33]==0x400000 && r[36]==0x8100004a);
                assert(r[37]==0x1000000 && r[38]==0x1000000-r[17] && r[39]==0x1000050);
            } else {
                for(unsigned i=30;i<40;i++)assert(!r[i]);
            }
            if(r[5]==7)assert(r[29]==(mode==13?2:mode==14?1:3));
        }
        for(unsigned j=1024;j<4096;j++) {
            assert(*((unsigned char*)0x81000000+j)==0xa5);
            assert(*((unsigned char*)0x1000000+j)==0xa5);
        }
        printf("case %d actual_x86=1 phase=%u allocs=%d virtuals=%d bytes=%u flushes=%d closed=%d handoffs=%d\n",mode,output_size>=128?((uint32_t*)output)[5]:0,allocs,virtuals,output_size,flushes,closes,handoffs);
        char name[40];snprintf(name,sizeof(name),"case%02d.bin",mode);
        FILE *capture=fopen(name,"wbx");assert(capture);assert(fwrite(output,1,output_size,capture)==output_size);fclose(capture);
        cases++;
    }
    printf("PASS %u actual-wrapper cases; kernel/file effects modeled; CLI trapped before privileged execution\n",cases);
    free(image);return 0;
}

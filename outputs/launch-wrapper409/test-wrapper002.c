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

#define API __attribute__((stdcall))
static jmp_buf done;
static int mode, allocs, physcalls, virtuals, creates, writes, flushes, closes;
static unsigned char output[128];
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
    clear_df(); physcalls++; assert(va==0x80400000 || va==0x81000000);
    uint32_t pa=va&0x7fffffff;
    if(mode==4 && physcalls==1) __asm__ volatile("std" ::: "cc");
    return pa;
}
static uint32_t API virtual_alloc(uint32_t *base,uint32_t zero,uint32_t *size,uint32_t type,uint32_t prot) {
    clear_df(); virtuals++;
    assert(*base==0x1000000 && zero==0 && *size==4096 && type==0x3000 && prot==4);
    return mode==3 ? 0xc0000017u : 0;
}
static uint32_t API create(uint32_t *handle,uint32_t access,uint32_t *oa,uint32_t *iosb,
                           void *allocation,uint32_t attrs,uint32_t share,uint32_t disposition,uint32_t options) {
    clear_df(); creates++;
    assert(access==0x40100000 && !allocation && attrs==0x80 && share==0 && disposition==2 && options==0x62);
    assert(oa[0]==0 && oa[2]==0x40);
    uint16_t *name=(void*)oa[1];uint32_t *ptr=(void*)((char*)name+4);
    const char *expected="\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot409a\\report.bin";
    assert(name[0]==strlen(expected) && name[1]==name[0]+1 && strcmp((char*)*ptr,expected)==0);
    if(mode==5)return 0xc0000035u; /* existing report */
    *handle=0x4090;iosb[0]=0;iosb[1]=2;return 0;
}
static uint32_t API write_file(uint32_t handle,uint32_t event,uint32_t apc,uint32_t ctx,
                              uint32_t *iosb,const void *buf,uint32_t bytes,uint32_t offset) {
    clear_df();writes++;
    assert(handle==0x4090 && !event && !apc && !ctx && !offset);
    assert((writes==1 && bytes==64)||(writes==2 && bytes==16));
    if((mode==10 && writes==1)||(mode==11 && writes==2))return 0xc0000185u;
    uint32_t actual=bytes-((mode==6 && writes==1)||(mode==7 && writes==2));
    assert(output_size+actual<=sizeof(output));memcpy(output+output_size,buf,actual);output_size+=actual;
    iosb[0]=0;iosb[1]=actual;return 0;
}
static uint32_t API flush(uint32_t handle,uint32_t *iosb) {
    clear_df();flushes++;assert(handle==0x4090);iosb[0]=0;iosb[1]=0;
    return ((mode==8 && flushes==1)||(mode==9 && flushes==2)) ? 0xc0000185u : 0;
}
static uint32_t API close_file(uint32_t handle) {clear_df();closes++;assert(handle==0x4090);return 0;}
static void API reboot(uint32_t type) {clear_df();assert(type==1);longjmp(done,1);}

int main(int argc,char **argv) {
    assert(argc==2 && sizeof(void*)==4);
    FILE *f=fopen(argv[1],"rb");assert(f);assert(!fseek(f,0,SEEK_END));image_size=ftell(f);rewind(f);
    image=malloc(image_size);assert(image && fread(image,1,image_size,f)==image_size);fclose(f);
    assert(mmap((void*)0x10000,0x60000,7,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x10000);
    assert(mmap((void*)0x80400000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x80400000);
    assert(mmap((void*)0x81000000,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x81000000);
    void *hooks[]={alloc,physical,virtual_alloc,create,write_file,flush,close_file,reboot};
    unsigned cases=0;
    for(mode=0;mode<13;mode++) {
        allocs=physcalls=virtuals=creates=writes=flushes=closes=0;output_size=0;
        memset(output,0,sizeof(output));memcpy((void*)0x10000,image,image_size);
        memset((void*)0x80400000,0x5a,0x100000);
        for(unsigned i=0;i<8;i++)((uint32_t*)0x11000)[i]=(uint32_t)hooks[i];
        if(!setjmp(done)) {
            if(mode==12)__asm__ volatile("std" ::: "cc");
            ((void(*)(void))0x11100)();abort();
        }
        assert(creates==1);
        if(mode==5)assert(writes==0 && closes==0 && output_size==0);
        else assert(closes==1);
        if(output_size>=64) {
            uint32_t *r=(void*)output;
            assert(r[0]==0x39303458 && r[1]==1 && r[2]==64 && r[3]==0x40900101);
            assert(r[5]==(mode==1?1:mode==2?2:mode==3?3:mode==4?5:4));
            assert(r[12]==288316);
            if(mode==12)assert(r[4]&0x400);
            if(mode==4)assert(r[13]&0x400);
            if(mode==3)assert(r[10]==0xc0000017u);
            if(r[5]==4)assert(r[10]==0 && r[11]==4096 && r[14]==0x1000000);
        }
        assert(allocs==(mode==1 || mode==4?1:2));
        assert(virtuals==!(mode==1 || mode==2 || mode==4));
        if(mode==1 || mode==4)assert(*(unsigned char*)0x80400000==0x5a);
        else assert(!memcmp((void*)0x80400000,image+12288,288316));
        unsigned expected=mode==5||mode==10?0:mode==6?63:mode==7?79:mode==8||mode==11?64:80;
        assert(output_size==expected);
        if(output_size==80)assert(!memcmp(output+64,"DONE\1\0\0\0\1\1\x90\x40\x40\0\0\0",16));
        printf("case %d actual_x86=1 phase=%u allocs=%d virtuals=%d bytes=%u flushes=%d closed=%d\n",mode,output_size>=64?((uint32_t*)output)[5]:0,allocs,virtuals,output_size,flushes,closes);
        char name[40];snprintf(name,sizeof(name),"case%02d.bin",mode);
        FILE *capture=fopen(name,"wbx");assert(capture);assert(fwrite(output,1,output_size,capture)==output_size);fclose(capture);
        cases++;
    }
    printf("PASS %u actual-wrapper cases; kernel/file effects modeled\n",cases);
    free(image);return 0;
}

/* SPDX-License-Identifier: MIT
 * Owned, standalone stock-kernel video API comparison. No Windows changes.
 * Fresh E:\Applications\XWNField430 output only; never overwrite a result.
 */
#include <hal/video.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdint.h>
#include "pattern.h"
static HANDLE log_file=INVALID_HANDLE_VALUE;
static uint32_t row[FW];
static uint32_t record[32];
static unsigned failure;
static int write_exact(HANDLE h,const void *p,DWORD n) {
    DWORD done=0;return WriteFile(h,p,n,&done,NULL) && done==n;
}
static int emit(void) {
    return write_exact(log_file,record,sizeof(record)) && FlushFileBuffers(log_file);
}
static int available(unsigned w,unsigned h) {
    VIDEO_MODE v;void *p=0;
    while(XVideoListModes(&v,32,60,&p))
        if((unsigned)v.width==w && (unsigned)v.height==h) return 1;
    return 0;
}
static void paint(uint32_t *fb,unsigned w,unsigned h,unsigned phase,unsigned x0,unsigned y0,unsigned mode) {
    for(unsigned y=0;y<h;y++) for(unsigned x=0;x<w;x++) {
        unsigned color=0x202020;
        if(y<16) color=mode==0?0x2040ff:0xff8020;
        if(x>=x0 && x<x0+FW && y>=y0 && y<y0+FH)
            color=field_pixel(x-x0,y-y0,phase);
        fb[y*w+x]=color;
    }
    XVideoFlushFB();
}
static int capture(volatile uint32_t *fb,unsigned w,unsigned phase,unsigned x0,unsigned y0,unsigned index) {
    char path[]="E:\\Applications\\XWNField430\\capture-0.bgrx";
    path[sizeof(path)-7]=(char)('0'+index);
    HANDLE f=CreateFileA(path,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(f==INVALID_HANDLE_VALUE) return 5;
    unsigned bad=0;int ok=1;
    for(unsigned y=0;y<FH;y++) {
        for(unsigned x=0;x<FW;x++) {
            row[x]=fb[(y0+y)*w+x0+x];
            if((row[x]&0xffffff)!=field_pixel(x,y,phase)) bad++;
        }
        if(!write_exact(f,row,sizeof(row))) {ok=0;break;}
    }
    if(!FlushFileBuffers(f)) ok=0;
    if(!CloseHandle(f)) ok=0;
    record[10]=bad;
    return !ok?6:bad?7:0;
}
static int show(unsigned w,unsigned h,unsigned mode) {
    if(!XVideoSetMode(w,h,32,60)) return 1;
    VIDEO_MODE v=XVideoGetMode();uint32_t *fb=(uint32_t*)XVideoGetFB();
    if(!fb || v.width!=(int)w || v.height!=(int)h || v.bpp!=32 || v.refresh!=60) return 2;
    unsigned allocation=MmQueryAllocationSize(fb);
    if(allocation<w*h*4u) return 3;
    record[2]=mode;record[4]=w;record[5]=h;record[6]=(uint32_t)fb;
    record[7]=MmGetPhysicalAddress(fb);record[8]=allocation;
    record[9]=VIDEOREG(0x600800);
    for(unsigned i=0;i<16;i++) record[16+i]=VIDEOREG(0x680800+i*4);
    for(unsigned phase=0;phase<4;phase++) {
        unsigned x0=32,y0=32,frames=0;DWORD begin=GetTickCount();
        paint(fb,w,h,phase,x0,y0,mode);
        do {
            if(phase==2) {
                x0=32+frames%80;y0=32+(frames*3)%64;
                paint(fb,w,h,phase,x0,y0,mode);
            }
            frames++;Sleep(40);
        } while((DWORD)(GetTickCount()-begin)<10000 && frames<250);
        record[3]=phase;record[11]=frames;record[12]=GetTickCount()-begin;
        record[14]=x0;record[15]=y0;
        unsigned e=capture(fb,w,phase,x0,y0,mode*4+phase);
        if(e) return e;
        if(!emit()) return 8;
    }
    return 0;
}
int main(void) {
    log_file=CreateFileA("E:\\Applications\\XWNField430\\result.bin",GENERIC_WRITE,0,NULL,
                         CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(log_file==INVALID_HANDLE_VALUE) goto end;
    record[0]=0x430c0de;record[1]=1;record[3]=99;record[13]=XVideoGetEncoderSettings();
    if(!emit()) {failure=9;goto close;}
    if((record[13]&255)!=AV_PACK_HDTV || !available(1280,720) || !available(1920,1080)) {
        failure=10;goto close;
    }
    failure=show(1280,720,0);
    if(!failure) failure=show(1920,1080,1);
close:
    record[2]=failure;record[3]=100;
    (void)emit();CloseHandle(log_file);
end:
    Sleep(1000);HalReturnToFirmware(HalRebootRoutine);return 0;
}

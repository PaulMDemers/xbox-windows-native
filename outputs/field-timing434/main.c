/* SPDX-License-Identifier: MIT
 * Read-only raster observation. Mode selection uses the stock API; no timing,
 * encoder, interrupt-enable, framebuffer-address or GPU command writes here.
 * CRTC selector is saved/restored with interrupts masked only for 23 reads.
 */
#include <hal/video.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdint.h>
#include "pattern.h"
#define CAPACITY 32768u
static uint32_t before[128],after[128],samples[CAPACITY][6];
static const unsigned char cr[]={0,1,2,3,4,5,6,7,9,0x10,0x11,0x12,0x13,0x15,0x16,0x17,0x18,0x19,0x1a,0x25,0x28,0x2d,0x39};
static const uint32_t mm[]={0x600800,0x600804,0x680508,0x680600,
 0x680800,0x680804,0x680808,0x68080c,0x680810,0x680814,0x680818,
 0x680820,0x680824,0x680828,0x68082c,0x680830,0x680834,0x680838,
 0x680848,0x680880,0x680884,0x680888,0x68088c,0x680898,0x68089c,
 0x6808c0,0x6808c4,0x68084c,0x680630};
static void split(uint32_t *p,ULONGLONG v){p[0]=(uint32_t)v;p[1]=(uint32_t)(v>>32);}
static void registers(uint32_t *r){
 volatile unsigned char *index=(volatile unsigned char*)(VIDEO_BASE+0x6013d4);
 volatile unsigned char *data=(volatile unsigned char*)(VIDEO_BASE+0x6013d5);
 unsigned flags,restored;
 __asm__ __volatile__("pushfl; popl %0; cli":"=r"(flags)::"memory");
 unsigned saved=*index;r[16]=saved;
 for(unsigned i=0;i<sizeof(cr);i++){*index=cr[i];r[32+i]=*data;}
 *index=(unsigned char)saved;r[17]=*index;
 __asm__ __volatile__("pushl %0; popfl"::"r"(flags):"memory","cc");
 __asm__ __volatile__("pushfl; popl %0":"=r"(restored)::"memory");
 r[18]=flags;r[19]=restored;r[20]=sizeof(cr);r[21]=sizeof(mm)/sizeof(mm[0]);
 for(unsigned i=0;i<r[21];i++)r[64+i]=VIDEOREG(mm[i]);
}
static uint32_t pixel(unsigned x,unsigned y,unsigned stage){
 if(y<16)return stage==1?0xff8020:0x2040ff;
 if(x>=32 && x<32+FW && y>=32 && y<32+FH)return field_pixel(x-32,y-32,0);
 return 0x202020;
}
static int write_exact(HANDLE h,const void *p,DWORD n){DWORD done=0;return WriteFile(h,p,n,&done,NULL)&&done==n;}
static int save(unsigned stage,unsigned count){
 char name[]="D:\\raster-0.dat";name[10]=(char)('0'+stage);
 HANDLE h=CreateFileA(name,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(h==INVALID_HANDLE_VALUE)return 0;
 int ok=write_exact(h,before,sizeof(before))&&write_exact(h,after,sizeof(after))&&write_exact(h,samples,count*sizeof(samples[0]));
 IO_STATUS_BLOCK io={0};NTSTATUS s=NtFlushBuffersFile(h,&io);
 if(s!=0 || io.Status!=0)ok=0;
 if(!CloseHandle(h))ok=0;
 return ok;
}
static unsigned run(unsigned stage){
 unsigned w=stage==1?1920:1280,h=stage==1?1080:720;
 if(!XVideoSetMode(w,h,32,60))return 1;
 VIDEO_MODE v=XVideoGetMode();volatile uint32_t *fb=(volatile uint32_t*)XVideoGetFB();
 if(!fb || v.width!=(int)w || v.height!=(int)h || v.bpp!=32 || v.refresh!=60)return 2;
 unsigned allocation=MmQueryAllocationSize((void*)fb),physical=MmGetPhysicalAddress((void*)fb);
 if(allocation<w*h*4u || physical>=0x4000000u || allocation>0x4000000u-physical)return 3;
 for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++)fb[y*w+x]=pixel(x,y,stage);
 XVideoFlushFB();Sleep(100);
 for(unsigned i=0;i<128;i++)before[i]=after[i]=0;
 before[0]=0x434c0de;before[1]=1;before[2]=stage;before[3]=w;before[4]=h;
 before[5]=w*4;before[6]=physical;before[7]=VIDEOREG(0x600800);before[8]=allocation;
 ULONGLONG freq=KeQueryPerformanceFrequency();split(before+9,freq);
 before[13]=v.refresh;before[14]=v.bpp;before[15]=XVideoGetEncoderSettings();
 before[26]=XboxKrnlVersion.Build;before[27]=XboxKrnlVersion.Qfe;
 for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++)if(fb[y*w+x]!=pixel(x,y,stage))before[28]++;
 registers(before);
 unsigned error=0,count=0;
 if(freq<1000 || freq>1000000000ull || before[6]!=before[7] || before[28] ||
    before[16]!=before[17] || ((before[18]^before[19])&0x200))error=4;
 ULONGLONG begin=KeQueryPerformanceCounter(),end=begin;
 DWORD tick=GetTickCount();
 if(!error){
  while(count<CAPACITY && end>=begin && end-begin<freq/5 && (DWORD)(GetTickCount()-tick)<1000){
   ULONGLONG a=KeQueryPerformanceCounter();uint32_t raw=VIDEOREG(0x600808);
   ULONGLONG b=KeQueryPerformanceCounter();
   split(samples[count],a);samples[count][2]=raw;split(samples[count]+3,b);samples[count][5]=count;
   count++;KeStallExecutionProcessor(10);end=KeQueryPerformanceCounter();
  }
  if(end<begin || end-begin<freq/5 || count==CAPACITY || count<64 || (DWORD)(GetTickCount()-tick)>=1000)error=5;
 }
 for(unsigned i=0;i<128;i++)after[i]=before[i];
 after[11]=count;after[12]=error;split(after+22,begin);split(after+24,end);
 after[30]=(DWORD)(GetTickCount()-tick);
 for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++)if(fb[y*w+x]!=pixel(x,y,stage))after[29]++;
 registers(after);
 if(after[29] || after[16]!=after[17] || ((after[18]^after[19])&0x200))after[12]=6;
 if(!save(stage,count))return 7;
 return after[12];
}
int main(void){
 HANDLE h=CreateFileA("D:\\result.dat",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(h==INVALID_HANDLE_VALUE)goto end;
 uint32_t r[8]={0x434c0de,1,99,0,0,0,0,0};
 if(!write_exact(h,r,sizeof(r)))goto close;
 if((XVideoGetEncoderSettings()&255)!=AV_PACK_HDTV){r[3]=10;goto terminal;}
 for(unsigned stage=0;stage<3;stage++){r[3]=run(stage);if(r[3])break;r[4]++;}
terminal:
 r[2]=100;(void)write_exact(h,r,sizeof(r));
close:
 {IO_STATUS_BLOCK io={0};(void)NtFlushBuffersFile(h,&io);(void)CloseHandle(h);}
end:
 Sleep(1000);HalReturnToFirmware(HalRebootRoutine);return 0;
}

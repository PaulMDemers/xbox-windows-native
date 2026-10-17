/* SPDX-License-Identifier: MIT */
#include <hal/video.h>
#include <pbkit/pbkit.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdint.h>
#include "pattern.h"
#define MAGIC 0x435c0deu
static HANDLE journal=INVALID_HANDLE_VALUE;
static volatile uint32_t *fb;
static unsigned base,allocation,freepages,completed;
static const unsigned char cr[]={0,1,2,3,4,5,6,7,9,0x10,0x11,0x12,0x13,0x15,0x16,0x17,0x18,0x19,0x1a,0x25,0x28,0x2d,0x39};
static const uint32_t mm[]={0x600800,0x600804,0x680508,0x680600,
 0x680800,0x680804,0x680808,0x68080c,0x680810,0x680814,0x680818,
 0x680820,0x680824,0x680828,0x68082c,0x680830,0x680834,0x680838,
 0x680848,0x680880,0x680884,0x680888,0x68088c,0x680898,0x68089c,
 0x6808c0,0x6808c4,0x68084c,0x680630};
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

static int write_exact(HANDLE f,const void *p,DWORD n){DWORD done=0;return WriteFile(f,p,n,&done,NULL)&&done==n;}
static int flush(HANDLE f){IO_STATUS_BLOCK io={0};return NtFlushBuffersFile(f,&io)==0&&io.Status==0;}
static int record(unsigned event,unsigned error,int init){
 uint32_t r[16]={MAGIC,1,event,error,completed,(uint32_t)init,freepages,
  (uint32_t)fb,base,allocation,VIDEOREG(0x600800),VIDEOREG(0x600804),GetTickCount(),0,0,0};
 return write_exact(journal,r,sizeof(r))&&flush(journal);
}
static unsigned pixel(unsigned x,unsigned y,unsigned phase){
 if(y<16)return phase<2?0xff8020:0x00ffff;
 if(x>=32&&x<32+FW&&y>=32&&y<32+FH)return field_pixel(x-32,y-32,phase&1);
 return 0x202020;
}
static unsigned phase(unsigned n){
 uint32_t r[128]={0};VIDEO_MODE mode=XVideoGetMode();
 if(XVideoGetFB()!=(void*)fb||MmGetPhysicalAddress((void*)fb)!=base||
    MmQueryAllocationSize((void*)fb)!=allocation||mode.width!=1920||mode.height!=1080||mode.bpp!=32||mode.refresh!=60)return 20;
 for(unsigned y=0;y<1080;y++)for(unsigned x=0;x<1920;x++)fb[y*1920+x]=pixel(x,y,n);
 XVideoFlushFB();Sleep(100);
 r[0]=MAGIC;r[1]=1;r[2]=n;r[3]=1920;r[4]=1080;r[5]=7680;
 r[6]=base;r[7]=VIDEOREG(0x600800);r[8]=allocation;r[9]=(uint32_t)fb;r[10]=freepages;
 r[13]=mode.refresh;r[14]=mode.bpp;r[15]=XVideoGetEncoderSettings();r[22]=GetTickCount();r[23]=n>=2;
 if(n>=2){r[24]=pb_back_buffer_width();r[25]=pb_back_buffer_height();r[26]=pb_back_buffer_pitch();r[27]=MmGetPhysicalAddress(pb_back_buffer());}
 for(unsigned y=0;y<1080;y++)for(unsigned x=0;x<1920;x++)if(fb[y*1920+x]!=pixel(x,y,n))r[28]++;
 registers(r);r[30]=VIDEOREG(0x600808);
 if(r[7]!=base||r[28]||r[16]!=r[17]||((r[18]^r[19])&0x200))r[11]=21;
 char name[]="D:\\phase-0.dat";name[9]=(char)('0'+n);
 HANDLE f=CreateFileA(name,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(f==INVALID_HANDLE_VALUE)return 22;
 int ok=write_exact(f,r,sizeof(r));
 for(unsigned y=0;y<FH&&ok;y++)ok=write_exact(f,(const void*)(fb+(y+32)*1920+32),FW*4);
 if(!flush(f))ok=0;
 if(!CloseHandle(f))ok=0;
 if(!ok)return 23;
 if(r[11])return r[11];
 completed++;
 if(!record(10+n,0,n>=2))return 24;
 Sleep(10000);
 return 0;
}
int main(void){
 unsigned error=0;int init=0;
 journal=CreateFileA("D:\\result.dat",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(journal==INVALID_HANDLE_VALUE)goto end;
 if(!record(99,0,0)){error=1;goto terminal;}
 if((XVideoGetEncoderSettings()&255)!=AV_PACK_HDTV){error=2;goto terminal;}
 if(!XVideoSetMode(1920,1080,32,60)){error=3;goto terminal;}
 fb=(volatile uint32_t*)XVideoGetFB();if(!fb){error=4;goto terminal;}
 base=MmGetPhysicalAddress((void*)fb);allocation=MmQueryAllocationSize((void*)fb);
 if(allocation<8294400||base>=0x4000000||allocation>0x4000000-base){error=5;goto terminal;}
 MM_STATISTICS stats={0};stats.Length=sizeof(stats);
 if(MmQueryStatistics(&stats)!=0){error=6;goto terminal;}freepages=stats.AvailablePages;
 error=phase(0);if(error)goto terminal;
 error=phase(1);if(error)goto terminal;
 if(MmQueryStatistics(&stats)!=0){error=6;goto terminal;}freepages=stats.AvailablePages;
 if(freepages<48u*1024u*1024u/4096u){error=7;goto terminal;}
 if(!record(20,0,0)){error=8;goto terminal;}
 init=pb_init();
 if(!record(21,init!=0,init)){error=9;goto terminal;}
 if(init!=0){error=10;goto terminal;}
 DWORD start=GetTickCount();
 while(pb_busy()&&(DWORD)(GetTickCount()-start)<10000)Sleep(1);
 if(pb_busy()){error=11;goto terminal;}
 pb_show_debug_screen();Sleep(100);
 error=phase(2);if(error)goto terminal;
 error=phase(3);
terminal:
 (void)record(100,error,init);(void)CloseHandle(journal);
end:
 Sleep(1000);HalReturnToFirmware(HalRebootRoutine);return 0;
}

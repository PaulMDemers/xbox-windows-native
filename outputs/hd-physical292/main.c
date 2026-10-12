/* SPDX-License-Identifier: MIT
 * Standalone kernel mode API diagnostic. Separate logged physical validation, after emulator admission.
 * No EEPROM writes, PBKit/firmware channel commands or Windows-driver changes.
 */
#include <hal/video.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>
typedef struct {
 uint32_t magic,version,bytes,phase,error,stage,settings,changes;
 uint32_t width,height,bpp,refresh,fb,physical,allocation,scanout;
 uint32_t hvalid,vvalid,total_pages,mismatches;
 uint32_t fp[16],crc,log_ok;
} Record;
volatile Record record292;
__attribute__((noinline)) void checkpoint292(unsigned phase,volatile Record *r) {
 __asm__ __volatile__("" ::: "memory");r->phase=phase;__asm__ __volatile__("" ::: "memory");
}
static HANDLE logfile=INVALID_HANDLE_VALUE;
static unsigned log_ok;
static void report(const char *format,...) {
 char text[512];DWORD written=0;va_list args;va_start(args,format);
 int n=vsnprintf(text,sizeof(text),format,args);va_end(args);
 if(n<0 || n>=(int)sizeof(text)) {log_ok=0;return;}
 if(logfile!=INVALID_HANDLE_VALUE) {
  IO_STATUS_BLOCK io;
  if(!WriteFile(logfile,text,(DWORD)n,&written,NULL) || written!=(DWORD)n ||
     (LONG)NtFlushBuffersFile(logfile,&io)<0) log_ok=0;
 }
 record292.log_ok=log_ok;
}
static uint32_t framebuffer_crc(volatile unsigned char *data,unsigned bytes) {
 uint32_t table[256];
 for(unsigned i=0;i<256;i++) {uint32_t c=i;for(unsigned b=0;b<8;b++) c=(c>>1)^((c&1)?0xedb88320u:0);table[i]=c;}
 uint32_t c=0xffffffffu;
 for(unsigned i=0;i<bytes;i++) c=table[(c^data[i])&255]^(c>>8);
 return c^0xffffffffu;
}
static uint32_t pixel(unsigned x,unsigned y,unsigned w,unsigned h) {
 if(x==0 || y==0 || x+1==w || y+1==h) return 0xffffffff;
 return 0xff000000u | ((x&255u)<<16) | ((y&255u)<<8) | ((x^y)&255u);
}
static int available(unsigned w,unsigned h) {
 VIDEO_MODE v;void *p=0;
 while(XVideoListModes(&v,32,60,&p)) if((unsigned)v.width==w && (unsigned)v.height==h) return 1;
 return 0;
}
static int show(unsigned w,unsigned h,unsigned stage) {
 report("SET stage=%u width=%u height=%u tick=%lu\r\n",stage,w,h,(unsigned long)GetTickCount());
 if(!XVideoSetMode(w,h,32,60)) return 1;
 record292.changes++;
 VIDEO_MODE v=XVideoGetMode();uint32_t *fb=(uint32_t*)XVideoGetFB();
 if(!fb || v.width!=(int)w || v.height!=(int)h || v.bpp!=32 || v.refresh!=60) return 2;
 unsigned n=w*h,allocation=MmQueryAllocationSize(fb);
 if(allocation<n*4u) return 3;
 for(unsigned y=0;y<h;y++) for(unsigned x=0;x<w;x++) fb[y*w+x]=pixel(x,y,w,h);
 XVideoFlushFB();
 unsigned bad=0;
 for(unsigned y=0;y<h;y++) for(unsigned x=0;x<w;x++) if(fb[y*w+x]!=pixel(x,y,w,h)) bad++;
 record292.stage=stage;record292.width=w;record292.height=h;record292.bpp=v.bpp;record292.refresh=v.refresh;
 record292.fb=(uint32_t)fb;record292.physical=MmGetPhysicalAddress(fb);record292.allocation=allocation;
 record292.scanout=VIDEOREG(0x600800);record292.hvalid=VIDEOREG(0x680838);record292.vvalid=VIDEOREG(0x680818);
 record292.mismatches=bad;
 for(unsigned i=0;i<16;i++) record292.fp[i]=VIDEOREG(0x680800+i*4);
 record292.crc=framebuffer_crc((volatile unsigned char*)fb,n*4);
 report("MODE stage=%u width=%u height=%u bytes=%u allocation=%u physical=%08lx scanout=%08lx hvalid=%lu vvalid=%lu mismatches=%u crc=%08lx tick=%lu\r\n",
  stage,w,h,n*4,allocation,(unsigned long)record292.physical,(unsigned long)record292.scanout,
  (unsigned long)record292.hvalid,(unsigned long)record292.vvalid,bad,(unsigned long)record292.crc,(unsigned long)GetTickCount());
 for(unsigned i=0;i<16;i++) report("FP stage=%u index=%u value=%08lx\r\n",stage,i,(unsigned long)record292.fp[i]);
 return bad?4:0;
}
int main(void) {
 logfile=CreateFileA("D:\\hd292.txt",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 log_ok=logfile!=INVALID_HANDLE_VALUE;record292.log_ok=log_ok;
 report("XWN_HD292 version=1 kernel=%u.%u.%u.%u\r\n",XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe);
 MM_STATISTICS m={0};m.Length=sizeof(m);
 record292.magic=0x292c0de;record292.version=1;record292.bytes=sizeof(Record);
 record292.settings=XVideoGetEncoderSettings();
 report("SETTINGS value=%08lx\r\n",(unsigned long)record292.settings);
 if(MmQueryStatistics(&m)!=0) {record292.error=10;goto end;}
 record292.total_pages=m.TotalPhysicalPages;
 /* Refuse missing cable/capability; never force AV-pack detection. */
 if((record292.settings&255)!=AV_PACK_HDTV || (record292.settings&0xe0000)!=0xe0000 ||
    !available(1280,720) || !available(1920,1080) || !available(640,480)) {record292.error=11;goto end;}
 record292.error=show(1280,720,1);if(record292.error) goto restore;
 checkpoint292(11,&record292);Sleep(10000);
 record292.error=show(1920,1080,2);if(record292.error) goto restore;
 checkpoint292(22,&record292);Sleep(25000);
restore: {
 unsigned earlier=record292.error;unsigned fallback=show(640,480,3);
 record292.error=earlier?earlier:fallback;
 if(!record292.error) {checkpoint292(33,&record292);Sleep(5000);}
}
end:
 report("COMPLETE error=%lu log_ok=%u mode_changes=%lu\r\n",(unsigned long)record292.error,log_ok,(unsigned long)record292.changes);
 if(logfile!=INVALID_HANDLE_VALUE && !CloseHandle(logfile)) log_ok=0;
 record292.log_ok=log_ok;
 checkpoint292(record292.error?255:44,&record292);
 Sleep(10000);HalReturnToFirmware(HalRebootRoutine);return 0;
}

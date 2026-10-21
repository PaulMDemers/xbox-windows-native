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
volatile Record record631;
__attribute__((noinline)) void checkpoint631(unsigned phase,volatile Record *r) {
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
 record631.log_ok=log_ok;
}

/* Only documented timing storage; never status/interrupt-clear registers. */
static const unsigned char cr_indices[]={0,1,2,3,4,5,6,7,9,0x10,0x11,0x12,0x13,0x15,0x16,0x17,0x18,0x19,0x1a,0x25,0x28,0x2d,0x39};
static const uint32_t mm_offsets[]={0x600804,0x680508,0x680600};
typedef struct {
 uint32_t magic,stage,index_before,index_after,flags_before,flags_after;
 uint32_t cr[23],mm[3];
} Timing;
volatile Timing timing631;
static void timing_capture(unsigned stage) {
 volatile unsigned char *index=(volatile unsigned char*)(VIDEO_BASE+0x6013d4);
 volatile unsigned char *data=(volatile unsigned char*)(VIDEO_BASE+0x6013d5);
 unsigned flags,after;
 __asm__ __volatile__("pushfl; popl %0; cli":"=r"(flags)::"memory");
 unsigned saved=*index;
 timing631.magic=0x63171a;timing631.stage=stage;timing631.index_before=saved;
 for(unsigned i=0;i<23;i++){*index=cr_indices[i];timing631.cr[i]=*data;}
 for(unsigned i=0;i<3;i++)timing631.mm[i]=VIDEOREG(mm_offsets[i]);
 *index=(unsigned char)saved;timing631.index_after=*index;
 __asm__ __volatile__("pushl %0; popfl"::"r"(flags):"memory","cc");
 __asm__ __volatile__("pushfl; popl %0":"=r"(after)::"memory");
 timing631.flags_before=flags;timing631.flags_after=after;
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
 record631.changes++;
 VIDEO_MODE v=XVideoGetMode();uint32_t *fb=(uint32_t*)XVideoGetFB();
 if(!fb || v.width!=(int)w || v.height!=(int)h || v.bpp!=32 || v.refresh!=60) return 2;
 unsigned n=w*h,allocation=MmQueryAllocationSize(fb);
 if(allocation<n*4u) return 3;
 for(unsigned y=0;y<h;y++) for(unsigned x=0;x<w;x++) fb[y*w+x]=pixel(x,y,w,h);
 XVideoFlushFB();
 unsigned bad=0;
 for(unsigned y=0;y<h;y++) for(unsigned x=0;x<w;x++) if(fb[y*w+x]!=pixel(x,y,w,h)) bad++;
 record631.stage=stage;record631.width=w;record631.height=h;record631.bpp=v.bpp;record631.refresh=v.refresh;
 record631.fb=(uint32_t)fb;record631.physical=MmGetPhysicalAddress(fb);record631.allocation=allocation;
 record631.scanout=VIDEOREG(0x600800);record631.hvalid=VIDEOREG(0x680838);record631.vvalid=VIDEOREG(0x680818);
 record631.mismatches=bad;
 for(unsigned i=0;i<16;i++) record631.fp[i]=VIDEOREG(0x680800+i*4);
 timing_capture(stage);
 if(timing631.index_before!=timing631.index_after || ((timing631.flags_before^timing631.flags_after)&0x200))return 5;
 record631.crc=framebuffer_crc((volatile unsigned char*)fb,n*4);
 report("MODE stage=%u width=%u height=%u bytes=%u allocation=%u physical=%08lx scanout=%08lx hvalid=%lu vvalid=%lu mismatches=%u crc=%08lx tick=%lu\r\n",
  stage,w,h,n*4,allocation,(unsigned long)record631.physical,(unsigned long)record631.scanout,
  (unsigned long)record631.hvalid,(unsigned long)record631.vvalid,bad,(unsigned long)record631.crc,(unsigned long)GetTickCount());
 for(unsigned i=0;i<16;i++) report("FP stage=%u index=%u value=%08lx\r\n",stage,i,(unsigned long)record631.fp[i]);
 report("TIMING stage=%u index_before=%lu index_after=%lu flags_before=%08lx flags_after=%08lx\r\n",stage,(unsigned long)timing631.index_before,(unsigned long)timing631.index_after,(unsigned long)timing631.flags_before,(unsigned long)timing631.flags_after);
 for(unsigned i=0;i<23;i++)report("CRTC stage=%u index=%02x value=%02lx\r\n",stage,cr_indices[i],(unsigned long)timing631.cr[i]);
 for(unsigned i=0;i<3;i++)report("MMIO stage=%u offset=%08lx value=%08lx\r\n",stage,(unsigned long)mm_offsets[i],(unsigned long)timing631.mm[i]);
 unsigned pitch=8u*(((timing631.cr[17]&0xe0u)<<3)|timing631.cr[12]);
 report("GEOMETRY stage=%u pitch=%u format=%lu interlace=%02lx\r\n",stage,pitch,
  (unsigned long)(timing631.cr[20]&15u),(unsigned long)timing631.cr[22]);
 if(bad)return 4;
 if(record631.hvalid!=w-1 || record631.vvalid!=h-1 || pitch!=4*w ||
    (timing631.cr[20]&15u)!=3 || timing631.cr[22]!=0xffu) return 6;
 return 0;
}
int main(void) {
 logfile=CreateFileA("D:\\hd631.txt",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 log_ok=logfile!=INVALID_HANDLE_VALUE;record631.log_ok=log_ok;
 report("XWN_HD631 version=1 kernel=%u.%u.%u.%u\r\n",XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe);
 MM_STATISTICS m={0};m.Length=sizeof(m);
 record631.magic=0x631c0de;record631.version=1;record631.bytes=sizeof(Record);
 record631.settings=XVideoGetEncoderSettings();
 report("SETTINGS value=%08lx\r\n",(unsigned long)record631.settings);
 if(MmQueryStatistics(&m)!=0) {record631.error=10;goto end;}
 record631.total_pages=m.TotalPhysicalPages;
 if(m.TotalPhysicalPages!=16384) {record631.error=12;goto end;}
 /* Refuse missing cable/capability; never force AV-pack detection. */
 if((record631.settings&255)!=AV_PACK_HDTV || (record631.settings&0xa0000)!=0xa0000 ||
    !available(1280,720) || !available(720,480)) {record631.error=11;goto end;}
 record631.error=show(720,480,1);if(record631.error) goto restore;
 checkpoint631(11,&record631);Sleep(10000);
 record631.error=show(1280,720,2);if(record631.error) goto restore;
 checkpoint631(22,&record631);Sleep(10000);
restore: {
 unsigned earlier=record631.error;unsigned fallback=show(720,480,3);
 record631.error=earlier?earlier:fallback;
 if(!record631.error) {checkpoint631(33,&record631);Sleep(10000);}
}
end:
 report("COMPLETE error=%lu log_ok=%u mode_changes=%lu\r\n",(unsigned long)record631.error,log_ok,(unsigned long)record631.changes);
 if(logfile!=INVALID_HANDLE_VALUE && !CloseHandle(logfile)) log_ok=0;
 record631.log_ok=log_ok;
 checkpoint631(record631.error?255:44,&record631);
 Sleep(10000);HalReturnToFirmware(HalRebootRoutine);return 0;
}

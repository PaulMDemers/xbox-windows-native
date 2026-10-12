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
volatile Record record307;
__attribute__((noinline)) void checkpoint307(unsigned phase,volatile Record *r) {
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
 record307.log_ok=log_ok;
}

/* Only documented timing storage; never status/interrupt-clear registers. */
static const unsigned char cr_indices[]={0,1,2,3,4,5,6,7,9,0x10,0x11,0x12,0x13,0x15,0x16,0x17,0x18,0x19,0x1a,0x25,0x28,0x2d,0x39};
static const uint32_t mm_offsets[]={0x600804,0x680508,0x680600};
typedef struct {
 uint32_t magic,stage,index_before,index_after,flags_before,flags_after;
 uint32_t cr[23],mm[3],base,size,avset,avoption,smbwrite,smbread,kernel_pages,kernel_valid,kernel_saved;
} Timing;
volatile Timing timing307;
static void timing_capture(unsigned stage) {
 volatile unsigned char *index=(volatile unsigned char*)(VIDEO_BASE+0x6013d4);
 volatile unsigned char *data=(volatile unsigned char*)(VIDEO_BASE+0x6013d5);
 unsigned flags,after;
 __asm__ __volatile__("pushfl; popl %0; cli":"=r"(flags)::"memory");
 unsigned saved=*index;
 timing307.magic=0x30771a;timing307.stage=stage;timing307.index_before=saved;
 for(unsigned i=0;i<23;i++){*index=cr_indices[i];timing307.cr[i]=*data;}
 for(unsigned i=0;i<3;i++)timing307.mm[i]=VIDEOREG(mm_offsets[i]);
 *index=(unsigned char)saved;timing307.index_after=*index;
 __asm__ __volatile__("pushl %0; popfl"::"r"(flags):"memory","cc");
 __asm__ __volatile__("pushfl; popl %0":"=r"(after)::"memory");
 timing307.flags_before=flags;timing307.flags_after=after;
}
/* Read-only bounded resident kernel capture, kept private for encoder-path analysis.
 * Missing pages are zeroed and explicitly counted; never presented as real bytes.
 * No encoder access until its actual readback protocol is established. */
static int capture_kernel(void) {
 uintptr_t av=(uintptr_t)AvSetDisplayMode,base=0;uint32_t size=0;
 timing307.avset=av;timing307.avoption=(uintptr_t)AvSendTVEncoderOption;
 timing307.smbwrite=(uintptr_t)HalWriteSMBusValue;timing307.smbread=(uintptr_t)HalReadSMBusValue;
 if(av<0x80010000u || av>=0x80400000u)return 20;
 for(uintptr_t p=av&~4095u;p>=0x80010000u && av-p<0x200000u;p-=4096){
  if(!MmIsAddressValid((void*)p) || !MmIsAddressValid((void*)(p+4095)))continue;
  const unsigned char *b=(const unsigned char*)p;
  if(*(const uint16_t*)b!=0x5a4d)continue;
  unsigned pe=*(const uint32_t*)(b+0x3c);
  if(pe>0xe00 || *(const uint32_t*)(b+pe)!=0x4550 || *(const uint16_t*)(b+pe+4)!=0x14c || *(const uint16_t*)(b+pe+24)!=0x10b)continue;
  size=*(const uint32_t*)(b+pe+24+56);
  if(size<4096 || size>0x200000 || av-p>=size)continue;
  base=p;break;
 }
 if(!base)return 21;
 timing307.base=base;timing307.size=size;
 HANDLE h=CreateFileA("D:\\kernel307.bin",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 unsigned char blank[4096]={0};unsigned ok=h!=INVALID_HANDLE_VALUE;
 for(unsigned offset=0;offset<size;offset+=4096){
  unsigned length=size-offset<4096?size-offset:4096;
  unsigned valid=MmIsAddressValid((void*)(base+offset)) && MmIsAddressValid((void*)(base+offset+length-1));
  DWORD written=0;timing307.kernel_pages++;timing307.kernel_valid+=!!valid;
  report("KPAGE offset=%08x valid=%u\r\n",offset,valid);
  if(h!=INVALID_HANDLE_VALUE && (!WriteFile(h,valid?(void*)(base+offset):blank,length,&written,NULL) || written!=length))ok=0;
 }
 if(h!=INVALID_HANDLE_VALUE){IO_STATUS_BLOCK io;if((LONG)NtFlushBuffersFile(h,&io)<0)ok=0;if(!CloseHandle(h))ok=0;}
 timing307.kernel_saved=ok;
 report("KERNEL base=%08lx bytes=%lu avset=%08lx avoption=%08lx smbwrite=%08lx smbread=%08lx pages=%lu valid=%lu saved=%u\r\n",
  (unsigned long)base,(unsigned long)size,(unsigned long)av,(unsigned long)timing307.avoption,(unsigned long)timing307.smbwrite,(unsigned long)timing307.smbread,(unsigned long)timing307.kernel_pages,(unsigned long)timing307.kernel_valid,ok);
 return 0;
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
 record307.changes++;
 VIDEO_MODE v=XVideoGetMode();uint32_t *fb=(uint32_t*)XVideoGetFB();
 if(!fb || v.width!=(int)w || v.height!=(int)h || v.bpp!=32 || v.refresh!=60) return 2;
 unsigned n=w*h,allocation=MmQueryAllocationSize(fb);
 if(allocation<n*4u) return 3;
 for(unsigned y=0;y<h;y++) for(unsigned x=0;x<w;x++) fb[y*w+x]=pixel(x,y,w,h);
 XVideoFlushFB();
 unsigned bad=0;
 for(unsigned y=0;y<h;y++) for(unsigned x=0;x<w;x++) if(fb[y*w+x]!=pixel(x,y,w,h)) bad++;
 record307.stage=stage;record307.width=w;record307.height=h;record307.bpp=v.bpp;record307.refresh=v.refresh;
 record307.fb=(uint32_t)fb;record307.physical=MmGetPhysicalAddress(fb);record307.allocation=allocation;
 record307.scanout=VIDEOREG(0x600800);record307.hvalid=VIDEOREG(0x680838);record307.vvalid=VIDEOREG(0x680818);
 record307.mismatches=bad;
 for(unsigned i=0;i<16;i++) record307.fp[i]=VIDEOREG(0x680800+i*4);
 timing_capture(stage);
 if(timing307.index_before!=timing307.index_after || ((timing307.flags_before^timing307.flags_after)&0x200))return 5;
 record307.crc=framebuffer_crc((volatile unsigned char*)fb,n*4);
 report("MODE stage=%u width=%u height=%u bytes=%u allocation=%u physical=%08lx scanout=%08lx hvalid=%lu vvalid=%lu mismatches=%u crc=%08lx tick=%lu\r\n",
  stage,w,h,n*4,allocation,(unsigned long)record307.physical,(unsigned long)record307.scanout,
  (unsigned long)record307.hvalid,(unsigned long)record307.vvalid,bad,(unsigned long)record307.crc,(unsigned long)GetTickCount());
 for(unsigned i=0;i<16;i++) report("FP stage=%u index=%u value=%08lx\r\n",stage,i,(unsigned long)record307.fp[i]);
 report("TIMING stage=%u index_before=%lu index_after=%lu flags_before=%08lx flags_after=%08lx\r\n",stage,(unsigned long)timing307.index_before,(unsigned long)timing307.index_after,(unsigned long)timing307.flags_before,(unsigned long)timing307.flags_after);
 for(unsigned i=0;i<23;i++)report("CRTC stage=%u index=%02x value=%02lx\r\n",stage,cr_indices[i],(unsigned long)timing307.cr[i]);
 for(unsigned i=0;i<3;i++)report("MMIO stage=%u offset=%08lx value=%08lx\r\n",stage,(unsigned long)mm_offsets[i],(unsigned long)timing307.mm[i]);
 return bad?4:0;
}
int main(void) {
 logfile=CreateFileA("D:\\hd307.txt",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 log_ok=logfile!=INVALID_HANDLE_VALUE;record307.log_ok=log_ok;
 report("XWN_HD307 version=1 kernel=%u.%u.%u.%u\r\n",XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe);
 MM_STATISTICS m={0};m.Length=sizeof(m);
 record307.magic=0x307c0de;record307.version=1;record307.bytes=sizeof(Record);
 record307.settings=XVideoGetEncoderSettings();
 report("SETTINGS value=%08lx\r\n",(unsigned long)record307.settings);
 if(MmQueryStatistics(&m)!=0) {record307.error=10;goto end;}
 record307.total_pages=m.TotalPhysicalPages;
 record307.error=capture_kernel();if(record307.error)goto end;
 /* Refuse missing cable/capability; never force AV-pack detection. */
 if((record307.settings&255)!=AV_PACK_HDTV || (record307.settings&0xe0000)!=0xe0000 ||
    !available(1280,720) || !available(1920,1080) || !available(640,480)) {record307.error=11;goto end;}
 record307.error=show(1280,720,1);if(record307.error) goto restore;
 checkpoint307(11,&record307);Sleep(10000);
 record307.error=show(1920,1080,2);if(record307.error) goto restore;
 checkpoint307(22,&record307);Sleep(25000);
restore: {
 unsigned earlier=record307.error;unsigned fallback=show(640,480,3);
 record307.error=earlier?earlier:fallback;
 if(!record307.error) {checkpoint307(33,&record307);Sleep(5000);}
}
end:
 report("COMPLETE error=%lu log_ok=%u mode_changes=%lu\r\n",(unsigned long)record307.error,log_ok,(unsigned long)record307.changes);
 if(logfile!=INVALID_HANDLE_VALUE && !CloseHandle(logfile)) log_ok=0;
 record307.log_ok=log_ok;
 checkpoint307(record307.error?255:44,&record307);
 Sleep(10000);HalReturnToFirmware(HalRebootRoutine);return 0;
}

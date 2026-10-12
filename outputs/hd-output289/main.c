/* SPDX-License-Identifier: MIT
 * Standalone kernel mode API diagnostic. EMULATOR ONLY until separately reviewed.
 * No EEPROM writes, PBKit/firmware channel commands or Windows-driver changes.
 */
#include <hal/video.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdint.h>
typedef struct {
 uint32_t magic,version,bytes,phase,error,stage,settings,changes;
 uint32_t width,height,bpp,refresh,fb,physical,allocation,scanout;
 uint32_t hvalid,vvalid,total_pages,mismatches;
 uint32_t fp[16];
} Record;
volatile Record record289;
__attribute__((noinline)) void checkpoint289(unsigned phase,volatile Record *r) {
 __asm__ __volatile__("" ::: "memory");r->phase=phase;__asm__ __volatile__("" ::: "memory");
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
 if(!XVideoSetMode(w,h,32,60)) return 1;
 record289.changes++;
 VIDEO_MODE v=XVideoGetMode();uint32_t *fb=(uint32_t*)XVideoGetFB();
 if(!fb || v.width!=(int)w || v.height!=(int)h || v.bpp!=32 || v.refresh!=60) return 2;
 unsigned n=w*h,allocation=MmQueryAllocationSize(fb);
 if(allocation<n*4u) return 3;
 for(unsigned y=0;y<h;y++) for(unsigned x=0;x<w;x++) fb[y*w+x]=pixel(x,y,w,h);
 XVideoFlushFB();
 unsigned bad=0;
 for(unsigned y=0;y<h;y++) for(unsigned x=0;x<w;x++) if(fb[y*w+x]!=pixel(x,y,w,h)) bad++;
 record289.stage=stage;record289.width=w;record289.height=h;record289.bpp=v.bpp;record289.refresh=v.refresh;
 record289.fb=(uint32_t)fb;record289.physical=MmGetPhysicalAddress(fb);record289.allocation=allocation;
 record289.scanout=VIDEOREG(0x600800);record289.hvalid=VIDEOREG(0x680838);record289.vvalid=VIDEOREG(0x680818);
 record289.mismatches=bad;
 for(unsigned i=0;i<16;i++) record289.fp[i]=VIDEOREG(0x680800+i*4);
 return bad?4:0;
}
int main(void) {
 MM_STATISTICS m={0};m.Length=sizeof(m);
 record289.magic=0x289c0de;record289.version=1;record289.bytes=sizeof(Record);
 record289.settings=XVideoGetEncoderSettings();
 if(MmQueryStatistics(&m)!=0) {record289.error=10;goto end;}
 record289.total_pages=m.TotalPhysicalPages;
 /* Refuse missing cable/capability; never force AV-pack detection. */
 if((record289.settings&255)!=AV_PACK_HDTV || (record289.settings&0xe0000)!=0xe0000 ||
    !available(1280,720) || !available(1920,1080) || !available(640,480)) {record289.error=11;goto end;}
 record289.error=show(1280,720,1);if(record289.error) goto restore;
 checkpoint289(11,&record289);Sleep(2000);
 record289.error=show(1920,1080,2);if(record289.error) goto restore;
 checkpoint289(22,&record289);Sleep(2000);
restore: {
 unsigned earlier=record289.error;unsigned fallback=show(640,480,3);
 record289.error=earlier?earlier:fallback;
 if(!record289.error) checkpoint289(33,&record289);
}
end:
 checkpoint289(record289.error?255:44,&record289);
 Sleep(10000);HalReturnToFirmware(HalRebootRoutine);return 0;
}

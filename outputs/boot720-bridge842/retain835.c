/* SPDX-License-Identifier: GPL-2.0-or-later
 * Fixed Xbox1.6 boot: retain kernel-established720p. No timing/encoder writes.
 * This profile is entered only by the retail64 kernel frontend and checked bridge.
 */
#include "boot.h"
#include "memory_layout.h"
#include "drivers/video/BootVideo.h"
#include "drivers/video/encoder.h"

_Static_assert(RAMSIZE==0x04000000 && FB_SIZE==0x00900000 &&
 (FB_START&0x0fffffff)==0x03700000 && MAX_INITRD_END==0x03700000,
 "retained720 must match Windows framebuffer reservation");

static unsigned read32(unsigned o) { return *(volatile unsigned *)(0xfd000000+o); }
static unsigned char cr(unsigned i) {
 volatile unsigned char *index=(void *)0xfd6013d4,*data=(void *)0xfd6013d5;
 unsigned char old=*index,v;*index=i;v=*data;*index=old;return v;
}
static void stop835(void) __attribute__((noreturn));
static void stop835(void) { __asm__ volatile("cli");for(;;)__asm__ volatile("hlt"); }
static int geometry835(void) {
 return read32(0x680838)==1279 && read32(0x680818)==719 &&
  8*(((cr(0x19)&0xe0)<<3)|cr(0x13))==5120 && (cr(0x28)&15)==3 &&
  cr(0x39)==0xff;
}
static unsigned pfb835;
void XwnRetain720Entry835(void) {
 unsigned fb=read32(0x600800);
 if (!geometry835() || (fb&4095) || fb<0x02800000 || fb>0x04000000-3686400)
  stop835();
 pfb835=read32(0x100200);
 /* Disable inherited GPU/display interrupts, retain scanout/timings/encoder.
  * The rest of platform startup owns CPU interrupt routing from this point. */
 *(volatile unsigned *)0xfd000140=0;
 *(volatile unsigned *)0xfd600140=0;
}
void XwnRetain720Mode835(CURRENT_VIDEO_MODE_DETAILS *m) {
 if (!geometry835() || read32(0x100200)!=pfb835 || xbox_ram!=64)stop835();
 /* FB was cleared by ordinary startup. Only its base address changes; all
  * width/height/pitch/format and external encoder settings stay established. */
 *(volatile unsigned *)0xfd600800=0x03700000;
 if(read32(0x600800)!=0x03700000 || !geometry835())stop835();
 memset(m,0,sizeof(*m));m->m_dwFrameBufferStart=FB_START;
 m->m_pbBaseAddressVideo=(void *)0xfd000000;m->m_bBPP=32;
 m->width=1280;m->height=720;m->xmargin=40;m->ymargin=40;
 m->m_bAvPack=1;VIDEO_AV_MODE=1;video_encoder=ENCODER_XCALIBUR;
}

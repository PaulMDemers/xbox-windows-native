/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifdef XWN_HD_TIMING_1080I
#ifndef XWN_HD_RESERVATION
#error HD timing requires the reviewed nine-MiB reservation
#endif
#include "boot.h"
#include "memory_layout.h"
#include "timer.h"
#include "xwn_hd_adapter.h"
volatile struct xwn_hd_state XwnHdState316;
static uint32_t hd_r32(void *o,uint32_t a){(void)o;return *(volatile uint32_t*)(0xfd000000u+a);}
static void hd_w32(void *o,uint32_t a,uint32_t v){(void)o;*(volatile uint32_t*)(0xfd000000u+a)=v;}
static uint8_t hd_r8(void *o,uint32_t a){(void)o;return *(volatile uint8_t*)(0xfd000000u+a);}
static void hd_w8(void *o,uint32_t a,uint8_t v){(void)o;*(volatile uint8_t*)(0xfd000000u+a)=v;}
static uint16_t hd_in16(void *o,uint16_t p){(void)o;return IoInputWord(p);}
static uint8_t hd_in8(void *o,uint16_t p){(void)o;return IoInputByte(p);}
static void hd_out16(void *o,uint16_t p,uint16_t v){(void)o;IoOutputWord(p,v);}
static void hd_out8(void *o,uint16_t p,uint8_t v){(void)o;IoOutputByte(p,v);}
static void hd_delay(void *o,unsigned us){(void)o;wait_us(us);}
int XwnHdTry1080(CURRENT_VIDEO_MODE_DETAILS *mode,unsigned encoder,unsigned cable,unsigned flags){
 const struct xwn_hd_io io={0,hd_r32,hd_w32,hd_r8,hd_w8,hd_in16,hd_in8,hd_out16,hd_out8,hd_delay};
 const struct xwn_hd_request r={2,(uint32_t)xbox_ram*1024u*1024u,FB_START&0x0fffffffu,FB_SIZE,316160u,encoder,cable,flags};
 int result=xwn_hd_apply(&io,&r,&XwnHdState316);
 if(result<0){
  /* Partial display setup cannot fall through into Windows or legacy setup.
   * Request the same quick reset as the existing SMC helper, with a bounded
   * transaction. If hardware does not reset, halt with state retained. */
  (void)xwn_hd_smb_write(&io,0x10,0x02,0x01);
  __asm__ __volatile__("cli" ::: "memory");
  for(;;)__asm__ __volatile__("hlt");
 }
 if(result==1){mode->width=1920;mode->height=1080;mode->xmargin=0;mode->ymargin=0;}
 return result;
}
#endif

/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* Validate every touched page segment before any caller copies bytes. */
static int range632(unsigned offset,unsigned length,int (*valid)(void *,uint32_t),void *o) {
 if(!length || length>4096 || offset>=623712 || length>623712-offset || !valid)return 0;
 uint32_t at=0x80010000u+offset,end=at+length;
 while(at<end) {
  uint32_t next=(at&~4095u)+4096;if(next>end)next=end;
  if(!valid(o,at) || !valid(o,next-1))return 0;
  at=next;
 }
 return 1;
}

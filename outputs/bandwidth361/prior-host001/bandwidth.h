/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_BANDWIDTH361_H
#define XWN_BANDWIDTH361_H
#include <stdint.h>
#define B361_SLOTS 4u
#define B361_ROW 3840u
#define B361_ROWS 540u
#define B361_LENGTH (B361_ROW*B361_ROWS)
#define B361_GUARD 64u
#define B361_META 64u
#define B361_PACKET (B361_META+2*16640u)
#define B361_WORDS (16u+B361_SLOTS*B361_PACKET)
#define B361_BYTES (4u*B361_WORDS)
typedef struct {uint32_t issued,published;uint32_t words[B361_SLOTS][B361_PACKET];} B361_STATE;
typedef struct {
 unsigned slot,active;unsigned char *allocation,*scratch;
 uint32_t *record;uintptr_t shadow,screen;unsigned pitch,offset;
} B361_CONTEXT;
static __inline void b361_q(uint32_t *p,uint64_t n){p[0]=(uint32_t)n;p[1]=(uint32_t)(n>>32);}
static __inline unsigned b361_compare(const unsigned char *a,const volatile unsigned char *b,
 unsigned bytes,unsigned rows,unsigned stride)
{
 unsigned x,y,bad=0;for(y=0;y<rows;y++)for(x=0;x<bytes;x++)
  if(a[y*bytes+x]!=b[y*stride+x])++bad;
 return bad;
}
static __inline unsigned b361_guards(const unsigned char *p)
{
 unsigned i,bad=0;for(i=0;i<B361_GUARD;i++) {
  if(p[i]!=(unsigned char)(i^0xa5))++bad;
  if(p[B361_GUARD+B361_LENGTH+i]!=(unsigned char)(i^0x5a))++bad;
 }return bad;
}
static __inline int b361_ticks(int64_t a,int64_t b,uint64_t *n)
{
 if(a<0||b<a)return 0;*n=(uint64_t)b-(uint64_t)a;return 1;
}
#endif

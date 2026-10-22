/* SPDX-License-Identifier: GPL-2.0-or-later
 * Bounded snapshots of the previously observed631 timing subset.
 * CRTC index selection is restored. No CLI/STI, data writes or status read.
 * Indexed reads are skipped when IF is set; RAM data is not a durable receipt.
 */
#ifndef XWN_READBACK651_H
#define XWN_READBACK651_H
#include "xwn_hd_adapter.h"
static const unsigned char cr651_indices[23]={0,1,2,3,4,5,6,7,9,0x10,0x11,0x12,0x13,0x15,0x16,0x17,0x18,0x19,0x1a,0x25,0x28,0x2d,0x39};
static const unsigned mm651_offsets[18]={0x680800,0x680804,0x680808,0x68080c,0x680810,0x680814,0x680818,0x680820,0x680824,0x680828,0x68082c,0x680830,0x680834,0x680838,0x680600,0x680508,0x600804,0x6806a0};
struct readback651 {unsigned captured,cr_captured,index_before,index_after,flags_before,flags_after;unsigned cr[23],mm[18];};
static void capture651(const struct xwn_hd_io *io,volatile struct readback651 *s,unsigned (*flags)(void)) {
 unsigned i;
 *s=(struct readback651){0};
 for(i=0;i<18;i++)s->mm[i]=io->r32(io->opaque,mm651_offsets[i]);
 s->captured=1;s->flags_before=flags();
 if(!(s->flags_before&0x200)) {
  s->index_before=io->r8(io->opaque,0x6013d4);
  for(i=0;i<23;i++) {
   io->w8(io->opaque,0x6013d4,cr651_indices[i]);
   s->cr[i]=io->r8(io->opaque,0x6013d5);
  }
  io->w8(io->opaque,0x6013d4,(unsigned char)s->index_before);
  s->index_after=io->r8(io->opaque,0x6013d4);
  s->flags_after=flags();
  s->cr_captured=s->index_before==s->index_after && !((s->flags_before^s->flags_after)&0x200);
 } else s->flags_after=s->flags_before;
}
/* Bit0 CRTC mismatch,bit1 FP/general mismatch,bit2 unknown/incomplete. */
static unsigned match651(const volatile struct readback651 *s,const struct xwn_hd_profile *p) {
 unsigned i,j,bad=0;
 if(!s->captured || !s->cr_captured)return 4;
 for(i=0;i<23;i++) {
  unsigned index=cr651_indices[i],mask=index==0x19?0xe0:index==0x2d?1:255;
  for(j=0;j<35;j++)if(xwn_hd_crtc_indices[j]==index)break;
  if(j==35)return 4;
  if((s->cr[i]&mask)!=(p->crtc[j]&mask))bad|=1;
 }
 for(i=0;i<15;i++) {
  for(j=0;j<28;j++)if(xwn_hd_mmio_offsets[j]==mm651_offsets[i])break;
  if(j==28)return 4;
  if(s->mm[i]!=p->mmio[j])bad|=2;
 }
 return bad;
}
#endif

#ifdef XWN_HD_TIMING_720P
/* SPDX-License-Identifier: GPL-2.0-or-later
 * Explicit progressive HDTV transaction. Hardware access is supplied by the native wrapper;
 * the same orchestration is exercised with modeled I/O in host tests.
 */
#include "xwn_hd_adapter.h"
#define BUS_POLLS 1000u
#define SYNC_POLLS 10000u
#define VBLANK_POLLS 100000u
#define O io->opaque
int xwn_hd_smb_write(const struct xwn_hd_io *io,uint8_t address,uint8_t reg,uint8_t value) {
 unsigned i;uint16_t status;
 for(i=0;i<BUS_POLLS;i++) {
  if(!(io->in16(O,0xc000)&0x0800))break;
  io->delay(O,10);
 }
 if(i==BUS_POLLS)return 1;
 io->out8(O,0xc004,(uint8_t)(address<<1));
 io->out8(O,0xc008,reg);io->out16(O,0xc006,value);
 status=io->in16(O,0xc000);io->out16(O,0xc000,status);
 io->out8(O,0xc002,0x1a);
 for(i=0;i<BUS_POLLS;i++) {
  status=io->in8(O,0xc000);
  if(status&0x36) return ((status&0x10) && !(status&0x26))?0:3;
  io->delay(O,10);
 }
 return 2;
}
static void cr(const struct xwn_hd_io *io,uint8_t index,uint8_t value) {
 io->w8(O,0x6013d4,index);io->w8(O,0x6013d5,value);
}
static int enc(const struct xwn_hd_io *io,volatile struct xwn_hd_state *s,uint8_t r,uint8_t v) {
 int e;s->smb_attempts++;e=xwn_hd_smb_write(io,0x45,r,v);
 if(e){s->error=10u+(unsigned)e;return 0;}s->smb_completed++;return 1;
}
static int edge(const struct xwn_hd_io *io,volatile struct xwn_hd_state *s,unsigned wanted) {
 unsigned i;
 for(i=0;i<VBLANK_POLLS;i++) {
  s->vblank_polls++;
  if((io->r8(O,0x6013da)&8)==wanted)return 1;
  io->delay(O,10);
 }
 s->error=22;return 0;
}
int xwn_hd_apply(const struct xwn_hd_io *io,const struct xwn_hd_request *r,volatile struct xwn_hd_state *s) {
 struct xwn_hd_profile p;unsigned i;uint32_t update=0;
 static const uint8_t seq[5]={3,0x21,15,0,6};
 static const uint8_t gra[9]={0,0,0,0,0,0x40,5,15,255};
 static const uint8_t attr[20]={1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,1,0x4a,15,0,0};
 if(!s)return 0;
 *s=(struct xwn_hd_state){0};
 if(!io || !r || !io->r32 || !io->w32 || !io->r8 || !io->w8 ||
    !io->in16 || !io->in8 || !io->out16 || !io->out8 || !io->delay)return 0;
 if((r->mode!=XWN_HD_720P && r->mode!=XWN_HD_480P) ||
    r->encoder!=0 || r->cable!=3 ||
    !(r->video_flags&(r->mode==XWN_HD_480P?8u:2u)) ||
    !xwn_hd_layout_valid(r->mode,r->ram,r->fb,r->reserved,r->hidden) ||
    !xwn_hd_get_profile(r->mode,&p))return 0;
 s->stage=1;s->vpll=io->r32(O,0x680508);s->pcrtc=io->r32(O,0x600804);
 /* Retain clocks/PCRTC configuration; observations are not new programming values. */
 s->mutated=1;io->out8(O,0x80d3,5);
 io->w8(O,0xc03c4,1);io->w8(O,0xc03c5,0x21);
 for(i=0;i<SYNC_POLLS;i++) {
  update=io->r32(O,0x6806a0);s->sync_polls++;
  if(!((update^(update>>4))&1))break;
  io->delay(O,10);
 }
 if(i==SYNC_POLLS){s->error=21;goto fail;}
 cr(io,0x1f,0x57);cr(io,0x21,0xff);cr(io,0x28,0);
 io->w32(O,0x100200,0x03070003);io->w32(O,0x600800,r->fb);
 io->w32(O,0x680880,0x21121111);s->stage=2;
 if(!enc(io,s,0xba,0x80) || !enc(io,s,0xba,0x3f) || !enc(io,s,0x6c,0x46))goto fail;
 io->delay(O,1);if(!enc(io,s,0x6c,0xc6))goto fail;
 for(i=0;i<13;i++)if(!enc(io,s,xwn_hd_encoder_indices[i],p.encoder[i]))goto fail;
 s->stage=3;io->out8(O,0x80d6,4);io->out8(O,0x80d8,4);
 io->w32(O,0x68050c,io->r32(O,0x68050c)|0x10020000u);
 io->w8(O,0xc03c3,1);io->w8(O,0xc03c2,0xe3);
 /* Known common DAC setup from the existing Cromwell path. */
 io->w32(O,0x680884,0);io->w32(O,0x680888,0);
 io->w32(O,0x68088c,0x10001000);io->w32(O,0x680890,0x10000000);io->w32(O,0x680894,0x10000000);
 for(i=0;i<26;i++)io->w32(O,xwn_hd_mmio_offsets[i],p.mmio[i]);
 io->w32(O,0x680600,p.mmio[27]);
 for(i=0;i<5;i++){io->w8(O,0xc03c4,(uint8_t)i);io->w8(O,0xc03c5,seq[i]);}
 for(i=0;i<9;i++){io->w8(O,0xc03ce,(uint8_t)i);io->w8(O,0xc03cf,gra[i]);}
 (void)io->r8(O,0x6013da);
 for(i=0;i<20;i++){io->w8(O,0x6013c0,(uint8_t)i);io->w8(O,0x6013c0,attr[i]);}
 io->w8(O,0x6013c0,0x20);
 cr(io,0x11,0);for(i=0;i<35;i++)cr(io,xwn_hd_crtc_indices[i],p.crtc[i]);
 io->w32(O,0x6806a0,(~update)&1);
 io->w8(O,0xc03c4,1);io->w8(O,0xc03c5,1);s->stage=4;
 for(i=0;i<3;i++)if(!edge(io,s,0) || !edge(io,s,8))goto fail;
 io->w32(O,0x680880,p.mmio[26]);io->delay(O,1);
 /* Never read/modify/write unknown6c readback. Use the declared reset image. */
 if(!enc(io,s,0x6c,0xc6) || !enc(io,s,0xba,p.encoder[13]))goto fail;
 io->w32(O,0x600800,r->fb);
 /* Exact readable geometry and pitch check before exposing the new output. */
 if(io->r32(O,0x680838)!=p.width-1 || io->r32(O,0x680818)!=p.height-1){s->error=23;goto fail;}
 io->w8(O,0x6013d4,0x13);
 if(io->r8(O,0x6013d5)!=p.crtc[19]){s->error=24;goto fail;}
 io->w8(O,0x6013d4,0x19);
 if((io->r8(O,0x6013d5)&0xe0)!=(p.crtc[25]&0xe0)){s->error=24;goto fail;}
 io->w8(O,0x6013d4,0x28);
 if(io->r8(O,0x6013d5)!=p.crtc[34]){s->error=24;goto fail;}
 io->out8(O,0x80d3,4);s->stage=5;return 1;
fail:
 io->out8(O,0x80d3,5);s->stage=255;return -1;
}

#endif

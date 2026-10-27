/* SPDX-License-Identifier: GPL-2.0-or-later
 * HOST-ONLY transaction candidate; no XBE or physical admission.
 * Source recipe: pinned Cromwell Xcalibur720x480. VGA lock/attribute access
 * review: Linux v6.12 nouveau dispnv04/hw.h. See SOURCE-REVIEW.md for limits.
 * Never touch interrupt pending/enables, VPLL/selection or PFB configuration.
 */
#include "transaction.h"
#include "delay712.h"
#include "gpu_types.h"
extern void SetGPURegister(const GPU_PARAMETER *,uint8_t *);
static uint32_t r32(volatile uint8_t *g,unsigned o){return *(volatile uint32_t *)(g+o);}
static void w32(volatile uint8_t *g,unsigned o,uint32_t v){*(volatile uint32_t *)(g+o)=v;}
static uint8_t indexed(volatile uint8_t *g,unsigned o,uint8_t i){g[o]=i;return g[o+1];}
static void put(volatile uint8_t *g,unsigned o,uint8_t i,uint8_t v){g[o]=i;g[o+1]=v;}
static uint8_t cr(volatile uint8_t *g,uint8_t i){return indexed(g,0x6013d4,i);}
static void cw(volatile uint8_t *g,uint8_t i,uint8_t v){put(g,0x6013d4,i,v);}
static uint8_t sr(volatile uint8_t *g,uint8_t i){return indexed(g,0xc03c4,i);}
static void sw(volatile uint8_t *g,uint8_t i,uint8_t v){put(g,0xc03c4,i,v);}
static void out8(uint16_t p,uint8_t v){__asm__ volatile("outb %0,%w1"::"a"(v),"d"(p):"memory");}
static uint8_t in8(void *c,unsigned o){uint8_t v;(void)c;__asm__ volatile("inb %w1,%0":"=a"(v):"d"((uint16_t)(0xc000+o)):"memory");return v;}
static uint16_t in16(void *c,unsigned o){uint16_t v;(void)c;__asm__ volatile("inw %w1,%0":"=a"(v):"d"((uint16_t)(0xc000+o)):"memory");return v;}
static void bus8(void *c,unsigned o,uint8_t v){(void)c;out8((uint16_t)(0xc000+o),v);}
static void bus16(void *c,unsigned o,uint16_t v){(void)c;__asm__ volatile("outw %0,%w1"::"a"(v),"d"((uint16_t)(0xc000+o)):"memory");}
static uint32_t tick(void *c){uint32_t v;(void)c;__asm__ volatile("inl %w1,%0":"=a"(v):"d"((uint16_t)0x8008):"memory");return v;}
static const struct xcal_bus bus={0,in8,in16,bus8,bus16,100000};
static uint32_t pitch(volatile uint8_t *g)
{return (cr(g,0x13)|((cr(g,0x19)&0xe0)<<3)|((cr(g,0x25)&0x20)<<6))<<3;}
int bounds704(const struct request704 *r)
{
 if(!r||r->ram!=0x4000000||r->base<0x2000000||r->base>=r->ram||
 (r->base&4095)||r->allocation<3686400||r->allocation>r->ram-r->base||
 r->checked_bytes<3686400||r->checked_bytes>r->allocation||r->contiguous!=1||
 r->alias_checked!=1||r->width!=1280||r->height!=720||r->pitch!=5120||r->depth!=32||
 r->confirmed_xcalibur!=1||r->cable_byte!=1||!(r->flags&0x80000)||
 r->timer_hz!=3375000||r->tv_path_confirmed!=1)return 0;
 return !(r->base<0x2800000&&0x2600000<r->base+r->allocation);
}
static int context(volatile uint8_t *g)
{return r32(g,0x680508)==0x3c20d&&r32(g,0x68050c)==0x100a0400&&
 r32(g,0x680880)==0x21101100&&r32(g,0x100200)==0x3070003&&r32(g,0x600804)==3;}
/* Reblank on failure without a retry, including failure after enable request.
 * Readback proves only sequencer bit5, not the physical ACPI output gate. */
static unsigned blank(volatile uint8_t *g)
{sw(g,1,(uint8_t)(sr(g,1)|0x20));out8(0x80d3,5);return !!(sr(g,1)&0x20);}
static const uint32_t setup[][2]={{0x680884,0},{0x680888,0},{0x68088c,0x10001000},
 {0x680890,0x10000000},{0x680894,0x10000000},{0x680898,0x10000000},
 {0x68089c,0x10000000},{0x680880,0x21101100},{0x680630,2},
 {0x68084c,0x00801080},{0x6808c4,0x40801080}};
static const uint8_t cs[][2]={{0x14,0},{0x17,0xe3},{0x19,0x10},{0x1b,5},{0x22,255},{0x33,0x11}};
static const uint32_t timing[][2]={{0x680800,479},{0x680804,524},{0x680808,479},
 {0x68080c,489},{0x680810,492},{0x680814,0},{0x680818,479},{0x680820,719},
 {0x680824,779},{0x680828,719},{0x68082c,738},{0x680830,770},{0x680834,0},{0x680838,719}};
static const uint8_t cv[][3]={{0,255,0x5c},{1,255,0x59},{2,255,0x59},{3,31,0},
 {4,255,0x5d},{5,0x9f,0x9e},{6,255,0x0c},{7,255,0x3e},{9,0x60,0x40},
 {0x10,255,0xe9},{0x12,255,0xdf},{0x13,255,0x68},{0x15,255,0xdf},
 {0x16,0x7f,0x0c},{0x17,255,0xe3},{0x18,255,255},{0x19,255,0x30},
 {0x1a,255,4},{0x25,255,0x10},{0x28,255,0x83},{0x2d,31,0},{0x39,255,255}};
static const uint8_t preserved[][2]={{3,0xe0},{5,0x60},{9,0x9f},{0x16,0x80},{0x2d,0xe0},{0x11,0x7f}};
static const uint8_t seq[]={3,0x21,15,0,6},gr[]={0,0,0,0,0,0x40,5,15,255};
static uint8_t av(unsigned i){return i<15?(uint8_t)(i+1):i==15?1:i==16?0x4a:i==17?15:0;}
static void attr_select(volatile uint8_t *g,uint8_t i)
{(void)g[0x6013da];g[0x6013c0]=(uint8_t)(i|0x20);}
static int check_setup(volatile uint8_t *g,int after_geometry)
{
 for(unsigned i=0;i<sizeof(setup)/sizeof(setup[0]);++i)if(r32(g,setup[i][0])!=setup[i][1])return 0;
 for(unsigned i=0;i<sizeof(cs)/sizeof(cs[0]);++i)
  if(cr(g,cs[i][0])!=(after_geometry&&cs[i][0]==0x19?0x30:cs[i][1]))return 0;
 return 1;
}
static int check_geometry(const struct request704 *r,volatile uint8_t *g,struct result704 *o)
{
 o->width=r32(g,0x680838)+1;o->height=r32(g,0x680818)+1;o->pitch=pitch(g);
 o->start=r32(g,0x600800);o->format=cr(g,0x28);o->interlace=cr(g,0x39);
 if(!context(g)||o->width!=720||o->height!=480||o->pitch!=2880||o->start!=r->base||o->format!=0x83||o->interlace!=255)return 0;
 for(unsigned i=0;i<sizeof(timing)/sizeof(timing[0]);++i)if(r32(g,timing[i][0])!=timing[i][1])return 0;
 for(unsigned i=0;i<sizeof(cv)/sizeof(cv[0]);++i)if((cr(g,cv[i][0])&cv[i][1])!=cv[i][2])return 0;
 for(unsigned i=0;i<6;++i)if((cr(g,preserved[i][0])&preserved[i][1])!=o->preserved[i])return 0;
 return !(cr(g,0x11)&0x80)&&cr(g,0x21)==o->saved_cr21;
}
static int check_vga(volatile uint8_t *g)
{
 for(unsigned i=0;i<5;++i)if(sr(g,(uint8_t)i)!=seq[i])return 0;
 for(unsigned i=0;i<9;++i)if(indexed(g,0xc03ce,(uint8_t)i)!=gr[i])return 0;
 for(unsigned i=0;i<20;++i){attr_select(g,(uint8_t)i);if(g[0x6013c1]!=av(i))return 0;}
 return cr(g,0x44)==0;
}
/* Authored border/quadrants/checker patch. All access stays in720*480*4.
 * Read every written pixel; caller separately proves mapping/cache attributes. */
static uint32_t pixel(unsigned x,unsigned y)
{
 if(x<4||x>=716||y<4||y>=476)return 0xffffffff;
 if(y<64)return 0xff00ff00;
 if(y>=360&&y<440&&x>=160&&x<560)return ((x/8+y/8)&1)?0xffffffff:0xff000000;
 return y<240?(x<360?0xffff0000:0xff00ff00):(x<360?0xff0000ff:0xffffffff);
}
int native_transaction704(const struct request704 *r,volatile uint8_t *g,volatile uint32_t *fb,struct result704 *o)
{
 uint32_t f;uint8_t csel,ssel,gsel;
 if(!o)return T704_ARGUMENT;
 *o=(struct result704){0};o->wait_status=0xffffffff;
 if(!r||!g||!fb){o->error=T704_ARGUMENT;return o->error;}
 if(!bounds704(r)||(uint32_t)g!=0xfd000000||(uint32_t)fb!=r->base){o->error=T704_LAYOUT;return o->error;}
 __asm__ volatile("pushfl;popl %0":"=r"(f));
 if(f&0x200){o->error=T704_IF;return o->error;}
 csel=g[0x6013d4];ssel=g[0xc03c4];gsel=g[0xc03ce];o->phase=1;
 o->saved_cr11=cr(g,0x11);o->saved_cr21=cr(g,0x21);
 for(unsigned i=0;i<6;++i)o->preserved[i]=cr(g,preserved[i][0])&preserved[i][1];
 /* Do not alter shadow/owner routing. Require the source-defined unlocked
  * shadow masks and primary owner; reject doublescan rather than inheriting it.
  * Physical admission still needs these previously uncaptured fields. */
 if(!context(g)||r32(g,0x600800)!=r->base||r32(g,0x680838)!=1279||
 r32(g,0x680818)!=719||pitch(g)!=5120||cr(g,0x28)!=0x83||cr(g,0x39)!=255||
 (o->saved_cr11&0x80)||(cr(g,0x21)&0xfa)!=0xfa||cr(g,0x44)!=0||(cr(g,9)&0x80)){
  o->error=T704_BASELINE;goto done;
 }
 /*712 diagnostic: only a bounded blank/restore pair, not a mode change.
  * Require and restore the exact visible sequencer state. */
 o->saved_seq1=sr(g,1);
 if(o->saved_seq1!=1){o->error=0x7121;goto done;}
 o->phase=2;sw(g,1,(uint8_t)(o->saved_seq1|0x20));out8(0x80d3,5);
 o->blank_seq1=sr(g,1);o->blank_readback=(o->blank_seq1==0x21);
 if(!o->blank_readback){o->error=0x7122;goto restore712;}
 o->phase=3;o->wait_status=wait712(tick,0,&o->settle);
 o->error=o->wait_status==DELAY_OK?0x712:0x7123;
restore712:
 /* Exactly one restoration request even on blank/read/timer failure. No retry.
  * This is a diagnostic recovery pair, not704's post-programming reblank rule. */
 o->phase=4;o->enable_requested=1;out8(0x80d3,4);sw(g,1,(uint8_t)o->saved_seq1);
 o->restored_seq1=sr(g,1);
 if(o->restored_seq1!=o->saved_seq1||!context(g)){o->error=0x7124;}
 else{o->blank_readback=0;}
 o->phase=5;goto done;
 o->phase=2;o->blank_readback=blank(g);
 if(!o->blank_readback){o->error=T704_BLANK;goto fail;}
 o->phase=3;cw(g,0x1f,0x57);
 /* CR11 also contains legacy interrupt controls. Refuse a locked baseline
  * above; never write this register merely to clear its protection bit. */
 if(cr(g,0x11)!=o->saved_cr11){o->error=T704_UNLOCK;goto fail;}
 /* CR1f readback is not the write key; later changed-register readbacks
  * check whether writes took effect. Do not assume reading57 proves unlock. */
 o->phase=4;
 for(unsigned i=0;i<sizeof(setup)/sizeof(setup[0]);++i)w32(g,setup[i][0],setup[i][1]);
 for(unsigned i=0;i<sizeof(cs)/sizeof(cs[0]);++i)cw(g,cs[i][0],cs[i][1]);
 if(!check_setup(g,0)){o->error=T704_SETUP;goto fail;}
 o->phase=5;
 const GPU_PARAMETER target={720,720,738,779,480,489,489,524,524,4,3};
 SetGPURegister(&target,(uint8_t *)g);cw(g,0x39,255);w32(g,0x600800,r->base);
 if(!check_geometry(r,g,o)||!check_setup(g,1)){o->error=T704_GEOMETRY;goto fail;}
 o->phase=6;
 if(encoder704(&bus,tick,0,&o->encoder)!=1){o->error=T704_ENCODER;goto fail;}
 o->phase=7;
 cw(g,0x44,3);
 for(unsigned i=0;i<5;++i)sw(g,(uint8_t)i,seq[i]);
 for(unsigned i=0;i<9;++i)put(g,0xc03ce,(uint8_t)i,gr[i]);
 cw(g,0x44,0);
 for(unsigned i=0;i<20;++i){attr_select(g,(uint8_t)i);g[0x6013c0]=av(i);}
 attr_select(g,0);
 out8(0x80d8,4);out8(0x80d6,5);
 if(!check_vga(g)||!check_setup(g,1)||!check_geometry(r,g,o)){o->error=T704_READBACK;goto fail;}
 o->phase=8;
 for(unsigned y=0;y<480;++y)for(unsigned x=0;x<720;++x)fb[y*720+x]=pixel(x,y);
 for(unsigned y=0;y<480;++y)for(unsigned x=0;x<720;++x){
  if(fb[y*720+x]!=pixel(x,y)){o->error=T704_DRAW;goto fail;}++o->pixels_verified;
 }
 o->phase=9;
 if(delay500_candidate(tick,0,1,&o->settle)!=DELAY_OK){o->error=T704_SETTLE;goto fail;}
 if(!check_vga(g)||!check_setup(g,1)||!check_geometry(r,g,o)){o->error=T704_READBACK;goto fail;}
 o->phase=10;o->enable_requested=1;out8(0x80d3,4);sw(g,1,1);
 if(sr(g,1)!=1||!context(g)){o->error=T704_ENABLE;goto fail;}
 o->blank_readback=0;o->phase=11;o->error=T704_OK;goto done;
fail:
 o->blank_readback=blank(g);
done:
 g[0x6013d4]=csel;g[0xc03c4]=ssel;g[0xc03ce]=gsel;
 return o->error;
}

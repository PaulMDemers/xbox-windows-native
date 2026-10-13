/* SPDX-License-Identifier: GPL-2.0-or-later
 * Read-only non-PAE NT5 observation. All privileged access is supplied by the
 * adapter. A failed/partial record is never a cache-policy authorization.
 */
#ifndef XWN_MEMORY354_CAPTURE_H
#define XWN_MEMORY354_CAPTURE_H
#include <stdint.h>
#define M354_ROWS 4096u
#define M354_HEAD 256u
#define M354_WORDS (M354_HEAD + M354_ROWS * 4u)
#define M354_BYTES (M354_WORDS * 4u)
enum { M354_INPUT=1, M354_CPU=2, M354_READ=4, M354_SELF=8,
       M354_PAGE=16, M354_CAPACITY=32, M354_CHANGED=64, M354_OWNER=128 };
typedef struct {
 uint32_t owner,surface,object,shadow,screen,width,height,pitch,bpp;
} M354_VIEW;
typedef struct {
 int (*reg)(void *,unsigned,uint32_t *);
 int (*cpuid)(void *,uint32_t,uint32_t *);
 int (*msr)(void *,uint32_t,uint32_t *);
 int (*read)(void *,uint32_t,uint32_t *);
 void *ctx;
} M354_IO;
static int m354_cpu(M354_IO *io,uint32_t *o)
{
 uint32_t c[4],i; static const uint32_t fixed[11]={0x250,0x258,0x259,
  0x268,0x269,0x26a,0x26b,0x26c,0x26d,0x26e,0x26f};
 for(i=0;i<4;i++)if(!io->reg(io->ctx,i,o+i))return 0;
 if((o[3]&3)||!(o[0]&0x80000000u)||(o[2]&0x20))return 0;
 if(!io->cpuid(io->ctx,0,c))return 0;
 o[4]=c[0];o[5]=c[1];o[6]=c[3];o[7]=c[2];
 if(o[4]<1||o[5]!=0x756e6547||o[6]!=0x49656e69||o[7]!=0x6c65746e)return 0;
 if(!io->cpuid(io->ctx,1,c))return 0;
 o[8]=c[0];o[9]=c[3];o[10]=c[2];
 /* Owned Pentium III family only; unsupported CPUs remain explicit failures. */
 if(((o[8]>>8)&15)!=6||((o[8]>>4)&15)!=8||(o[8]&0x0fff0000u)||
    (o[9]&0x11020u)!=0x11020u||(o[9]&0x10000000u))return 0;
 if(!io->msr(io->ctx,0x277,o+12)||!io->msr(io->ctx,0xfe,o+14)||
    !io->msr(io->ctx,0x2ff,o+16))return 0;
 o[11]=o[14]&255;if(!o[11]||o[11]>8)return 0;
 if(!io->cpuid(io->ctx,0x80000000u,c))return 0;
 o[18]=c[0];o[20]=36; /* P6 fallback per Intel MTRR physical-address width. */
 if(c[0]>=0x80000008u){
  if(!io->cpuid(io->ctx,0x80000008u,c))return 0;
  o[19]=1;o[20]=c[0]&255;
 }
 if(o[20]<32||o[20]>36)return 0;
 for(i=0;i<o[11];i++){
  if(!io->msr(io->ctx,0x200+2*i,o+24+4*i)||
     !io->msr(io->ctx,0x201+2*i,o+26+4*i))return 0;
 }
 if(o[14]&256)for(i=0;i<11;i++)if(!io->msr(io->ctx,fixed[i],o+56+2*i))return 0;
 return 1;
}
static void m354_capture(const M354_VIEW *v,M354_IO *io,uint32_t *o)
{
 uint32_t i,role,base,last,va,pde,pte,self,at,length=0,reg;
 for(i=0;i<M354_WORDS;i++)o[i]=0;
 o[0]=0x4d57584e;o[1]=354;o[2]=M354_BYTES;o[15]=M354_ROWS;
 o[4]=v->owner;o[5]=v->surface;o[6]=v->object;o[7]=v->shadow;o[8]=v->screen;
 o[9]=v->width;o[10]=v->height;o[11]=v->pitch;o[12]=v->bpp;
 if(!v->owner||!v->surface||!v->object||v->width<640||v->width>1920||
    v->height<480||v->height>1080||v->bpp!=32||v->pitch!=v->width*4){o[3]|=M354_INPUT;return;}
 length=v->pitch*v->height;o[13]=length;
 if(v->shadow<0x80000000u||v->screen<0x80000000u||
    v->shadow>0xffffffffu-length||v->screen>0xffffffffu-length||
    (v->shadow<v->screen+length&&v->screen<v->shadow+length)){
  o[3]|=M354_INPUT;return;
 }
 if(!m354_cpu(io,o+16)){o[3]|=M354_CPU;return;}
 if(!io->read(io->ctx,0xc0300c00u,&self)){o[3]|=M354_READ;return;}
 o[176]=self;
 if(!(self&1)||(self&0x80)||((self^o[17])&0xfffff000u)){
  o[3]|=M354_SELF;return;
 }
 for(role=0;role<2;role++){
  base=role?v->screen:v->shadow;last=(base+length-1)&0xfffff000u;
  for(va=base&0xfffff000u;;va+=4096){
   if(o[14]>=M354_ROWS){o[3]|=M354_CAPACITY;return;}
   at=M354_HEAD+4*o[14]++;o[at]=role;o[at+1]=va;
   if(!io->read(io->ctx,0xc0300000u+(va>>22)*4,&pde)){o[3]|=M354_READ;return;}
   o[at+2]=pde;
   /* No speculative dereference through an absent/large/user page table. */
   if(!(pde&1)||(pde&0x84)){o[3]|=M354_PAGE;return;}
   if(!io->read(io->ctx,0xc0000000u+(va>>12)*4,&pte)){o[3]|=M354_READ;return;}
   o[at+3]=pte;
   if((pte&7)!=3){o[3]|=M354_PAGE;return;}
   if(va==last)break;
  }
 }
 /* Re-read every translation; A/D bits are hardware-mutated, not cache policy.
  * Equal endpoints do NOT exclude transient ABA/TLB aliases between reads. */
 for(i=0;i<o[14];i++){
  at=M354_HEAD+4*i;va=o[at+1];
  if(!io->read(io->ctx,0xc0300000u+(va>>22)*4,&pde)){
   o[3]|=M354_READ;return;
  }
  if((pde^o[at+2])&~0x60u){o[3]|=M354_CHANGED;return;}
  if(!io->read(io->ctx,0xc0000000u+(va>>12)*4,&pte)){
   o[3]|=M354_READ;return;
  }
  if((pte^o[at+3])&~0x60u){o[3]|=M354_CHANGED;return;}
 }
 if(!m354_cpu(io,o+96)){o[3]|=M354_CPU;return;}
 for(i=0;i<80;i++)if(o[16+i]!=o[96+i])o[3]|=M354_CHANGED;
 if(!io->read(io->ctx,0xc0300c00u,&reg)){o[3]|=M354_READ;return;}
 o[177]=reg;if((reg^self)&~0x60u)o[3]|=M354_CHANGED;
}
#endif

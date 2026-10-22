/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "classify.h"
/* Read captured RAM only. No live CPU, PCI, MSR or MMIO access. */
unsigned cpu_bits665(const struct admission656 *a){
 unsigned b=0;
 if(!a)return 32;
 if((a->cr0&0xe0000001u)!=1)b|=1;
 if(a->flags&0x200)b|=2;
 if((a->cpuid_edx&0x1020)!=0x1020)b|=4;
 if(a->ram!=0x4000000 && a->ram!=0x8000000)b|=8;
 if(a->esp<0x027c0000 || a->esp>=0x02800000)b|=16;
 return b;
}
unsigned cpu_stage665(const struct admission656 *a){
 unsigned b=cpu_bits665(a);
 return b&32?3:b&7?1:b&24?2:0;
}
unsigned mask665(unsigned encode,unsigned entry,unsigned show,unsigned admission,unsigned send,const struct result656 *r,const struct admission656 *a){
 unsigned b;
 if(encode)return 0x10; /* one red slot: encoding failure */
 if(entry)return 0xff; /* solid amber: entry latch failure */
 switch(show){
 case 0:break;
 case 1:return 0xc6; /* red, amber, green, off: delay failure */
 case 2:return 0xc4; /* red, amber, off, off: busy timeout */
 case 3:return 0x4c; /* green, amber, off, off: completion status error */
 case 4:return 0x84; /* red, green, off, off: completion timeout */
 default:return 0xc7; /* red, amber, green, green: unexpected show code */
 }
 if(r->used && !r->safe_to_continue)return 0xf0; /* solid red: unsafe */
 if(admission==A656_CPU){
  b=cpu_bits665(a);
  if(b&32 || !b)return 0x01; /* one green slot: missing/inconsistent */
  /* inspect() returns early for these three; RAM/ESP cannot cause that return. */
  if(b&7)b&=7;else b&=24;
  switch(b){
  case 1:return 0x50; /* CR0: even red/off */
  case 2:return 0x55; /* IF: even amber/off */
  case 4:return 0xa5; /* CPUID: red/green */
  case 8:return 0x5f; /* RAM: green/amber */
  case 16:return 0xf5; /* ESP: red/amber */
  default:return 0x05; /* multiple predicates at the relevant stage: green/off */
  }
 }
 if(admission)return 0x11; /* one amber slot: different/unknown admission */
 if(send)return 0x33; /* two amber slots: sender error */
 if(r->used && r->safe_to_continue && r->completed==3)return 0x0f;
 return 0x03; /* two green slots: incomplete/unexpected */
}

/* Compare saved snapshots only, after the caller establishes IF-only admission.
 * Captured is a validity marker. IF-clear data with captured=0 is not evidence.
 */
#include <stddef.h>
typedef char ReceiptSize665[sizeof(struct xwn652_data)==704?1:-1];
typedef char PreOffset665[offsetof(struct xwn652_data,pre)==328?1:-1];
typedef char PostOffset665[offsetof(struct xwn652_data,post)==516?1:-1];
typedef char AdmissionFlags665[offsetof(struct admission656,flags)==4?1:-1];
unsigned context665(const struct xwn652_data *d,const struct admission656 *a,unsigned eligible){
 unsigned p,q;
 if(!eligible || !d || !a || (cpu_bits665(a)&7)!=2)return 0;
 if(d->pre[0]>1 || d->post[0]>1 || (d->post[0] && d->state[2]!=1))return 4;
 if(!d->pre[0] && !d->post[0])return 3;
 if(!d->pre[0])return 1;
 if(!d->post[0])return 2;
 if(((d->pre[4]^d->pre[5])|(d->post[4]^d->post[5]))&0x200)return 5;
 p=!!(d->pre[4]&0x200);q=!!(d->post[4]&0x200);
 return 6+2*p+q;
}
unsigned context_mask665(unsigned c){
 static const unsigned masks[10]={0x50,0x55,0xf5,0x5f,0xff,0xa5,0x03,0x30,0x33,0x0f};
 return c<10?masks[c]:0xff;
}

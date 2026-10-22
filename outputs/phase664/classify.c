/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "classify.h"
/* Read captured RAM only. No live CPU, PCI, MSR or MMIO access. */
unsigned cpu_bits664(const struct admission656 *a){
 unsigned b=0;
 if(!a)return 32;
 if((a->cr0&0xe0000001u)!=1)b|=1;
 if(a->flags&0x200)b|=2;
 if((a->cpuid_edx&0x1020)!=0x1020)b|=4;
 if(a->ram!=0x4000000 && a->ram!=0x8000000)b|=8;
 if(a->esp<0x027c0000 || a->esp>=0x02800000)b|=16;
 return b;
}
unsigned cpu_stage664(const struct admission656 *a){
 unsigned b=cpu_bits664(a);
 return b&32?3:b&7?1:b&24?2:0;
}
unsigned mask664(unsigned encode,unsigned entry,unsigned show,unsigned admission,unsigned send,const struct result656 *r,const struct admission656 *a){
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
  b=cpu_bits664(a);
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

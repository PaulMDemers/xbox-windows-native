/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <assert.h>
#include <stdio.h>
#include "classify.h"
int main(void){
 unsigned bits,used,safe,completed,admission,send,cases=0;
 for(bits=0;bits<32;bits++){
  struct admission656 a={0};
  unsigned expected,group=bits&7?bits&7:bits&24;
  a.cr0=bits&1?0x80000001:1;a.flags=bits&2?0x200:0;
  a.cpuid_edx=bits&4?0x20:0x1020;a.ram=bits&8?0:0x4000000;
  a.esp=bits&16?0x02800000:0x027fe000;
  assert(cpu_bits662(&a)==bits);
  assert(cpu_stage662(&a)==(bits&7?1:bits&24?2:0));
  switch(group){case 0:expected=1;break;case 1:expected=80;break;case 2:expected=85;break;case 4:expected=165;break;case 8:expected=95;break;case 16:expected=245;break;default:expected=5;}
  for(used=0;used<2;used++)for(safe=0;safe<2;safe++)for(completed=0;completed<5;completed++)
  for(admission=0;admission<=6;admission++)for(send=0;send<=11;send++){
   struct result656 r={0};unsigned v;
   r.used=used;r.safe_to_continue=safe;r.completed=completed;
   v=mask662(0,0,0,admission,send,&r,&a);
   if(used&&!safe)assert(v==240);
   else if(admission==1)assert(v==expected);
   else if(admission)assert(v==17);
   else if(send)assert(v==51);
   else if(used&&safe&&completed==3)assert(v==15);
   else assert(v==3);
   assert(mask662(1,0,0,admission,send,&r,&a)==16);
   assert(mask662(0,1,0,admission,send,&r,&a)==255);
   assert(mask662(0,0,1,admission,send,&r,&a)==255);cases++;
  }
 }
 {
  struct admission656 a={0};struct result656 r={0};
  assert(cpu_bits662(0)==32 && cpu_stage662(0)==3);
  assert(mask662(0,0,0,A656_CPU,1,&r,0)==1);
  a.cr0=1;a.cpuid_edx=0x1020;a.ram=0x8000000;a.esp=0x027c0000;
  assert(cpu_bits662(&a)==0);a.esp--;assert(cpu_bits662(&a)==16);
  a.esp=0x027fffff;assert(cpu_bits662(&a)==0);a.esp++;assert(cpu_bits662(&a)==16);
  a.esp=0x027fe000;a.cr0=0;assert(cpu_bits662(&a)==1);
  a.cr0=0x20000001;assert(cpu_bits662(&a)==1);a.cr0=0x40000001;assert(cpu_bits662(&a)==1);
  a.cr0=0x11;assert(cpu_bits662(&a)==0);a.cpuid_edx=0x1000;assert(cpu_bits662(&a)==4);
 }
 printf("{\"status\":\"pass\",\"cases\":%u,\"boundary_checks\":12}\n",cases);return 0;
}

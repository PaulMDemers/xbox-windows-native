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
  assert(cpu_bits665(&a)==bits);
  assert(cpu_stage665(&a)==(bits&7?1:bits&24?2:0));
  switch(group){case 0:expected=1;break;case 1:expected=80;break;case 2:expected=85;break;case 4:expected=165;break;case 8:expected=95;break;case 16:expected=245;break;default:expected=5;}
  for(used=0;used<2;used++)for(safe=0;safe<2;safe++)for(completed=0;completed<5;completed++)
  for(admission=0;admission<=6;admission++)for(send=0;send<=11;send++){
   struct result656 r={0};unsigned v;
   r.used=used;r.safe_to_continue=safe;r.completed=completed;
   v=mask665(0,0,0,admission,send,&r,&a);
   if(used&&!safe)assert(v==240);
   else if(admission==1)assert(v==expected);
   else if(admission)assert(v==17);
   else if(send)assert(v==51);
   else if(used&&safe&&completed==3)assert(v==15);
   else assert(v==3);
   assert(mask665(1,0,0,admission,send,&r,&a)==16);
   assert(mask665(0,1,0,admission,send,&r,&a)==255);
   assert(mask665(0,0,1,admission,send,&r,&a)==198);
   assert(mask665(0,0,2,admission,send,&r,&a)==196);
   assert(mask665(0,0,3,admission,send,&r,&a)==76);
   assert(mask665(0,0,4,admission,send,&r,&a)==132);
   assert(mask665(0,0,5,admission,send,&r,&a)==199);
   assert(mask665(0,2,1,admission,send,&r,&a)==255);cases++;
  }
 }
 {
  struct admission656 a={0};struct result656 r={0};
  assert(cpu_bits665(0)==32 && cpu_stage665(0)==3);
  assert(mask665(0,0,0,A656_CPU,1,&r,0)==1);
  a.cr0=1;a.cpuid_edx=0x1020;a.ram=0x8000000;a.esp=0x027c0000;
  assert(cpu_bits665(&a)==0);a.esp--;assert(cpu_bits665(&a)==16);
  a.esp=0x027fffff;assert(cpu_bits665(&a)==0);a.esp++;assert(cpu_bits665(&a)==16);
  a.esp=0x027fe000;a.cr0=0;assert(cpu_bits665(&a)==1);
  a.cr0=0x20000001;assert(cpu_bits665(&a)==1);a.cr0=0x40000001;assert(cpu_bits665(&a)==1);
  a.cr0=0x11;assert(cpu_bits665(&a)==0);a.cpuid_edx=0x1000;assert(cpu_bits665(&a)==4);
 }
 {
  struct xwn652_data d={0};struct admission656 a={0};
  unsigned pc,qc,pb,pa,qb,qa,eligible,n=0;
  static const unsigned masks[10]={80,85,245,95,255,165,3,48,51,15};
  a.cr0=1;a.flags=0x200;a.cpuid_edx=0x1020;
  for(pc=0;pc<3;pc++)for(qc=0;qc<3;qc++)
  for(pb=0;pb<2;pb++)for(pa=0;pa<2;pa++)for(qb=0;qb<2;qb++)for(qa=0;qa<2;qa++)for(eligible=0;eligible<2;eligible++){
   unsigned expected;
   d.pre[0]=pc;d.post[0]=qc;d.state[2]=1;
   d.pre[4]=2+(pb?512:0);d.pre[5]=2+(pa?512:0);
   d.post[4]=2+(qb?512:0);d.post[5]=2+(qa?512:0);
   if(!eligible)expected=0;
   else if(pc==2 || qc==2)expected=4;
   else if(!pc&&!qc)expected=3;
   else if(!pc)expected=1;
   else if(!qc)expected=2;
   else if(pb!=pa || qb!=qa)expected=5;
   else expected=pb?(qb?9:8):(qb?7:6);
   assert(context665(&d,&a,eligible)==expected);assert(context_mask665(expected)==masks[expected]);n++;
  }
  assert(n==288);d.pre[0]=d.post[0]=1;d.state[2]=0;assert(context665(&d,&a,1)==4);
  assert(context665(0,&a,1)==0 && context665(&d,0,1)==0);
  d.state[2]=1;a.flags=0;assert(context665(&d,&a,1)==0);
  a.flags=512;a.cr0=0;assert(context665(&d,&a,1)==0);
  assert(context_mask665(10)==255);
 }
 printf("{\"status\":\"pass\",\"cases\":%u,\"boundary_checks\":12,\"context_cases\":288,\"context_boundaries\":6}\n",cases);return 0;
}

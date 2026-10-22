/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <assert.h>
#include <stdio.h>
#include "classify.h"
int main(void){
 unsigned used,safe,completed,admission,send,cases=0;
 const unsigned codes[]={0,80,85,165,95,245,5};
 for(used=0;used<2;used++)for(safe=0;safe<2;safe++)for(completed=0;completed<5;completed++)
 for(admission=0;admission<=6;admission++)for(send=0;send<=11;send++){
  struct result656 r={0};unsigned v;
  r.used=used;r.safe_to_continue=safe;r.completed=completed;v=mask661(0,0,0,admission,send,&r);
  if(used&&!safe)assert(v==240);
  else if(admission)assert(v==codes[admission]);
  else if(send)assert(v==51);
  else if(used&&safe&&completed==3)assert(v==15);
  else assert(v==1);
  assert(mask661(1,0,0,admission,send,&r)==16);
  assert(mask661(0,1,0,admission,send,&r)==255);
  assert(mask661(0,0,1,admission,send,&r)==255);cases++;
 }
 printf("{\"status\":\"pass\",\"cases\":%u}\n",cases);return 0;
}

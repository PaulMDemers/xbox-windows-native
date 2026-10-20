#include <assert.h>
#include <stdio.h>
#include "phase.h"
int main(void){
 PHASE605 s={0,0};unsigned int n;
 assert(phase605(&s,0,0)==0&&s.phase==0);
 assert(phase605(&s,0,3)==0&&s.deferred==0);
 assert(phase605(&s,1,3)==1&&s.phase==0&&s.deferred==1);
 assert(phase605(&s,1,1)==1&&s.phase==0);
 assert(phase605(&s,1,0)==2&&s.phase==1&&s.deferred==1);
 for(n=0;n<100;n++)assert(phase605(&s,1,n)==0&&s.phase==1);
 assert(phase605(&s,0,0)==0&&s.phase==1);
 s.phase=2;assert(phase605(&s,1,0)==-1);
 s.phase=0;s.deferred=2;assert(phase605(&s,1,0)==-1);
 s.deferred=0;assert(phase605(&s,2,0)==-1&&s.phase==0);
 assert(phase605(&s,1,0)==2&&s.phase==1);
 puts("PHASE605 PASS: pending drain, one transition, 100 duplicate requests, 3 invalid states");return 0;
}

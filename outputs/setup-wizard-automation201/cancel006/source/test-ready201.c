#include <assert.h>
#include <stdio.h>
#include "ready201.h"
int main(void){struct xwn_ready201 r={0};unsigned n=0;
 assert(!xwn_ready_hold(&r,1,8,1,2,9,100));n++;
 for(uint32_t t=100;t<5100;t++){assert(!xwn_ready_hold(&r,1,8,1,2,9,t));n++;}
 assert(xwn_ready_hold(&r,1,8,1,2,9,5100));n++;
 assert(!xwn_ready_hold(&r,1,8,3,2,9,5101));n++;
 assert(!xwn_ready_hold(&r,1,8,3,2,10,11000));n++;
 assert(!xwn_ready_hold(&r,0,8,3,2,10,17000)&&!r.present);n++;
 assert(!xwn_ready_hold(&r,1,8,3,2,10,18000));n++;
 xwn_ready_reset(&r);assert(!r.present);n++;
 assert(!xwn_ready_hold(&r,1,8,3,2,10,UINT32_MAX-100));n++;
 assert(!xwn_ready_hold(&r,1,8,3,2,10,4898));n++;
 assert(xwn_ready_hold(&r,1,8,3,2,10,4899));n++;
 assert(!xwn_ready_hold(&r,1,9,3,2,10,4900));n++;
 printf("Actual readiness header: %u assertions PASS\n",n);return 0;}

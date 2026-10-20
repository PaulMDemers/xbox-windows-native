/* MIT. Same call pairing code as target recorder; fail-closed state controls. */
#include <assert.h>
#include <stdio.h>
#include "calls.h"
static FRAME601 frame(U32 id,U32 ret,U32 sp) {
    FRAME601 f={0};f.id=id;f.ret=ret;f.entry_sp=sp;return f;
}
int main(void) {
    STACK601 a={0},b={0};FRAME601 out;unsigned i;
    assert(sizeof(U32)==4);
    assert(enter601(&a,frame(1,100,1000),4));
    assert(enter601(&b,frame(2,100,2000),8));
    assert(enter601(&a,frame(3,100,900),0));
    assert(leave601(&b,100,2012,&out)==1&&out.id==2);
    assert(leave601(&a,100,904,&out)==1&&out.id==3);
    assert(leave601(&a,100,1008,&out)==1&&out.id==1);
    assert(leave601(&a,100,1008,&out)==0);
    assert(enter601(&a,frame(4,100,1000),0));
    assert(leave601(&a,100,1008,&out)==-1&&a.depth==1);
    assert(enter601(&a,frame(5,200,900),8));
    assert(leave601(&a,100,1004,&out)==-1&&a.depth==2);
    assert(leave601(&a,300,1100,&out)==-1&&a.depth==2);
    assert(leave601(&a,300,800,&out)==0&&a.depth==2);
    assert(!enter601(&a,frame(6,300,1000),0));
    assert(!enter601(&b,frame(7,0,1000),0));
    assert(!enter601(&b,frame(8,100,0),0));
    assert(!enter601(&b,frame(9,100,0xfffffffcu),0));
    assert(!enter601(&b,frame(10,100,1000),65));
    for(i=0;i<32;i++)assert(enter601(&b,frame(11+i,100,4000-16*i),0));
    assert(!enter601(&b,frame(43,100,3000),0));
    puts("CALLS601 PASS: thread sharing, recursion, stale sites, 9 rejection controls");
    return 0;
}

/* SPDX-License-Identifier: GPL-2.0-or-later
 * Synthetic host vectors only. stdout is a binary fixture, never Xbox data.
 */
#include "packet.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void fill(uint32_t *p,unsigned n,unsigned group,unsigned seed) {
    unsigned i; for(i=0;i<n;i++)
        p[i]=0x80000000u^(seed*0x01010101u)^(group*0x112233u)^(i*0x9e3779b9u);
}
int main(void) {
    struct xwn655_identity id={{0},{0}}, bad;
    struct xwn652_data d={0};
    uint8_t guarded[XWN655_BYTES+2], baseline[XWN655_BYTES+2];
    unsigned i,seed,checks=0;
    for(i=0;i<16;i++) id.attempt[i]=(uint8_t)(i+1);
    for(i=0;i<32;i++) id.build_id[i]=(uint8_t)(i+128);
    d.post_kind=1;
    memset(guarded,0xa5,sizeof guarded); memcpy(baseline,guarded,sizeof guarded);
    for(i=0;i<XWN655_BYTES;i++) {
        assert(xwn655_encode(&id,&d,guarded+1,i)==-1);
        assert(!memcmp(guarded,baseline,sizeof guarded)); checks++;
    }
#define BAD(expr) do { assert((expr)==-1); assert(!memcmp(guarded,baseline,sizeof guarded)); checks++; } while(0)
    BAD(xwn655_encode(NULL,&d,guarded+1,XWN655_BYTES));
    BAD(xwn655_encode(&id,NULL,guarded+1,XWN655_BYTES));
    BAD(xwn655_encode(&id,&d,NULL,XWN655_BYTES));
    bad=id; memset(bad.attempt,0,16); BAD(xwn655_encode(&bad,&d,guarded+1,XWN655_BYTES));
    bad=id; memset(bad.build_id,0,32); BAD(xwn655_encode(&bad,&d,guarded+1,XWN655_BYTES));
    d.result=-2; BAD(xwn655_encode(&id,&d,guarded+1,XWN655_BYTES));
    d.result=2; BAD(xwn655_encode(&id,&d,guarded+1,XWN655_BYTES));
    d.result=0; d.post_kind=0; BAD(xwn655_encode(&id,&d,guarded+1,XWN655_BYTES));
    d.post_kind=3; BAD(xwn655_encode(&id,&d,guarded+1,XWN655_BYTES));
    for(seed=0;seed<64;seed++) {
        d.result=(int)(seed%3)-1; d.post_kind=1+seed%2;
        fill(d.request,8,0,seed); fill(d.state,9,1,seed); fill(d.trace,63,2,seed);
        fill(d.pre,47,3,seed); fill(d.post,47,4,seed);
        if(seed==0) { d.state[0]=255; d.state[1]=22; d.pre[0]=1; d.post[0]=0; }
        assert(xwn655_encode(&id,&d,guarded+1,XWN655_BYTES)==0);
        assert(guarded[0]==0xa5 && guarded[XWN655_BYTES+1]==0xa5); checks++;
        assert(fwrite(guarded+1,1,XWN655_BYTES,stdout)==XWN655_BYTES);
    }
    assert(!fflush(stdout));
    fprintf(stderr,"{\"checks\":%u,\"synthetic_records\":64}\n",checks);
    return 0;
}

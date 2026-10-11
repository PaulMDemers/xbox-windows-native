#include <assert.h>
#include <stdio.h>
#include "pending-mask.c"
int main(void) {
    unsigned tests=0;
    for(unsigned mask=0;mask<512;mask++) {
        unsigned bits[9],original=0;
        for(unsigned i=0;i<9;i++){bits[i]=(mask>>i)&1;original|=bits[i];}
        unsigned v=x263_pending_mask(bits[0],bits[1],bits[2],bits[3],bits[4],bits[5],bits[6],bits[7],bits[8]);
        assert(v==mask && !!v==!!original);tests++;
        for(unsigned i=0;i<9;i++)bits[i]*=0xffffffffu;
        assert(x263_pending_mask(bits[0],bits[1],bits[2],bits[3],bits[4],bits[5],bits[6],bits[7],bits[8])==mask);tests++;
    }
    printf("%u combinations preserve exact boolean refusal and bit identity\n",tests);
}

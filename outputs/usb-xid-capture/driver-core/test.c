/* SPDX-License-Identifier: MIT */
#include "xid_wire.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned cases;
static void unchanged(const uint8_t *b,uint32_t n,int expected)
{
    xwn_xid_sample output,prior;
    memset(&output,0xa5,sizeof(output));prior=output;
    assert(xwn_xid_decode(b,n,&output)==expected);
    assert(memcmp(&output,&prior,sizeof(output))==0);cases++;
}
int main(void)
{
    uint8_t wire[32]={0,20};xwn_xid_sample sample;
    unchanged(NULL,0,XWN_XID_NO_DATA);
    unchanged(NULL,20,XWN_XID_INVALID);
    assert(xwn_xid_decode(wire,20,NULL)==XWN_XID_INVALID);cases++;
    unchanged(wire,0xffffffffu,XWN_XID_INVALID);
    for(unsigned n=0;n<33;n++) if(n!=20) unchanged(wire,n,n==0?XWN_XID_NO_DATA:XWN_XID_INVALID);
    for(unsigned n=1;n<256;n++){wire[0]=n;unchanged(wire,20,XWN_XID_INVALID);}
    wire[0]=0;
    for(unsigned n=0;n<256;n++) {
        if(n!=20){wire[1]=n;unchanged(wire,20,XWN_XID_INVALID);}
    }
    wire[1]=20;
    /* Exercise every signed axis code, every pressure byte, all digital bits. */
    for(unsigned word=0;word<65536;word++) {
        wire[2]=word;wire[3]=word>>8;
        for(unsigned i=0;i<8;i++)wire[4+i]=(uint8_t)(word+i);
        for(unsigned i=0;i<4;i++){wire[12+2*i]=word;wire[13+2*i]=word>>8;}
        assert(xwn_xid_decode(wire,20,&sample)==XWN_XID_SAMPLE);
        assert(sample.digital==word);
        for(unsigned i=0;i<8;i++)assert(sample.pressure[i]==(uint8_t)(word+i));
        for(unsigned i=0;i<4;i++)assert(sample.sticks[i]==(word>=32768?(int)word-65536:(int)word));
        cases++;
    }
    /* Actual physical states, not a guessed emulator-only payload. */
    memset(wire,0,sizeof(wire));wire[1]=20;wire[13]=0x9d;wire[15]=0x62;wire[17]=0x9d;
    assert(xwn_xid_decode(wire,20,&sample)==XWN_XID_SAMPLE);
    assert(sample.sticks[0]==-25344&&sample.sticks[1]==25088&&sample.sticks[2]==-25344&&sample.sticks[3]==0);cases++;
    printf("%u XID decode checks passed\n",cases);return 0;
}

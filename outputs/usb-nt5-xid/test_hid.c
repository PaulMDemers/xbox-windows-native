/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "xid_hid.h"
int main(void)
{
    unsigned i,j,checks=0;uint8_t report[13],config[]={9,2,32,0,1,1,0,0x80,50,9,4,0,0,2,0x58,0x42,0,0,7,5,0x81,3,32,0,4,7,5,2,3,32,0,4};
    uint8_t xid[]={16,0x42,0,1,1,1,20,6,255,255,255,255,255,255,255,255};
    uint8_t ep=0; xwn_xid_sample s;
    memset(&s,0,sizeof(s));
    for(i=0;i<65536;i++) {
        s.sticks[0]=(int16_t)(i<32768?(int)i:(int)i-65536);
        s.sticks[1]=s.sticks[2]=s.sticks[3]=s.sticks[0];s.digital=(uint16_t)i;
        xwn_xid_to_hid(&s,report);
        assert(report[0]==1 && report[1]==(i&255) && report[2]==0);
        for(j=0;j<4;j++) assert(report[3+2*j]==(i&255) && report[4+2*j]==(i>>8));
        checks++;
    }
    memset(&s,0,sizeof(s));
    for(i=0;i<8;i++) for(j=0;j<256;j++) {
        memset(s.pressure,0,8);s.pressure[i]=(uint8_t)j;xwn_xid_to_hid(&s,report);
        assert(report[2]==((i<6 && j)?(1u<<i):0));
        assert(report[11]==(i==6?j:0) && report[12]==(i==7?j:0));checks++;
    }
    assert(xwn_xid_config(config,32,&ep) && ep==0x81);checks++;
    config[20]=0x82;assert(xwn_xid_config(config,32,&ep) && ep==0x82);checks++;
    for(i=0;i<40;i++) if(i!=32) {ep=9;assert(!xwn_xid_config(config,i,&ep) && ep==9);checks++;}
    for(i=0;i<32;i++) {
        if(i==6 || i==7 || i==8 || i==17) continue; /* permitted string/power fields */
        for(j=0;j<256;j++) {
            uint8_t save=config[i];int expected=j==save || (i==20 && j==0x81);
            config[i]=(uint8_t)j;ep=9;assert(xwn_xid_config(config,32,&ep)==expected);
            if(!expected) assert(ep==9);
            config[i]=save;checks++;
        }
    }
    assert(xwn_xid_descriptor(xid,16));checks++;
    for(i=0;i<16;i++) for(j=0;j<256;j++) {
        uint8_t save=xid[i];xid[i]=(uint8_t)j;assert(xwn_xid_descriptor(xid,16)==(j==save));xid[i]=save;checks++;
    }
    assert(!xwn_xid_config(NULL,32,&ep) && !xwn_xid_config(config,32,NULL));checks++;
    assert(!xwn_xid_descriptor(NULL,16));checks++;
    for(i=0;i<24;i++) if(i!=16) {assert(!xwn_xid_descriptor(xid,i));checks++;}
    printf("PASS %u HID mapping/descriptor checks\n",checks);return 0;
}

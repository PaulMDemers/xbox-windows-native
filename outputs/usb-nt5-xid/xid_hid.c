/* SPDX-License-Identifier: MIT */
#include "xid_hid.h"
const uint8_t xwn_report_descriptor[] = {
    0x05,0x01, 0x09,0x05, 0xa1,0x01, 0x85,0x01,
    0x05,0x09, 0x19,0x01, 0x29,0x0e, 0x15,0x00, 0x25,0x01,
    0x75,0x01, 0x95,0x0e, 0x81,0x02,
    0x75,0x01, 0x95,0x02, 0x81,0x03,
    0x05,0x01, 0x09,0x30, 0x09,0x31, 0x09,0x33, 0x09,0x34,
    0x16,0x00,0x80, 0x26,0xff,0x7f, 0x75,0x10, 0x95,0x04, 0x81,0x02,
    0x09,0x32, 0x09,0x35, 0x15,0x00, 0x26,0xff,0x00,
    0x75,0x08, 0x95,0x02, 0x81,0x02, 0xc0
};
const unsigned xwn_report_descriptor_size=sizeof(xwn_report_descriptor);
void xwn_xid_to_hid(const xwn_xid_sample *sample, uint8_t report[XWN_REPORT_SIZE])
{
    unsigned i; uint16_t buttons=sample->digital & 255u;
    for(i=0;i<6;i++) if(sample->pressure[i]) buttons|=(uint16_t)(1u<<(8+i));
    report[0]=1; report[1]=(uint8_t)buttons; report[2]=(uint8_t)(buttons>>8);
    for(i=0;i<4;i++) {
        uint16_t axis=(uint16_t)sample->sticks[i];
        report[3+2*i]=(uint8_t)axis; report[4+2*i]=(uint8_t)(axis>>8);
    }
    report[11]=sample->pressure[6]; report[12]=sample->pressure[7];
}
int xwn_xid_config(const uint8_t *b,unsigned n,uint8_t *endpoint)
{
    if(!b || !endpoint || n!=32) return 0;
    if(b[0]!=9 || b[1]!=2 || b[2]!=32 || b[3]!=0 || b[4]!=1 || b[5]!=1) return 0;
    if(b[9]!=9 || b[10]!=4 || b[11]!=0 || b[12]!=0 || b[13]!=2 ||
       b[14]!=0x58 || b[15]!=0x42 || b[16]!=0) return 0;
    if(b[18]!=7 || b[19]!=5 || (b[20]!=0x81 && b[20]!=0x82) ||
       b[21]!=3 || b[22]!=32 || b[23]!=0 || b[24]!=4) return 0;
    if(b[25]!=7 || b[26]!=5 || b[27]!=2 || b[28]!=3 || b[29]!=32 ||
       b[30]!=0 || b[31]!=4) return 0;
    *endpoint=b[20]; return 1;
}
int xwn_xid_descriptor(const uint8_t *b,unsigned n)
{
    unsigned i;
    const uint8_t prefix[]={16,0x42,0,1,1,1,20,6};
    if(!b || n!=16) return 0;
    for(i=0;i<8;i++) if(b[i]!=prefix[i]) return 0;
    for(i=8;i<16;i++) if(b[i]!=255) return 0;
    return 1;
}

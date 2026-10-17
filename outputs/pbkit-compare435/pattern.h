/* SPDX-License-Identifier: MIT */
#ifndef FIELD428_PATTERN_H
#define FIELD428_PATTERN_H
#define FW 1024u
#define FH 512u
static unsigned field_pixel(unsigned x,unsigned y,unsigned phase)
{
    unsigned row=y+(phase==1);
    if(x<320) return (row&1)?0xffffffu:0;
    if(x<640) return ((row/2)&1)?0xffffffu:0;
    /* Each scanline has a unique ten-bit binary label, with RGB parity marks. */
    if(x<960) return ((row>>( (x-640)/32))&1)?0xffffffu:0;
    return (row&1)?0x00ff00u:0xff00ffu;
}
#endif

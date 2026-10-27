/* SPDX-License-Identifier: GPL-2.0-or-later
 * Success indication only: caller has completed native read preflight.
 * Two bounded SMC byte writes. No reset, retry or inherited-status clearing.
 */
#include <stdint.h>
#include "xcal_bus.h"
static uint16_t r16(uint16_t p)
{uint16_t v;__asm__ volatile("inw %w1,%0":"=a"(v):"d"(p):"memory");return v;}
static uint8_t r8(uint16_t p)
{uint8_t v;__asm__ volatile("inb %w1,%0":"=a"(v):"d"(p):"memory");return v;}
static void w16(uint16_t p,uint16_t v)
{__asm__ volatile("outw %0,%w1"::"a"(v),"d"(p):"memory");}
static void w8(uint16_t p,uint8_t v)
{__asm__ volatile("outb %0,%w1"::"a"(v),"d"(p):"memory");}
static int write_led(uint8_t reg,uint8_t value)
{
    uint16_t status=r16(0xc000);
    if(status&0x800)return XCAL_BUSY;
    if(status&0x36)return XCAL_DIRTY_STATUS;
    w8(0xc004,0x20);w8(0xc008,reg);w16(0xc006,value);w8(0xc002,0x1a);
    for(unsigned i=0;i<100000;++i){
        uint8_t s=r8(0xc000)&0x36;
        if(!s)continue;
        w16(0xc000,s);return (s&0x26)?XCAL_BUS_ERROR:XCAL_OK;
    }
    return XCAL_TIMEOUT;
}
int XcalIndicate689(volatile uint32_t *progress)
{
    uint32_t flags;__asm__ volatile("pushfl;popl %0":"=r"(flags)::"memory");
    progress[0]=0;progress[1]=0;progress[2]=0;
    if(flags&0x200){progress[2]=1001;return 0;}
    ++progress[0];int e=write_led(8,0x5f); /* green/amber alternating */
    if(e){progress[2]=e;return 0;}
    ++progress[1];++progress[0];e=write_led(7,1);
    if(e){progress[2]=e;return 0;}
    ++progress[1];return 1;
}

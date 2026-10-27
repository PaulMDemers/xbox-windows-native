/* SPDX-License-Identifier: GPL-2.0-or-later
 * HOST-ONLY native I/O binding candidate. No physical admission is implied.
 * Caller must own SMBus exclusively after a validated firmware handoff, confirm
 * this controller/clock mapping and remain with IF clear for the entire call.
 * This file never disables interrupts or clears inherited pending status.
 */
#include "xcal_bus.h"
#include "profile.h"
#define XCAL_NATIVE_CONTEXT 1001
static unsigned flags(void)
{ unsigned v; __asm__ volatile("pushfl; popl %0":"=r"(v));return v; }
static uint8_t r8(void *p,unsigned o)
{ uint8_t v;(void)p;__asm__ volatile("inb %w1,%0":"=a"(v):"d"((uint16_t)(0xc000+o)):"memory");return v; }
static uint16_t r16(void *p,unsigned o)
{ uint16_t v;(void)p;__asm__ volatile("inw %w1,%0":"=a"(v):"d"((uint16_t)(0xc000+o)):"memory");return v; }
static void w8(void *p,unsigned o,uint8_t v)
{ (void)p;__asm__ volatile("outb %0,%w1"::"a"(v),"d"((uint16_t)(0xc000+o)):"memory"); }
static void w16(void *p,unsigned o,uint16_t v)
{ (void)p;__asm__ volatile("outw %0,%w1"::"a"(v),"d"((uint16_t)(0xc000+o)):"memory"); }
static uint32_t pm(void *p)
{ uint32_t v;(void)p;__asm__ volatile("inl %w1,%0":"=a"(v):"d"((uint16_t)0x8008):"memory");return v; }
/* Fixed poll budget bounds CPU reads, not elapsed wall time. */
static const struct xcal_bus bus={0,r8,r16,w8,w16,100000};
int native_read(uint8_t reg,uint32_t *value,struct xcal_trace *trace)
{
    if(flags()&0x200) return XCAL_NATIVE_CONTEXT;
    return xcal_read32(&bus,reg,value,trace);
}
int native_write(uint8_t reg,uint32_t value,struct xcal_trace *trace)
{
    if(flags()&0x200) return XCAL_NATIVE_CONTEXT;
    return xcal_write32(&bus,reg,value,trace);
}
/* Nonzero enum result is failure. Caller supplies the retained observation. */
int native_delay(struct delay_observation *o,unsigned clock_qualified)
{
    if(flags()&0x200) return XCAL_NATIVE_CONTEXT;
    return delay500_candidate(pm,0,clock_qualified,o);
}

int native_profile(const struct xcal_request *r,struct xcal_progress *p)
{
 if(flags()&0x200)return XCAL_NATIVE_CONTEXT;
 return xcal_program700(&bus,r,pm,0,p);
}

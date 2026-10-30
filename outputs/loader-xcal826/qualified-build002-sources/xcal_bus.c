/* SPDX-License-Identifier: GPL-2.0-or-later
 * Based on authored681 block helper; status definitions reviewed against
 * Linux i2c-amd756.c (nForce supported), pinned in references001.json.
 * No Linux abort/reset/retry or inherited-status clearing is imported.
 */
#include "xcal_bus.h"
#define BUSY 0x0808u
#define TERMINAL 0x0037u
#define ERROR 0x0027u
static int transfer(const struct xcal_bus *b,uint8_t reg,uint32_t *value,
                    int read,struct xcal_trace *t)
{
    if(!b || !value || !t || !b->r8 || !b->r16 || !b->w8 || !b->w16 ||
       !b->poll_limit || b->poll_limit>1000000) return XCAL_ARGUMENT;
    *t=(struct xcal_trace){0xffff,0xffff,0xffff,0xffff,0,0};
    t->entry=b->r16(b->ctx,0);
    if(t->entry&BUSY) return XCAL_BUSY;
    if(t->entry&TERMINAL) return XCAL_DIRTY_STATUS;
    b->w8(b->ctx,4,(uint8_t)(0xe0+read));
    b->w8(b->ctx,8,reg);
    if(!read) {
        for(unsigned i=0;i<4;++i)b->w8(b->ctx,9,(uint8_t)(*value>>(8*i)));
        b->w16(b->ctx,6,4);
    }
    /* Direction is encoded in address bit0. Block type5 + start8;
     * do not inherit the legacy write's unexplained extra control bit0x10. */
    b->w8(b->ctx,2,0x0d);
    for(unsigned i=0;i<b->poll_limit;++i) {
        t->last=b->r16(b->ctx,0);++t->polls;
        /* A terminal flag while host/bus still active is not consumable.
         * Wait within the same finite budget; never acknowledge while busy. */
        if((t->last&BUSY) || !(t->last&TERMINAL))continue;
        int result=(t->last&ERROR)?XCAL_BUS_ERROR:XCAL_OK;
        uint32_t received=0;
        if(result==XCAL_OK && read) {
            t->length=b->r16(b->ctx,6);
            if(t->length!=4)result=XCAL_BLOCK_LENGTH;
            else for(unsigned j=0;j<4;++j)received|=(uint32_t)b->r8(b->ctx,9)<<(8*j);
        }
        t->ack=t->last&TERMINAL;
        b->w16(b->ctx,0,(uint16_t)t->ack);
        t->final=b->r16(b->ctx,0);
        if(t->final&(BUSY|TERMINAL))return XCAL_FINAL_STATUS;
        if(result==XCAL_OK && read)*value=received;
        return result;
    }
    t->final=b->r16(b->ctx,0); /* diagnostic only; no late ack/retry */
    return XCAL_TIMEOUT;
}
int xcal_read32(const struct xcal_bus *b,uint8_t r,uint32_t *v,struct xcal_trace *t)
{return transfer(b,r,v,1,t);}
int xcal_write32(const struct xcal_bus *b,uint8_t r,uint32_t v,struct xcal_trace *t)
{return transfer(b,r,&v,0,t);}

/* SPDX-License-Identifier: GPL-2.0-or-later
 * Bounded byte reads for the native video admission path only.
 * Do not acknowledge status belonging to an earlier/unknown transaction.
 */
#include "xcal_bus.h"
int xcal_config_read(const struct xcal_bus *b,uint8_t address,uint8_t reg,uint8_t *value)
{
    int allowed=(address==0x10 && reg==4) ||
                (address==0x54 && ((reg>=0x58 && reg<=0x5b) || reg==0x96));
    if(!allowed || !value || !b || !b->r8 || !b->r16 || !b->w8 || !b->w16 ||
       !b->poll_limit || b->poll_limit>1000000) return XCAL_ARGUMENT;
    uint16_t entry=b->r16(b->ctx,0);
    if(entry&0x0800) return XCAL_BUSY;
    if(entry&0x0036) return XCAL_DIRTY_STATUS;
    b->w8(b->ctx,4,(uint8_t)((address<<1)|1));
    b->w8(b->ctx,8,reg);
    b->w8(b->ctx,2,0x0a);
    for(unsigned i=0;i<b->poll_limit;++i) {
        uint8_t status=b->r8(b->ctx,0)&0x36;
        if(!status) continue;
        int error=(status&0x26)?XCAL_BUS_ERROR:XCAL_OK;
        uint8_t data=0;
        if(!error) data=b->r8(b->ctx,6);
        b->w16(b->ctx,0,status);
        if(!error) *value=data;
        return error;
    }
    return XCAL_TIMEOUT;
}

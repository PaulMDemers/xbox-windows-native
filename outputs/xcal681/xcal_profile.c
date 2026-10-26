/* SPDX-License-Identifier: GPL-2.0-or-later
 * Retains legacy reset/table order. Hardware qualification remains pending.
 */
#include "xcal_profile.h"
#include "xcal_table.h"
static uint32_t swap(uint32_t n)
{ return (n>>24) | ((n>>8)&0xff00) | ((n<<8)&0xff0000) | (n<<24); }
static int transfer(const struct xcal_bus *b, struct xcal_progress *p,
                    unsigned reg, uint32_t value, int read)
{
    ++p->attempted;
    p->error = read ? xcal_read32(b,(uint8_t)reg,&value) : xcal_write32(b,(uint8_t)reg,value);
    if (p->error) return 0;
    ++p->completed; return 1;
}
int xcal_program_table(const struct xcal_bus *b, const struct xcal_request *r,
                      int (*pause500)(void *), void *context, struct xcal_progress *p)
{
    if (!p) return 0;
    *p = (struct xcal_progress){0};
    if (!b || !r || !pause500 || r->mode != 3 || r->confirmed_xcalibur != 1 ||
        r->cable != 3 || !(r->flags & 8) || r->ram != (64u<<20) ||
        r->fb != (55u<<20) || r->reserved != (9u<<20) || r->hidden != 316160) return 0;
    p->phase = 1;
    /* Read completion validates the protocol response, not a chip ID.
     * Values are not borrowed to program another device. */
    if (!transfer(b,p,4,0,1) || !transfer(b,p,4,0x0f000000,0) ||
        !transfer(b,p,0,0,1) || !transfer(b,p,0,0,0)) return -1;
    p->phase = 2;
    for (unsigned reg=0; reg<144; ++reg) {
        if (!transfer(b,p,reg,swap(xcal_table[reg]),0)) return -1;
        ++p->table_completed;
        if (!pause500(context)) { p->error=100; return -1; }
        ++p->delay_completed;
    }
    p->phase=3;
    return 1;
}

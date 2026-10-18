/* SPDX-License-Identifier: MIT */
#include "engine.h"
#include <string.h>
static void le32(unsigned char *p, uint32_t v)
{
    for (unsigned i=0;i<4;++i) p[i]=(unsigned char)(v>>(i*8));
}
void receipt527(unsigned char out[48], unsigned stage, const uint16_t kernel[4])
{
    memset(out,0,48);
    memcpy(out,"X527",4);
    le32(out+4,1); le32(out+8,48); le32(out+12,527); le32(out+16,stage);
    for (unsigned i=0;i<4;++i) le32(out+20+4*i,kernel[i]);
    le32(out+36,stage==2 ? 1 : 0);
    uint32_t h=2166136261u;
    for (unsigned i=0;i<44;++i) h=(h^out[i])*16777619u;
    le32(out+44,h);
}
static int store(const struct io527 *io, unsigned stage, const unsigned char data[48])
{
    size_t n=0;
    unsigned char back[49];
    if (!io->open(io->ctx,stage,1)) return 0;
    int ok=io->write(io->ctx,data,48,&n) && n==48;
    if (ok) ok=io->flush(io->ctx);
    /* Once acquired, close exactly once even on a failed write or flush. */
    if (!io->close(io->ctx)) ok=0;
    if (!ok) return 0;
    if (!io->open(io->ctx,stage,0)) return 0;
    n=0;
    ok=io->read(io->ctx,back,sizeof(back),&n) && n==48 && !memcmp(data,back,48);
    if (!io->close(io->ctx)) ok=0;
    return ok;
}
int run527(const struct io527 *io, const uint16_t kernel[4])
{
    unsigned char data[48];
    for (unsigned stage=1;stage<=2;++stage) {
        receipt527(data,stage,kernel);
        if (!store(io,stage,data)) return 0;
    }
    return 1;
}

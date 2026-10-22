/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "packet.h"
static void word(uint8_t *p, uint32_t v) {
    unsigned i; for (i=0;i<4;i++) p[i]=(uint8_t)(v>>(8*i));
}
static int nonzero(const uint8_t *p, unsigned n) {
    unsigned i; uint8_t v=0; for(i=0;i<n;i++) v|=p[i]; return v!=0;
}
static uint32_t crc(const uint8_t *p, unsigned n) {
    uint32_t v=0xffffffffu; unsigned i,b;
    for(i=0;i<n;i++) { v^=p[i]; for(b=0;b<8;b++)
        v=(v>>1)^((0u-(v&1u))&0xedb88320u); }
    return v^0xffffffffu;
}
static void words(uint8_t *p, const uint32_t *v, unsigned n) {
    unsigned i; for(i=0;i<n;i++) word(p+4*i,v[i]);
}
int xwn655_encode(const struct xwn655_identity *id, const struct xwn652_data *d,
                  uint8_t *out, size_t capacity) {
    static const uint8_t magic[8]={'X','W','N','6','5','5','U','1'};
    unsigned i;
    if(!id || !d || !out || capacity<XWN655_BYTES ||
       !nonzero(id->attempt,16) || !nonzero(id->build_id,32) ||
       d->result < -1 || d->result > 1 ||
       (d->post_kind!=1 && d->post_kind!=2)) return -1;
    for(i=0;i<8;i++) out[i]=magic[i];
    word(out+8,1); word(out+12,XWN655_BYTES);
    for(i=0;i<16;i++) out[16+i]=id->attempt[i];
    for(i=0;i<32;i++) out[32+i]=id->build_id[i];
    word(out+64,(uint32_t)d->result); word(out+68,d->post_kind);
    words(out+72,d->request,8); words(out+104,d->state,9);
    words(out+140,d->trace,63); words(out+392,d->pre,47);
    words(out+580,d->post,47); word(out+768,crc(out,768));
    return 0;
}

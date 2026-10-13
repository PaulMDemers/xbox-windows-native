#ifndef XWN_LARGE327_ORACLE_H
#define XWN_LARGE327_ORACLE_H
#include <stdint.h>
static inline int lg_layout(uint32_t w,uint32_t h,uint32_t *cw,uint32_t *ch,uint32_t *bytes) {
    if(!((w==256&&h==128)||(w==640&&h==360)||(w==960&&h==540)))return 0;
    *cw=w+48;*ch=h+48;*bytes=(*cw)*(*ch)*4;return 1;
}
static inline uint32_t lg_pixel(uint32_t x,uint32_t y) {
    return 0xa5000000u|(((x*13u+y*3u+17u)&255u)<<16)|
           (((x*5u+y*11u+29u)&255u)<<8)|((x*7u+y*19u+43u)&255u);
}
static inline uint32_t lg_expected(uint32_t kind,uint32_t count,uint32_t w,uint32_t h,uint32_t x,uint32_t y) {
    if(kind==0&&count&&x>=16&&x<16+w&&y>=16&&y<16+h)
        return ((count-1)&1)?0:0xffffffu;
    if(kind==2) {
        while(count&&x>=32&&x<32+w&&y>=32&&y<32+h){x-=16;y-=16;--count;}
    } else if(kind==3) {
        while(count&&x>=16&&x<16+w&&y>=16&&y<16+h){x+=16;y+=16;--count;}
    }
    return lg_pixel(x,y)&0xffffffu;
}
#endif

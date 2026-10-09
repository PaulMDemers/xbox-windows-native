/* Exact scalar-word scanout sequence; no cache/FPU/GPU state changes.
 * Caller supplies valid mapped spans; alignment/alias guards choose old copy.
 * SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_ROW_STORE_H
#define XWN_ROW_STORE_H
typedef unsigned int XW_U32;
typedef __UINTPTR_TYPE__ XW_PTR;
typedef unsigned long long XW_U64;
typedef char XW_WIDTH_CHECK[(sizeof(XW_U32)==4 && sizeof(XW_PTR)==sizeof(void*))?1:-1];
static __inline int XwEligible(XW_PTR d,XW_PTR s,unsigned bytes)
{
    XW_PTR endd,ends;
    if(!bytes || ((d|s|bytes)&3))return 0;
    endd=d+bytes;ends=s+bytes;
    if(endd<d || ends<s)return 0;
    return !(d<ends && s<endd);
}
static __inline XW_U32 XwLoad(const unsigned char *source)
{
    XW_U32 word;
    /* Explicit builtin avoids type-punning a GDI byte buffer; compiled NT5
     * review must show integer loads/stores, no helper/FPU/vector sequence. */
    __builtin_memcpy(&word,source,4);
    return word;
}
static __inline unsigned XwCopyRow(void *target,const void *source,
                                   unsigned bytes,int enabled)
{
    volatile XW_U32 *d;const unsigned char *s;unsigned words;
    if(!enabled || !XwEligible((XW_PTR)target,(XW_PTR)source,bytes)) {
        memmove(target,source,bytes);return 0;
    }
    d=(volatile XW_U32*)target;s=(const unsigned char*)source;words=bytes/4;
    /* Ordered full-expression volatile32bit stores match the old forward
     * word copy's store width. Never emit wider writes or cross row bounds. */
    while(words>=8) {
        d[0]=XwLoad(s);d[1]=XwLoad(s+4);d[2]=XwLoad(s+8);d[3]=XwLoad(s+12);
        d[4]=XwLoad(s+16);d[5]=XwLoad(s+20);d[6]=XwLoad(s+24);d[7]=XwLoad(s+28);
        d+=8;s+=32;words-=8;
    }
    while(words){*d++=XwLoad(s);s+=4;--words;}
    return 1;
}
#endif

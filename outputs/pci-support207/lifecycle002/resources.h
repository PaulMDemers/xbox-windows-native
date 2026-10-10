/* SPDX-License-Identifier: MIT
 * Observed NT5/x86 resource profiles only. No hardware access or allocation.
 * C200 is preserved, not probed or assigned a guessed controller role.
 */
#ifndef XWN_RESOURCES_OWNERSHIP001_H
#define XWN_RESOURCES_OWNERSHIP001_H
enum { XWN_PROFILE_NONE, XWN_PROFILE_PHYSICAL, XWN_PROFILE_XEMU };
static unsigned xwn_r32(const unsigned char *p)
{ return (unsigned)p[0]|((unsigned)p[1]<<8)|((unsigned)p[2]<<16)|((unsigned)p[3]<<24); }
static void xwn_w32(unsigned char *p,unsigned v)
{ unsigned i;for(i=0;i<4;++i)p[i]=(unsigned char)(v>>(i*8)); }
static int xwn_zero(const unsigned char *p,unsigned size)
{ unsigned i;for(i=0;i<size;++i)if(p[i])return 0;return 1; }
static int xwn_tag(const unsigned char *d,unsigned bar)
{
    return xwn_r32(d)==0x00018100 && !xwn_r32(d+4) &&
           xwn_r32(d+8)==1 && xwn_r32(d+12)==bar && xwn_zero(d+16,16);
}
static int xwn_port_requirement(const unsigned char *d,unsigned option,
                                unsigned length,unsigned base)
{
    unsigned alignment=xwn_r32(d+12), end=base+length-1;
    return xwn_r32(d)==(0x00010100|option) && xwn_r32(d+4)==0x31 &&
           xwn_r32(d+8)==length && alignment && !(alignment&(alignment-1)) &&
           !(base&(alignment-1)) && !xwn_r32(d+20) && xwn_r32(d+16)<=base &&
           (xwn_r32(d+28) || xwn_r32(d+24)>=end);
}
/* Validate every alternative before editing. Failed calls leave p/profile exact.
 * The caller supplies a real buffer size, bounded by the OS allocation contract.
 * Preserve descriptor order, BAR0, interrupt and every private tag byte.
 */
static int xwn_pin_resources(unsigned char *p,unsigned size,unsigned *profile)
{
    unsigned pass,offset,list,alternatives,kind=0;
    if(!p || !profile || size<40 || size>131232 || xwn_r32(p)!=size ||
       xwn_r32(p+4)!=5 || xwn_r32(p+8) || xwn_r32(p+12)!=0x21 ||
       !xwn_zero(p+16,12))return 1;
    alternatives=xwn_r32(p+28);if(!alternatives || alternatives>16)return 1;
    for(pass=0;pass<2;++pass) {
        offset=32;
        for(list=0;list<alternatives;++list) {
            unsigned count,here,first,i;unsigned char *d;
            if(offset>size-8 || xwn_r32(p+offset)!=0x00010001)return 1;
            count=xwn_r32(p+offset+4);
            if(count>(size-offset-8)/32 || (count!=3 && count!=9))return 1;
            here=count==9 ? XWN_PROFILE_PHYSICAL : XWN_PROFILE_XEMU;
            if(kind && kind!=here)return 2;
            kind=here;d=p+offset+8;first=here==XWN_PROFILE_PHYSICAL ? 2 : 0;
            if(here==XWN_PROFILE_PHYSICAL) {
                /* BAR0 is unrelated to the two observed boot ranges. Retain it. */
                if(xwn_r32(d)!=0x00010100 || xwn_r32(d+4)!=0x31 ||
                   xwn_r32(d+8)!=16 || !xwn_tag(d+32,0) || !xwn_tag(d+7*32,2))return 2;
                if(xwn_r32(d+8*32)!=0x00030200 || xwn_r32(d+8*32+4) ||
                   !xwn_zero(d+8*32+16,16))return 2;
            }
            if(!xwn_tag(d+(first+2)*32,1))return 2;
            for(i=0;i<(here==XWN_PROFILE_PHYSICAL ? 4U : 2U);++i) {
                unsigned index=first+i+(i>=2), base=i<2 ? 0xc000 : 0xc200;
                unsigned length=here==XWN_PROFILE_PHYSICAL && i<2 ? 16 : 32;
                unsigned char *port=d+index*32;
                if(!xwn_port_requirement(port,(i&1) ? 8 : 1,length,base))return 3;
                if(pass) {
                    xwn_w32(port+12,1);xwn_w32(port+16,base);xwn_w32(port+20,0);
                    xwn_w32(port+24,base+length-1);xwn_w32(port+28,0);
                }
            }
            offset+=8+count*32;
        }
        if(offset!=size)return 1;
    }
    *profile=kind;return 0;
}
/* Exact port coverage in a counted NT5 x86 CM_RESOURCE_LIST. Ignore only
 * interrupts/private descriptors, never an unexpected port/memory range.
 * No assumption that a single C000 range establishes the physical profile.
 */
static int xwn_check_resources(const unsigned char *p,unsigned size,unsigned profile)
{
    unsigned count,i,primary=0,secondary=0,bar0=0;
    if(!p || size<20 || xwn_r32(p)!=1 || xwn_r32(p+4)!=5 || xwn_r32(p+8) ||
       xwn_r32(p+12)!=0x00010001 ||
       (profile!=XWN_PROFILE_PHYSICAL && profile!=XWN_PROFILE_XEMU))return 1;
    count=xwn_r32(p+16);
    if(!count || count>16 || count!=(size-20)/16 || (size-20)%16)return 1;
    for(i=0;i<count;++i) {
        const unsigned char *d=p+20+16*i;
        if(d[0]==1) {
            unsigned base=xwn_r32(d+4),length=xwn_r32(d+12);
            if(d[2]!=1 || d[3] || xwn_r32(d+8))return 2;
            if(base==0xc000 && length==(profile==XWN_PROFILE_PHYSICAL ? 16U : 32U))++primary;
            else if(profile==XWN_PROFILE_PHYSICAL && base==0xc200 && length==32)++secondary;
            /* Physical BAR0 may acquire a separate 16-byte port. Reject overlap. */
            else if(profile!=XWN_PROFILE_PHYSICAL || length!=16 || base>0xfff0 ||
                    (base<=0xc00f && base+15>=0xc000) ||
                    (base<=0xc21f && base+15>=0xc200) || ++bar0>1)return 2;
        } else if(d[0]!=2 && d[0]!=0x81)return 2;
    }
    return primary==1 && secondary==(profile==XWN_PROFILE_PHYSICAL ? 1U : 0U) ? 0 : 3;
}
#endif

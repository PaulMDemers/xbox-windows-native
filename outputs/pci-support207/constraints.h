/* SPDX-License-Identifier: MIT
 * Restrict the observed NT5 PCI BAR1 requirement group to C000 before allocation.
 * Exact NT5 x86 layouts/private PCI tags only. No allocations or direct PCI writes.
 */
#ifndef XWN_CONSTRAINTS207_H
#define XWN_CONSTRAINTS207_H
static unsigned xwn_get32(const unsigned char *p)
{ return (unsigned)p[0]|((unsigned)p[1]<<8)|((unsigned)p[2]<<16)|((unsigned)p[3]<<24); }
static void xwn_put32(unsigned char *p,unsigned v)
{ unsigned i;for(i=0;i<4;++i)p[i]=(unsigned char)(v>>(8*i)); }
/* Fail without changing any byte. The source is an OS-owned buffer of size bytes. */
static int xwn_pin_requirements(unsigned char *p,unsigned size)
{
    unsigned pass,offset,alternatives,list;
    if(!p || size<40 || size>131232 || xwn_get32(p)!=size || xwn_get32(p+4)!=5 || xwn_get32(p+8)!=0 || xwn_get32(p+12)!=0x21) return 1;
    alternatives=xwn_get32(p+28); if(!alternatives || alternatives>16) return 1;
    for(pass=0;pass<2;++pass) {
        offset=32;
        for(list=0;list<alternatives;++list) {
            unsigned count,i,group=0,found=0;
            if(offset>size-8) return 1;
            count=xwn_get32(p+offset+4);
            if(!count || count>256 || count>(size-offset-8)/32) return 1;
            for(i=0;i<count;++i) {
                unsigned char *d=p+offset+8+i*32;
                if(d[1]==0x81) {
                    if(xwn_get32(d+8)==1 && xwn_get32(d+12)==1 && xwn_get32(d+16)==0) {
                        unsigned j;
                        if(++found!=1 || group==i) return 2;
                        for(j=group;j<i;++j) {
                            unsigned char *port=p+offset+8+j*32;
                            unsigned length=xwn_get32(port+8),end=0xc000+length-1;
                            if(port[1]!=1 || !(port[4]&1) || (length!=16 && length!=32) ||
                               xwn_get32(port+20)!=0 || xwn_get32(port+16)>0xc000 ||
                               (xwn_get32(port+28)==0 && xwn_get32(port+24)<end)) return 3;
                            if(pass) {
                                xwn_put32(port+12,1); /* alignment */
                                xwn_put32(port+16,0xc000);xwn_put32(port+20,0);
                                xwn_put32(port+24,end);xwn_put32(port+28,0);
                            }
                        }
                    }
                    group=i+1;
                }
            }
            if(found!=1) return 2;
            offset+=8+count*32;
        }
        if(offset!=size) return 1;
    }
    return 0;
}
#endif

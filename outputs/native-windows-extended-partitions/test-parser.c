#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "xboxpart.h"

static unsigned char table[512], saved[512];
static const unsigned int starts[] = {5633024,4609024,1024,1537024,3073024,15633072};
static const unsigned int counts[] = {10000048,1024000,1536000,1536000,1536000,472764096};
static void put(unsigned int at, unsigned int value)
{
    unsigned int i;
    for (i=0;i<4;i++) table[at+i]=(unsigned char)(value>>(i*8));
}
static int parse(unsigned int bytes, unsigned long long capacity)
{
    XWN_XBOX_PARTITION parts[14]; unsigned int count=99, i,j;
    int result=XwnXboxParsePartitionTable(table,bytes,capacity,parts,&count);
    if (result==1) {
        assert(count>=5 && count<=14);
        for(i=0;i<count;i++) {
            assert(parts[i].Count && (unsigned long long)parts[i].Start+parts[i].Count<=capacity);
            for(j=0;j<i;j++) assert((unsigned long long)parts[i].Start+parts[i].Count<=parts[j].Start ||
                                     (unsigned long long)parts[j].Start+parts[j].Count<=parts[i].Start);
        }
    } else assert(count==0);
    return result;
}
int main(void)
{
    unsigned int i, state=0x12345678;
    memcpy(table,"****PARTINFO****",16);
    for(i=0;i<6;i++) {put(48+i*32+16,0x80000000U);put(48+i*32+20,starts[i]);put(48+i*32+24,counts[i]);}
    memcpy(saved,table,512);
    assert(parse(512,488397168)==1);
    assert(parse(512,488397167)==-1); /* exact disk end, no CHS rounding */
    assert(parse(512,0)==-1);
    assert(parse(511,488397168)==-1);
    assert(parse(513,488397168)==-1);
    memset(table,0,512); assert(parse(512,488397168)==0);
    memcpy(table,saved,512); table[16]=1; assert(parse(512,488397168)==-1);
    memcpy(table,saved,512); put(48+5*32+20,5633024); assert(parse(512,488397168)==-1);
    memcpy(table,saved,512); put(48+24,0x98f800); assert(parse(512,488397168)==-1); /* legacy E/F overlap */
    memcpy(table,saved,512); put(48+5*32+24,0); assert(parse(512,488397168)==-1);
    memcpy(table,saved,512); put(48+5*32+20,0xfffffff0U);put(48+5*32+24,0x100);assert(parse(512,0xffffffffULL)==-1);
    memcpy(table,saved,512);put(48+4*32+16,0);assert(parse(512,488397168)==-1);
    memcpy(table,saved,512);put(48+5*32+28,1);assert(parse(512,488397168)==-1);
    memcpy(table,saved,512);put(48+5*32+16,0x80000001U);assert(parse(512,488397168)==-1);
    for(i=0;i<30000;i++) {
        memcpy(table,saved,512);
        state=state*1664525U+1013904223U;
        table[state%512]^=(unsigned char)((state>>16)|1);
        parse(512,488397168);
    }
    puts("Valid 250 GB table accepted; boundary/overlap/overflow/extension cases rejected; 30000 mutations checked.");
    return 0;
}

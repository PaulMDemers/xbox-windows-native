#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "pattern.h"
#define VIDEO_ADAPTER_MASK 255u
#define VIDEO_STANDARD_MASK 65280u
#define AV_PACK_HDTV 4u
#define VIDEO_MODE_720P 0x20000u
static int actual(uint32_t settings, int memory_status, uint32_t pages) {
unsigned standard = settings & VIDEO_STANDARD_MASK;
struct { uint32_t TotalPhysicalPages; } memory = {pages};
return (settings & VIDEO_ADAPTER_MASK) == AV_PACK_HDTV &&
                   (settings & VIDEO_MODE_720P) && (standard == 0x100 || standard == 0x200) &&
                   memory_status == 0 && memory.TotalPhysicalPages == 16384;
}
int main(void) {
unsigned count=0;
for(unsigned pack=0;pack<256;pack++)for(unsigned standard=0;standard<256;standard++)for(unsigned flags=0;flags<16;flags++){
uint32_t settings=pack+(standard<<8)+(flags<<16);
assert(actual(settings,0,16384)==(pack==4 && (standard==1 || standard==2) && (flags&2)));
assert(!actual(settings,-1,16384));assert(!actual(settings,0,32768));count+=3;
}
uint32_t *storage=calloc(1280*720+2,sizeof(uint32_t));assert(storage);storage[0]=0xdeadbeef;storage[1280*720+1]=0xfacefeed;uint32_t *fb=storage+1;
    for (unsigned y = 0; y < 720; ++y)
        for (unsigned x = 0; x < 1280; ++x) fb[y * 1280 + x] = baseline_pixel(x,y,1280,720);
assert(storage[0]==0xdeadbeef && storage[1280*720+1]==0xfacefeed);
assert(fb[100*1280+80]==0xff0000 && fb[100*1280+240]==0x00ff00 && fb[100*1280+400]==0x0000ff);
assert(fb[0]==0xffffff && fb[1280*720-1]==0xffffff);free(storage);
printf("PASS %u admission assertions and extracted1280x720 pattern loop bounds\n",count);
}
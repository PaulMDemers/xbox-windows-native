#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#define VIDEO_ADAPTER_MASK 255u
#define VIDEO_STANDARD_MASK 65280u
#define AV_PACK_STANDARD 1u
static int actual(uint32_t settings, int memory_status, uint32_t pages) {
unsigned standard = settings & VIDEO_STANDARD_MASK;
struct { uint32_t TotalPhysicalPages; } memory = {pages};
return (settings & VIDEO_ADAPTER_MASK) == AV_PACK_STANDARD && (standard == 0x100 || standard == 0x200) &&
                   memory_status == 0 && memory.TotalPhysicalPages == 16384;
}
int main(void) {
unsigned count=0;
for(unsigned pack=0;pack<256;pack++)for(unsigned standard=0;standard<256;standard++)for(unsigned flags=0;flags<16;flags++){
uint32_t settings=pack+(standard<<8)+(flags<<16);
assert(actual(settings,0,16384)==(pack==1 && (standard==1 || standard==2)));
assert(!actual(settings,-1,16384));assert(!actual(settings,0,32768));count+=3;
}
printf("PASS %u admission assertions\n",count);
}
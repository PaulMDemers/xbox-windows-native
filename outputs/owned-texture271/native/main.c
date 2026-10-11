/* Standalone nxdk texture control, not a Windows driver or ownership handoff.
 * Draw setup follows the installed nxdk MIT-licensed triangle/mesh samples.
 * pbkit creates the application's own objects before the observed interval.
 * No disk/network writes, host acknowledgments via guest memory, or GPU resets
 * occur during the two measurements. All allocations remain held until halt.
 */
#include <hal/video.h>
#include <pbkit/pbkit.h>
#include <xboxkrnl/xboxkrnl.h>
#include <windows.h>
#include <stdint.h>
#include <string.h>
#include <strings.h>
#define W 16u
#define H 8u
#define BLOCK 4096u
#define PAYLOAD 256u
#define MASK(mask,val) (((val) << (ffs(mask)-1)) & (mask))
#define CLEAR 0xff0c0c0cu
typedef struct {float pos[4],uv[4];} Vertex;
typedef struct {
    uint32_t magic,version,bytes,phase,error,cookie;
    uint32_t allocation[4],physical[4],texture[4],texture_physical[4];
    uint32_t width,height,pitch,block_size,payload_offset;
    uint32_t target,target_physical,target_pitch,target_height,vertices,vertices_bytes,vertices_physical;
    uint32_t waits,elapsed[4],source_errors[2],pixel_errors[2];
    uint32_t pixels[2][(W+2)*(H+2)];
} Record;
volatile Record record271;
static unsigned char *blocks[4];
static Vertex *vertices;
static DWORD *frame;
_Static_assert(sizeof(DWORD)==4,"Framebuffer pixels require32-bit DWORD");
static const Vertex quad[12]={
    {{32,32,0.1f,1},{0,0,0,1}},{{48,32,0.1f,1},{16,0,0,1}},{{48,40,0.1f,1},{16,8,0,1}},
    {{32,32,0.1f,1},{0,0,0,1}},{{48,40,0.1f,1},{16,8,0,1}},{{32,40,0.1f,1},{0,8,0,1}},
    {{80,80,0.1f,1},{0,0,0,1}},{{96,80,0.1f,1},{16,0,0,1}},{{96,88,0.1f,1},{16,8,0,1}},
    {{80,80,0.1f,1},{0,0,0,1}},{{96,88,0.1f,1},{16,8,0,1}},{{80,88,0.1f,1},{0,8,0,1}}
};
__attribute__((noinline)) void checkpoint271(unsigned phase,volatile Record *r,unsigned cookie)
{
    __asm__ __volatile__("" ::: "memory");
    r->phase=phase;r->cookie=cookie;
    __asm__ __volatile__("" ::: "memory");
}
static void stop(unsigned error)
{
    record271.error=error;
    checkpoint271(error?0xff:33,&record271,0x271c0deu);
    Sleep(15000); /* bounded capture window, followed by guest halt, never reboot */
    HalReturnToFirmware(HalHaltRoutine);
}
static bool idle(unsigned index)
{
    uint32_t *p=pb_begin();
    p=pb_push1(p,NV20_TCL_PRIMITIVE_3D_ASK_FOR_IDLE,0);
    p=pb_push1(p,NV20_TCL_PRIMITIVE_3D_NOP,0);pb_end(p);
    DWORD begin=GetTickCount();
    while(pb_busy()) {
        if ((DWORD)(GetTickCount()-begin)>10000) return false;
        Sleep(1);
    }
    record271.elapsed[index]=GetTickCount()-begin;record271.waits++;
    return true; /* guest FIFO/status only; host ownership still needs attestation */
}
static uint32_t texel(unsigned u,unsigned x,unsigned y)
{
    unsigned r=0,g=0,b=0;
    if(u==0) r=(x&1)?32:0;
    if(u==1) g=(y&1)?64:0;
    if(u==2) b=((x^y)&1)?128:0;
    if(u==3) r=g=b=(((x>>1)^(y>>1))&1)?16:0;
    return 0xff000000u|(r<<16)|(g<<8)|b;
}
static unsigned char expected_byte(unsigned u,unsigned n)
{
    if(n<PAYLOAD || n>=PAYLOAD+W*H*4) return (unsigned char)(0xa5u^u^(n*13u));
    n-=PAYLOAD;unsigned pixel=n/4;
    return (unsigned char)(texel(u,pixel%W,pixel/W)>>(8*(n%4)));
}
static void sources(unsigned stage)
{
    unsigned errors=0;
    for(unsigned u=0;u<4;u++) for(unsigned n=0;n<BLOCK;n++)
        errors+=blocks[u][n]!=expected_byte(u,n);
    record271.source_errors[stage]=errors;
}
static void capture(unsigned stage)
{
    /* pbkit's explicit linear AGP alias, stable extra-buffer identity. */
    volatile uint32_t *linear=pb_agp_access(frame);
    unsigned stride=record271.target_pitch/4,n=0,errors=0;
    for(unsigned y=31;y<41;y++) for(unsigned x=31;x<49;x++) {
        uint32_t actual=linear[y*stride+x],expected=CLEAR;
        if(x>=32 && x<48 && y>=32 && y<40) {
            unsigned xx=x-32,yy=y-32;
            expected=0xff000000u;
            for(unsigned u=0;u<4;u++) expected+=(texel(u,xx,yy)&0xffffffu);
        }
        record271.pixels[stage][n++]=actual;errors+=actual!=expected;
    }
    record271.pixel_errors[stage]=errors;
}
static void program(bool textured)
{
    uint32_t *p=pb_begin();
    if(textured) {
        #include "ps.inl"
    } else {
        /* flat.inl has no TS program; clear the previous four sample stages. */
        p=pb_push1(p,NV097_SET_SHADER_STAGE_PROGRAM,0);
        p=pb_push1(p,NV097_SET_SHADER_OTHER_STAGE_INPUT,0);
        #include "flat.inl"
    }
    pb_end(p);
}
static void draw(unsigned first)
{
    uint32_t *p=pb_begin();
    p=pb_push1(p,NV097_SET_BEGIN_END,NV097_SET_BEGIN_END_OP_TRIANGLES);
    p=pb_push1(p,0x40000000|NV097_DRAW_ARRAYS,MASK(NV097_DRAW_ARRAYS_COUNT,5)|first);
    p=pb_push1(p,NV097_SET_BEGIN_END,NV097_SET_BEGIN_END_OP_END);pb_end(p);
}
static void enable(bool on)
{
    uint32_t *p=pb_begin();
    for(unsigned u=0;u<4;u++) p=pb_push1(p,NV097_SET_TEXTURE_CONTROL0+u*64,on?NV097_SET_TEXTURE_CONTROL0_ENABLE:0);
    pb_end(p);
}
static bool allocations_valid(void)
{
    uint32_t a[6],n[6];
    for(unsigned i=0;i<4;i++) {a[i]=record271.physical[i];n[i]=BLOCK;}
    a[4]=record271.target_physical;n[4]=record271.target_pitch*record271.target_height;
    a[5]=record271.vertices_physical;n[5]=sizeof(quad);
    for(unsigned i=0;i<6;i++) {
        if(!n[i] || a[i]>MAXRAM || n[i]>MAXRAM-a[i]+1) return false;
        for(unsigned j=0;j<i;j++) if(a[i]<a[j]+n[j] && a[j]<a[i]+n[i]) return false;
    }
    /* Push-buffer/DMA-object ranges require independent live host attestation. */
    for(unsigned i=0;i<4;i++) if(MmGetPhysicalAddress(blocks[i]+BLOCK-1)!=a[i]+BLOCK-1) return false;
    return true;
}
static void setup_draw(void)
{
    const uint32_t vs_program[]={
        #include "vs.inl"
    };
    uint32_t *p=pb_begin();
    p=pb_push1(p,NV097_SET_TRANSFORM_PROGRAM_START,0);
    p=pb_push1(p,NV097_SET_TRANSFORM_EXECUTION_MODE,
        MASK(NV097_SET_TRANSFORM_EXECUTION_MODE_MODE,NV097_SET_TRANSFORM_EXECUTION_MODE_MODE_PROGRAM)|
        MASK(NV097_SET_TRANSFORM_EXECUTION_MODE_RANGE_MODE,NV097_SET_TRANSFORM_EXECUTION_MODE_RANGE_MODE_PRIV));
    p=pb_push1(p,NV097_SET_TRANSFORM_PROGRAM_CXT_WRITE_EN,0);
    p=pb_push1(p,NV097_SET_TRANSFORM_PROGRAM_LOAD,0);pb_end(p);
    for(unsigned i=0;i<sizeof(vs_program)/16;i++) {
        p=pb_begin();pb_push(p++,NV097_SET_TRANSFORM_PROGRAM,4);
        memcpy(p,&vs_program[i*4],16);p+=4;pb_end(p);
    }
    p=pb_begin();
    /* Generated vp20 c[0] is1: explicitly initialize its hardware slot96. */
    p=pb_push1(p,NV097_SET_TRANSFORM_CONSTANT_LOAD,96);
    const float ones[4]={1,1,1,1};
    pb_push(p++,NV097_SET_TRANSFORM_CONSTANT,4);memcpy(p,ones,sizeof(ones));p+=4;
    pb_push(p++,NV097_SET_VERTEX_DATA_ARRAY_FORMAT,16);
    for(unsigned i=0;i<16;i++) *p++=NV097_SET_VERTEX_DATA_ARRAY_FORMAT_TYPE_F;
    unsigned attrs[]={0,9},counts[]={4,4},offsets[]={0,16};
    for(unsigned i=0;i<2;i++) {
        p=pb_push1(p,NV097_SET_VERTEX_DATA_ARRAY_FORMAT+attrs[i]*4,
            MASK(NV097_SET_VERTEX_DATA_ARRAY_FORMAT_TYPE,NV097_SET_VERTEX_DATA_ARRAY_FORMAT_TYPE_F)|
            MASK(NV097_SET_VERTEX_DATA_ARRAY_FORMAT_SIZE,counts[i])|
            MASK(NV097_SET_VERTEX_DATA_ARRAY_FORMAT_STRIDE,sizeof(Vertex)));
        p=pb_push1(p,NV097_SET_VERTEX_DATA_ARRAY_OFFSET+attrs[i]*4,((uint32_t)vertices+offsets[i])&0x03ffffff);
    }
    p=pb_push1(p,NV097_SET_ALPHA_TEST_ENABLE,0);
    p=pb_push1(p,NV097_SET_BLEND_ENABLE,0);
    p=pb_push1(p,NV097_SET_CULL_FACE_ENABLE,0);
    p=pb_push1(p,NV097_SET_DEPTH_TEST_ENABLE,0);
    p=pb_push1(p,NV097_SET_DITHER_ENABLE,0);
    p=pb_push1(p,NV097_SET_STENCIL_TEST_ENABLE,0);
    p=pb_push1(p,NV097_SET_COLOR_MASK,0x01010101);
    for(unsigned u=0;u<4;u++) {
        p=pb_push1(p,NV097_SET_TEXTURE_OFFSET+u*64,record271.texture_physical[u]);
        p=pb_push1(p,NV097_SET_TEXTURE_FORMAT+u*64,0x0001122a); /* sample's linear A8R8G8B8, DMA B, 2D, one level */
        p=pb_push1(p,NV097_SET_TEXTURE_CONTROL1+u*64,(W*4)<<16);
        p=pb_push1(p,NV097_SET_TEXTURE_IMAGE_RECT+u*64,(W<<16)|H);
        p=pb_push1(p,NV097_SET_TEXTURE_ADDRESS+u*64,0x00030303);
        p=pb_push1(p,NV097_SET_TEXTURE_FILTER+u*64,0x01010000); /* nearest MIN/MAG, zero bias */
    }
    pb_end(p);
}
int main(void)
{
    memset((void *)&record271,0,sizeof(record271));
    record271.magic=0x58323731;record271.version=271;record271.bytes=sizeof(record271);
    record271.width=W;record271.height=H;record271.pitch=W*4;
    record271.block_size=BLOCK;record271.payload_offset=PAYLOAD;
    if(!XVideoSetMode(640,480,32,REFRESH_DEFAULT)) {stop(10);return 1;}
    pb_set_color_format(NV097_SET_SURFACE_FORMAT_COLOR_LE_A8R8G8B8,false);pb_extra_buffers(1);
    if(pb_init()) {stop(1);return 1;}
    frame=pb_extra_buffer(0);record271.target=(uint32_t)frame;
    record271.target_physical=MmGetPhysicalAddress(frame);
    record271.target_pitch=pb_back_buffer_pitch();record271.target_height=pb_back_buffer_height();
    if(!frame || record271.target_height!=480 || record271.target_pitch<640*4) {stop(2);return 1;}
    for(unsigned u=0;u<4;u++) {
        blocks[u]=MmAllocateContiguousMemoryEx(BLOCK,0,MAXRAM,4096,PAGE_READWRITE|PAGE_WRITECOMBINE);
        if(!blocks[u]) {stop(3);return 1;}
        record271.allocation[u]=(uint32_t)blocks[u];record271.physical[u]=MmGetPhysicalAddress(blocks[u]);
        record271.texture[u]=(uint32_t)blocks[u]+PAYLOAD;record271.texture_physical[u]=record271.physical[u]+PAYLOAD;
        for(unsigned n=0;n<BLOCK;n++) blocks[u][n]=expected_byte(u,n);
    }
    vertices=MmAllocateContiguousMemoryEx(sizeof(quad),0,MAXRAM,0,PAGE_READWRITE|PAGE_WRITECOMBINE);
    if(!vertices) {stop(4);return 1;}
    memcpy(vertices,quad,sizeof(quad));record271.vertices=(uint32_t)vertices;record271.vertices_bytes=sizeof(quad);
    record271.vertices_physical=MmGetPhysicalAddress(vertices);
    if(!allocations_valid()) {stop(11);return 1;}
    __asm__ __volatile__("sfence" ::: "memory");
    pb_target_extra_buffer(0);pb_erase_depth_stencil_buffer(0,0,640,480);
    pb_fill(0,0,640,480,CLEAR);setup_draw();program(true);enable(true);draw(0);
    if(!idle(0)) {stop(5);return 1;}
    capture(0);sources(0);
    /* Disable and cause normal binder processing via an actual flat draw. */
    enable(false);program(false);draw(6);
    if(!idle(1)) {stop(6);return 1;}
    checkpoint271(11,&record271,0x271c0deu);
    if(record271.pixel_errors[0] || record271.source_errors[0]) {stop(7);return 1;}
    program(true);enable(true);draw(0);
    if(!idle(2)) {stop(8);return 1;}
    capture(1);sources(1);
    checkpoint271(22,&record271,0x271c0deu);
    stop(record271.pixel_errors[1] || record271.source_errors[1]?9:0);
    return 0;
}

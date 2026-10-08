/* SPDX-License-Identifier: MIT
 * Emulator-only swizzled color/Z16 drawing oracle. No Windows or physical deployment.
 * The private pbkit copy adds two read-only accessors; rendering is unchanged.
 */
#include <hal/video.h>
#include <hal/xbox.h>
#include <hal/debug.h>
#include <nxdk/mount.h>
#include <pbkit/pbkit.h>
#include <pbkit/nv_regs.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

extern DWORD *xwn_depth_buffer(void);
extern DWORD xwn_depth_pitch(void);
#define W 640u
#define H 480u
#define ROOT "E:\\xwngpu153\\"
static HANDLE logf = INVALID_HANDLE_VALUE;
static DWORD *snapshot;
static unsigned captures, stores, failed;

static int flush(HANDLE h) {
    IO_STATUS_BLOCK io;
    return NT_SUCCESS(NtFlushBuffersFile(h, &io));
}
static void report(const char *fmt, ...) {
    char b[512]; DWORD n; va_list ap;
    va_start(ap, fmt); int len = vsnprintf(b, sizeof(b), fmt, ap); va_end(ap);
    if (len < 0 || len >= (int)sizeof(b) ||
        !WriteFile(logf, b, len, &n, NULL) || n != (DWORD)len || !flush(logf)) failed = 1;
}
static int idle(void) {
    DWORD start = GetTickCount();
    while (pb_busy()) {
        if (GetTickCount() - start > 10000) {
            report("FAIL gpu_timeout\r\n"); failed = 1; return 0;
        }
        Sleep(0);
    }
    return 1;
}

#define MASK(mask, val) (((val) << (ffs(mask)-1)) & (mask))
#define BACKGROUND 0xff15324au
static DWORD *vertices;
static void init_shader(void)
{
    uint32_t *p;
    int       i;

    /* Setup vertex shader */
    uint32_t vs_program[] = {
        #include "vs.inl"
    };

    p = pb_begin();

    /* Set run address of shader */
    p = pb_push1(p, NV097_SET_TRANSFORM_PROGRAM_START, 0);

    /* Set execution mode */
    p = pb_push1(p, NV097_SET_TRANSFORM_EXECUTION_MODE,
                 MASK(NV097_SET_TRANSFORM_EXECUTION_MODE_MODE, NV097_SET_TRANSFORM_EXECUTION_MODE_MODE_PROGRAM)
                 | MASK(NV097_SET_TRANSFORM_EXECUTION_MODE_RANGE_MODE, NV097_SET_TRANSFORM_EXECUTION_MODE_RANGE_MODE_PRIV));

    p = pb_push1(p, NV097_SET_TRANSFORM_PROGRAM_CXT_WRITE_EN, 0);

    pb_end(p);

    /* Set cursor for program upload */
    p = pb_begin();
    p = pb_push1(p, NV097_SET_TRANSFORM_PROGRAM_LOAD, 0);
    pb_end(p);

    /* Copy program instructions (16-bytes each) */
    for (i=0; i<sizeof(vs_program)/16; i++) {
        p = pb_begin();
        pb_push(p++, NV097_SET_TRANSFORM_PROGRAM, 4);
        memcpy(p, &vs_program[i*4], 4*4);
        p+=4;
        pb_end(p);
    }

    /* Setup fragment shader */
    p = pb_begin();
    #include "ps.inl"
    pb_end(p);
}

/* Set an attribute pointer */
static void set_attrib_pointer(unsigned int index, unsigned int format, unsigned int size, unsigned int stride, const void* data)
{
    uint32_t *p = pb_begin();
    p = pb_push1(p, NV097_SET_VERTEX_DATA_ARRAY_FORMAT + index*4,
                 MASK(NV097_SET_VERTEX_DATA_ARRAY_FORMAT_TYPE, format) | \
                 MASK(NV097_SET_VERTEX_DATA_ARRAY_FORMAT_SIZE, size) |  \
                 MASK(NV097_SET_VERTEX_DATA_ARRAY_FORMAT_STRIDE, stride));
    p = pb_push1(p, NV097_SET_VERTEX_DATA_ARRAY_OFFSET + index*4, (uint32_t)data & 0x03ffffff);
    pb_end(p);
}


static void setup(void) {
    init_shader();
    uint32_t *q=pb_begin();
    q=pb_push1(q,NV097_SET_DEPTH_TEST_ENABLE,1);
    q=pb_push1(q,NV097_SET_STENCIL_TEST_ENABLE,0);
    q=pb_push1(q,NV097_SET_DEPTH_FUNC,0x207);
    q=pb_push1(q,NV097_SET_DEPTH_MASK,1);
    q=pb_push1(q,NV097_SET_CULL_FACE_ENABLE,0);
    q=pb_push1(q,NV097_SET_BLEND_ENABLE,0);
    q=pb_push1(q,NV097_SET_ALPHA_TEST_ENABLE,0);
    q=pb_push1(q,NV097_SET_LIGHTING_ENABLE,0);
    pb_push(q++,NV097_SET_VERTEX_DATA_ARRAY_FORMAT,16);
    for(unsigned i=0;i<16;i++) *q++=NV097_SET_VERTEX_DATA_ARRAY_FORMAT_TYPE_F;
    pb_end(q);
    set_attrib_pointer(0,NV097_SET_VERTEX_DATA_ARRAY_FORMAT_TYPE_F,4,32,vertices);
    set_attrib_pointer(3,NV097_SET_VERTEX_DATA_ARRAY_FORMAT_TYPE_F,4,32,vertices+4);
}
static void begin_draw(void) {
    uint32_t *q=pb_begin();
    q=pb_push1(q,NV097_SET_BEGIN_END,NV097_SET_BEGIN_END_OP_TRIANGLES);pb_end(q);
}
static void queue_vertices(void) {
    uint32_t *q=pb_begin();
    q=pb_push1(q,0x40000000|NV097_DRAW_ARRAYS,MASK(NV097_DRAW_ARRAYS_COUNT,5));pb_end(q);
}
static void end_draw(void) {
    uint32_t *q=pb_begin();q=pb_push1(q,NV097_SET_BEGIN_END,NV097_SET_BEGIN_END_OP_END);pb_end(q);
}
#define ARENA_BYTES 32768u
static unsigned swizzled_pixel(unsigned x,unsigned y,unsigned width,unsigned height) {
    unsigned result=0,bit=1;
    for(unsigned source=1;source<width||source<height;source<<=1) {
        if(source<width){if(x&source)result|=bit;bit<<=1;}
        if(source<height){if(y&source)result|=bit;bit<<=1;}
    }
    return result;
}
static void bind_shape(unsigned shape) {
    unsigned lw=shape?5:6,lh=shape?6:5,w=1u<<lw,h=1u<<lh;
    uint32_t *q=pb_begin();
    q=pb_push2(q,NV097_SET_SURFACE_CLIP_HORIZONTAL,w<<16,h<<16);
    q=pb_push1(q,NV097_SET_SURFACE_FORMAT,8|(1<<4)|(2<<8)|(lw<<16)|(lh<<24));
    q=pb_push3(q,NV097_SET_SURFACE_PITCH,w*4|((w*2)<<16),0,0);pb_end(q);
    report("SHAPE %u %u %u\r\n",shape,w,h);
}
static int draw(unsigned stage) {
    float x0=stage?17:8,x1=stage?29:24,y0=stage?11:6,y1=stage?23:18;
    float red=stage?0:1,green=stage?1:0;
    float v[6][8]={
        {x0,y0,0,1,red,green,1,1},{x1,y0,0,1,red,green,1,1},{x1,y1,0,1,red,green,1,1},
        {x0,y0,0,1,red,green,1,1},{x1,y1,0,1,red,green,1,1},{x0,y1,0,1,red,green,1,1}};
    memcpy(vertices,v,sizeof(v));__asm__ __volatile__("sfence" ::: "memory");
    begin_draw();queue_vertices();end_draw();return idle();
}
static int capture(unsigned shape,unsigned depth,unsigned stage,volatile unsigned char *p) {
    for(unsigned i=0;i<ARENA_BYTES;i++)((unsigned char*)snapshot)[i]=p[i];
    char path[100];DWORD n;snprintf(path,sizeof(path),ROOT "q%u-d%u-s%u.raw",shape,depth,stage);
    HANDLE f=CreateFileA(path,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(f==INVALID_HANDLE_VALUE){failed=1;return 0;}
    int ok=WriteFile(f,snapshot,ARENA_BYTES,&n,NULL)&&n==ARENA_BYTES&&flush(f);CloseHandle(f);
    if(!ok){failed=1;return 0;}captures++;report("CAPTURE %u %u %u %u\r\n",shape,depth,stage,ARENA_BYTES);return !failed;
}
int main(void) {
    XVideoSetMode(W,H,32,REFRESH_DEFAULT);
    logf=CreateFileA("D:\\bootstrap.log",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(logf==INVALID_HANDLE_VALUE){XReboot();return 1;}
    int was=nxIsDriveMounted('E'),mounted=was||nxMountDrive('E',"\\Device\\Harddisk0\\Partition1\\");
    report("MOUNT_E %d %d %lu\r\n",was,mounted,mounted?0ul:GetLastError());
    int made=mounted&&CreateDirectoryA("E:\\xwngpu153",NULL);
    report("CREATE_OUTPUT %d %lu\r\n",made,made?0ul:GetLastError());CloseHandle(logf);
    if(!made){XReboot();return 1;}
    logf=CreateFileA(ROOT "result.log",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(logf==INVALID_HANDLE_VALUE){XReboot();return 1;}
    snapshot=malloc(ARENA_BYTES);report("BEGIN 153 2 2 3 32768\r\n");
    pb_extra_buffers(1);int status=pb_init();report("INIT_RETURN %d\r\n",status);
    vertices=MmAllocateContiguousMemoryEx(6*8*sizeof(float),0,0x3ffb000,0,PAGE_READWRITE|PAGE_WRITECOMBINE);
    if(status||!snapshot||!vertices){report("FAIL init\r\n");CloseHandle(logf);XReboot();return 1;}
    pb_target_extra_buffer(0);setup();
    volatile unsigned char *arenas[2]={(volatile unsigned char*)pb_extra_buffer(0),(volatile unsigned char*)xwn_depth_buffer()};
    for(unsigned d=0;d<2;d++)report("ARENA %u %08lx 32768\r\n",d,(DWORD)arenas[d]&0x03ffffff);
    for(unsigned q=0;q<2&&!failed;q++) {
        if(!idle())break;
        for(unsigned d=0;d<2;d++)for(unsigned i=0;i<ARENA_BYTES;i++)arenas[d][i]=0xa5;
        __asm__ __volatile__("sfence" ::: "memory");bind_shape(q);
        if(!draw(0))break;report("DRAW_IDLE %u 0\r\n",q);
        for(unsigned d=0;d<2;d++)if(!capture(q,d,0,arenas[d]))failed=1;
        unsigned w=q?32:64,h=q?64:32;
        for(unsigned d=0;d<2;d++)for(unsigned n=0;n<2;n++) {
            unsigned idx=swizzled_pixel(n?12:3,n?9:5,w,h);
            if(d)((volatile uint16_t*)arenas[d])[idx]=n?0x9876:0x4321;
            else ((volatile uint32_t*)arenas[d])[idx]=n?0xff765432:0xff123456;
            stores++;
        }
        __asm__ __volatile__("sfence" ::: "memory");report("CPU_PATCH %u 4\r\n",q);
        for(unsigned d=0;d<2;d++)if(!capture(q,d,1,arenas[d]))failed=1;
        if(!draw(1))break;report("DRAW_IDLE %u 1\r\n",q);
        for(unsigned d=0;d<2;d++)if(!capture(q,d,2,arenas[d]))failed=1;
    }
    pb_kill();report("KILL_RETURN\r\n");report("COMPLETE %u %u %u\r\n",captures,stores,failed);
    report("NORMAL_REBOOT_REQUEST\r\n");CloseHandle(logf);free(snapshot);MmFreeContiguousMemory(vertices);XReboot();return failed?1:0;
}

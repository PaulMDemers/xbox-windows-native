/* SPDX-License-Identifier: MIT
 * Emulator-only color/Z24S8 coherence oracle. No Windows or physical deployment.
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
#define ROOT "E:\\xwngpu145\\"
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
    q=pb_push1(q,NV097_SET_DEPTH_TEST_ENABLE,0);
    q=pb_push1(q,NV097_SET_STENCIL_TEST_ENABLE,0);
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
static void cpu_store(unsigned mode,volatile DWORD *p,DWORD pitch) {
    /* Same value, disjoint from triangle coverage: no ambiguous racing pixels. */
    p[5*(pitch/4)+3]=BACKGROUND;
    __asm__ __volatile__("sfence" ::: "memory");
    ++stores;report("CPU_STORE %u 3 5 %08x\r\n",mode,BACKGROUND);
}
static int capture(unsigned mode,volatile DWORD *p,DWORD pitch) {
    for(unsigned y=0;y<H;y++) for(unsigned x=0;x<W;x++) snapshot[y*W+x]=p[y*(pitch/4)+x];
    char path[100];DWORD n;snprintf(path,sizeof(path),ROOT "case%u.raw",mode);
    HANDLE f=CreateFileA(path,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(f==INVALID_HANDLE_VALUE){failed=1;return 0;}
    int ok=WriteFile(f,snapshot,W*H*4,&n,NULL)&&n==W*H*4&&flush(f);CloseHandle(f);
    if(!ok){failed=1;return 0;}++captures;
    report("CAPTURE %u %lu\r\n",mode,W*H*4);return !failed;
}
int main(void) {
    XVideoSetMode(W,H,32,REFRESH_DEFAULT);
    logf=CreateFileA("D:\\bootstrap.log",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(logf==INVALID_HANDLE_VALUE){XReboot();return 1;}
    int was_mounted=nxIsDriveMounted('E');
    int mounted=was_mounted||nxMountDrive('E',"\\Device\\Harddisk0\\Partition1\\");
    report("MOUNT_E %d %d %lu\r\n",was_mounted,mounted,mounted?0ul:GetLastError());
    int created=mounted&&CreateDirectoryA("E:\\xwngpu145",NULL);
    report("CREATE_OUTPUT %d %lu\r\n",created,created?0ul:GetLastError());CloseHandle(logf);
    if(!created){XReboot();return 1;}
    logf=CreateFileA(ROOT "result.log",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(logf==INVALID_HANDLE_VALUE){XReboot();return 1;}
    snapshot=malloc(W*H*4);report("BEGIN 145 4 640 480\r\n");
    pb_extra_buffers(1);int status=pb_init();report("INIT_RETURN %d\r\n",status);
    if(status||!snapshot){report("FAIL init\r\n");CloseHandle(logf);XReboot();return 1;}
    pb_target_extra_buffer(0);
    static const float v[6][8]={
      {128,96,0,1,1,0,1,1},{192,96,0,1,1,0,1,1},{192,160,0,1,1,0,1,1},
      {128,96,0,1,1,0,1,1},{192,160,0,1,1,0,1,1},{128,160,0,1,1,0,1,1}};
    vertices=MmAllocateContiguousMemoryEx(sizeof(v),0,0x3ffb000,0,PAGE_READWRITE|PAGE_WRITECOMBINE);
    if(!vertices){failed=1;}else{memcpy(vertices,v,sizeof(v));__asm__ __volatile__("sfence" ::: "memory");setup();}
    volatile DWORD *p=pb_extra_buffer(0);DWORD pitch=pb_back_buffer_pitch();
    report("SURFACE %08lx %lu\r\n",(DWORD)p&0x03ffffff,pitch);
    if(pitch!=W*4)failed=1;
    for(unsigned mode=0;mode<4&&!failed;mode++) {
      report("CASE %u\r\n",mode);pb_fill(0,0,W,H,BACKGROUND);if(!idle())break;
      report("CLEAR_IDLE %u\r\n",mode);
      if(mode==1)cpu_store(mode,p,pitch);
      begin_draw();if(!idle())break;report("BEGIN_IDLE %u\r\n",mode);
      if(mode==2)cpu_store(mode,p,pitch);
      queue_vertices();if(!idle())break;report("ARRAYS_IDLE %u\r\n",mode);
      if(mode==3)cpu_store(mode,p,pitch);
      end_draw();if(!idle())break;report("END_IDLE %u\r\n",mode);
      if(!capture(mode,p,pitch))break;
    }
    pb_kill();report("KILL_RETURN\r\n");
    report("COMPLETE %u %u %u\r\n",captures,stores,failed);report("NORMAL_REBOOT_REQUEST\r\n");
    CloseHandle(logf);if(vertices)MmFreeContiguousMemory(vertices);free(snapshot);XReboot();return failed?1:0;
}

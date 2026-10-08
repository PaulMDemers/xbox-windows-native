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

extern DWORD *xwn_depth_buffer(void);
extern DWORD xwn_depth_pitch(void);
#define W 640u
#define H 480u
#define ROOT "E:\\xwngpu149\\"
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

#define ARENA_BYTES 32768u
static void bind_surface(unsigned depth,unsigned slot) {
    unsigned cp=depth?256:(slot?320:256), zp=depth?(slot?192:128):128;
    unsigned offset=slot?(depth?2048:4096):0;
    uint32_t *q=pb_begin();
    q=pb_push2(q,NV097_SET_SURFACE_CLIP_HORIZONTAL,64<<16,64<<16);
    q=pb_push1(q,NV097_SET_SURFACE_FORMAT,8|(1<<4)|(1<<8)|(6<<16)|(6<<24));
    q=pb_push3(q,NV097_SET_SURFACE_PITCH,cp|(zp<<16),depth?0:offset,depth?offset:0);
    pb_end(q);
    report("BIND %u %u %u %u\r\n",depth,slot,offset,depth?zp:cp);
}
static void clear_region(unsigned depth,unsigned x,unsigned y,unsigned w,unsigned h,DWORD value) {
    if(depth)pb_set_depth_stencil_buffer_region(NV097_SET_SURFACE_FORMAT_ZETA_Z16,value,0,x,y,w,h);
    else pb_fill(x,y,w,h,value);
}
static int capture(unsigned depth,unsigned stage,volatile unsigned char *p) {
    for(unsigned i=0;i<ARENA_BYTES;i++)((unsigned char*)snapshot)[i]=p[i];
    char path[100];DWORD n;snprintf(path,sizeof(path),ROOT "d%u-s%u.raw",depth,stage);
    HANDLE f=CreateFileA(path,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(f==INVALID_HANDLE_VALUE){failed=1;return 0;}
    int ok=WriteFile(f,snapshot,ARENA_BYTES,&n,NULL)&&n==ARENA_BYTES&&flush(f);CloseHandle(f);
    if(!ok){failed=1;return 0;}captures++;report("CAPTURE %u %u %u\r\n",depth,stage,ARENA_BYTES);return !failed;
}
static int exercise(unsigned depth) {
    volatile unsigned char *p=(volatile unsigned char*)(depth?xwn_depth_buffer():pb_extra_buffer(0));
    report("ARENA %u %08lx %u\r\n",depth,(DWORD)p&0x03ffffff,ARENA_BYTES);
    for(unsigned i=0;i<ARENA_BYTES;i++)p[i]=0xa5;
    __asm__ __volatile__("sfence" ::: "memory");
    bind_surface(depth,0);clear_region(depth,0,0,64,64,depth?0x3157:0xff3157a9);if(!idle())return 0;
    report("UNREAD_A %u\r\n",depth);
    bind_surface(depth,1);clear_region(depth,7,9,17,11,depth?0x6824:0xff6824d1);if(!idle()||!capture(depth,0,p))return 0;
    unsigned bpp=depth?2:4,off=depth?2048:4096,pitch=depth?192:320;
    for(unsigned y=3;y<8;y++)for(unsigned x=2;x<7;x++) {
      unsigned idx=off+y*pitch+x*bpp;
      if(depth)*(volatile uint16_t*)(p+idx)=(uint16_t)(0x9000^(y<<5)^x);
      else *(volatile uint32_t*)(p+idx)=0x92740000^(y<<8)^x;
      stores++;
    }
    __asm__ __volatile__("sfence" ::: "memory");report("CPU_PATCH %u 25\r\n",depth);
    if(!capture(depth,1,p))return 0;
    bind_surface(depth,0);clear_region(depth,20,17,11,19,depth?0xbcde:0xffbcdE73);
    return idle()&&capture(depth,2,p);
}
int main(void) {
    XVideoSetMode(W,H,32,REFRESH_DEFAULT);
    logf=CreateFileA("D:\\bootstrap.log",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(logf==INVALID_HANDLE_VALUE){XReboot();return 1;}
    int was=nxIsDriveMounted('E'),mounted=was||nxMountDrive('E',"\\Device\\Harddisk0\\Partition1\\");
    report("MOUNT_E %d %d %lu\r\n",was,mounted,mounted?0ul:GetLastError());
    int made=mounted&&CreateDirectoryA("E:\\xwngpu149",NULL);
    report("CREATE_OUTPUT %d %lu\r\n",made,made?0ul:GetLastError());CloseHandle(logf);
    if(!made){XReboot();return 1;}
    logf=CreateFileA(ROOT "result.log",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(logf==INVALID_HANDLE_VALUE){XReboot();return 1;}
    snapshot=malloc(ARENA_BYTES);report("BEGIN 149 2 3 32768\r\n");
    pb_extra_buffers(1);int status=pb_init();report("INIT_RETURN %d\r\n",status);
    if(status||!snapshot){report("FAIL init\r\n");CloseHandle(logf);XReboot();return 1;}
    pb_target_extra_buffer(0);if(idle())for(unsigned d=0;d<2&&!failed;d++)if(!exercise(d))failed=1;
    pb_kill();report("KILL_RETURN\r\n");report("COMPLETE %u %u %u\r\n",captures,stores,failed);
    report("NORMAL_REBOOT_REQUEST\r\n");CloseHandle(logf);free(snapshot);XReboot();return failed?1:0;
}

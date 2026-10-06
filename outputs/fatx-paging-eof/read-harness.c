/* Host harness around the actual extracted VfatCommonRead, not an NT ABI test. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
typedef int32_t NTSTATUS; typedef uint32_t ULONG; typedef int BOOLEAN;
typedef void *PVOID; typedef unsigned char *PUCHAR;
typedef union { int64_t QuadPart; struct { uint32_t LowPart; int32_t HighPart; } u; } LARGE_INTEGER;
typedef struct { NTSTATUS Status; uintptr_t Information; } IO_STATUS;
typedef struct { ULONG Flags; IO_STATUS IoStatus; } IRP;
typedef struct { struct { LARGE_INTEGER FileSize,AllocationSize; } RFCB; ULONG Flags; int FileLock; int directory; } FCB,*PVFATFCB;
typedef struct { void *FsContext,*PrivateCacheMap; } FILE_OBJECT;
typedef struct { struct { struct { LARGE_INTEGER ByteOffset; ULONG Length; } Read; } Parameters; } STACK;
typedef struct { struct { ULONG BytesPerSector; } FatInfo; } DEVICE;
typedef struct { IRP *Irp; ULONG Flags; FILE_OBJECT *FileObject; STACK *Stack; DEVICE *DeviceExt; } CONTEXT,*PVFAT_IRP_CONTEXT;
#define TRUE 1
#define FALSE 0
#define IRP_PAGING_IO 1
#define IRP_NOCACHE 2
#define IRPCONTEXT_CANWAIT 1
#define FCB_IS_VOLUME 1
#define FCB_IS_FAT 2
#define STATUS_SUCCESS 0
#define STATUS_PENDING 0x103
#define STATUS_FILE_LOCK_CONFLICT ((NTSTATUS)-1)
#define STATUS_INSUFFICIENT_RESOURCES ((NTSTATUS)-2)
#define IoWriteAccess 0
#define BooleanFlagOn(a,b) (!!((a)&(b)))
#define NT_SUCCESS(s) ((s)>=0)
#define ROUND_UP_64(a,b) (((a)+(b)-1)&~((int64_t)(b)-1))
#define vfatFCBIsDirectory(f) ((f)->directory)
#define FsRtlAreThereCurrentFileLocks(...) 0
#define FsRtlCheckLockForReadAccess(...) 1
#define vfatAddToStat(...) ((void)0)
#define CcInitializeCacheMap(...) ((void)0)
#define CcCopyRead(...) 1
#define ASSERT assert
#define _SEH2_TRY if (1)
#define _SEH2_EXCEPT(x) else
#define _SEH2_GetExceptionCode() (-3)
#define _SEH2_END
#define RtlZeroMemory(p,n) memset(p,0,n)
static unsigned char memory[16384];
static ULONG limit,actual; static int force_short,fail_read,null_after_read;
static PVOID VfatGetUserBuffer(IRP *i,BOOLEAN paging) { (void)i;(void)paging;return null_after_read&&actual?NULL:memory+32; }
static NTSTATUS VfatLockUserBuffer(IRP *i,ULONG len,int access) { (void)i;(void)access;assert(len<=sizeof(memory)-64);limit=len;return 0; }
static NTSTATUS VfatReadFileData(CONTEXT *c,ULONG len,LARGE_INTEGER off,ULONG *done) {
    (void)c;(void)off;assert(len<=limit);if(fail_read)return -4;
    *done=force_short&&len>128?128:len;actual=*done;memset(memory+32,0xa5,*done);return 0;
}
static NTSTATUS VfatReadPagingTail(CONTEXT *c,ULONG len,LARGE_INTEGER off,ULONG *done) { return VfatReadFileData(c,len,off,done); }
/* INSERT_ACTUAL_FUNCTION */
int main(void) {
    unsigned tests=0,failures=0;
    const ULONG tails[]={1,2,127,511,512,513,4095,4096,4097};
    for(unsigned t=0;t<sizeof(tails)/sizeof(tails[0]);++t)
    for(unsigned mode=0;mode<7;++mode) {
        IRP irp={IRP_PAGING_IO|IRP_NOCACHE,{0,0}}; FCB f={0}; FILE_OBJECT fo={&f,NULL}; STACK st={0}; DEVICE d={{512}};
        CONTEXT c={&irp,IRPCONTEXT_CANWAIT,&fo,&st,&d};
        memset(memory,0xcd,sizeof(memory));limit=actual=0;force_short=fail_read=null_after_read=0;
        st.Parameters.Read.ByteOffset.QuadPart=4096;st.Parameters.Read.Length=8192;
        f.RFCB.FileSize.QuadPart=4096+tails[t];
        if(mode==1)f.Flags=FCB_IS_VOLUME;
        if(mode==2)f.Flags=FCB_IS_FAT;
        if(mode==3)f.directory=1;
        if(mode==4)irp.Flags=IRP_NOCACHE;
        if(mode==5)force_short=1;
        if(mode==6)fail_read=1;
        NTSTATUS status=VfatCommonRead(&c);unsigned bad=0;
        for(unsigned i=0;i<sizeof(memory);++i) {
            unsigned char expected=0xcd;
            if(i>=32 && i<32+actual)expected=0xa5;
            if((mode==0||mode==5)&&i>=32+tails[t]&&i<32+actual)expected=0;
            if(memory[i]!=expected)bad++;
        }
        if(mode==6 ? status!=-4||irp.IoStatus.Information!=0 : status!=0||irp.IoStatus.Information!=actual)bad++;
        tests++;if(bad)failures++;
    }
    printf("{\"cases\":%u,\"failures\":%u}\n",tests,failures);
    return failures?1:0;
}

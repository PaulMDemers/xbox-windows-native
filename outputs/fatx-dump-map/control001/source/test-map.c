/* Host ABI shim: execute the actual paging-map builder and new mapping code.
 * This tests algorithms/ownership; it does not emulate NT SEH or its ABI. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXULONG UINT32_MAX
#define MAXLONGLONG INT64_MAX
#define NonPagedPool 0
#define KernelMode 0
#define FCB_IS_PAGE_FILE 8
#define FCB_IS_VOLUME 16
#define FCB_IS_FAT 4
#define FCB_DELETE_PENDING 2
#define STATUS_SUCCESS ((int32_t)0)
#define STATUS_INVALID_PARAMETER ((int32_t)0xc000000d)
#define STATUS_FILE_CORRUPT_ERROR ((int32_t)0xc0000102)
#define STATUS_INSUFFICIENT_RESOURCES ((int32_t)0xc000009a)
#define STATUS_INTEGER_OVERFLOW ((int32_t)0xc0000095)
#define NT_SUCCESS(s) ((s)>=0)
#define BooleanFlagOn(v,b) (((v)&(b))!=0)
#define min(a,b) ((a)<(b)?(a):(b))
#define FIELD_OFFSET(t,f) ((uint32_t)__builtin_offsetof(t,f))
#define _SEH2_TRY if (1)
#define _SEH2_EXCEPT(x) else
#define _SEH2_GetExceptionCode() STATUS_INVALID_PARAMETER
#define _SEH2_END
typedef uint32_t ULONG;
typedef uint64_t ULONGLONG;
typedef int32_t NTSTATUS;
typedef void *PVOID;
typedef union {int64_t QuadPart; struct {uint32_t LowPart;int32_t HighPart;};} LARGE_INTEGER,*PLARGE_INTEGER;
typedef struct MAP {struct MAP *Previous; ULONG FileSize,ClusterCount,Clusters[1];} VFAT_PAGING_MAP,*PVFAT_PAGING_MAP;
typedef struct {ULONG BytesPerCluster,BytesPerSector,SectorsPerCluster,NumberOfClusters,dataStart,Sectors;} FATINFO,*PFATINFO;
typedef struct {FATINFO FatInfo;int IsFatX;} EXT,*PDEVICE_EXTENSION;
typedef struct {ULONG Flags;PVFAT_PAGING_MAP PagingMap;struct{LARGE_INTEGER FileSize;} RFCB;ULONG entry;int Directory;} FCB,*PVFATFCB;
typedef struct {struct {struct{ULONG InputBufferLength,OutputBufferLength;void *Type3InputBuffer;} FileSystemControl;} Parameters;} IO_STACK_LOCATION,*PIO_STACK_LOCATION;
typedef struct {int RequestorMode;void *UserBuffer;struct{uintptr_t Information;} IoStatus;} IRP,*PIRP;
typedef struct {void *FsContext;} FILE_OBJECT;
typedef struct {PIO_STACK_LOCATION Stack;PIRP Irp;FILE_OBJECT *FileObject;PDEVICE_EXTENSION DeviceExt;} CTX,*PVFAT_IRP_CONTEXT;
static int Live,AllocCalls,FailAt;static size_t LastAllocation;
static void *ExAllocatePoolWithTag(int pool,size_t n,unsigned tag){(void)tag;assert(pool==0);++AllocCalls;LastAllocation=n;if(FailAt==AllocCalls)return NULL;void*p=calloc(1,n);assert(p);++Live;return p;}
static void ExFreePool(void*p){assert(p&&Live>0);--Live;free(p);}
static void *InterlockedExchangePointer(void *volatile *p,void*v){void*o=*p;*p=v;return o;}
static void *InterlockedCompareExchangePointer(void *volatile *p,void*v,void*c){void*o=*p;if(o==c)*p=v;return o;}
static int vfatVolumeIsFatX(PDEVICE_EXTENSION e){return e->IsFatX;}
static int vfatFCBIsDirectory(PVFATFCB f){return f->Directory;}
static ULONG vfatDirEntryGetFirstCluster(PDEVICE_EXTENSION e,ULONG*p){(void)e;return *p;}
static ULONG Chain[1024],ChainCount,Walk;static NTSTATUS ChainError;
static NTSTATUS GetNextCluster(PDEVICE_EXTENSION e,ULONG c,ULONG*n){(void)e;assert(Walk<ChainCount);++Walk;if(ChainError)return ChainError;ULONG at=0;while(at<ChainCount&&Chain[at]!=c)++at;assert(at<ChainCount);*n=at+1<ChainCount?Chain[at+1]:MAXULONG;return 0;}
#include "artifacts/paging-builder.inc"
#include "dump-map.inc"
static unsigned Checks;
static void clean(FCB*f){while(f->PagingMap){void*p=f->PagingMap;f->PagingMap=f->PagingMap->Previous;ExFreePool(p);}assert(Live==0);}
static LARGE_INTEGER large(int64_t n){LARGE_INTEGER r;r.QuadPart=n;return r;}
static void expected_error(PVFAT_PAGING_MAP m,FATINFO*fi,int64_t size,NTSTATUS code){PLARGE_INTEGER p=(void*)(uintptr_t)1;assert(VfatMakeDumpMapping(m,fi,large(size),&p)==code&&p==(void*)(uintptr_t)1);++Checks;}
static void mapping(PVFAT_PAGING_MAP m,FATINFO*fi,ULONG size){PLARGE_INTEGER p=NULL;assert(VfatMakeDumpMapping(m,fi,large(size),&p)==0);ULONG i=0,done=0;while(p[i*2].QuadPart){assert(p[i*2].QuadPart>0&&p[i*2].QuadPart<=size-done);int64_t off=p[i*2+1].QuadPart;for(ULONG pos=0;pos<(ULONG)p[i*2].QuadPart;pos+=fi->BytesPerSector){ULONG v=done+pos,index=v/fi->BytesPerCluster,within=v%fi->BytesPerCluster;uint64_t want=((uint64_t)fi->dataStart+(uint64_t)(m->Clusters[index]-2)*fi->SectorsPerCluster)*fi->BytesPerSector+within;assert((uint64_t)(off+pos)==want);}done+=(ULONG)p[i*2].QuadPart;++i;assert(i<=m->ClusterCount);}assert(done==size&&p[i*2+1].QuadPart==0&&LastAllocation==(i+1)*16);ExFreePool(p);++Checks;}
int main(void){
 EXT e={{65536,512,128,10000,128,1280128},1};FCB f={0};f.Flags=FCB_IS_PAGE_FILE;f.RFCB.FileSize=large(3*65536);f.entry=20;
 ChainCount=3;Chain[0]=20;Chain[1]=21;Chain[2]=40;assert(VfatBuildPagingMap(&e,&f)==0&&Walk==3);++Checks;
 mapping(f.PagingMap,&e.FatInfo,512);mapping(f.PagingMap,&e.FatInfo,65536);mapping(f.PagingMap,&e.FatInfo,65536+512);mapping(f.PagingMap,&e.FatInfo,3*65536);
 expected_error(NULL,&e.FatInfo,65536,STATUS_INVALID_PARAMETER);expected_error(f.PagingMap,&e.FatInfo,-1,STATUS_INVALID_PARAMETER);expected_error(f.PagingMap,&e.FatInfo,0,STATUS_INVALID_PARAMETER);expected_error(f.PagingMap,&e.FatInfo,1,STATUS_INVALID_PARAMETER);expected_error(f.PagingMap,&e.FatInfo,3*65536+512,STATUS_INVALID_PARAMETER);expected_error(f.PagingMap,&e.FatInfo,0x100000000LL,STATUS_INVALID_PARAMETER);
 FATINFO save=e.FatInfo;e.FatInfo.BytesPerCluster=0;expected_error(f.PagingMap,&e.FatInfo,65536,STATUS_INVALID_PARAMETER);e.FatInfo=save;e.FatInfo.BytesPerSector=513;expected_error(f.PagingMap,&e.FatInfo,65536,STATUS_INVALID_PARAMETER);e.FatInfo=save;e.FatInfo.Sectors=200;expected_error(f.PagingMap,&e.FatInfo,65536,STATUS_FILE_CORRUPT_ERROR);e.FatInfo=save;
 f.PagingMap->ClusterCount=2;expected_error(f.PagingMap,&e.FatInfo,65536,STATUS_FILE_CORRUPT_ERROR);f.PagingMap->ClusterCount=3;f.PagingMap->Clusters[0]=1;expected_error(f.PagingMap,&e.FatInfo,65536,STATUS_FILE_CORRUPT_ERROR);f.PagingMap->Clusters[0]=10002;expected_error(f.PagingMap,&e.FatInfo,65536,STATUS_FILE_CORRUPT_ERROR);f.PagingMap->Clusters[0]=20;
 FailAt=AllocCalls+1;expected_error(f.PagingMap,&e.FatInfo,65536,STATUS_INSUFFICIENT_RESOURCES);FailAt=0;
 IO_STACK_LOCATION sl={0};IRP irp={0};FILE_OBJECT fo={&f};CTX ctx={&sl,&irp,&fo,&e};LARGE_INTEGER req=large(65536);PLARGE_INTEGER out=NULL;sl.Parameters.FileSystemControl.InputBufferLength=8;sl.Parameters.FileSystemControl.OutputBufferLength=sizeof(void*);sl.Parameters.FileSystemControl.Type3InputBuffer=&req;irp.UserBuffer=&out;
 assert(VfatQueryRetrievalPointers(&ctx)==0&&out&&irp.IoStatus.Information==sizeof(void*));ExFreePool(out);++Checks;
 for(int n=0;n<9;++n){out=(void*)(uintptr_t)1;irp.IoStatus.Information=0;switch(n){case 0:irp.RequestorMode=1;break;case 1:ctx.FileObject=NULL;break;case 2:fo.FsContext=NULL;break;case 3:e.IsFatX=0;break;case 4:f.Flags=0;break;case 5:f.Directory=1;break;case 6:sl.Parameters.FileSystemControl.InputBufferLength=7;break;case 7:sl.Parameters.FileSystemControl.OutputBufferLength=0;break;case 8:sl.Parameters.FileSystemControl.Type3InputBuffer=NULL;break;}
 assert(VfatQueryRetrievalPointers(&ctx)==STATUS_INVALID_PARAMETER&&out==(void*)(uintptr_t)1&&!irp.IoStatus.Information);++Checks;irp.RequestorMode=0;ctx.FileObject=&fo;fo.FsContext=&f;e.IsFatX=1;f.Flags=FCB_IS_PAGE_FILE;f.Directory=0;sl.Parameters.FileSystemControl.InputBufferLength=8;sl.Parameters.FileSystemControl.OutputBufferLength=sizeof(void*);sl.Parameters.FileSystemControl.Type3InputBuffer=&req;}
 clean(&f);
 /* The existing builder refuses cyclic/bad/short chains before publication. */
 for(int n=0;n<4;++n){Walk=0;ChainCount=3;Chain[0]=20;Chain[1]=n==0?20:n==1?MAXULONG:n==2?1:21;Chain[2]=20;ChainError=n==3?STATUS_FILE_CORRUPT_ERROR:0;assert(VfatBuildPagingMap(&e,&f)==STATUS_FILE_CORRUPT_ERROR&&!f.PagingMap);assert(Live==0);++Checks;}ChainError=0;
 /* Distinct deterministic chains: independent per-sector oracle, varied prefix. */
 uint32_t seed=0x472901;
 for(unsigned round=0;round<4000;++round){ULONG count=1+round%31;ChainCount=count;Walk=0;for(ULONG n=0;n<count;++n)Chain[n]=20+n*3;f.entry=20;f.RFCB.FileSize=large(count*65536);assert(VfatBuildPagingMap(&e,&f)==0);seed=seed*1664525+1013904223;ULONG size=(1+seed%(count*128))*512;mapping(f.PagingMap,&e.FatInfo,size);clean(&f);}
 assert(Live==0);printf("checks=%u allocations=%d leaks=%d random_cases=4000\n",Checks,AllocCalls,Live);return 0;
}

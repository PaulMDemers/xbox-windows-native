"""Actual root sizing/traversal/label routines with modeled FAT and cache I/O."""
import hashlib,json,os,re,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;B=Path('/home/paul/xbox-windows-native/boot720839-source001/fatx/drivers/filesystems/vfatfs');O=Path('/mnt/c/xwn839/root001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists();O.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'passed':False,'physical_access':False,'scope':'Actual C root-size, NextCluster, OffsetToCluster, ClusterToSector, ReadVolumeLabel with modeled FAT/cache/disk APIs. No NT runtime/persistence claim.'}
def function(p,name,ret='NTSTATUS'):
 s=p.read_text(encoding='latin1');a=s.index('\n'+name+'(');a=s.rfind('\n'+ret,0,a)+1;b=s.index('{',a);depth=1;i=b+1
 while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[a:i].replace('Cache838','Cache839').replace('ReadVolumeLabel','ReadVolumeLabel'+('Old' if '838' in str(p) else 'New'))
stub=r'''
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <setjmp.h>
typedef uint32_t ULONG,*PULONG;typedef uint64_t ULONGLONG;typedef uintptr_t ULONG_PTR;typedef int BOOLEAN,NTSTATUS;typedef void *PVOID;typedef char *PCHAR;typedef unsigned char *PUCHAR;
typedef union {int64_t QuadPart;struct {uint32_t LowPart;int32_t HighPart;};struct {uint32_t LowPart;int32_t HighPart;} u;} LARGE_INTEGER;
typedef struct {unsigned char FilenameLength,Attrib;char Filename[42];unsigned char rest[20];} FATX_DIR_ENTRY;
typedef struct {unsigned char Filename[11],Attrib,rest[20];} FAT_DIR_ENTRY;
typedef union {FATX_DIR_ENTRY FatX;FAT_DIR_ENTRY Fat;} DIR_ENTRY,*PDIR_ENTRY;
typedef struct {char *Buffer;unsigned short Length,MaximumLength;} OEM_STRING,UNICODE_STRING,*PUNICODE_STRING;
typedef struct {int Type;} DEVOBJ,*PDEVICE_OBJECT;
typedef struct {struct {LARGE_INTEGER FileSize;} RFCB;void *FileObject;} FCB,*PVFATFCB;
typedef struct {struct {ULONG FatType,NumberOfClusters,BytesPerCluster,SectorsPerCluster,rootStart,dataStart;} FatInfo;ULONG FatXRootSize;int DirResource;} DEV,*PDEVICE_EXTENSION;
#define NT_SUCCESS(s) ((s)>=0)
#define STATUS_SUCCESS 0
#define STATUS_FILE_CORRUPT_ERROR (-1)
#define STATUS_INSUFFICIENT_RESOURCES (-2)
#define PAGE_SIZE 4096
#define FAT16 16
#define FAT32 32
#define FATX16 116
#define FATX32 132
#define TRUE 1
#define FALSE 0
#define MAP_WAIT 1
#define ASSERT assert
#define NonPagedPool 0
#define TAG_DIRENT 0
#define DbgPrint(...) ((void)0)
#define _SEH2_TRY if(1)
#define _SEH2_EXCEPT(x) else
#define _SEH2_GetExceptionCode() (-9)
#define _SEH2_END
static ULONG chain[128],reads,failAt,extendCalls,pinned,maps,releases,badsite,badoff;static jmp_buf trap;
static unsigned char *cache;static FCB root;static ULONG cacheSize;
static BOOLEAN vfatVolumeIsFatX(PDEVICE_EXTENSION d){return d->FatInfo.FatType==FATX16 || d->FatInfo.FatType==FATX32;}
static NTSTATUS GetNextCluster(PDEVICE_EXTENSION d,ULONG c,PULONG n){(void)d;reads++;assert(reads<1024);if(c==failAt)return -77;assert(c<128);*n=chain[c];return 0;}
static NTSTATUS GetNextClusterExtend(PDEVICE_EXTENSION d,ULONG c,PULONG n){extendCalls++;return GetNextCluster(d,c,n);}
static int ExAcquireResourceExclusiveLite(int *r,int w){(void)r;(void)w;return 1;}
static void ExReleaseResourceLite(int *r){(void)r;}
static PVFATFCB vfatOpenRootFCB(PDEVICE_EXTENSION d){(void)d;return &root;}
static void vfatReleaseFCB(PDEVICE_EXTENSION d,PVFATFCB f){(void)d;assert(f==&root);releases++;}
static int Cache839Map(ULONG site,PVOID f,LARGE_INTEGER *o,ULONG n,ULONG fl,PVOID *c,PVOID *b){(void)f;(void)fl;maps++;if(o->QuadPart<0 || (uint64_t)o->QuadPart+n>cacheSize){badsite=site;badoff=o->LowPart;longjmp(trap,1);}*c=cache;*b=cache+o->LowPart;pinned++;return 1;}
static void CcUnpinData(PVOID c){assert(c==cache && pinned);pinned--;}
static PVOID ExAllocatePoolWithTag(int p,ULONG n,int t){(void)p;(void)t;return malloc(n);}
static void ExFreePoolWithTag(PVOID p,int t){(void)t;free(p);}
static NTSTATUS VfatReadDisk(PDEVICE_OBJECT d,LARGE_INTEGER *o,ULONG n,PUCHAR b,int w){(void)d;(void)o;(void)n;(void)b;(void)w;assert(0);return -1;}
static NTSTATUS RtlOemStringToUnicodeString(PUNICODE_STRING u,OEM_STRING *o,int a){(void)a;assert(o->Length<=u->MaximumLength);memcpy(u->Buffer,o->Buffer,o->Length);u->Length=o->Length;return 0;}
static void vfat8Dot3ToString(FAT_DIR_ENTRY *e,PUNICODE_STRING u){(void)e;(void)u;}
'''
test=r'''
static void setup(DEV *d,unsigned type,unsigned cb){memset(d,0,sizeof(*d));memset(chain,0,sizeof(chain));d->FatInfo.FatType=type;d->FatInfo.NumberOfClusters=126;d->FatInfo.BytesPerCluster=cb;d->FatInfo.SectorsPerCluster=cb/512;d->FatInfo.rootStart=8;d->FatInfo.dataStart=8+cb/512;reads=0;failAt=0;extendCalls=0;}
int main(void){DEV d;ULONG size,c,cases=0;char label[64];UNICODE_STRING u={label,0,sizeof(label)};
assert(sizeof(FATX_DIR_ENTRY)==64 && sizeof(FAT_DIR_ENTRY)==32);
for(unsigned type=FATX16;type<=FATX32;type+=16)for(unsigned cb=4096;cb<=65536;cb*=4){
 setup(&d,type,cb);chain[1]=0xffffffff;assert(FatXRootSize839(&d,&size)==0 && size==cb && reads==1);cases++;
 chain[1]=9;chain[9]=2;chain[2]=11;chain[11]=0xffffffff;reads=0;assert(FatXRootSize839(&d,&size)==0 && size==4*cb && reads==4);cases++;
 unsigned order[]={1,9,2,11};for(unsigned i=0;i<4;i++){reads=0;assert(OffsetToCluster(&d,1,i*cb,&c,FALSE)==0 && c==order[i]);assert(ClusterToSector(&d,c)==8+(uint64_t)(c-1)*(cb/512));cases++;}
 c=1;reads=0;assert(NextCluster(&d,1,&c,FALSE)==0 && c==9 && extendCalls==0);cases++;
 c=1;reads=0;assert(NextCluster(&d,1,&c,TRUE)==0 && c==9 && extendCalls==1);cases++;
 /* Model disk/cache transfer using the actual offset and sector routines.
  * Distinct unrelated clusters prove a fragmented chain is not read linearly. */
 unsigned char *disk=malloc(20*cb);assert(disk);for(unsigned i=0;i<20;i++)memset(disk+i*cb,i,cb);
 cacheSize=size;cache=malloc(size);assert(cache);for(unsigned i=0;i<4;i++){reads=0;assert(OffsetToCluster(&d,1,i*cb,&c,FALSE)==0);uint64_t off=(ClusterToSector(&d,c)-d.FatInfo.rootStart)*512;memcpy(cache+i*cb,disk+off,cb);assert(cache[i*cb]==order[i]-1);}
 cases++;free(disk);memset(cache,0,cacheSize);root.RFCB.FileSize.QuadPart=cacheSize;root.FileObject=&root;pinned=maps=releases=0;
 DIR_ENTRY *e=(DIR_ENTRY*)(cache+3*cb+64);e->FatX.Attrib=8;e->FatX.FilenameLength=4;memcpy(e->FatX.Filename,"ROOT",4);u.Length=0;
 assert(ReadVolumeLabelNew(&d,0,TRUE,&u)==0 && u.Length==4 && !memcmp(label,"ROOT",4) && !pinned && releases==1);cases++;
 memset(cache,0,cacheSize);u.Length=0;maps=releases=0;assert(ReadVolumeLabelNew(&d,0,TRUE,&u)==0 && !u.Length && !pinned && maps==cacheSize/4096 && releases==1);cases++;
 ((DIR_ENTRY*)cache)->FatX.FilenameLength=0xff;maps=releases=0;assert(ReadVolumeLabelNew(&d,0,TRUE,&u)==0 && maps==1 && !pinned);cases++;free(cache);
 /* Cycles, dangling links, read failures and size overflow refuse a size. */
 chain[1]=1;reads=0;assert(FatXRootSize839(&d,&size)==STATUS_FILE_CORRUPT_ERROR && size==0 && reads==1);cases++;
 chain[1]=9;chain[9]=2;chain[2]=9;reads=0;assert(FatXRootSize839(&d,&size)==STATUS_FILE_CORRUPT_ERROR && size==0 && reads<10);cases++;
 chain[1]=0;reads=0;assert(FatXRootSize839(&d,&size)==STATUS_FILE_CORRUPT_ERROR && !size);cases++;
 chain[1]=128;reads=0;assert(FatXRootSize839(&d,&size)==STATUS_FILE_CORRUPT_ERROR && !size);cases++;
 chain[1]=9;failAt=9;reads=0;assert(FatXRootSize839(&d,&size)==-77 && !size);cases++;
}
setup(&d,FATX32,0x80000000);chain[1]=2;chain[2]=0xffffffff;assert(FatXRootSize839(&d,&size)==STATUS_FILE_CORRUPT_ERROR && size==0);cases++;
setup(&d,FATX32,16384);cacheSize=16384;cache=calloc(1,cacheSize);assert(cache);root.RFCB.FileSize.QuadPart=cacheSize;pinned=0;
if(!setjmp(trap)){ReadVolumeLabelOld(&d,0,TRUE,&u);assert(0);}else assert(badsite==39 && badoff==0x4000 && !pinned);cases++;
maps=releases=0;assert(ReadVolumeLabelNew(&d,0,TRUE,&u)==0 && maps==4 && !pinned && releases==1);cases++;free(cache);
setup(&d,FAT16,16384);c=1;assert(NextCluster(&d,1,&c,FALSE)==0 && c==33);assert(OffsetToCluster(&d,1,32768,&c,FALSE)==0 && c==72);assert(ClusterToSector(&d,2)==40);cases++;
printf("PASS %u root-chain/EOF cases; old code reproduces site39/4000/40/4000\n",cases);return 0;}
'''
try:
 old=Path('/home/paul/xbox-windows-native/boot720838-source002/fatx/drivers/filesystems/vfatfs')
 h=(B/'vfat.h').read_text(encoding='latin1');macros='\n'.join(line for line in h.splitlines() if line.startswith(('#define ENTRY_','#define FAT_ENTRY_','#define FATX_ENTRY_','#define FAT_ENTRIES_PER_PAGE','#define FATX_ENTRIES_PER_PAGE')))
 code=stub+macros+'\n'+(B/'root839.c').read_text().replace('#include "vfat.h"','')
 for p,n,ret in [(B/'rw.c','NextCluster','NTSTATUS'),(B/'rw.c','OffsetToCluster','NTSTATUS'),(B/'fat.c','ClusterToSector','ULONGLONG'),(old/'fsctl.c','ReadVolumeLabel','NTSTATUS'),(B/'fsctl.c','ReadVolumeLabel','NTSTATUS')]:code+='\n'+function(p,n,ret)
 (O/'test.c').write_text(code+test);r['source_hashes']={n:sha(B/n) for n in ['root839.c','rw.c','fat.c','fsctl.c','fcb.c','vfat.h']}
 # Source-path review of actual I/O dispatch and cache-size construction.
 rw=(B/'rw.c').read_text(encoding='latin1');assert rw.count('if (FirstCluster == 1 && !vfatVolumeIsFatX(DeviceExt))')==4
 fcb=(B/'fcb.c').read_text(encoding='latin1');assert 'FCB->entry.FatX.FileSize = pVCB->FatXRootSize;' in fcb and 'Size = pVCB->FatXRootSize;' in fcb and 'Size = vfatVolumeIsFatX(Vcb) ? Vcb->FatXRootSize :' in fcb
 fs=(B/'fsctl.c').read_text(encoding='latin1');assert fs.index('Status = FatXRootSize839(')<fs.index('ReadVolumeLabel(DeviceExt, 0,')
 r['source_dispatch_and_size_audit']=True
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4';r['compiler_sha256']=sha(cc)
 c=subprocess.run([str(cc),'-O1','-g','-Wall','-Wextra','-fsanitize=address,undefined','-fno-pie','-no-pie',str(O/'test.c'),'-o',str(O/'test')],capture_output=True,timeout=60);(O/'build.log').write_bytes(c.stdout+c.stderr);assert c.returncode==0,c.stderr.decode()
 c=subprocess.run([str(O/'test')],capture_output=True,timeout=30);(O/'run.log').write_bytes(c.stdout+c.stderr);assert c.returncode==0,c.stderr.decode();r['result']=c.stdout.decode().strip();r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:
 r['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in O.iterdir() if p.is_file()};(K/'root001.json').write_text(json.dumps(r,indent=2)+'\n');print(r.get('result',r.get('error')))

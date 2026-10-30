"""Exercise actual FAT metadata routines with bounded cache-map substitutes."""
import hashlib,json,os,re,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;B=Path('/home/paul/xbox-windows-native/boot720839-source001');O=Path('/mnt/c/xwn839/fatpage002')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists();O.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'passed':False,'physical_access':False,'scope':'Actual eight FAT16/32 get/count/allocate/write routines with bounded memory cache substitutes; not NT cache-manager or disk-persistence qualification.'}
names=[f'FAT{bits}{op}' for bits in [16,32] for op in ['GetNextCluster','FindAndMarkAvailableCluster','CountAvailableClusters','WriteCluster']]
def extract(p):
 s=p.read_text();a=re.search(r'#define\s+CACHEPAGESIZE',s).start();b=s.index('\n\n',a);parts=[s[a:b]]
 for n in names:
  a=s.index('\n'+n+'(');a=s.rfind('\nNTSTATUS',0,a)+1;b=s.index('{',a);depth=1;i=b+1
  while depth:
   depth+=(s[i]=='{')-(s[i]=='}');i+=1
  parts.append(s[a:i])
 return '\n\n'.join(parts).replace('Cache837','Cache839')
stub=r'''
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <setjmp.h>
typedef uint32_t ULONG,*PULONG;typedef int32_t LONG,*PLONG;typedef uint16_t USHORT,*PUSHORT;
typedef uintptr_t ULONG_PTR;typedef void *PVOID;typedef int NTSTATUS;
typedef union {int64_t QuadPart;struct {uint32_t LowPart;int32_t HighPart;};} LARGE_INTEGER;
typedef struct {struct {ULONG FatType,BytesPerCluster,NumberOfClusters;} FatInfo;PVOID FATFileObject;ULONG LastAvailableCluster,AvailableClusters,AvailableClustersValid;} DEV,*PDEVICE_EXTENSION;
#define FAT16 16
#define FAT32 32
#define FATX16 116
#define FATX32 132
#define PAGE_SIZE 4096
#define ROUND_DOWN(v,a) ((v)&~((a)-1))
#define STATUS_SUCCESS 0
#define STATUS_DISK_FULL (-1)
#define STATUS_UNSUCCESSFUL (-2)
#define STATUS_FILE_CORRUPT_ERROR (-3)
#define MAP_WAIT 1
#define PIN_WAIT 1
#define TRUE 1
#define FALSE 0
#define ASSERT assert
#define NT_ASSERT assert
#define VFAT_BREAK_ON_CORRUPTION 1
#define DPRINT(...) ((void)0)
#define DPRINT1(...) ((void)0)
#define _SEH2_TRY if(1)
#define _SEH2_EXCEPT(x) else
#define _SEH2_YIELD(x) x
#define _SEH2_GetExceptionCode() (-99)
#define _SEH2_END
static struct {ULONG Flags;} global;
static typeof(global) *VfatGlobalData=&global;
static unsigned char *table;static ULONG size,dirty,pinned,maps,badsite,badoff,badlen;static jmp_buf trap;
static int Cache839Map(ULONG site,PVOID f,LARGE_INTEGER *o,ULONG n,ULONG fl,PVOID *c,PVOID *b){
 (void)f;(void)fl;maps++;if(o->QuadPart<0 || (uint64_t)o->QuadPart+n>size){badsite=site;badoff=o->LowPart;badlen=n;longjmp(trap,1);}
 assert(n && !(o->LowPart%4096));*c=table;*b=table+o->LowPart;pinned++;return 1;
}
#define Cache839Pin Cache839Map
static void CcUnpinData(PVOID c){assert(c==table && pinned);pinned--;}
static void CcSetDirtyPinnedData(PVOID c,PVOID t){(void)t;assert(c==table && pinned);dirty++;}
static LONG InterlockedDecrement(PLONG p){return --*p;}
'''
test=r'''
static void put(unsigned i,unsigned width,ULONG v){if(width==2)((PUSHORT)table)[i]=(USHORT)v;else((PULONG)table)[i]=v;}
static ULONG get(unsigned i,unsigned width){return width==2?((PUSHORT)table)[i]:((PULONG)table)[i];}
int main(void){DEV d={0};ULONG cases=0,next,old,cluster;unsigned widths[]={2,4};
#ifdef LEGACY
 size=0x132000;table=calloc(1,size);assert(table);d.FatInfo.FatType=FATX32;d.FatInfo.BytesPerCluster=16384;d.FatInfo.NumberOfClusters=size/4-14;
 if(!setjmp(trap)){FAT32CountAvailableClusters(&d);assert(0);}else{assert(badsite==29 && badoff==0x130000 && badlen==0x4000);puts("PASS old code reproduces site29/130000/4000/132000");}free(table);return 0;
#else
 if(setjmp(trap)){fprintf(stderr,"unexpected map overflow site=%u offset=%x len=%x size=%x\n",badsite,badoff,badlen,size);return 2;}
 for(unsigned wi=0;wi<2;wi++)for(unsigned kind=0;kind<2;kind++)for(unsigned cp=1;cp<=16;cp*=4)for(unsigned pages=1;pages<=17;pages++){
  unsigned w=widths[wi],fatx=kind,ft=fatx?(w==2?FATX16:FATX32):(w==2?FAT16:FAT32),chunk=cp*4096;
  size=pages*4096;if(!fatx)size=(size+chunk-1)/chunk*chunk;
  table=calloc(1,size);assert(table);memset(&d,0,sizeof(d));d.FatInfo.FatType=ft;d.FatInfo.BytesPerCluster=chunk;d.FatInfo.NumberOfClusters=size/w-14;
  unsigned end=d.FatInfo.NumberOfClusters+2,expected=0;ULONG marker=w==2?0xffff:(fatx?0xffffffff:0x0fffffff);
  for(unsigned i=0;i<size/w;i++)put(i,w,marker);
  for(unsigned i=2;i<end;i++){ULONG v=i%5?marker:0;put(i,w,v);expected+=v==0;}
  if(w==2)assert(FAT16CountAvailableClusters(&d)==0);else assert(FAT32CountAvailableClusters(&d)==0);
  assert(d.AvailableClustersValid && d.AvailableClusters==expected && !pinned);cases++;
  for(unsigned i=2;i<end;i++)put(i,w,marker);
  put(end-1,w,0);d.LastAvailableCluster=end-3;d.AvailableClusters=1;dirty=0;
  assert((w==2?FAT16FindAndMarkAvailableCluster(&d,&cluster):FAT32FindAndMarkAvailableCluster(&d,&cluster))==0);
  assert(cluster==end-1 && get(cluster,w)==marker && dirty==1 && d.AvailableClusters==0 && !pinned);cases++;
  assert((w==2?FAT16FindAndMarkAvailableCluster(&d,&cluster):FAT32FindAndMarkAvailableCluster(&d,&cluster))==STATUS_DISK_FULL && !pinned);cases++;
  put(2,w,0);d.LastAvailableCluster=end-1;d.AvailableClusters=1;
  assert((w==2?FAT16FindAndMarkAvailableCluster(&d,&cluster):FAT32FindAndMarkAvailableCluster(&d,&cluster))==0 && cluster==2 && !pinned);cases++;
  unsigned last=size/w-1;put(last,w,marker);assert((w==2?FAT16GetNextCluster(&d,last,&next):FAT32GetNextCluster(&d,last,&next))==0 && next==0xffffffff && !pinned);cases++;
  put(last,w,w==2?0xabcd:0xa0000123);dirty=0;
  assert((w==2?FAT16WriteCluster(&d,last,w==2?0x1234:0xb0000456,&old):FAT32WriteCluster(&d,last,0xb0000456,&old))==0);
  assert(old==(w==2?0xabcd:(fatx?0xa0000123:0x123)) && get(last,w)==(w==2?0x1234:(fatx?0xb0000456:0xa0000456)) && dirty==1 && !pinned);cases++;
  put(last,w,w==2?1234:0xa0000123);assert((w==2?FAT16GetNextCluster(&d,last,&next):FAT32GetNextCluster(&d,last,&next))==0 && next==(w==2?1234:(fatx?0xa0000123:0x123)));cases++;
  free(table);
 }
 size=0x132000;table=calloc(1,size);assert(table);memset(&d,0,sizeof(d));d.FatInfo.FatType=FATX32;d.FatInfo.BytesPerCluster=16384;d.FatInfo.NumberOfClusters=size/4-14;
 assert(FAT32CountAvailableClusters(&d)==0 && d.AvailableClusters==d.FatInfo.NumberOfClusters && !pinned);cases++;free(table);
 printf("PASS %u actual FAT routine cases; %u bounded cache maps\n",cases,maps);return 0;
#endif
}
'''
try:
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4';r['compiler_sha256']=sha(cc);r['sources']={};r['results']={}
 for name,p in [('before',Path('/home/paul/xbox-windows-native/boot720837-source001/fatx/drivers/filesystems/vfatfs/fat.c')),('after',B/'fatx/drivers/filesystems/vfatfs/fat.c')]:
  r['sources'][name]=sha(p);(O/(name+'.c')).write_text(stub+extract(p)+test)
  args=[str(cc),'-O1','-g','-Wall','-Wextra','-fsanitize=address,undefined','-fno-pie','-no-pie']+(['-DLEGACY'] if name=='before' else [])+[str(O/(name+'.c')),'-o',str(O/name)]
  c=subprocess.run(args,capture_output=True,timeout=60);(O/(name+'-build.log')).write_bytes(c.stdout+c.stderr);assert c.returncode==0,c.stderr.decode()
  c=subprocess.run([str(O/name)],capture_output=True,timeout=45);(O/(name+'-run.log')).write_bytes(c.stdout+c.stderr);assert c.returncode==0,c.stderr.decode();r['results'][name]=c.stdout.decode().strip()
 r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:
 r['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in O.iterdir() if p.is_file()};(K/'fatpage002.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r.get('results',r.get('error'))))

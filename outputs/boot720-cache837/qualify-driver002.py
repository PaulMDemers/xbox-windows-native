"""Compile actual diagnostic code with substituted kernel/cache/display calls."""
import hashlib,json,os,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn837/driver-host002')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists();O.mkdir(parents=True)
r={'passed':False,'physical_access':False,'scope':'Actual cache837.c/h with modeled kernel/cache APIs. No NT cache-manager emulation.'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stub=r'''
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <setjmp.h>
#include <assert.h>
#define NTHALAPI
typedef char *PCH;typedef void VOID,*PVOID;typedef uint32_t ULONG;typedef int32_t LONG,*PLONG;typedef uintptr_t ULONG_PTR;
typedef unsigned char *PUCHAR;typedef int BOOLEAN;
typedef union {long long QuadPart;struct {uint32_t LowPart;int32_t HighPart;};} LARGE_INTEGER,*PLARGE_INTEGER;
typedef struct {struct {LARGE_INTEGER FileSize;} RFCB;ULONG Flags;} VFATFCB,*PVFATFCB;
typedef struct {void *FsContext;} FILE_OBJECT,*PFILE_OBJECT;
typedef int KBUGCHECK_CALLBACK_RECORD;
#define NTAPI
#define UNREFERENCED_PARAMETER(x) ((void)(x))
static jmp_buf trap;static ULONG stop,args[4];static int forwarded,registered;static char display[1024];
static void HalDisplayString(char *s){assert(strlen(display)+strlen(s)<sizeof(display));strcat(display,s);}
static LONG InterlockedIncrement(volatile LONG *p){return ++*p;}
static LONG InterlockedExchange(PLONG p,LONG n){LONG old=*p;*p=n;return old;}
static void KeInitializeCallbackRecord(KBUGCHECK_CALLBACK_RECORD *r){*r=0;}
static int KeRegisterBugCheckCallback(KBUGCHECK_CALLBACK_RECORD *r,void (*cb)(void *,ULONG),void *b,ULONG n,PUCHAR name){(void)r;(void)cb;(void)b;(void)n;(void)name;registered++;return 1;}
static void KeBugCheckEx(ULONG c,ULONG_PTR a,ULONG_PTR b,ULONG_PTR d,ULONG_PTR e){stop=c;args[0]=a;args[1]=b;args[2]=d;args[3]=e;longjmp(trap,1);}
static int CcMapData(PFILE_OBJECT f,PLARGE_INTEGER o,ULONG n,ULONG flags,PVOID *b,PVOID *p){(void)f;(void)o;(void)n;(void)flags;*b=(void *)1;*p=(void *)2;forwarded++;return 1;}
#define CcPinRead CcMapData
'''
test=r'''
int main(void){unsigned cases=0;VFATFCB f={0};FILE_OBJECT file={&f};LARGE_INTEGER off;void *b=0,*p=0;
Cache837Initialize();assert(registered==1);
struct Case {long long o,s;unsigned n,bad;} v[]={
{0,16384,4096,0},{12288,16384,4096,0},{16384,16384,1,1},{0,1,4096,0},{4096,1,1,1},
{-1,4096,1,1},{0,-1,1,1},{0,0,1,1},{0,0,0,0},{0xfffff000LL,16384,4096,1},
{0x100000000LL,0x100001000LL,4096,0},{0x100001000LL,0x100001000LL,1,1},
{0,0x80000000LL,0xffffffffU,1},{0x7ffffffffffff000LL,0x7fffffffffffffffLL,4096,0}};
for(unsigned i=0;i<sizeof(v)/sizeof(v[0]);i++){
 assert(cache837_bad(v[i].o,v[i].n,v[i].s)==v[i].bad);cases++;
 f.RFCB.FileSize.QuadPart=v[i].s;off.QuadPart=v[i].o;int before=forwarded;
 if(!setjmp(trap)){assert(Cache837Map(i+1,&file,&off,v[i].n,1,&b,&p)==1);assert(!v[i].bad);assert(forwarded==before+1 && b==(void *)1 && p==(void *)2);}
 else {assert(v[i].bad && stop==0xE8370001 && args[0]==i+1 && args[1]==off.LowPart && args[2]==v[i].n && args[3]==f.RFCB.FileSize.LowPart);assert(forwarded==before);}
 cases++;
}
f.RFCB.FileSize.QuadPart=4096;off.QuadPart=0;
for(unsigned i=0;i<32;i++){assert(Cache837Pin(100+i,&file,&off,4096,1,&b,&p));cases++;}
callback837(NULL,0);assert(strstr(display,"XWN837:") && strstr(display,"00000083"));cases++;
file.FsContext=NULL;if(!setjmp(trap)){Cache837Map(999,&file,&off,1,1,&b,&p);assert(0);}else assert(stop==0xE8370003 && args[0]==999);cases++;
printf("PASS %u actual diagnostic cases\n",cases);return 0;}
'''
try:
 (O/'vfat.h').write_text(stub)
 for n in ['cache837.c','cache837.h']:(O/n).write_bytes((K/n).read_bytes())
 (O/'test.c').write_text('#include "cache837.c"\n'+test)
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 r['compiler_sha256']=sha(cc);r['sources']={n:sha(K/n) for n in ['cache837.c','cache837.h']}
 p=subprocess.run([str(cc),'-O1','-Wall','-Wextra','-fsanitize=address,undefined',str(O/'test.c'),'-o',str(O/'test')],capture_output=True,timeout=60);(O/'build.log').write_bytes(p.stdout+p.stderr);assert not p.returncode,p.stderr.decode()
 p=subprocess.run([str(O/'test')],capture_output=True,timeout=15);(O/'run.log').write_bytes(p.stdout+p.stderr);assert not p.returncode,p.stderr.decode();r['result']=p.stdout.decode().strip();r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:
 r['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in O.iterdir() if p.is_file()};(K/'driver-host002.json').write_text(json.dumps(r,indent=2)+'\n');print(r.get('result',r.get('error')))

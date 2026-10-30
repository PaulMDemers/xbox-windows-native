"""Exercise actual load841 observation code with substituted NT interfaces."""
from pathlib import Path
import os,json,subprocess,hashlib
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn841/load-host002')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists();O.mkdir(parents=True)
r={'passed':False,'physical_access':False,'scope':'Actual observer C with host substitutes; not Windows image-loader validation'}
stub=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>
typedef uint32_t ULONG;typedef int32_t LONG,NTSTATUS;typedef unsigned short WCHAR;
typedef void VOID,*PVOID,*HANDLE;typedef unsigned char *PUCHAR;typedef char *PCH;
typedef struct{unsigned short Length,MaximumLength;WCHAR *Buffer;} UNICODE_STRING,*PUNICODE_STRING;
typedef union{long long QuadPart;struct{ULONG LowPart;LONG HighPart;};} LARGE_INTEGER;
typedef struct{struct{LARGE_INTEGER FileSize;}RFCB;} VFATFCB,*PVFATFCB;
typedef struct{UNICODE_STRING FileName;void *FsContext;}FILE_OBJECT,*PFILE_OBJECT;
typedef struct{ULONG Flags;struct{uintptr_t Information;}IoStatus;}IRP;
typedef struct{PFILE_OBJECT FileObject;IRP *Irp;}VFAT_IRP_CONTEXT,*PVFAT_IRP_CONTEXT;
typedef struct{unsigned SystemModeImage;}IMAGE_INFO,*PIMAGE_INFO;
typedef int KBUGCHECK_CALLBACK_RECORD;
#define NTHALAPI
#define NTAPI
#define TRUE 1
#define IRP_PAGING_IO 2
#define NT_SUCCESS(s) ((s)>=0)
#define UNREFERENCED_PARAMETER(x) ((void)(x))
static unsigned char buffer[1024];static char display[4096];static int callbacks,notify;
static NTSTATUS simulated_notify_status;
static PUCHAR VfatGetUserBuffer(IRP *p,int paging){(void)p;assert(paging);return buffer;}
static LONG InterlockedIncrement(volatile LONG *p){return ++*p;}
static NTSTATUS PsSetLoadImageNotifyRoutine(void (*f)(PUNICODE_STRING,HANDLE,PIMAGE_INFO)){assert(f);notify++;return simulated_notify_status;}
static void KeInitializeCallbackRecord(KBUGCHECK_CALLBACK_RECORD *p){*p=0;}
static int KeRegisterBugCheckCallback(KBUGCHECK_CALLBACK_RECORD *p,void (*f)(PVOID,ULONG),void *b,ULONG n,PUCHAR name){(void)p;assert(f&&b&&n&&name);callbacks++;return 1;}
static void KeBugCheckEx(ULONG a,ULONG b,ULONG c,ULONG d,ULONG e){(void)a;(void)b;(void)c;(void)d;(void)e;abort();}
static void HalDisplayString(PCH s){assert(strlen(s)+strlen(display)<sizeof(display));strcat(display,s);}
'''
tests=r'''
static UNICODE_STRING name(WCHAR *s){UNICODE_STRING n={0,0,s};while(s[n.Length/2])n.Length+=2;return n;}
int main(void){unsigned cases=0;Load841Initialize();assert(callbacks==1&&notify==1&&NotifyStatus841==0);cases++;
WCHAR *names[]={L"xboxvnt5.sys",L"\\WINNT\\System32\\DRIVERS\\XBOXVNT5.SYS",L"/System32/VideoPrt.Sys",L"xwnown.dll",L"axboxvnt5.sys",L"xboxvnt5.sys.old",L"",L"\\abc\\ntoskrnl.exe"};
unsigned expected[]={0,0,1,2,3,3,3,3};
for(unsigned i=0;i<8;i++){UNICODE_STRING n=name(names[i]);assert(identify841(&n)==expected[i]);cases++;}
assert(identify841(NULL)==3);cases++;
UNICODE_STRING n=name(names[0]);n.Length--;assert(identify841(&n)==3);cases++;
VFATFCB f={0};FILE_OBJECT file={name(names[1]),&f};IRP irp={IRP_PAGING_IO,{512}};VFAT_IRP_CONTEXT ctx={&file,&irp};LARGE_INTEGER off;off.QuadPart=0;
f.RFCB.FileSize.QuadPart=511;memset(buffer,0x97,sizeof(buffer));buffer[511]=0;
Load841Open(&file,0);assert(LoadRows841[0].Opens==1&&LoadRows841[0].OpenStatus==0);cases++;
Load841Read(&ctx,0,512,off);assert(LoadRows841[0].Reads==1&&LoadRows841[0].Size==511&&LoadRows841[0].Tail==0&&buffer[510]==0x97&&buffer[512]==0x97);cases++;
Load841Read(&ctx,(NTSTATUS)0xc0000001,512,off);assert(LoadRows841[0].Returned==0&&LoadRows841[0].Tail==0xffffffff&&LoadRows841[0].ReadStatus==0xc0000001);cases++;
irp.Flags=0;Load841Read(&ctx,0,512,off);assert(LoadRows841[0].Tail==0xffffffff);cases++;
IMAGE_INFO info={1};image841(&file.FileName,NULL,&info);assert(LoadRows841[0].Images==1);cases++;
image841(&file.FileName,(HANDLE)1,&info);assert(LoadRows841[0].Images==1);cases++;
info.SystemModeImage=0;image841(&file.FileName,NULL,&info);assert(LoadRows841[0].Images==1);cases++;
dump841(NULL,0);assert(strstr(display,"LOAD841")&&strstr(display,"FFFFFFFF"));cases++;
simulated_notify_status=(NTSTATUS)0xc000009a;Load841Initialize();assert(NotifyStatus841==simulated_notify_status);cases++;
printf("PASS %u actual display-load observation cases\n",cases);return 0;}
'''
try:
 (O/'vfat.h').write_text(stub);(O/'load841.c').write_bytes((K/'load841.c').read_bytes());(O/'test.c').write_text('#include "load841.c"\n'+tests)
 cc=Path('/usr/bin/gcc-12').resolve();assert hashlib.sha256(cc.read_bytes()).hexdigest()=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 p=subprocess.run([str(cc),'-O1','-Wall','-Wextra','-fshort-wchar','-fsanitize=address,undefined',str(O/'test.c'),'-o',str(O/'test')],capture_output=True,timeout=60);(O/'build.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0,p.stderr.decode()
 p=subprocess.run([str(O/'test')],capture_output=True,timeout=15);(O/'run.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0,p.stderr.decode()
 r['result']=p.stdout.decode();r['source_sha256']=hashlib.sha256((K/'load841.c').read_bytes()).hexdigest();r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:
 r['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in O.iterdir() if p.is_file()};(K/'load-host002.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['result'])

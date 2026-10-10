"""Compile the actual usb() body under a deterministic NT-style lifetime shim.
Not a concurrency proof or substitute for guest/hardware PnP tests.
"""
import hashlib,json,os,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent
src=(k/'driver.c').read_text()
start=src.index('static NTSTATUS usb(');end=src.index('\nstatic NTSTATUS lower_sync',start)
function=src[start:end]
out=k/'artifacts'/sys.argv[1]/'host-tests';out.mkdir(parents=True,exist_ok=False)
prefix=r'''
#include <assert.h>
#include <setjmp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef int32_t NTSTATUS;
typedef unsigned long ULONG;
typedef long long LONGLONG;
typedef struct {long long QuadPart;} LARGE_INTEGER;
typedef struct {int set;} KEVENT;
typedef struct {struct {int Function;NTSTATUS Status;} UrbHeader;} URB,*PURB;
typedef struct {int MajorFunction;struct {struct {ULONG IoControlCode;} DeviceIoControl;struct {void *Argument1;} Others;} Parameters;} STACK,*PIO_STACK_LOCATION;
typedef struct {int RequestorMode;struct {NTSTATUS Status;} IoStatus;STACK next;KEVENT *event;int completed,live;} IRP,*PIRP;
typedef struct {int StackSize;} LOWER;
typedef struct {LOWER *Lower;} DEVICE;
#define FALSE 0
#define TRUE 1
#define NotificationEvent 0
#define KernelMode 0
#define Executive 0
#define IRP_MJ_INTERNAL_DEVICE_CONTROL 15
#define IOCTL_INTERNAL_USB_SUBMIT_URB 2228227
#define STATUS_SUCCESS 0
#define STATUS_TIMEOUT 258
#define STATUS_PENDING 259
#define STATUS_NOT_SUPPORTED ((int32_t)0xc00000bb)
#define STATUS_INSUFFICIENT_RESOURCES ((int32_t)0xc000009a)
#define STATUS_IO_TIMEOUT ((int32_t)0xc00000b5)
#define STATUS_IO_DEVICE_ERROR ((int32_t)0xc0000185)
#define NT_SUCCESS(s) ((s)>=0)
#define USBD_SUCCESS(s) ((s)>=0)
#define signal_done 0
static IRP request;static int mode,waits,cancels,frees,calls;static jmp_buf stuck;
static PIRP IoAllocateIrp(int size,int quota) {(void)quota;assert(size==4);if(mode==0)return NULL;request.live=1;return &request;}
static void KeInitializeEvent(KEVENT *e,int kind,int value){(void)kind;e->set=value;}
static PIO_STACK_LOCATION IoGetNextIrpStackLocation(PIRP p){return &p->next;}
static void IoSetCompletionRoutine(PIRP p,int f,KEVENT *e,int a,int b,int c){assert(!f && a && b && c);p->event=e;}
static void complete(NTSTATUS status){assert(request.live && !request.completed);request.completed=1;request.IoStatus.Status=status;request.event->set=1;}
static NTSTATUS IoCallDriver(LOWER *l,PIRP p){
 assert(l->StackSize==4 && p->live);calls++;
 assert(p->next.MajorFunction==15 && p->next.Parameters.DeviceIoControl.IoControlCode==2228227);
 if(mode==1)complete(0);if(mode==2)complete(STATUS_NOT_SUPPORTED);
 if(mode==3){((PURB)p->next.Parameters.Others.Argument1)->UrbHeader.Status=-1;complete(0);}
 return mode<4?request.IoStatus.Status:STATUS_PENDING;
}
static NTSTATUS KeWaitForSingleObject(KEVENT *e,int why,int kind,int alert,LARGE_INTEGER *due){
 (void)why;(void)kind;assert(!alert && request.live);waits++;
 if(due){assert(due->QuadPart==-1000000);if(mode==4)complete(0);if(mode==5)complete(STATUS_NOT_SUPPORTED);
   if(mode==7){complete(0);return STATUS_TIMEOUT;} /* completion just after timeout */
   return e->set?0:STATUS_TIMEOUT;}
 assert(cancels==1);if(mode==8){assert(!frees && request.live);longjmp(stuck,1);}
 assert(e->set);return 0;
}
static void IoCancelIrp(PIRP p){assert(p->live);cancels++;if(!p->completed && mode!=8)complete(STATUS_NOT_SUPPORTED);}
static void IoFreeIrp(PIRP p){assert(p->live && p->completed && p->event->set);p->live=0;frees++;}
'''
suffix=r'''
int main(void){LOWER lower={4};DEVICE d={&lower};int tests=0;URB u;NTSTATUS s;
 for(mode=0;mode<9;mode++){
  memset(&request,0,sizeof(request));memset(&u,0,sizeof(u));waits=cancels=frees=calls=0;
  if(setjmp(stuck)){assert(mode==8 && !frees && request.live && cancels==1);tests++;continue;}
  s=usb(&d,&u,100);
  if(mode==0)assert(s==STATUS_INSUFFICIENT_RESOURCES && !calls && !frees);
  else{assert(frees==1 && calls==1 && !request.live);
   if(mode==1 || mode==4)assert(s==0 && !cancels);
   if(mode==2 || mode==5)assert(s==STATUS_NOT_SUPPORTED && !cancels);
   if(mode==3)assert(s==STATUS_IO_DEVICE_ERROR && !cancels);
   if(mode==6 || mode==7)assert(s==STATUS_IO_TIMEOUT && cancels==1 && waits==2);
  }tests++;
 }printf("PASS %d actual transport fault schedules\n",tests);return 0;}
'''
(out/'transport.c').write_text(prefix+function+suffix)
gcc='C:/msys64/mingw64/bin/gcc.exe'
os.environ['PATH']=str(Path(gcc).parent)+';'+os.environ['PATH']
subprocess.run([gcc,'-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-clobbered',str(out/'transport.c'),'-o',str(out/'transport.exe')],check=True)
result=subprocess.check_output([str(out/'transport.exe')],text=True)
assert result.startswith('PASS 9 ')
(k/'transport-tests.json').write_text(json.dumps(dict(passed=True,result=result.strip(),driver_sha256=hashlib.sha256(src.encode()).hexdigest(),actual_usb_body_sha256=hashlib.sha256(function.encode()).hexdigest(),scope='Nine deterministic schedules of actual usb() body: allocation failure; sync/async success/failure; USB failure; cancel/drain; timeout-completion race; missing drain retains memory. No IRQ/concurrency/PnP qualification.'),indent=2)+'\n')
print(result.strip())

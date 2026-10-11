/* Execute actual native dispatch with mocked NT primitives, not NT5 ABI proof. */
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "driver.c"
static int Locked,FailWait,Elevated,Freed,Completed;
static void *Memory;
int KeGetCurrentIrql(void){return Elevated;}
NTSTATUS KeWaitForSingleObject(void *p,int a,int b,int c,LARGE_INTEGER *t)
{(void)p;(void)a;(void)b;(void)c;assert(t->QuadPart==-20000000);if(FailWait)return STATUS_TIMEOUT;assert(!Locked);Locked=1;return STATUS_SUCCESS;}
void KeReleaseMutex(KMUTEX *p,int b){(void)p;(void)b;assert(Locked);Locked=0;}
void KeInitializeMutex(KMUTEX *p,ULONG b){(void)p;(void)b;}
void *MmAllocateContiguousMemorySpecifyCache(ULONG n,PHYSICAL_ADDRESS l,PHYSICAL_ADDRESS h,PHYSICAL_ADDRESS b,int c)
{assert(n==16384 && l.QuadPart==0x100000 && h.QuadPart==0x03bfffff && !b.QuadPart && c==MmNonCached && !Memory);return Memory=malloc(n);}
PHYSICAL_ADDRESS MmGetPhysicalAddress(void *p){PHYSICAL_ADDRESS a={0x200000+(unsigned char *)p-(unsigned char *)Memory};return a;}
void MmFreeContiguousMemorySpecifyCache(void *p,ULONG n,int c){assert(p==Memory && n==16384 && c==MmNonCached);Freed++;free(p);Memory=NULL;}
void ObReferenceObject(void *p){((FILE_OBJECT *)p)->refs++;}
void IoCompleteRequest(PIRP i,int n){assert(!i->completed && n==IO_NO_INCREMENT);i->completed=1;Completed++;}
void RtlInitUnicodeString(PUNICODE_STRING u,const void *p){(void)u;assert(p);}
NTSTATUS IoCreateDevice(PDRIVER_OBJECT d,ULONG e,PUNICODE_STRING n,ULONG t,ULONG c,int x,PDEVICE_OBJECT *o)
{static DEVICE_OBJECT dev;(void)d;(void)e;(void)n;(void)t;(void)c;(void)x;*o=&dev;return STATUS_SUCCESS;}
NTSTATUS IoCreateSymbolicLink(PUNICODE_STRING a,PUNICODE_STRING b){(void)a;(void)b;return STATUS_SUCCESS;}
void IoDeleteDevice(PDEVICE_OBJECT p){(void)p;}
static X258Reply Reply;
static NTSTATUS send(FILE_OBJECT *f,unsigned major,unsigned op,unsigned gen,unsigned seed,unsigned in,unsigned out)
{
 IRP i={0};X258Request q={op,gen,seed,0};memset(&Reply,0xcc,sizeof(Reply));memcpy(&Reply,&q,sizeof(q));
 i.stack.MajorFunction=major;i.stack.FileObject=f;i.AssociatedIrp.SystemBuffer=&Reply;
 i.stack.Parameters.DeviceIoControl.IoControlCode=X258_IOCTL;
 i.stack.Parameters.DeviceIoControl.InputBufferLength=in;i.stack.Parameters.DeviceIoControl.OutputBufferLength=out;
 NTSTATUS s=dispatch(NULL,&i);assert(i.completed && s==i.IoStatus.Status);
 assert(i.IoStatus.Information==(major==IRP_MJ_DEVICE_CONTROL && s==STATUS_SUCCESS?sizeof(Reply):0));return s;
}
#define CALL(f,op,gen,seed) send(f,IRP_MJ_DEVICE_CONTROL,op,gen,seed,sizeof(X258Request),sizeof(Reply))
int main(void)
{
 DRIVER_OBJECT d={0};UNICODE_STRING path;FILE_OBJECT f={.refs=1},other={.refs=1};
 assert(DriverEntry(&d,&path)==STATUS_SUCCESS && !d.DriverUnload);
 assert(send(&f,IRP_MJ_DEVICE_CONTROL,1,0,0,sizeof(X258Request)-1,sizeof(Reply))==STATUS_INVALID_PARAMETER && !Memory);
 assert(send(&f,IRP_MJ_DEVICE_CONTROL,1,0,0,sizeof(X258Request),sizeof(Reply)-1)==STATUS_INVALID_PARAMETER && !Memory);
 assert(CALL(&f,X258_ALLOCATE,0,0)==STATUS_SUCCESS && Reply.status==X258_OK && f.refs==2);
 assert(CALL(&f,X258_WRITE,1,2)==STATUS_SUCCESS && Reply.status==X258_OK);
 assert(CALL(&f,X258_READ,1,0)==STATUS_SUCCESS && Reply.status==X258_OK);
 for(unsigned n=0;n<X258_BYTES;n++)assert(Reply.data[n]==(unsigned char)((n*37u+(n/16)*19u+(n/256)*7u)^166u));
 assert(CALL(&other,X258_READ,1,0)==STATUS_SUCCESS && Reply.status==X258_OWNER && !Reply.physical && !Reply.bytes);
 for(unsigned n=0;n<X258_BYTES;n++)assert(!Reply.data[n]);
 FailWait=1;assert(send(&f,IRP_MJ_CLEANUP,0,0,0,0,0)==STATUS_UNSUCCESSFUL);assert(Memory && !Freed && f.refs==2);FailWait=0;
 Elevated=2;assert(send(&f,IRP_MJ_CLEANUP,0,0,0,0,0)==STATUS_UNSUCCESSFUL);assert(Memory && !Freed);Elevated=0;
 assert(send(&f,IRP_MJ_CLEANUP,0,0,0,0,0)==STATUS_SUCCESS && Arena.closed);
 assert(send(&f,IRP_MJ_CLOSE,0,0,0,0,0)==STATUS_SUCCESS && Memory && !Freed && f.refs==2);
 assert(CALL(&f,X258_READ,1,0)==STATUS_SUCCESS && Reply.status==X258_QUARANTINED);
 assert(CALL(&other,X258_ALLOCATE,0,0)==STATUS_SUCCESS && Reply.status==X258_BUSY);
 free(Memory);printf("PASS actual_bridge completions=%d bytes=16384 held_until_reboot=1\n",Completed);
}

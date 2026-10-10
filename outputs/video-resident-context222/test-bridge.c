/* Execute actual driver.c with host substitutes. No NT5 runtime/ABI claim. */
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include "driver.c"
static int FailWait,WaitCalls,Locked,Elevated,QueueCount,Completed,WorkItems;
static void *Allocation;
static PIO_WORKITEM QueuedWork;
static void (*QueuedCallback)(PDEVICE_OBJECT,PVOID);
static void *QueuedParameter;
int KeGetCurrentIrql(void){return Elevated;}
NTSTATUS KeWaitForSingleObject(void *o,int a,int b,int c,LARGE_INTEGER *t){(void)o;(void)a;(void)b;(void)c;assert(t->QuadPart==-20000000);WaitCalls++;if(FailWait){FailWait--;return STATUS_TIMEOUT;}assert(!Locked);Locked=1;return STATUS_SUCCESS;}
void KeReleaseMutex(KMUTEX *m,int b){(void)m;(void)b;assert(Locked);Locked=0;}
void KeInitializeMutex(KMUTEX *m,ULONG b){(void)m;(void)b;}
void *MmAllocateContiguousMemorySpecifyCache(ULONG n,PHYSICAL_ADDRESS l,PHYSICAL_ADDRESS h,PHYSICAL_ADDRESS b,int c){assert(n==16384 && l.QuadPart==0x100000 && h.QuadPart==0x03bfffff && !b.QuadPart && c==MmNonCached && !Allocation);return Allocation=malloc(n);}
PHYSICAL_ADDRESS MmGetPhysicalAddress(void *p){PHYSICAL_ADDRESS a={0x200000+(unsigned char *)p-(unsigned char *)Allocation};return a;}
void MmFreeContiguousMemorySpecifyCache(void *p,ULONG n,int c){assert(p==Allocation && n==16384 && c==MmNonCached);free(p);Allocation=NULL;}
void ObReferenceObject(void *p){FILE_OBJECT *f=p;assert(f->refs);f->refs++;}
void ObDereferenceObject(void *p){FILE_OBJECT *f=p;assert(f->refs>1);f->refs--;}
void *ExAllocatePoolWithTag(int pool,size_t n,ULONG tag){assert(pool==NonPagedPool && tag==0x32323258);return calloc(1,n);}
void ExFreePool(void *p){free(p);}
PIO_WORKITEM IoAllocateWorkItem(PDEVICE_OBJECT d){PIO_WORKITEM w=malloc(sizeof(*w));assert(w);w->device=d;WorkItems++;return w;}
void IoFreeWorkItem(PIO_WORKITEM w){assert(w && WorkItems);WorkItems--;free(w);}
void IoMarkIrpPending(PIRP i){assert(!i->completed);i->pending=1;}
void IoQueueWorkItem(PIO_WORKITEM w,void (*f)(PDEVICE_OBJECT,PVOID),int q,PVOID p){assert(!QueuedWork && q==DelayedWorkQueue && ((PIRP)p)->pending);QueuedWork=w;QueuedCallback=f;QueuedParameter=p;QueueCount++;}
void IoCompleteRequest(PIRP i,int n){assert(!i->completed && n==IO_NO_INCREMENT);i->completed=1;Completed++;}
void RtlInitUnicodeString(PUNICODE_STRING u,const void *p){(void)u;assert(p);}
NTSTATUS IoCreateDevice(PDRIVER_OBJECT d,ULONG e,PUNICODE_STRING n,ULONG t,ULONG c,int x,PDEVICE_OBJECT *out){static DEVICE_OBJECT v;(void)d;(void)e;(void)n;(void)t;(void)c;(void)x;*out=&v;return STATUS_SUCCESS;}
NTSTATUS IoCreateSymbolicLink(PUNICODE_STRING a,PUNICODE_STRING b){(void)a;(void)b;return STATUS_SUCCESS;}
void IoDeleteDevice(PDEVICE_OBJECT d){(void)d;}
static void finish_queue(void){PIO_WORKITEM w=QueuedWork;void (*f)(PDEVICE_OBJECT,PVOID)=QueuedCallback;void *p=QueuedParameter;assert(w);QueuedWork=NULL;f(w->device,p);}
static IRP request(unsigned major,PFILE_OBJECT f){IRP i={0};i.stack.MajorFunction=major;i.stack.FileObject=f;return i;}
int main(void)
{
    DRIVER_OBJECT d={0};UNICODE_STRING u={0};DEVICE_OBJECT device={0};FILE_OBJECT owner={.refs=1},other={.refs=1};
    assert(DriverEntry(&d,&u)==STATUS_SUCCESS && !d.DriverUnload);
    IRP create=request(IRP_MJ_CREATE,&owner);assert(dispatch(&device,&create)==STATUS_SUCCESS && owner.FsContext);
    create=request(IRP_MJ_CREATE,&other);assert(dispatch(&device,&create)==STATUS_SUCCESS && WorkItems==2);
    X222Request q={X222_ALLOCATE,0};X222Reply reply;
    x222_action(&Manager,&Ops,&owner,&q,&reply);assert(reply.status==X222_OK && owner.refs==2);
    IRP clean=request(IRP_MJ_CLEANUP,&owner);FailWait=3;int start=WaitCalls;
    assert(dispatch(&device,&clean)==STATUS_PENDING && clean.pending && !clean.completed && owner.refs==3);
    finish_queue();assert(clean.completed && clean.IoStatus.Status==STATUS_SUCCESS && WaitCalls-start==4 && !Allocation && owner.refs==1);
    x222_action(&Manager,&Ops,&owner,&q,&reply);assert(reply.status==X222_OK);
    clean=request(IRP_MJ_CLEANUP,&owner);FailWait=9;start=WaitCalls;
    assert(dispatch(&device,&clean)==STATUS_PENDING);finish_queue();
    assert(clean.completed && clean.IoStatus.Status==STATUS_UNSUCCESSFUL && WaitCalls-start==9 && Allocation && owner.refs==2);
    X222Request foreign={X222_CLEANUP,0};x222_action(&Manager,&Ops,&other,&foreign,&reply);assert(reply.status==X222_OWNER && owner.refs==2);
    x222_action(&Manager,&Ops,&owner,&foreign,&reply);assert(reply.status==X222_OK && !Allocation && owner.refs==1);
    x222_action(&Manager,&Ops,&owner,&q,&reply);assert(reply.status==X222_OK);
    clean=request(IRP_MJ_CLEANUP,&owner);Elevated=1;
    assert(dispatch(&device,&clean)==STATUS_PENDING);Elevated=0;finish_queue();
    assert(clean.completed && clean.IoStatus.Status==STATUS_SUCCESS && !Allocation && owner.refs==1);
    clean=request(IRP_MJ_CLEANUP,&other);assert(dispatch(&device,&clean)==STATUS_SUCCESS);
    IRP close=request(IRP_MJ_CLOSE,&owner);assert(dispatch(&device,&close)==STATUS_SUCCESS && !owner.FsContext);
    close=request(IRP_MJ_CLOSE,&other);assert(dispatch(&device,&close)==STATUS_SUCCESS && !other.FsContext);
    assert(!WorkItems && !Locked && !QueuedWork && QueueCount==3 && Manager.allocations==3 && Manager.releases==3 && Manager.cleanup_releases==3);
    printf("PASS actual_driver_bridge retries=3 exhaustion=8 elevated_defer=1 references_balanced=1 workitems=0 completed=%d\n",Completed);
    return 0;
}

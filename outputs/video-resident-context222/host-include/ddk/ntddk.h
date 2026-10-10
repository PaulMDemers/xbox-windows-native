/* Host-only ABI substitutes for executing the unchanged native bridge logic.
 * Not an NT5 ABI, scheduler, object-manager or residency qualification. */
#ifndef X222_HOST_NTDDK
#define X222_HOST_NTDDK
#include <stdint.h>
#include <stddef.h>
#define NTAPI
typedef void VOID,*PVOID;
typedef uint32_t ULONG;
typedef int32_t NTSTATUS;
typedef struct { int64_t QuadPart; } LARGE_INTEGER,PHYSICAL_ADDRESS;
typedef struct { int unused; } KMUTEX,UNICODE_STRING,*PUNICODE_STRING;
typedef struct { ULONG Flags; } DEVICE_OBJECT,*PDEVICE_OBJECT;
typedef struct { void *FsContext; unsigned refs; } FILE_OBJECT,*PFILE_OBJECT;
typedef struct {
    unsigned MajorFunction; PFILE_OBJECT FileObject;
    struct { struct { ULONG IoControlCode,InputBufferLength,OutputBufferLength; } DeviceIoControl; } Parameters;
} IO_STACK_LOCATION,*PIO_STACK_LOCATION;
typedef struct {
    IO_STACK_LOCATION stack;
    struct { void *SystemBuffer; } AssociatedIrp;
    struct { NTSTATUS Status; ULONG Information; } IoStatus;
    int pending,completed;
} IRP,*PIRP;
typedef struct IO_WORKITEM { PDEVICE_OBJECT device; } IO_WORKITEM,*PIO_WORKITEM;
typedef NTSTATUS (*DISPATCH)(PDEVICE_OBJECT,PIRP);
typedef struct { DISPATCH MajorFunction[28]; void *DriverUnload; } DRIVER_OBJECT,*PDRIVER_OBJECT;
#define IRP_MJ_CREATE 0
#define IRP_MJ_CLOSE 2
#define IRP_MJ_DEVICE_CONTROL 14
#define IRP_MJ_CLEANUP 18
#define IRP_MJ_MAXIMUM_FUNCTION 27
#define STATUS_SUCCESS 0
#define STATUS_PENDING 0x103
#define STATUS_TIMEOUT 0x102
#define STATUS_UNSUCCESSFUL ((NTSTATUS)0xc0000001)
#define STATUS_INSUFFICIENT_RESOURCES ((NTSTATUS)0xc000009a)
#define STATUS_INVALID_DEVICE_REQUEST ((NTSTATUS)0xc0000010)
#define STATUS_INVALID_PARAMETER ((NTSTATUS)0xc000000d)
#define NT_SUCCESS(s) ((s)>=0)
#define PASSIVE_LEVEL 0
#define Executive 0
#define KernelMode 0
#define FALSE 0
#define NonPagedPool 0
#define MmNonCached 0
#define DelayedWorkQueue 0
#define IO_NO_INCREMENT 0
#define DO_DEVICE_INITIALIZING 0x80
#define FILE_DEVICE_UNKNOWN 0x22
#define METHOD_BUFFERED 0
#define FILE_WRITE_ACCESS 2
#define CTL_CODE(d,f,m,a) (((d)<<16)|((a)<<14)|((f)<<2)|(m))
#define IoGetCurrentIrpStackLocation(i) (&(i)->stack)
int KeGetCurrentIrql(void);
NTSTATUS KeWaitForSingleObject(void *,int,int,int,LARGE_INTEGER *);
void KeReleaseMutex(KMUTEX *,int);
void KeInitializeMutex(KMUTEX *,ULONG);
void *MmAllocateContiguousMemorySpecifyCache(ULONG,PHYSICAL_ADDRESS,PHYSICAL_ADDRESS,PHYSICAL_ADDRESS,int);
PHYSICAL_ADDRESS MmGetPhysicalAddress(void *);
void MmFreeContiguousMemorySpecifyCache(void *,ULONG,int);
void ObReferenceObject(void *);
void ObDereferenceObject(void *);
void *ExAllocatePoolWithTag(int,size_t,ULONG);
void ExFreePool(void *);
PIO_WORKITEM IoAllocateWorkItem(PDEVICE_OBJECT);
void IoFreeWorkItem(PIO_WORKITEM);
void IoMarkIrpPending(PIRP);
void IoQueueWorkItem(PIO_WORKITEM,void (*)(PDEVICE_OBJECT,PVOID),int,PVOID);
void IoCompleteRequest(PIRP,int);
void RtlInitUnicodeString(PUNICODE_STRING,const void *);
NTSTATUS IoCreateDevice(PDRIVER_OBJECT,ULONG,PUNICODE_STRING,ULONG,ULONG,int,PDEVICE_OBJECT *);
NTSTATUS IoCreateSymbolicLink(PUNICODE_STRING,PUNICODE_STRING);
void IoDeleteDevice(PDEVICE_OBJECT);
#endif

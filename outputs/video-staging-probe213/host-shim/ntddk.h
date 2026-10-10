/* Host-only fault injection shim; never supplied to an NT5 build. */
#ifndef XGT_HOST_NTDDK
#define XGT_HOST_NTDDK
#include <stdint.h>
#include <stddef.h>
typedef uint32_t ULONG;typedef uint64_t ULONGLONG;typedef int32_t LONG;
typedef uint8_t UCHAR,BOOLEAN;typedef UCHAR *PUCHAR;typedef void VOID;
typedef union { int64_t QuadPart;struct { uint32_t LowPart;int32_t HighPart; }; } PHYSICAL_ADDRESS;
#define NTAPI
#define TRUE 1
#define FALSE 0
#define PASSIVE_LEVEL 0
#define MmNonCached 0
ULONG KeGetCurrentIrql(void);
void *MmAllocateContiguousMemorySpecifyCache(size_t,PHYSICAL_ADDRESS,PHYSICAL_ADDRESS,PHYSICAL_ADDRESS,int);
void MmFreeContiguousMemorySpecifyCache(void *,size_t,int);
PHYSICAL_ADDRESS MmGetPhysicalAddress(void *);
void RtlFillMemory(void *,size_t,UCHAR);
void RtlCopyMemory(void *,const void *,size_t);
#endif

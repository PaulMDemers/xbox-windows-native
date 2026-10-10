/* Host-only providers; never supplied to a native NT5 build. */
#ifndef XGN_HOST_NTDDK
#define XGN_HOST_NTDDK
#include <stdint.h>
#include <stddef.h>
typedef uint32_t ULONG;typedef int32_t LONG;typedef uintptr_t ULONG_PTR;
typedef unsigned char *PUCHAR;typedef void *PVOID;typedef ULONG *PULONG;
typedef void VOID;
#define NTAPI
#define PASSIVE_LEVEL 0
ULONG KeGetCurrentIrql(void);
LONG InterlockedCompareExchange(volatile LONG *,LONG,LONG);
ULONG XgnRead(PULONG);
#define READ_REGISTER_ULONG(p) XgnRead(p)
#endif

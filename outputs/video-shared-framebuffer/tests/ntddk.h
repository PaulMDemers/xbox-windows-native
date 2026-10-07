#pragma once
#include <stdint.h>
#include <stddef.h>
#include <pthread.h>
#include <assert.h>
typedef uint32_t ULONG;
typedef int32_t LONG, NTSTATUS;
typedef uintptr_t ULONG_PTR;
typedef void *PVOID;
typedef void VOID;
typedef int BOOLEAN, KIRQL;
typedef pthread_mutex_t KSPIN_LOCK;
#define NTAPI
#define NTSYSAPI
#define C_ASSERT(x) _Static_assert(x, #x)
#define TRUE 1
#define FALSE 0
#define MAXULONG UINT32_MAX
#define MmNonCached 0
#define PASSIVE_LEVEL 0
#define STATUS_SUCCESS 0
#define STATUS_INVALID_PARAMETER ((NTSTATUS)0xc000000d)
#define STATUS_DEVICE_NOT_READY ((NTSTATUS)0xc00000a3)
#define STATUS_DEVICE_BUSY ((NTSTATUS)0x80000011)
static _Thread_local KIRQL test_irql;
static KIRQL KeGetCurrentIrql(void) { return test_irql; }
static LONG InterlockedCompareExchange(volatile LONG *p, LONG n, LONG old) {
    __atomic_compare_exchange_n(p, &old, n, 0, __ATOMIC_SEQ_CST, __ATOMIC_SEQ_CST); return old;
}
static LONG InterlockedExchange(volatile LONG *p, LONG n) { return __atomic_exchange_n(p,n,__ATOMIC_SEQ_CST); }
static void KeInitializeSpinLock(KSPIN_LOCK *p) { assert(!pthread_mutex_init(p,NULL)); }
static void KeAcquireSpinLock(KSPIN_LOCK *p, KIRQL *old) { assert(!pthread_mutex_lock(p)); *old=test_irql; test_irql=2; }
static void KeReleaseSpinLock(KSPIN_LOCK *p, KIRQL old) { test_irql=old; assert(!pthread_mutex_unlock(p)); }

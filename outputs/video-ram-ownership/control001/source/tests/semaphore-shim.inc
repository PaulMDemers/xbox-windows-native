#include <pthread.h>
#include <assert.h>
#include <stdlib.h>
static _Thread_local int SemDepth;
static int SemFail;
HSEMAPHORE EngCreateSemaphore(void) {
 pthread_mutex_t *m;
 if(SemFail)return NULL;
 m=malloc(sizeof(*m));assert(m);assert(!pthread_mutex_init(m,NULL));return m;
}
VOID EngDeleteSemaphore(HSEMAPHORE m) {assert(!SemDepth);assert(!pthread_mutex_destroy(m));free(m);}
VOID EngAcquireSemaphore(HSEMAPHORE m) {assert(!SemDepth);assert(!pthread_mutex_lock(m));SemDepth++;}
VOID EngReleaseSemaphore(HSEMAPHORE m) {assert(SemDepth==1);SemDepth--;assert(!pthread_mutex_unlock(m));}

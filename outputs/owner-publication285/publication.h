/* Proposed serialized-core adapter. Actual QEMU hooks/owners are not installed.
 * Zero-initialized stable-lifetime storage; no reset or free API. */
#include <stdatomic.h>
#include "lifetime.h"
#define P285_BYTES (64+G284_BYTES)
enum {P285_BUSY=1,P285_CLOSED=2,P285_CONTENTION=4,P285_FOREIGN=8};
typedef struct {
 atomic_uint armed,gate,seal_claim,terminal;
 uint64_t owner;
 G284 core;
 uint8_t bytes[P285_BYTES];
} P285;
static bool p285_arm(P285 *p,uint64_t owner,unsigned mode,const uint64_t ids[4],
 const uint64_t names[4],const uint8_t keys[4][G284_KEY],const uint64_t sizes[4])
{
 unsigned expected=0;
 if(!atomic_compare_exchange_strong_explicit(&p->armed,&expected,1,memory_order_acq_rel,memory_order_acquire))return false;
 p->owner=owner;
 bool okay=g284_arm(&p->core,owner,mode,ids,names,keys,sizes);
 atomic_store_explicit(&p->armed,okay?2u:3u,memory_order_release);return okay;
}
static void p285_error(P285 *p,unsigned bit)
{
 unsigned v=atomic_load_explicit(&p->gate,memory_order_acquire);
 /* A rejection linearized after closure cannot mutate the published union. */
 while(!(v&P285_CLOSED)) {
  if(atomic_compare_exchange_weak_explicit(&p->gate,&v,v|bit,memory_order_acq_rel,memory_order_acquire))return;
 }
}
static bool p285_enter(P285 *p,uint64_t owner)
{
 if(atomic_load_explicit(&p->armed,memory_order_acquire)!=2)return false;
 if(owner!=p->owner){p285_error(p,P285_FOREIGN);return false;}
 unsigned v=atomic_load_explicit(&p->gate,memory_order_acquire);
 for(;;) {
  if(v&P285_CLOSED)return false;
  if(v&P285_BUSY){p285_error(p,P285_CONTENTION);return false;}
  if(atomic_compare_exchange_weak_explicit(&p->gate,&v,v|P285_BUSY,memory_order_acq_rel,memory_order_acquire))return true;
 }
}
static void p285_leave(P285 *p)
{atomic_fetch_and_explicit(&p->gate,~P285_BUSY,memory_order_release);}
static bool p285_seal(P285 *p,uint64_t owner)
{
 if(atomic_load_explicit(&p->armed,memory_order_acquire)!=2)return false;
 if(owner!=p->owner){p285_error(p,P285_FOREIGN);return false;}
 unsigned expected=0;
 if(!atomic_compare_exchange_strong_explicit(&p->seal_claim,&expected,1,memory_order_acq_rel,memory_order_acquire))return false;
 unsigned v=atomic_fetch_or_explicit(&p->gate,P285_CLOSED,memory_order_acq_rel);
 if(v&P285_BUSY) {
  /* Preserve storage and let the in-flight callback leave. Do not touch core,
   * serialize it, retry sealing, or report a complete result. */
  atomic_store_explicit(&p->terminal,3,memory_order_release);return false;
 }
 bool core_okay=g284_seal(&p->core,owner);
 uint8_t *out=p->bytes;
 uint64_t words[8]={UINT64_C(0x3538324e5758),285,P285_BYTES,p->owner,
  (uint64_t)(v|P285_CLOSED),v&~(P285_BUSY|P285_CLOSED),p->core.errors,1};
 for(unsigned i=0;i<8;i++)g284_word(&out,words[i]);
 bool encoded=g284_encode(&p->core,out,G284_BYTES)==G284_BYTES;
 bool okay=core_okay&&encoded&&v==0;
 /* All terminal bytes become visible only after this distinct publication. */
 atomic_store_explicit(&p->terminal,okay?2u:4u,memory_order_release);return okay;
}
static bool p285_read(const P285 *p,uint8_t *out,unsigned capacity)
{
 if(capacity<P285_BYTES || atomic_load_explicit(&p->terminal,memory_order_acquire)!=2)return false;
 memcpy(out,p->bytes,P285_BYTES);return true;
}

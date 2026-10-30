/* Compile the exact full transaction and its wrapper in one auditable object. */
#include "transaction819.c"
#define transfer encoder_transfer819
#include "encoder.c"
#undef transfer
#include "xcal_bus.c"
#include "gpu_preserving.c"
__attribute__((noinline)) int kernel_transaction819(const struct request704 *r, volatile uint8_t *g, volatile uint32_t *fb, struct result704 *o, uint32_t *flags)
{
 uint32_t saved,masked,restored;
 __asm__ volatile("pushfl;popl %0;cli":"=r"(saved)::"memory");
 __asm__ volatile("pushfl;popl %0":"=r"(masked)::"memory");
 int rc=native_transaction704(r,g,fb,o);
 __asm__ volatile("pushl %0;popfl"::"r"(saved):"cc","memory");
 __asm__ volatile("pushfl;popl %0":"=r"(restored)::"memory");
 flags[0]=saved;flags[1]=masked;flags[2]=restored;
 return rc;
}

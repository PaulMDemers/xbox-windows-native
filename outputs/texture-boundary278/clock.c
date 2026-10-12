/*277 Proposed instrumentation at completed actual CPU insert/unlink sites.
 * Metadata only: never gates, skips, waits for, or changes the original work.
 * Global scope deliberately refuses any foreign CPU rather than merging owners.
 * Readers are the acknowledged exclusive job on that same CPU, not the monitor.
 * Static lifetime is the owned process; there is no reset/rearm API. */
static CPUState *x277_clock_owner;
static uint64_t x277_clock_value;
static unsigned x277_clock_error;
static void x277_clock_advance(CPUState *cpu)
{
    CPUState *old=qatomic_cmpxchg(&x277_clock_owner,NULL,cpu);
    if((old && old!=cpu) || !qemu_cpu_is_self(cpu) || !cpu_in_exclusive_context(cpu))
        qatomic_fetch_or(&x277_clock_error,1u);
    uint64_t before=qatomic_read(&x277_clock_value);
    for(;;) {
        if(before==UINT64_MAX) {qatomic_fetch_or(&x277_clock_error,2u);return;}
        uint64_t seen=qatomic_cmpxchg(&x277_clock_value,before,before+1);
        if(seen==before) return;
        before=seen;
    }
}
void mem_access_callback_clock277(CPUState *cpu,uint64_t *value,unsigned *error)
{
    /* No callback pointer is followed and no CPU work is queued by this read. */
    unsigned e=qatomic_read(&x277_clock_error);
    if(qatomic_read(&x277_clock_owner)!=cpu || !qemu_cpu_is_self(cpu) ||
       !cpu_in_exclusive_context(cpu)) e|=4u;
    *value=qatomic_read(&x277_clock_value);*error=e;
}

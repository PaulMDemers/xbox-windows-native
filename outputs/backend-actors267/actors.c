/*267 Append-only process-lifetime records: never recycle a generation. */
static X267Actor x267_actors[X267_ACTORS];
static unsigned x267_next, x267_overflow;
unsigned pgraph_gl_actor267_overflow(void)
{
    return __atomic_load_n(&x267_overflow,__ATOMIC_ACQUIRE);
}
static void *x267_run(void *argument)
{
    X267Actor *a=argument;
    x267_start(a,qemu_get_thread_id());
    void *result=a->function(a->argument);
    x267_finish(a);
    return result;
}
static void x267_create(QemuThread *thread,const char *name,
                        void *(*function)(void *),void *argument,
                        unsigned kind,X267Actor **owner_slot)
{
    unsigned slot=x267_reserve(&x267_next,&x267_overflow,X267_ACTORS);
    if (slot==X267_ACTORS) {
        *owner_slot=NULL;
        /* Preserve ordinary work if instrumentation saturates; ledger refuses. */
        qemu_thread_create(thread,name,function,argument,QEMU_THREAD_JOINABLE);
        return;
    }
    X267Actor *a=&x267_actors[slot];
    a->epoch=(uint64_t)slot+1;a->kind=kind;a->owner=(uintptr_t)argument;
    a->function=function;a->argument=argument;
    __atomic_store_n(&a->state,1,__ATOMIC_RELEASE);
    *owner_slot=a;
    qemu_thread_create(thread,name,x267_run,a,QEMU_THREAD_JOINABLE);
}

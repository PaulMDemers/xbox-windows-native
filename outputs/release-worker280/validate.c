static bool x280_validate_actual(NV2AState *d,X280Transaction *tx,X265State *s)
{
    X277Proof *p=&s->proof278;X260Slot *v=&s->boundary;
    p->stage=v->stage;p->worker=v->worker_thread;p->device=(uintptr_t)d;p->region=(uintptr_t)d->vram;
    p->function=p->cpu[0].count?p->cpu[0].callbacks[0].function:0;
    p->ram_base=memory_region_get_ram_addr(d->vram);p->ram_bytes=memory_region_size(d->vram);
    p->started=v->started;p->finished=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);p->deadline=v->deadline;
    p->cpu_stopped=qatomic_read(&qemu_get_cpu(0)->stopped);p->frontend_closed=xwn_frontend246_closed();
    p->pfifo_halted=qatomic_read(&d->pfifo.halt);p->render_fenced=v->admission.render_fenced;
    p->display_fenced=v->admission.display_fenced;p->pending=x274_pending(d);
    p->get_equals_put=d->pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]==d->pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT];
    p->method_error=d->pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE]&
        (NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT|NV_PFIFO_CACHE1_DMA_STATE_ERROR);
    p->unknown_owners=s->accounting_error || s->shader_jobs_unknown;
    unsigned contexts=0;
    for(unsigned i=0;i<s->ledger.count;i++) {
        uint64_t *row=s->ledger.rows[i];if(row[0]!=51)continue;
        if(row[1]<1 || row[1]>2 || !row[7] || row[3]!=row[4] || row[5]!=row[6] ||
           (contexts&(1u<<row[1])))return false;
        contexts|=1u<<row[1];
        if(row[1]==1)p->render_context=row[3];else p->display_context=row[3];
    }
    if(contexts!=6)return false;
    s->admission278=x280_validate(p,tx->candidate);return s->admission278==X277_OK;
}

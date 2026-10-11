"""Actual240 stop5: avoid invoking an inactive pusher when no work exists."""
def apply(root):
 p=root/'hw/xbox/nv2a/pfifo.c';s=p.read_text(encoding='utf-8')
 old='''    if (pfifo_wait232(d)) { budget.stop = 4;
    } else { pfifo_run_pusher(d, &budget); }'''
 new='''    /*241 Under the actual FIFO lock and halted producer admission. An empty
     * completed parser has nothing to consume, even when the pusher is parked.
     * Do not enable it, clear state/waits or simulate a completion. The renderer
     * still rechecks queue/frontend state and fences/downloads actual pixels. */
    if (qatomic_load_acquire(&d->preserve227.state) != 1 ||
        qemu_clock_get_ns(QEMU_CLOCK_REALTIME) >= budget.deadline) {
        budget.stop = 1;
    } else if (pfifo_wait232(d)) { budget.stop = 4;
    } else if (d->pfifo.regs[NV_PFIFO_CACHE1_DMA_GET] ==
               d->pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT] &&
               !(d->pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE] &
                 (NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT |
                  NV_PFIFO_CACHE1_DMA_STATE_ERROR))) {
        /* Zero commands consumed. Existing worker gates remain authoritative. */
    } else { pfifo_run_pusher(d, &budget); }'''
 assert s.count(old)==1;p.write_text(s.replace(old,new),encoding='utf-8')

"""Ordered one-shot diagnostic telemetry; no queue consumption or ownership grant."""
def replace(s, a, b):
    assert s.count(a) == 1, a[:100]
    return s.replace(a, b)

def apply(root):
    p = root/'hw/xbox/nv2a/nv2a_int.h'; s=p.read_text()
    s=replace(s, 'uint64_t bytes;\n        int64_t deadline;', 'uint64_t bytes;\n        uint32_t request_fifo[10], gate_fifo[10];\n        int64_t deadline;')
    s=replace(s, 'void nv2a_preserve227_finish(NV2AState *d, unsigned result);', 'void nv2a_preserve227_finish(NV2AState *d, unsigned result);\nvoid nv2a_preserve231_snapshot(NV2AState *d, uint32_t words[10]);')
    p.write_text(s)
    p=root/'hw/xbox/nv2a/nv2a.c'; s=p.read_text()
    s=s.replace('qatomic_read(&d->preserve227.state)', 'qatomic_load_acquire(&d->preserve227.state)')
    s=replace(s, '    qatomic_set(&d->preserve227.state, 1);', '    nv2a_preserve231_snapshot(d, d->preserve227.request_fifo);\n    qatomic_store_release(&d->preserve227.state, 1);')
    start=s.index('    return g_strdup_printf("state=%u surfaces='); end=s.index('\n}\n', start)
    s=s[:start]+'''    /* Only a worker-published terminal state orders its mutable tuple.
     * Timeout5 can precede late worker stores; never expose that tuple. Request
     * words are immutable before release1. There is no reuse/reset operation. */
    bool published = state == 3 || state == 4 || state == 6;
    GString *report = g_string_new(NULL);
    g_string_append_printf(report,
        "state=%u tuple_published=%u publication_version=231"
        " surfaces=%u dirty=%u downloaded=%u bytes=%" PRIu64
        " error=%u reason=%u references_retired=0 native_grant=0 old_halt=%u",
        state, published,
        published ? qatomic_read(&d->preserve227.surfaces) : 0,
        published ? qatomic_read(&d->preserve227.dirty) : 0,
        published ? qatomic_read(&d->preserve227.downloaded) : 0,
        published ? qatomic_read(&d->preserve227.bytes) : 0,
        published ? qatomic_read(&d->preserve227.error) : 0,
        published ? qatomic_read(&d->preserve227.reason) : 0,
        state ? d->preserve227.old_halt : 0);
    for (unsigned i = 0; i < 10; i++) {
        g_string_append_printf(report, " request%u=%u gate%u=%u", i,
            state ? qatomic_read(&d->preserve227.request_fifo[i]) : 0, i,
            published ? qatomic_read(&d->preserve227.gate_fifo[i]) : 0);
    }
    return g_string_free(report, false);'''+s[end:]
    s=replace(s, '    qatomic_set(&d->preserve227.state, result);', '    qatomic_store_release(&d->preserve227.state, result);')
    helper='''/*231 caller holds FIFO lock. Raw words, not a synthetic idle predicate.
 * PGRAPH FIFO has its existing atomic-access contract. Snapshots do not retire
 * references or write emulated registers. */
void nv2a_preserve231_snapshot(NV2AState *d, uint32_t words[10])
{
    const hwaddr offsets[9] = {
        NV_PFIFO_CACHE1_DMA_GET, NV_PFIFO_CACHE1_DMA_PUT,
        NV_PFIFO_CACHE1_DMA_STATE, NV_PFIFO_CACHE1_PUSH0,
        NV_PFIFO_CACHE1_PUSH1, NV_PFIFO_CACHE1_DMA_PUSH,
        NV_PFIFO_CACHE1_PULL0, NV_PFIFO_CACHE1_STATUS,
        NV_PFIFO_CACHE1_DMA_SUBROUTINE,
    };
    for (unsigned i = 0; i < 9; i++) {
        qatomic_set(&words[i], d->pfifo.regs[offsets[i]]);
    }
    qatomic_set(&words[9], qatomic_read(&d->pgraph.regs_[NV_PGRAPH_FIFO]));
}

'''
    s=replace(s, '/*228 claim terminal publication', helper+'/*228 claim terminal publication')
    p.write_text(s)
    p=root/'hw/xbox/nv2a/pgraph/gl/renderer.c'; s=p.read_text()
    s=replace(s, '    if (qatomic_read(&d->preserve227.state) == 1) {\n        unsigned result = 4;', '    if (qatomic_load_acquire(&d->preserve227.state) == 1) {\n        nv2a_preserve231_snapshot(d, d->preserve227.gate_fifo);\n        unsigned result = 4;')
    p.write_text(s)

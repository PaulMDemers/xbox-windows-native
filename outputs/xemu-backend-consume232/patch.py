"""Use the actual pusher with opt-in finite budgets; ordinary calls remain NULL."""
def replace(s,a,b):
    assert s.count(a)==1,a[:100]
    return s.replace(a,b)

def apply(root):
    p=root/'hw/xbox/nv2a/nv2a_int.h';s=p.read_text()
    s=replace(s,'unsigned state, surfaces, dirty, downloaded, error, reason;', 'unsigned state, surfaces, dirty, downloaded, error, reason;\n        unsigned consume_stop, consume_steps, consume_words, wait_before, wait_after;')
    s += '\nvoid nv2a_preserve232_consume(NV2AState *d);\n'
    p.write_text(s)
    p=root/'hw/xbox/nv2a/nv2a.c';s=p.read_text().replace('publication_version=231','publication_version=232')
    s=replace(s,'    return g_string_free(report, false);', '''    g_string_append_printf(report,
        " consume_stop=%u consume_steps=%u consume_words=%u wait_before=%u wait_after=%u",
        published ? qatomic_read(&d->preserve227.consume_stop) : 0,
        published ? qatomic_read(&d->preserve227.consume_steps) : 0,
        published ? qatomic_read(&d->preserve227.consume_words) : 0,
        published ? qatomic_read(&d->preserve227.wait_before) : 0,
        published ? qatomic_read(&d->preserve227.wait_after) : 0);
    return g_string_free(report, false);''');p.write_text(s)
    p=root/'hw/xbox/nv2a/pfifo.c';s=p.read_text()
    declaration='''/*232 one invocation, no reuse. Stops:1 expired/cancelled,2 words,
 *3 iterations,4 real wait,5 disabled/suspended access,6 parser error,
 *7 invalid DMA range/alignment,8 invalid puller count,9 incomplete parser.
 * Zero means genuinely empty queue/parser, not ownership. */
typedef struct PFIFOConsume232 {
    unsigned steps_left, words_left, steps, words, stop;
    int64_t deadline;
} PFIFOConsume232;
static void pfifo_run_pusher(NV2AState *d, PFIFOConsume232 *budget);'''
    s=replace(s,'static void pfifo_run_pusher(NV2AState *d);',declaration)
    s=replace(s,'static void pfifo_run_pusher(NV2AState *d)\n{','static void pfifo_run_pusher(NV2AState *d, PFIFOConsume232 *budget)\n{')
    s=replace(s,'            pfifo_run_pusher(d);','            pfifo_run_pusher(d, NULL);')
    helper='''/* Raw existing conditions, no clearing of any wait or error. Caller owns
 * FIFO lock; PGRAPH wait fields retain their existing atomic contract. */
static unsigned pfifo_wait232(NV2AState *d)
{
    return (!can_fifo_access(d) ? 1 : 0) |
        (qatomic_read(&d->pgraph.waiting_for_nop) ? 2 : 0) |
        (qatomic_read(&d->pgraph.waiting_for_flip) ? 4 : 0) |
        (qatomic_read(&d->pgraph.waiting_for_context_switch) ? 8 : 0);
}

static bool pfifo_budget232(NV2AState *d, PFIFOConsume232 *budget)
{
    if (qatomic_load_acquire(&d->preserve227.state) != 1 ||
        qemu_clock_get_ns(QEMU_CLOCK_REALTIME) >= budget->deadline) {
        budget->stop = 1;
    } else if (!budget->words_left) { budget->stop = 2;
    } else if (!budget->steps_left) { budget->stop = 3;
    } else if (pfifo_wait232(d)) { budget->stop = 4; }
    if (budget->stop) { return false; }
    budget->steps_left--; budget->steps++;
    return true;
}

'''
    s=replace(s,'static void pfifo_run_pusher(NV2AState *d, PFIFOConsume232 *budget)\n{',helper+'static void pfifo_run_pusher(NV2AState *d, PFIFOConsume232 *budget)\n{')
    s=replace(s,'GET_MASK(*dma_push, NV_PFIFO_CACHE1_DMA_PUSH_STATUS)) {\n        return;', 'GET_MASK(*dma_push, NV_PFIFO_CACHE1_DMA_PUSH_STATUS)) {\n        if (budget) { budget->stop = 5; }\n        return;')
    s=replace(s,'    /* We\'re running so there should be no pending errors... */', '''    if (budget && GET_MASK(*dma_state, NV_PFIFO_CACHE1_DMA_STATE_ERROR)) {
        budget->stop = 6; return;
    }
    /* We're running so there should be no pending errors... */''')
    s=replace(s,'        if (dma_get_v == dma_put_v) break;', '''        if (dma_get_v == dma_put_v) break;
        if (budget && !pfifo_budget232(d, budget)) { break; }
        unsigned consumed_words = 1;
        if (budget && (dma_put_v < dma_get_v || dma_put_v > dma_len ||
                       dma_get_v > dma_len || dma_len - dma_get_v < 4 ||
                       ((dma_put_v | dma_get_v) & 3))) {
            budget->stop = 7; break;
        }''')
    s=replace(s,'        num_words_available /= 4;', '''        num_words_available /= 4;
        if (budget) {
            num_words_available = MIN(num_words_available, budget->words_left);
        }''')
    s=replace(s,'            if (num_words_processed < 0) {\n                break;\n            }', '''            if (num_words_processed < 0) {
                if (budget) { budget->stop = 4; }
                break;
            }
            if (budget && (num_words_processed == 0 ||
                          (size_t)num_words_processed > num_words_available)) {
                budget->stop = 8; break;
            }
            consumed_words = num_words_processed;''')
    s=replace(s,'        *dma_get = dma_get_v;', '''        *dma_get = dma_get_v;
        if (budget) {
            budget->words_left -= consumed_words;
            budget->words += consumed_words;
        }''')
    s=replace(s,'    if (error) {\n        NV2A_DPRINTF("pb error:', '    if (error && budget) { budget->stop = 6; return; }\n    if (error) {\n        NV2A_DPRINTF("pb error:')
    wrapper='''/* Opt-in worker call under FIFO lock, only on the one stopped-VM request.
 * The host owns the frozen vCPU phase. No halt toggle or synthetic register
 * completion. Existing PGRAPH methods/lock transitions remain the consumer. */
void nv2a_preserve232_consume(NV2AState *d)
{
    PFIFOConsume232 budget = { .steps_left = 32768, .words_left = 32768,
                              .deadline = d->preserve227.deadline };
    qatomic_set(&d->preserve227.wait_before, pfifo_wait232(d));
    if (pfifo_wait232(d)) { budget.stop = 4;
    } else { pfifo_run_pusher(d, &budget); }
    qatomic_set(&d->preserve227.wait_after, pfifo_wait232(d));
    if (!budget.stop && (d->pfifo.regs[NV_PFIFO_CACHE1_DMA_GET] !=
                        d->pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT] ||
                        (d->pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE] &
                         NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT))) {
        budget.stop = 9;
    }
    qatomic_set(&d->preserve227.consume_stop, budget.stop);
    qatomic_set(&d->preserve227.consume_steps, budget.steps);
    qatomic_set(&d->preserve227.consume_words, budget.words);
}

'''
    s=replace(s,'void *pfifo_thread(void *arg)',wrapper+'void *pfifo_thread(void *arg)');p.write_text(s)
    p=root/'hw/xbox/nv2a/pgraph/gl/renderer.c';s=p.read_text()
    s=replace(s,'        nv2a_preserve231_snapshot(d, d->preserve227.gate_fifo);', '''        nv2a_preserve232_consume(d);
        nv2a_preserve231_snapshot(d, d->preserve227.gate_fifo);''')
    s=replace(s,'        if (frontend_locked) {\n            bool queue_empty =', '''        unsigned stop = qatomic_read(&d->preserve227.consume_stop);
        if (stop == 6 || stop == 7 || stop == 8) {
            result = 6;
            qatomic_set(&d->preserve227.reason, 16 + stop);
        } else if (frontend_locked && !stop) {
            bool queue_empty =''')
    # The original renderer unlock was inside its branch; retain on every trylock success.
    s=replace(s,'            qemu_mutex_unlock(&pg->renderer_lock);\n        }\n        /* Timeout', '''        }
        if (frontend_locked) { qemu_mutex_unlock(&pg->renderer_lock); }
        if (stop && result == 4) { qatomic_set(&d->preserve227.reason, 16 + stop); }
        /* Timeout''');p.write_text(s)

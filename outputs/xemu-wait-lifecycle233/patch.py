"""Read-only bounded wait journal; all record calls under existing PGRAPH lock."""
def replace(s,a,b):
    assert s.count(a)==1,a[:100];return s.replace(a,b)

def apply(root):
    p=root/'hw/xbox/nv2a/nv2a_int.h';s=p.read_text()
    start=s.index('typedef struct NV2AState');s=s[:start]+'''/*233 observer storage, no emulated ownership or register state. */
#define NV2A_WAIT233_CAPACITY 256
typedef struct NV2AWaitRow233 {
    uint64_t seq, when;
    uint32_t kind, value, pending, enabled, nsource, trapped, data, waits;
    uint32_t fifo_valid, fifo[10];
} NV2AWaitRow233;

'''+s[start:]
    s=replace(s,'    struct {\n        unsigned state, surfaces', '''    struct {
        uint64_t total;
        unsigned count, next;
        NV2AWaitRow233 rows[NV2A_WAIT233_CAPACITY];
    } wait233;
    struct {
        unsigned state, surfaces''')
    s+='''
void nv2a_wait233_fill(NV2AState *d, NV2AWaitRow233 *row,
                       unsigned kind, uint32_t value, bool fifo_valid);
void nv2a_wait233_record(NV2AState *d, unsigned kind, uint32_t value,
                         bool fifo_valid);
''';p.write_text(s)
    p=root/'hw/xbox/nv2a/pgraph/pgraph.c';s=p.read_text()
    pos=s.index('uint64_t pgraph_read(')
    s=s[:pos]+'''/*233 caller ALREADY holds PGRAPH lock. Never acquire FIFO here: the
 * producer released FIFO before dispatch. FIFO snapshots are valid only for
 * actual guest MMIO/reset callers that already hold both locks. */
void nv2a_wait233_fill(NV2AState *d, NV2AWaitRow233 *row,
                       unsigned kind, uint32_t value, bool fifo_valid)
{
    PGRAPHState *pg = &d->pgraph;
    memset(row, 0, sizeof(*row));
    row->when = qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    row->kind = kind; row->value = value;
    row->pending = pg->pending_interrupts; row->enabled = pg->enabled_interrupts;
    row->nsource = pgraph_reg_r(pg, NV_PGRAPH_NSOURCE);
    row->trapped = pgraph_reg_r(pg, NV_PGRAPH_TRAPPED_ADDR);
    row->data = pgraph_reg_r(pg, NV_PGRAPH_TRAPPED_DATA_LOW);
    row->waits = (!qatomic_read(&pg->regs_[NV_PGRAPH_FIFO]) ? 1 : 0) |
        (pg->waiting_for_nop ? 2 : 0) | (pg->waiting_for_flip ? 4 : 0) |
        (pg->waiting_for_context_switch ? 8 : 0);
    row->fifo_valid = fifo_valid;
    if (fifo_valid) { nv2a_preserve231_snapshot(d, row->fifo); }
}

void nv2a_wait233_record(NV2AState *d, unsigned kind, uint32_t value,
                         bool fifo_valid)
{
    if (d->wait233.total == UINT64_MAX) { return; }
    NV2AWaitRow233 *row = &d->wait233.rows[d->wait233.next];
    nv2a_wait233_fill(d, row, kind, value, fifo_valid);
    row->seq = ++d->wait233.total;
    d->wait233.next = (d->wait233.next + 1) % NV2A_WAIT233_CAPACITY;
    if (d->wait233.count < NV2A_WAIT233_CAPACITY) { d->wait233.count++; }
}

'''+s[pos:]
    s=replace(s,'    case NV_PGRAPH_INTR:\n        pg->pending_interrupts &= ~val;', '''    case NV_PGRAPH_INTR:
        nv2a_wait233_record(d, 4, val, true);
        pg->pending_interrupts &= ~val;''')
    s=replace(s,'        pfifo_kick(d);\n        break;\n    case NV_PGRAPH_INTR_EN:', '''        pfifo_kick(d);
        nv2a_wait233_record(d, 5, val, true);
        break;
    case NV_PGRAPH_INTR_EN:''')
    s=replace(s,'        pg->enabled_interrupts = val;\n        break;', '        pg->enabled_interrupts = val;\n        nv2a_wait233_record(d, 6, val, true);\n        break;')
    s=replace(s,'    assert(!(pg->pending_interrupts & NV_PGRAPH_INTR_ERROR));', '    nv2a_wait233_record(d, 1, parameter, false);\n    assert(!(pg->pending_interrupts & NV_PGRAPH_INTR_ERROR));')
    s=replace(s,'    pg->waiting_for_nop = true;', '    pg->waiting_for_nop = true;\n    nv2a_wait233_record(d, 2, parameter, false);')
    # Only NO_OPERATION; other methods have the same lock sequence.
    a=s.index('DEF_METHOD(NV097, NO_OPERATION)');z=s.index('DEF_METHOD(NV097, WAIT_FOR_IDLE)',a)
    part=s[a:z];part=replace(part,'    qemu_mutex_lock(&pg->lock);','    qemu_mutex_lock(&pg->lock);\n    nv2a_wait233_record(d, 3, parameter, false);');s=s[:a]+part+s[z:];p.write_text(s)
    p=root/'hw/xbox/nv2a/nv2a.c';s=p.read_text()
    s=replace(s,'    memset(d->pfifo.regs, 0, sizeof(d->pfifo.regs));', '    nv2a_wait233_record(d, 7, 0, true);\n    memset(d->pfifo.regs, 0, sizeof(d->pfifo.regs));')
    # Both existing locks held at reset end. Do NOT clear PG pending state.
    s=replace(s,'    nv2a_unlock_fifo(d);\n}\n\n/*227 stopped-VM diagnostic.', '    nv2a_wait233_record(d, 8, 0, true);\n    nv2a_unlock_fifo(d);\n}\n\n/*227 stopped-VM diagnostic.')
    pos=s.index('static void nv2a_realize(')
    s=s[:pos]+'''/*233 read-only property, all row reads ordered by existing PG lock.
 * Try-lock FIFO->PGRAPH avoids blocking BQL on a worker that needs BQL. */
static void wait233_format(GString *s, const NV2AWaitRow233 *row)
{
    g_string_append_printf(s, " row=%" PRIu64 ",%" PRIu64 ",%u,%u,%u,%u,%u,%u,%u,%u,%u",
        row->seq, row->when, row->kind, row->value, row->pending,
        row->enabled, row->nsource, row->trapped, row->data, row->waits,
        row->fifo_valid);
    for (unsigned i = 0; i < 10; i++) { g_string_append_printf(s, ",%u", row->fifo[i]); }
}

static char *wait233_report(Object *obj, Error **errp)
{
    NV2AState *d = NV2A_DEVICE(obj);
    if (qemu_mutex_trylock(&d->pfifo.lock)) { return g_strdup("version=233 busy=1 lock=1"); }
    if (qemu_mutex_trylock(&d->pgraph.lock)) {
        qemu_mutex_unlock(&d->pfifo.lock);return g_strdup("version=233 busy=1 lock=2");
    }
    GString *report = g_string_new(NULL);
    g_string_append_printf(report, "version=233 busy=0 total=%" PRIu64 " count=%u capacity=256 overwritten=%" PRIu64,
        d->wait233.total, d->wait233.count, d->wait233.total - d->wait233.count);
    NV2AWaitRow233 current;
    nv2a_wait233_fill(d, &current, 9, 0, true);wait233_format(report, &current);
    unsigned start = (d->wait233.next + NV2A_WAIT233_CAPACITY - d->wait233.count) % NV2A_WAIT233_CAPACITY;
    for (unsigned i = 0; i < d->wait233.count; i++) {
        wait233_format(report, &d->wait233.rows[(start + i) % NV2A_WAIT233_CAPACITY]);
    }
    qemu_mutex_unlock(&d->pgraph.lock);qemu_mutex_unlock(&d->pfifo.lock);
    return g_string_free(report, false);
}

'''+s[pos:]
    s=replace(s,'    object_property_add_str(OBJECT(d), "xwn-preserve227-report",', '    object_property_add_str(OBJECT(d), "xwn-wait233-report", wait233_report, NULL);\n    object_property_add_str(OBJECT(d), "xwn-preserve227-report",')
    p.write_text(s)

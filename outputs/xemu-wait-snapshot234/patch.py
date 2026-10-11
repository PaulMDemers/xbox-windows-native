"""ONE immutable worker snapshot, separate from unchanged232 preservation."""
def replace(s,a,b):
 assert s.count(a)==1,a[:100];return s.replace(a,b)

def apply(root):
 p=root/'hw/xbox/nv2a/nv2a_int.h';s=p.read_text()
 pos=s.index('typedef struct NV2AState')
 s=s[:pos]+'''/*234 resident copied tuple; monitor never reads the mutable journal. */
typedef struct NV2AWaitSnapshot234 {
    unsigned state;
    int64_t deadline;
    uint64_t total;
    unsigned count;
    NV2AWaitRow233 current, rows[NV2A_WAIT233_CAPACITY];
} NV2AWaitSnapshot234;

'''+s[pos:]
 s=replace(s,'    } wait233;','    } wait233;\n    NV2AWaitSnapshot234 snapshot234;')
 s=replace(s,'void nv2a_wait233_fill(','''bool nv2a_snapshot234_claim(NV2AState *d);
void nv2a_snapshot234_copy(NV2AState *d);
void nv2a_snapshot234_publish(NV2AState *d);
void nv2a_wait233_fill(''');p.write_text(s)
 p=root/'hw/xbox/nv2a/nv2a.c';s=p.read_text()
 a=s.index('/*233 read-only property');z=s.index('static void nv2a_realize',a)
 old=s[a:z];aformat=old.index('static void wait233_format');zformat=old.index('static char *wait233_report')
 formatter=old[aformat:zformat]
 block='''/*234 ONE request: 0 unused,1 requested,2 worker copying,7 publication
 * claimed,3 immutable terminal,5 timeout. No reset/reuse or guest-state write.
 * Deadline initialized before request release; reader only expires 1/2. */
static unsigned snapshot234_expire(NV2AState *d)
{
    unsigned state = qatomic_load_acquire(&d->snapshot234.state);
    if ((state == 1 || state == 2) &&
        qemu_clock_get_ns(QEMU_CLOCK_REALTIME) >= d->snapshot234.deadline) {
        qatomic_cmpxchg(&d->snapshot234.state, state, 5);
        state = qatomic_load_acquire(&d->snapshot234.state);
    }
    return state;
}

bool nv2a_snapshot234_claim(NV2AState *d)
{
    return snapshot234_expire(d) == 1 &&
        qatomic_cmpxchg(&d->snapshot234.state, 1, 2) == 1;
}

/* Caller holds actual PG lock, FIFO has been released. No FIFO reads. */
void nv2a_snapshot234_copy(NV2AState *d)
{
    d->snapshot234.total = d->wait233.total;
    d->snapshot234.count = d->wait233.count;
    nv2a_wait233_fill(d, &d->snapshot234.current, 9, 0, false);
    unsigned start = (d->wait233.next + NV2A_WAIT233_CAPACITY -
                      d->wait233.count) % NV2A_WAIT233_CAPACITY;
    for (unsigned i = 0; i < d->wait233.count; i++) {
        d->snapshot234.rows[i] =
            d->wait233.rows[(start + i) % NV2A_WAIT233_CAPACITY];
    }
}

/* All copied bytes precede release3. Timeout's CAS wins over late completion;
 * unpublished late storage stays invisible and can never be requested again. */
void nv2a_snapshot234_publish(NV2AState *d)
{
    if (snapshot234_expire(d) != 2) { return; }
    if (qatomic_cmpxchg(&d->snapshot234.state, 2, 7) != 2) { return; }
    qatomic_store_release(&d->snapshot234.state, 3);
}

'''+formatter+'''static void snapshot234_request(Object *obj, bool value, Error **errp)
{
    NV2AState *d = NV2A_DEVICE(obj);
    if (!value || qatomic_load_acquire(&d->snapshot234.state) != 0) {
        error_setg(errp, "snapshot234 requires ONE true request"); return;
    }
    /* Monitor owns BQL. Never block it waiting for FIFO or PG. */
    if (qemu_mutex_trylock(&d->pfifo.lock)) {
        error_setg(errp, "snapshot234 FIFO busy; request NOT accepted"); return;
    }
    d->snapshot234.deadline = qemu_clock_get_ns(QEMU_CLOCK_REALTIME) +
                              INT64_C(5000000000);
    qatomic_store_release(&d->snapshot234.state, 1);
    pfifo_kick(d);
    qemu_mutex_unlock(&d->pfifo.lock);
}

static bool snapshot234_requested(Object *obj, Error **errp)
{
    NV2AState *d = NV2A_DEVICE(obj);
    return qatomic_load_acquire(&d->snapshot234.state) != 0;
}

static char *snapshot234_report(Object *obj, Error **errp)
{
    NV2AState *d = NV2A_DEVICE(obj);
    unsigned state = snapshot234_expire(d);
    bool published = state == 3;
    GString *report = g_string_new(NULL);
    g_string_append_printf(report, "version=234 state=%u tuple_published=%u total=%" PRIu64 " count=%u capacity=256 overwritten=%" PRIu64,
        state, published, published ? d->snapshot234.total : 0,
        published ? d->snapshot234.count : 0,
        published ? d->snapshot234.total - d->snapshot234.count : 0);
    if (published) {
        wait233_format(report, &d->snapshot234.current);
        for (unsigned i = 0; i < d->snapshot234.count; i++) {
            wait233_format(report, &d->snapshot234.rows[i]);
        }
    }
    return g_string_free(report, false);
}

'''
 s=s[:a]+block+s[z:]
 s=replace(s,'    object_property_add_str(OBJECT(d), "xwn-wait233-report", wait233_report, NULL);', '''    object_property_add_bool(OBJECT(d), "xwn-snapshot234",
                             snapshot234_requested, snapshot234_request);
    object_property_add_str(OBJECT(d), "xwn-snapshot234-report", snapshot234_report, NULL);''');p.write_text(s)
 p=root/'hw/xbox/nv2a/pgraph/gl/renderer.c';s=p.read_text()
 s=replace(s,'    /* Request is one-shot and producer admission was halted under FIFO lock.', '''    /*234 worker enters with FIFO owned; claim once, then release FIFO BEFORE
     * PG acquisition. Copy only PG data, release PG before reacquiring FIFO.
     * Snapshot admission does not halt the producer or acquire BQL. */
    if (nv2a_snapshot234_claim(d)) {
        qemu_mutex_unlock(&d->pfifo.lock);
        qemu_mutex_lock(&pg->lock);
        nv2a_snapshot234_copy(d);
        qemu_mutex_unlock(&pg->lock);
        nv2a_snapshot234_publish(d);
        qemu_mutex_lock(&d->pfifo.lock);
    }

    /* Request is one-shot and producer admission was halted under FIFO lock.''');p.write_text(s)

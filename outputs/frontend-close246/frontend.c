/*246 Experimental UI actor gate. State:0 open,1 requested,2 closed,3 refused,
 *4 reopen requested,5 reopened. Scalar record is release/acquire published once.
 * No resource deletion, bindings changed or native ownership permit. */
static int frontend246_state;
static bool frontend246_ready;
static GLuint frontend246_last_texture;
static bool frontend246_last_fallback;
static struct {
    uint64_t when, thread, context;
    int loan, bql, error;
    GLuint texture;
    bool fallback, texture_live;
    GLenum fence_result;
    GLint bindings[7];
} frontend246_record;

static void frontend246_trace(int phase, uint64_t a, uint64_t b)
{
    trace_nv2a_lifecycle244(phase, qemu_clock_get_ns(QEMU_CLOCK_REALTIME),
                          qemu_get_thread_id(), 0, a, b);
}

bool xwn_frontend246_request(bool close)
{
    if (close) {
        if (qatomic_cmpxchg(&frontend246_state, 0, 1) != 0) { return false; }
        frontend246_trace(60, 1, 0);
        return true;
    }
    /* An abort may race the actor's terminal publication; bounded CAS retries. */
    for (int i = 0; i < 3; ++i) {
        int state = qatomic_load_acquire(&frontend246_state);
        if (state < 1 || state > 3) { return false; }
        if (qatomic_cmpxchg(&frontend246_state, state, 4) == state) {
            frontend246_trace(63, state, 4);
            return true;
        }
    }
    return false;
}

char *xwn_frontend246_report(void)
{
    int state = qatomic_load_acquire(&frontend246_state);
    bool ready = qatomic_load_acquire(&frontend246_ready);
    if (!ready) { return g_strdup_printf("version=246 state=%d ready=0", state); }
    return g_strdup_printf("version=246 state=%d ready=1 when=%"PRIu64
        " thread=%"PRIu64" context=%"PRIu64
        " loan=%d bql=%d error=%d texture=%u fallback=%d live=%d fence=%u"
        " binding0=%d binding1=%d binding2=%d binding3=%d binding4=%d binding5=%d binding6=%d",
        state, frontend246_record.when, frontend246_record.thread,
        frontend246_record.context, frontend246_record.loan,
        frontend246_record.bql, frontend246_record.error,
        frontend246_record.texture, frontend246_record.fallback,
        frontend246_record.texture_live, frontend246_record.fence_result,
        frontend246_record.bindings[0], frontend246_record.bindings[1],
        frontend246_record.bindings[2], frontend246_record.bindings[3],
        frontend246_record.bindings[4], frontend246_record.bindings[5],
        frontend246_record.bindings[6]);
}

/* Called only after the actual rendering token is exclusively acquired. */
static bool frontend246_gate(struct xemu_console *scon)
{
    int state = qatomic_load_acquire(&frontend246_state);
    if (state == 0 || state == 5) { return false; }
    if (state == 4) {
        frontend246_trace(64, 4, 5);
        qatomic_store_release(&frontend246_state, 5);
        return false;
    }
    if (state != 1) { return true; }
    frontend246_record.when = qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    frontend246_record.thread = qemu_get_thread_id();
    frontend246_record.bql = bql_locked();
    frontend246_record.loan = -1;
    frontend246_record.texture = frontend246_last_texture;
    frontend246_record.fallback = frontend246_last_fallback;
    if (frontend246_record.bql) {
        frontend246_record.error = 1; /* Never wait under BQL. */
    } else if (!SDL_GL_MakeCurrent(scon->real_window, scon->winctx)) {
        frontend246_record.error = 2;
    } else {
        frontend246_record.context = (uintptr_t)SDL_GL_GetCurrentContext();
        frontend246_record.loan = nv2a_frontend246_loan();
        if (frontend246_record.loan != 0) {
            frontend246_record.error = 3; /* Busy lock and live loan both refuse. */
        } else {
            frontend246_trace(66, frontend246_record.texture, 100000000);
            GLsync fence = glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE, 0);
            if (!fence) {
                frontend246_record.error = 4;
            } else {
                frontend246_record.fence_result = glClientWaitSync(
                    fence, GL_SYNC_FLUSH_COMMANDS_BIT, 100000000);
                glDeleteSync(fence);
                if (frontend246_record.fence_result != GL_ALREADY_SIGNALED &&
                    frontend246_record.fence_result != GL_CONDITION_SATISFIED) {
                    frontend246_record.error = 5;
                }
            }
            frontend246_trace(67, frontend246_record.fence_result,
                              frontend246_record.error);
            GLenum names[7] = { GL_TEXTURE_BINDING_2D, GL_CURRENT_PROGRAM,
                GL_ARRAY_BUFFER_BINDING, GL_ELEMENT_ARRAY_BUFFER_BINDING,
                GL_DRAW_FRAMEBUFFER_BINDING, GL_VERTEX_ARRAY_BINDING, GL_ACTIVE_TEXTURE };
            for (int i = 0; i < 7; ++i) {
                glGetIntegerv(names[i], &frontend246_record.bindings[i]);
                frontend246_trace(65, i, frontend246_record.bindings[i]);
            }
            frontend246_record.texture_live = glIsTexture(frontend246_record.texture);
            if (glGetError() != GL_NO_ERROR) { frontend246_record.error = 6; }
        }
    }
    qatomic_store_release(&frontend246_ready, true);
    int terminal = frontend246_record.error ? 3 : 2;
    /* Abort may already own state4. Do not overwrite it or reclose rendering. */
    if (qatomic_cmpxchg(&frontend246_state, 1, terminal) == 1) {
        frontend246_trace(61, terminal, frontend246_record.error);
    } else {
        frontend246_trace(68, qatomic_load_acquire(&frontend246_state), terminal);
    }
    return true;
}

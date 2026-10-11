/*265 UI actor's immutable copy. No revocation or texture deletion is performed.
 * The existing246 close operation remains one-shot, including its reopen path.
 */
extern unsigned xwn_hud265_texture(void);
extern unsigned xwn_thumbnail265_texture(void);
static X265Rows ui265_rows;
static unsigned ui265_error;
char *xwn_ui265_report(void);
char *xwn_ui265_data(unsigned page);
static void x265_ui_capture(void)
{
    if (ui265_rows.rows) {ui265_error=1;return;}
    ui265_rows.rows=g_malloc0_n(X265_UI_ROWS,sizeof(*ui265_rows.rows));
    ui265_rows.capacity=X265_UI_ROWS;
    int64_t deadline=qemu_clock_get_ns(QEMU_CLOCK_REALTIME)+1000000000LL;
    x265_add(&ui265_rows,40,qemu_get_thread_id(),(uintptr_t)SDL_GL_GetCurrentContext(),
        xwn_hud265_texture(),xwn_thumbnail265_texture(),
        frontend246_last_texture,frontend246_last_fallback,0);
    if (!x265_context(&ui265_rows,3,deadline)) ui265_error=2;
}
char *xwn_ui265_report(void)
{
    if (!qatomic_load_acquire(&frontend246_ready)) return g_strdup("version=265 ready=0");
    return g_strdup_printf("version=265 ready=1 epoch=1 error=%u rows=%u pages=%u overflow=%u frontend_state=%d retirement=0",
        ui265_error,ui265_rows.count,x265_page_count(ui265_rows.count),ui265_rows.overflow,
        qatomic_load_acquire(&frontend246_state));
}
char *xwn_ui265_data(unsigned page)
{
    if (!qatomic_load_acquire(&frontend246_ready)) return g_strdup("version=265 unavailable=1");
    return x265_rows_page(&ui265_rows,page,1);
}

/* Diagnostic arithmetic, GPL-2.0-or-later as framebuf. ULONG/ULONGLONG/LONGLONG
 * are supplied by the NT5 DDK (or exact-width host test shim). */
typedef struct {
    LONGLONG Frequency;
    ULONGLONG Minimum, Maximum, Ticks[4];
    ULONG Count[4], Errors, Overflows, Reads, Samples, Enabled;
} XWN_PROFILE;
static void XwnProfileIncrement(ULONG *value, ULONG *overflows)
{
    if (*value != (ULONG)~(ULONG)0) ++*value;
    else if (*overflows != (ULONG)~(ULONG)0) ++*overflows;
}
static void XwnProfileCalibration(XWN_PROFILE *s, LONGLONG before, LONGLONG after)
{
    ULONGLONG delta;
    XwnProfileIncrement(&s->Reads,&s->Overflows);
    XwnProfileIncrement(&s->Reads,&s->Overflows);
    XwnProfileIncrement(&s->Samples,&s->Overflows);
    if (before < 0 || after < before) {
        XwnProfileIncrement(&s->Errors,&s->Overflows); return;
    }
    delta=(ULONGLONG)after-(ULONGLONG)before;
    if (delta<s->Minimum) s->Minimum=delta;
    if (delta>s->Maximum) s->Maximum=delta;
}
static void XwnProfileAccumulate(XWN_PROFILE *s, ULONG kind, LONGLONG before, LONGLONG after)
{
    ULONGLONG delta;
    if (kind>=4) {XwnProfileIncrement(&s->Errors,&s->Overflows);return;}
    XwnProfileIncrement(&s->Count[kind],&s->Overflows);
    if (!s->Enabled) return;
    XwnProfileIncrement(&s->Reads,&s->Overflows);
    XwnProfileIncrement(&s->Reads,&s->Overflows);
    if (before<0 || after<before) {XwnProfileIncrement(&s->Errors,&s->Overflows);return;}
    delta=(ULONGLONG)after-(ULONGLONG)before;
    if (delta>(~(ULONGLONG)0)-s->Ticks[kind]) {
        s->Ticks[kind]=~(ULONGLONG)0;
        XwnProfileIncrement(&s->Overflows,&s->Overflows);
    } else s->Ticks[kind]+=delta;
}

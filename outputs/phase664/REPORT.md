# 664: separate startup from final IF indication

Source-only derivative of closed663. Only functional diagnostic change: entry
SMC pattern0x55 becomes0xe1 (three red slots then one green, no dark slot).
CPU classifier, native admission/sender, display and polling/timed code remain
unchanged. No interrupt state change. Final amber/off is now distinct from all
patterns explicitly requested before final latch. A failed final latch can
still retain earlier patterns; partial/unobserved hardware effects stay unknown.

Validate entry versus19 result cycles and timed dark/green-off; linked entry
writes, retained entry on show/final busy, retained green/off on final busy
after modeled IF rejection, and final status/completion failures. Raw I/O and
sender outcomes are modeled; these tests do not prove hardware execution.

Use fresh C:/xwn664, owned E:/Applications/XWNLatch664, fresh capture identity,
one SITE and180-second receiver. No Windows, hook or automatic reset. User
observation and manual recovery required. Keep ordinary720p and savedXBOX480.
No hardware result yet. Preserve663 ambiguity and older failures.

Qualified source tree fee04d21555adc4d6e9347ec797e529e6f674e14; XBE SHA256 236bff441cba516dd79ee1728e880f0a4eb4fbeae97e51422687b0eec7ac2514.
53,760 sanitizer combinations plus12 boundaries,35 exact-linked cases and47
artifact checks passed.20 unchanged native/display object sections. Entry is
distinct from19 final codes and timed dark/green-off. Host pre-build shell
parsing failure is retained in invocation-failure001; no build/console started
from that rejected command. No physical result yet.

## Watched result awaiting recovery

User confirmed even amber flashing on the previously reported held black screen.
This matches final IF rejection0x55; startup0xe1 is distinct. observation002
resolves the cadence uncertainty in001. Treat as observed diagnostic code, not
raw flags or final SMC completion receipt. Why IF was set is still unknown.
Capture finished with zero datagrams; owned host processes closed. Manual
recovery requested; no collection or shutdown-integrity claim yet.

## Closed after manual recovery

One collection/audit passed: all28 selected files unchanged,5 hives parse,
savedXBOX480 intact, event history unchanged with no new events/6006. Console
is at dashboard, no hook or owned host process. Firewall retained. This is
selected-file integrity, not a full FATX check or normal Windows shutdown.

Exact linked code review found BootDetectMemorySize calls malloc/free before
video initialization. malloc executes STI at0x26122d6 and valid free at0x26122fe.
Eight isolated allocator cases show normal returns enable IF regardless of
incoming IF; free(NULL) leaves IF cleared. Internal allocator calls are modeled.
This is a concrete earlier IF-enabling path consistent with the observed code,
not a recovered physical instruction/flag history or a Windows boot fix.

See linked_audit.py/linked-audit001.json for pins and bounded reproduction.
The ordinary explicit BootPciInterruptEnable remains later than the diagnostic
path; the allocator calls supply the earlier path missing in663's review.
No source patch to firmware/allocator/driver/CPU state. Preserve663 ambiguity,
662 indication failure,661 CPU category,Ftdisk49/Popup26 and all earlier failures.

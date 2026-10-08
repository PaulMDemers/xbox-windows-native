# Same-mode reset: ordinary strict PASS

Probe124 requests actual ChangeDisplaySettingsExA CDS_RESET between GDI cases12
and13. Windows enumerates one1024x576x32 mode at60Hz; CDS_TEST and CDS_RESET both
return0. Post-reset mode, driver identity and active primary remain correct.
No registry update or driver modification. API success alone is not lifecycle
coverage; the separate video-mode-trace case observes actual callback execution.

All26 real GDI cases,78 color-cursor phases and2,555,904 restored RGB pixels
pass.26 exact393216-byte cold references; source/reference immutability,
zero reference-rendering display callbacks and26 full-frame coherence checks.
Ten of14 drawing hooks observed; FillPath,StrokeAndFillPath,Paint,StretchBlt
remain unobserved. Cursor/drawing callback totals are not cursor-only counts.

Normal shutdown1/dashboard; full allocation325directories/6785files/326directory
clusters with zero errors/orphans. Five structural hives, protected/payload/startup
hashes pass. Same96MiB1536-cluster pagefile and inherited configuration. Zero new
warning/error/application events. Eleven malformed/failing actual-log mutations
rejected. verification.json and protocol-tests.json preserve exact input pins.

The first compile rejected misleading indentation after ReleaseDC; that source
and failure are preserved in probe-build-failure001. Corrected before any guest.
The initial host-pin review rejected line-ending changes in copied host-test
sources; original bytes restored before fixture preparation. No gate was relaxed.

Case candidate001 is CLOSED; never relaunch/recollect. Emulator-only; no physical,
speed, new-resolution, boot-video/crash-handoff or independently observed driver
lifecycle qualification from this ordinary run.

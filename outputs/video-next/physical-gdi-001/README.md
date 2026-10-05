# Physical GDI baseline attempt 001

The Xbox accepted one launch at 2026-10-05 21:09:38 UTC. The four-minute observer
did not establish a dashboard return. A screen-state question is pending; this
is not a crash diagnosis or a successful benchmark. Do not relaunch the trial.

All release driver/loader hashes and the original startup hash matched before
launch. Only the new `/F/xwngdi01` helper directory and the one-shot startup
script were written. The existing GDI v3 probe is byte-identical to the passing
emulator probe. The runner differs from the earlier Paint runner only in its
private working paths. Both use NT5-compatible imports and CREATE_NEW logs.
The runner requests a normal restart only if the probe exits successfully.

`trial.json` is the authoritative launch/collection state. Until collection
restores startup, `startup_enabled` remains true. Collection first checks and
restores the preserved original startup, then saves logs and verifies unchanged
drivers. `observe.py` never launches Windows; its timeout makes no crash claim.
After dashboard returns, run `trial.py collect` with the already configured
XWN_FTP_HOST/USER/PASSWORD environment, then `qualify.py`. Do not publish local
raw logs, Windows files or credentials.

The initial read-only preflight stopped on UnleashX's explicit 553
Directory-not-found response for the new directory. No writes or Windows launch
occurred then. The corrected check also verifies the CWD `/F` directory listing
before creation; it does not treat every 553 reply as permission to overwrite.

This is one bounded physical sample of five synchronous 256x128 operations,
including GdiFlush and visibility/message checks. Even a PASS will not measure
whole-window dragging FPS, prove storage stability, or establish variance across
boots. No write-combining, framebuffer mapping, GPU or display-mode changes were
made. The rebuilt overlay is tested separately in the emulator.

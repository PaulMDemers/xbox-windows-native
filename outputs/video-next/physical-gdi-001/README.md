# Physical GDI baseline attempt 001

The Xbox accepted one launch at 2026-10-05 21:09:38 UTC. The four-minute observer
did not establish a dashboard return. The user subsequently reported that the
attached "razor chroma ornata" keyboard causes Xromwell to hang, unplugged it,
and rebooted to the dashboard. The exact USB identity and root cause have not
been independently verified. This is a reported pre-Windows boot interruption,
not evidence of a Windows video-driver failure.

Collection completed at 21:17:26 UTC and restored the original startup script
with readback verification. Neither the probe log nor runner attempt log existed.
Both event logs were byte-identical to their prelaunch captures. All baseline
driver/loader and helper hashes matched. Qualification is false because the
workload was not exercised; there are no valid physical timings from this run.
The user-authorized retry is a separate attempt, `../physical-gdi-002`.

All release driver/loader hashes and the original startup hash matched before
launch. Only the new `/F/xwngdi01` helper directory and the one-shot startup
script were written. The existing GDI v3 probe is byte-identical to the passing
emulator probe. The runner differs from the earlier Paint runner only in its
private working paths. Both use NT5-compatible imports and CREATE_NEW logs.
The runner requests a normal restart only if the probe exits successfully.

`trial.json` is the authoritative completed collection state: `startup_enabled`
is false. Do not relaunch or recollect this attempt. `observe.py` never launches
Windows; its timeout makes no crash claim. The earlier collection timeout remains
preserved in `collection-attempt.json`. Do not publish local raw logs, Windows
files or credentials.

The initial read-only preflight stopped on UnleashX's explicit 553
Directory-not-found response for the new directory. No writes or Windows launch
occurred then. The corrected check also verifies the CWD `/F` directory listing
before creation; it does not treat every 553 reply as permission to overwrite.

This is one bounded physical sample of five synchronous 256x128 operations,
including GdiFlush and visibility/message checks. Even a PASS will not measure
whole-window dragging FPS, prove storage stability, or establish variance across
boots. No write-combining, framebuffer mapping, GPU or display-mode changes were
made. The rebuilt overlay is tested separately in the emulator.

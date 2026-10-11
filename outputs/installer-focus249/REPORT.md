#249 closed host preparation failure

The first diagnostic child closed before Windows launch: trace.py required
inventory001.json, omitted from the host-kit copy. There was no loader launch or
guest helper execution. Physical-memory mode restored, no armed breakpoints,
guest resumed; observer refused the absent loader_launch field and signalled
owned closure. HMP stop/quit exit0; cold audit completed once. Full allocation
6719files/320directories/321directoryclusters, zero errors/orphans, five structural
hives and protected/startup/policy/history checks passed. No new Windows events.
This is a failed diagnostic attempt, never qualification; do not replay/recollect.

Diagnostic helper compiled with original NT5 toolchain and only KERNEL32/USER32
imports. Exact inverse source check retains original006 policy/input/idle/timeout.
Only every-five-second read-only refused-action telemetry was added. Initial host
test import failure and incorrectly counted synthetic string preserved; corrected
003 tests accepted original positive log, kept original timeout negative, and
rejected six malformed telemetry samples. No emulator/driver rebuild or hardware
change. New250 kit must supply and preflight static inventory before launching.

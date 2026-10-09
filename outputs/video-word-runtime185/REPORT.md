# Ordinary scalar-row comparison 185

Both single ordinary emulator runs completed all drawing and cold integrity
checks. Each produced five independent probe samples: 20 original copy tests,
30 orientation/rectangle/complex-clip/24-bit/XOR tests, 15 posttiming pixel tests,
25 timing loops and 50 scanout RGB comparisons. All were exact. The candidate
counters demonstrate the new scalar row copier executed in every eligible case
and timed fill/upload/overlap loop; the control has zero scalar rows and bytes.

The control launched at 2026-10-09 03:49:26 UTC and returned to the dashboard at
03:51:51. The candidate launched at 03:53:16 and returned at 03:55:32. Both owned
emulator processes are closed. No debugger, UI intervention, second launch,
physical-console access or device-policy change occurred.

Both runs observed 1024x576x32 at 60 Hz. Their pending-install guard returned
0/0, requested normal restart and recorded one EventLog6006. Full cold allocation
was consistent: 334 directories, 6,739 files and 335 directory clusters, with
zero errors or orphan clusters. Five hives, 40 protected files and startup
matched their checks. SetupAPI remained byte-identical and all three inherited
explicit unused-device bindings remained intact, with no function services.
The 86 frozen input pins and per-case source snapshots still match.

Strict qualification remains **false** for the sole inherited Ftdisk49 event,
whose source, ID, type, strings and data match181 exactly. There is no application
event or popup delta. This is a scoped display/integrity result, not a waiver of
the event gate or a release/storage qualification. The unused-device policy is
emulator-only and does not provide audio or SMBus support.

| Operation | Control median ms/op | Candidate median ms/op |
| --- | ---: | ---: |
| Fill | 0.1725 | 0.1500 |
| DIB upload | 0.2100 | 0.1725 |
| Readback | 0.1500 | 0.1350 |
| Overlap right/down | 0.1875 | 0.1725 |
| Overlap left/up | 0.1950 | 0.1725 |

All five samples and outliers are retained in `pair-review.json`. The loops
stopped at 2,000 operations and measured only roughly 0.25–0.78 seconds, using
coarse GetTickCount. Control ran before candidate. The unchanged readback path
also appears faster, so these ratios cannot isolate the scalar copier's benefit
from background activity or run order. No physical speed improvement is claimed,
and115 is not selected for installation on this evidence.

The next discriminator is a fresh reverse-order pair using longer measured
intervals with the exact same184 drivers. It must preserve all existing pixel,
counter, guard, cold and event checks. Do not relaunch or recollect either185 case.
Authoritative records are `audit.json`, `closure.json` in each case,
`pair-review.json` and the independent `evidence-review.json`.

# Longer-interval reverse-order scalar comparison

The scalar-row candidate retained lower median fill, upload and overlap times
when boot order was reversed and all timing loops reached1.5 seconds. This
supports a separate hardware benchmark. It is not physical performance or
release qualification.

The candidate launched once at2026-10-09 04:06:05 UTC and returned normally at
04:09:05. The control then launched once at04:10:48 and returned at04:13:46.
All owned processes are closed. These are fresh siblings of the same immutable
181 parent, using the exact184 OFF/ON DLLs. No driver was rebuilt or changed.
The v8 probe changed only its version/window labels and operation cap, allowing
the existing1.5-second timing target to be reached. All corresponding duration
gates were checked on the captured records.

Each case passed65 exact pixel/copy checks,25 timed loops and50 scanout RGB
comparisons over five independent processes. Every loop measured1500ms; all
operations stayed below the20000 cap. Candidate115 counters show actual scalar
row and byte coverage in eligible cases and timed rendering loops. Control
scalar rows and bytes remain zero. Both observed1024x576x32 at60Hz.

| Operation | Control median ms/op | Candidate median ms/op | Candidate elapsed reduction |
| --- | ---: | ---: | ---: |
| Fill | 0.16211 | 0.14004 | 13.6% |
| DIB upload | 0.20442 | 0.17444 | 14.7% |
| Readback | 0.13908 | 0.13939 | -0.2% |
| Overlap right/down | 0.19557 | 0.16743 | 14.4% |
| Overlap left/up | 0.19460 | 0.16587 | 14.8% |

All samples and counts are retained in `pair-review.json`. `order-comparison.json`
compares this candidate-first run with185's control-first run; all four rendering
operations have lower candidate medians in both orders. The unchanged readback
median is nearly equal in the longer pair. Its first three samples contain no
upload rows; its last two contain global background uploads in both builds.
These counters include activity outside exclusive probe rendering and cannot
be used as an isolated latency attribution. Do not subtract or normalize
readback timing to manufacture a driver speed estimate. Coarse ticks, host
conditions, cache state and emulator instruction translation remain limitations.

Both pending-install guards returned0/0 and requested normal restart, with one
EventLog6006 and dashboard return. Full cold allocation is consistent in each:
334 directories,6739 files,335 directory clusters, zero errors/orphans. Five
hives,40 protected files and startup passed; SetupAPI remained byte-identical.
All three inherited explicit unused-device bindings and92 frozen pins/source
snapshots remain exact. No debugger, forced UI, setup/history reset, second
launch, physical action or policy change occurred.

Strict qualification remains **false**, solely for the exact inherited Ftdisk49
signature; there is no application/popup event delta. The event was not waived.
The emulator-only unused-device policy is not audio/SMBus function support and
must not be copied to the physical console.

Generation001 refused the raw guard-source byte comparison before any build or
fixture. Review also found that unrestricted numeric replacement changed
immutable site addresses. Its partial source and hashes are retained privately
with `generation001-refusal.json`. Corrected generation002 uses specific names,
preserves raw guard/sites bytes and passed independent source-delta/import/order
reviews before staging. It did not change either driver.

No further blind timing repetitions are planned. The next discriminator is a
separate rollback-protected physical OFF/ON comparison using these exact
drivers, probes and geometry. No physical package is installed, and the
physical0101/video0093 baseline,0088 rollback and immutable0.1.0 remain unchanged.
Never relaunch or recollect either186 case. See each case's audit/closure,
`evidence-review.json` and `order-comparison.json` for authoritative results.

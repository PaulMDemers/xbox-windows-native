# PC605: phase-delimited bitmap sampling qualified

A fresh original Windows 2000 control passed pristine and traced execution with
identical subject logs. The recorder captured192 paired calls and84 independently
decoded bitmap-header records. It exhausted startup sampling, deferred a phase
request until the recorded call returned, and captured32 further StretchDIBits
calls without accepting a second reset. This qualifies the mechanism needed for
an actual saved-park sample; it is not an RCT layout or performance result.

## Actual control

The existing601 graphics/arithmetic control and604 header reader remain intact.
The additional subject performs71 pixel-checked8x8 top-down32-bit RGB copies.
Together with the existing copy, there are36 calls per phase:32 recorded and four
skipped in each. Both pristine and traced subjects verify all added copies.

| Boundary | Recorded result |
| --- | --- |
| Request signaled inside a traced original export | One pending frame; startup count32 |
| Next safe entry after that return | Single phase0 to1 transition; four startup skips |
| Second request | Latched; no further transition or sample-counter reset |
| End |32 StretchDIBits pairs in each phase, four skipped entries in each |

Only StretchDIBits' sample counter resets. Its capped entry stays armed to observe
the request and count skips; skipped calls do not acquire invented return frames.
Other API caps remain unchanged. The recorder polls while its debuggee is stopped
at an owned breakpoint. This adds debugger overhead even after the sample cap
and cannot be treated as an uninstrumented process or frame-rate baseline.

The control retains the60-second/10000-event recorder limits. The runner launched
each subject once, recorded both exit0 results without forced termination, then
requested normal Windows restart. Guest runner ticks are operational records,
not clock-qualified game timing.

## Checks and preserved issues

The new host phase-state test passed pending-call drainage, a single transition,
100 duplicate requests and three invalid-state cases. Exact byte identity retains
604's qualified header reader and call-stack core; their prior tests were reused
by source identity, without reopening their closed runtimes.

Code inspection found that the frozen Python checker reused `phase` for a WORDS
descriptor marker, overwriting the new sampling-phase state. The original checker
and review scripts remain unchanged. `oracle_correction002.py` creates corrected
versions that rename that local marker only. No runtime, expected counts or
acceptance conditions changed. Review002 passed the actual cached trace.
Twenty-three existing mutations and eleven additional phase mutations were
rejected, including transitions with pending frames, missing/duplicate phase
markers, false depth/counts and false skip totals. Original review001 was not
executed because the checker collision was found before the cold review.

The inherited trace summary's generic32-per-API scope string is qualified here:
StretchDIBits has32 samples **per phase**, while other API caps remain32 overall.
Inherited console print labels mentioning604 in two review helpers do not identify
their input; their paths and hash receipts bind these checks to605.

The build succeeded on its first605 invocation; inherited `build002.py` naming
does not imply a605 build001 failure. Frozen source, NT5 imports, unchanged core,
media member readback and copied binary identity passed. Trace executable SHA256:
`49376bf4a7cc3e25fc54793bae82bf086c2f2a1080b1f46fe4788d21b3a617cf`.

The VM exited at2026-10-20 04:23:30UTC. Its final automatic screenshot raced the
already exited process and recorded FileNotFoundError with process_exit0; that
capture error is preserved. The subsequent cold audit enumerated6492 files and
310 directories, verified protected OS/tool/seed identity, five clean hives with
raw-value agreement, and one new EventLog6006. Independent cached raw event
timestamps place shutdown after startup despite differing record-number order.
The inherited DRM typed-value decoding limitation remains. This is not a complete
NTFS allocation/ownership audit.

All owned VM/build/cold processes exited.605 is CLOSED: never reopen, recollect,
overwrite or parent its runtime. No game or console access occurred. Xbox last
state remains dashboard/no owned hook;596 SOFTWARE cleanup remains cold-only.
Launcher/protected720p/saves/transfer ZIPs are unchanged; ZIPs exclude RCT.
Physical Ftdisk49/Srv2013/shutdown limitations remain.

See review002.json, oracle-tests002.json, phase-oracle-tests002.json,
event-timestamps001.json and final001.json. Next is the actual saved-park trace
specified in NEXT001.md, followed by clock-qualified costs and observer overhead.

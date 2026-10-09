# Ordinary183 closed: exact copies/coverage pass, no DIB upload speedup

Single control launch2026-10-09 03:06:18UTC returned03:08:37; candidate03:10:38
returned03:13:00. Both five independent processes completed20 existing copy/
readback/overlap checks plus30 exact orientation/rectangular/complex/24bit/XOR
checks,25timed loops and50scanout RGB comparisons. Candidate recorded10000timed
upload hits plus other eligible/background hits. Control hits/bytes remain zero;
all attempts use disabled engine path. Guard statuses0/0, NORMAL_RESTART_REQUEST0,
oneEventLog6006 and normal dashboard return each. No UI action or debugger.

Both cold F audits334directories/6739files/335directory clusters,0errors/orphans;
5structural hives/protected files/startup PASS. Original setup/event histories
retained; SetupAPI byte-unchanged. Original exact-ID unused package, IDs/bindings,
ConfigFlags0/no functionServices unchanged. This emulator-only package is not
functional audio/SMBus support or a Windows race fix. Both source snapshots and
83frozen pins exact. All owned sessions CLOSED; never relaunch/recollect.

Both strictFALSE solely exact Ftdisk49/HarddiskVolume6/error3, no application,
popup or other warning/error delta. No gate waiver. Independent pair review:

| Operation | Control median ms/op | Candidate median ms/op |
|---|---:|---:|
| Fill |0.1725|0.1650|
| DIB upload |0.2100|0.2175|
| Readback |0.1650|0.1500|
| Overlap right/down |0.2025|0.1875|
| Overlap left/up |0.2025|0.1875|

These are descriptive emulator elapsed values, with all five samples retained.
They are not physical FPS, isolated body costs or reliable evidence of small
gains. Candidate's first sample is slower across several operations. The targeted
upload shows no benefit, so114 is not selected for physical deployment.

Preparatory failures preserved: probe001 compile refused misleading adjacent
cleanup statements, corrected002 compiled; Windows freeze import failed and
dependent preflight refused absent pins before any output/fixture write, then
actual WSL freeze/preflights succeeded before bootstrap. No old case reused.
181 parent copied metadata-only to portable backing, qemu-img compare equal and
all original chain hashes unchanged. Physical baseline/rollback/0.1.0 untouched.

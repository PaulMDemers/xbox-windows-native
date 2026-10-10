# Native buffer precursor213

The actual NT5 allocation/copy/release path passed in a fresh ordinary emulator
child, paired with a probe-off control. No GPU command, new MMIO operation,
cache conversion, mode change or physical access was introduced. This validates
a small staging precursor; it does not accelerate the desktop.

Matched build003 uses the same common miniport object and exact retained provider
and display identities. ON adds only the reviewed kernel allocation, matching
free and physical-translation imports. The helper is in nondiscardable.text.
Individual native dependency/library pins, including materialized thin-archive
members, passed244 checks. This is a small pinned target build, not a clean full
source reconstruction. The106 donor and210-compatible source are explicit.

Candidate001 was accepted2026-10-10 01:10:28 UTC and closed01:14:27 UTC. Its trace
records passive IRQL,16KiB allocation at physical0018f000,15,365 checks/four strips
with reason0, then successful return after the matching MmNonCached free. Four
page translations plus the last byte matched. A58x13 rectangle passed through
1024-byte staging with different source/destination pitches256/272,26 row-copy
calls and independent source/destination/padding/guard checks. The allocation
was never referenced by DMA; translation is not a GPU device-address contract.

Both ordinary children retained five GDI samples,200 movement/readback steps,
65 text cases and exact119 upload coverage. Their phase byte totals are identical.
Each shut down normally and returned to the dashboard. Full cold allocation:
325 directories,6730 files,326 directory clusters,zero errors/orphans. Five hives,
protected files, startup and typed device policies passed. No measurement-interval
or application events occurred. No missed trace records were reported.

Whole-boot qualification remains FALSE in both for the actual inherited Ftdisk49
on HarddiskVolume6. It is not suppressed or waived. Neither these scoped passes
nor the native buffer call returns qualify GPU submission, physical operation,
performance, complete storage/dump recovery or release promotion.

Host planner tests in212 passed324 pixel/guard cases and100000 malformed plans at
O0/O2 ASan/UBSan. The exact native helper's host fault tests passed27 OFF/96 ON
checks across nine cases;45 trace-parser checks passed. Host providers are mocks;
the ordinary candidate supplies separate actual NT5 runtime evidence.

Failures remain preserved: host001/002 expected8 copies instead of the actual26;
build001 selected unbuilt210 objects; build002 exposed uncopied thin-archive
members; review001 selected original physical bootvid instead of the actual
shared0106 fixture provider; preparation wait001 had a wrong pre-source guard.
Control's first host auditor failed at a missing parser import before cold access.
The original failure/frozen inputs remain intact; the first successful cold audit
used the exact211 dependency and a new hash-guarded auditor. No guest was repeated.
A Windows pair-comparison invocation also stopped at WSL-only imports; the
read-only WSL comparison then passed. No failed outcome was relabelled as PASS.

emulator-pair-review.json and evidence-review.json retain exact closed results and
98 additional evidence pins. Actual xemu RAMIN backing remains an emulator-model
qualification limit described in212. Physical0101/video0093,0088 rollback and0.1.0
are unchanged. All root-owned213 processes are closed; candidate001 and control001
must never be relaunched or recollected.

# PC614 host-correlated coarse-clock control

613 remains CLOSED FAILED: reported QPC frequency26.52GHz made a two-second
sleep appear0.286s;33.55M work iterations completed under100ms. Do not reuse that
runtime, waive its gates or call it a performance pass.

Fresh immutable404 child, original workers only. Retain raw QPC diagnostics but
use tick counts as the candidate elapsed clock. Send bounded COM1 START/END
markers around each work interval; an independent host reader timestamps complete
lines with time.monotonic_ns. Compare host elapsed against guest tick elapsed
within max100ms or5percent, predeclared before launch. Two five-second sleep
controls and four1073741824-step LCG workloads, unsampled/sampled/sampled/unsampled.
Require busy CPU>=1s, sampled busy>=5 observations and sleep CPU<25percent. Retain
parent/child counter containment, deterministic checksum and8MiB commit growth.
All expected12 markers must arrive in order and agree with logged guest ticks.

This is PC TCG clock/counter qualification, not game costs or Xbox performance.
Host marker transit/scheduling delay bounds precision; no correction factor is
applied to QPC. Sampling costs are observed at coarse CPU timer resolution, not
assumed zero. A new game control still needs the matched save and phase evidence.
22GiB admission/2GiB budget/20GiB reserve; no physical access or driver changes.

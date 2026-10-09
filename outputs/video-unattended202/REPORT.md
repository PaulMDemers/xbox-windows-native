# Unattended hardware benchmark loop validated

Both physical202 runs completed without requesting manual wizard handling. Each
exact201helper006 cancelled four verified known wizards (targets1/2/3/4), joined0,
then the runner observed5100ms actual install idle. All five exact199v9 probes
completed:265 pixel checks,200 actual window paint/readbacks,25 timed loops,50 scanout
comparisons, valid profile/counter/caps coverage. SetupAPI measurement bookends were
byte-identical within each run (control314234bytes, candidate317456bytes), final
install query0, one unforced normal restart, EventLog6006 once and dashboard return.

Control accepted21:06:44UTC and returned21:10:38; candidate accepted21:12:32UTC and
returned21:16:36 on October9. Both collected once, restored normal startupFIRST,
then original display files/SYSTEM. Independent readback/current32-entry rollback,
protected/providers/deployed-helper hashes, ten structural/checksummed/sequenced
hive snapshots and typed policy checks pass. Persistent PCI/service policies remain
unchanged. Raw-review-control001.json and raw-review-candidate001.json reparse actual
packets and pin evidence. Both narrow display scopes PASS; both whole-boot strict
results remainFALSE for inherited Ftdisk49 before measurement. No interval warnings,
application events or popup failures. No full physical allocation/all-file, dump,
new-mode or release qualification. No physical baseline promotion; Xbox at dashboard.

The two fresh emulator siblings also passed the same joined-helper benchmark scope,
three emulator known targets1/2/5, identical284810-byte bookends, normal shutdown and
full cold allocation324dirs6727files325dirclusters with0errors/orphans, fivehives,
protected/history/typed policies. Thirty natural binding deltas retained. Wholeboot
strict soleFt49 FALSE. Control three brief monitor snapshot stop/resumes explicitly
recorded; first two wrong640 geometry captures are not graphics failures. Actual
cold mode1024x576x32 at60Hz. No unaffected emulator timing or physical-speed inference.

## Physical profiling observations

The implementation was identical except enabled profiling clocks (scalarOFF both).
Five samples per boot are descriptive within-boot samples, not independent boots.
The enabled-profile global mean elapsed time per observed upload box is roughly
1.55-1.56ms; corresponding EngCopyBits means are about0.83ms for DIB upload,0.86ms
for down/right overlap and1.11ms for up/left overlap. PatBlt engine mean about0.47ms.
These means include background/preemption and mixed clip boxes; they are not a
precise cost for one isolated rectangle. Complete-wrapper mean about1.56-1.58ms
includes upload body; adding the two double-counts. Framebuffer transfer is a
substantial cost, while complete-wrapper-minus-body overhead is comparatively small.
No calibration subtraction or exclusive CPU-time claim.

The window workloads are NOT globally matched: control uploaded20174728bytes in
1066boxes with570ms wall time; candidate43528468bytes in2082boxes with825ms wall time.
TextOut global counts279 versus876 also differ. Forty owned moves/readbacks pass both,
but other windows, exposure/clipping and global work are included; their exact
producer is unresolved. This cannot attribute the45percent wall difference to
profiling overhead or a regression. Candidate global upload-body elapsed around
529ms is informative about cost, not a clean comparative speedup. Small primitive
loop rate differences (~-0.7 to+1.5percent medians) do not establish an improvement.
See physical-comparison.json for exact samples/ranges and raw evidence pins.

## Next implementation target

Reduce unnecessary framebuffer byte volume before optimizing small bookkeeping.
Pinned198 display/shadow.c XwnTextOut calls XwnUpload(p,NULL,pco), which uses the
whole clip bound rather than an explicit text bound. Inspect the actual documented
text/glyph/opaque/extra-rectangle contract, then implement a conservative bounded
text-upload candidate with the current full-clip fallback for unsupported cases.
Retain clipping, surface ownership, framebuffer mapping/cache and synchronous
visibility contracts. Verify transparent/opaque/overhang/extra/complex-clip pixels,
actual transferred bytes and ordinary emulator cold checks before a new hardware
pair. For window comparisons, record or constrain exposed-background work so
changing global byte volume is explicit. No proposed fix is compiled or deployed.

## Preserved state

Exact198 providers/exact199probe/exact201helper remain unchanged; only new202 runner
joins the child before unchanged194 guards. Unknown/inactive dialogs still refuse,
Welcome remains, no devices disabled or settings/events suppressed. Prior200failed
candidate,003large-log stale suffix and original111nonASCII physical corruption/
restartunknown remain unresolved and separate. Preservephysical0101/video0093,
0088rollback and immutable0.1.0. Both owned202 emulator disks offloaded09m after
closure/hash/readback with original-path junctions; no backing-chain relocation.
All owned sessions CLOSED; no follow-up launch or automation running.

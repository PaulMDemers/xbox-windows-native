#651 staged, NO SITE: timing readback and sampled-status diagnostic

650's static review found that the intended480p timing values agree with the
retained successful stock631 readings. It did not establish actual register
state in the failing native launch. This candidate addresses that gap without
changing the mode table, polling predicate/limit or functional output ordering.
No651 physical result exists until launch, observation, collection and audit.

## Candidate and access scope

Private C:/xwn651/build001/default.xbe is303856 bytes, SHA256
97a3f1a1874aae98f260303b6e9ace5e27fbb324d2fdc24aab646726df4f1906.
Base tree remains633's70c0a6c5aff82537f489e7d18410d5980fa797a7 with its mode3
flags and GCC12 pin.649 adapter source and object text are identical. The new
wrapper reverses exactly to649;649's recorded reversal to633 remains retained.

Two snapshots bracket the original apply function. Before setup, only eligible
requests receive a snapshot. After setup, only a transaction marked mutated
receives one, before LED signaling/reset. On failure, this is after the original
fail-blank write, not an atomic snapshot before the timeout. Snapshots contain:

- Eighteen32-bit reads: fourteen observed FP timing fields, general control,
  VPLL, PCRTC_CONFIG and the already-used0x6806a0 handshake location.
- The23 CRTC indices used by631, only when sampled IF is clear. Their selector
  is saved/restored and verified. No CLI/STI is added. IF set produces an unknown
  CRTC comparison, not a fabricated match. Each enabled snapshot has18 r32,
  25 r8 and24 selector writes; IF-set snapshots have18 r32 and no indexed access.
- Flags before/after indexed access. This does not exclude NMI or establish a
  coherent hardware-wide snapshot; reads take time and may affect execution.

No CRTC data write, new video-status read, interrupt clear, clock programming,
encoder read or firmware-state borrowing is added. Existing status samples in
the649 RAM trace supply the failed-wait classification. Timing comparison uses
the established631 subset and masks; retained clock/config are observations,
not expected programming values. All detailed snapshots remain RAM-only.

## Watched indication

For error22 only, there are FOUR eight-requested-second indications separated
by two-requested-second dark pauses. The FIRST now identifies the failed wait;
it is not the old generic red/green prefix. Original reset follows the sequence.

| Slot | Meaning | Patterns |
|---|---|---|
|1|Failed wait|1 red/off;2 green/off;3 amber/off;4 red/green;5 red/amber;6 green/amber|
|2|Masked CRTC and FP/general comparison|both match green/off; CRTC mismatch red/off; FP mismatch amber/off; both mismatch red/amber; incomplete/unknown red/green|
|3|Existing samples in failed wait|constant0xff red/off; another constant byte green/off; varying byte amber/off; invalid/incomplete trace red/green|
|4|Post-result bits0/4 at0x6806a0|equal green/off; different red/off; not captured/all-ones red/green|

Other setup results retain the original single result-class indication. A
successful setup gives green/off and continues into Windows after eight requested
seconds. No automatic Windows restart hook is installed. Leave Windows running
if it appears; collect only after an explicitly observed return/restart.

Unknown, missing, mixed-up or unreadable indications are inconclusive. None
permits retrying an accepted/uncertain launch. Each diagnostic SMBus write is
attempted once; signaling failure remains possible. The unchanged timer delay
can hang if its timer freezes, so the observer's600-second bound is a host bound,
not a guarantee of console recovery. The user may need to reset a hung console.

These colors report predicates only. A comparison match is not boot success;
equal handshake bits do not establish completion of a particular request;
constant0xff is not proof of invalid MMIO. No exact byte/delta is externally
reported by this candidate. Capturing/indicating changes timing and code layout.

## Validation

-2042 ASan/UBSan capture/mask cases: all256 saved selectors for each progressive
 profile, IF skip, failed restoration/changed IF and every captured comparison bit.
-5143 LED/classification cases: all byte values, failed-wait classes, comparison
 masks, four slots, invalid states and every failed diagnostic write.
-44 differential adapter scenarios and235552 retained adapter assertions pass.
-140 exact linked wrapper/capture/LED outcomes exercise modeled callbacks,
 selectors, IF skip, ABI, reset and all nine possible indication-write failures.
-10 exact linked adapter/profile cases and32 compiled timer cases pass with
 synthetic hardware callbacks/IN values. No physical timing is inferred.
-Profile text/rodata, timer/library text match633; adapter text matches649.
 The unchanged bytes and new access scope are recorded in review001.json.
-Controller tests admit exactly one SITE for accepted or uncertain replies.

All compilation/temp/output is on C with20.02GiB output and WSL-backing checks.
No new VM/disk or recovery copy. Build lease released. No console experiment has
been repeated. Historical failures and closed647/648/649 evidence remain intact.

See actual preparation001/stage001 records for physical staging state, and
NEXT.md before any launch. Ordinary720p/startup are protected; unique owned
E:/Applications/XWNReadback651 only, no dashboardC access and no startup hook.
Automation remains paused. No functional fix or expanded platform claim.

Preparation and staging completed:28 selected baseline files, two staged files
read back exactly; no launch request. User watch-readiness question is pending.
Preparation observer9811 and staging process51059 exited0. No owned process
remains; no hook/rollback. Existing physical lease retained.

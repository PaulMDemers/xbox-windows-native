#245 natural callback retirement observed; display still active

The corrected fresh emulator run preserved all three dirty surfaces,3072000
bytes, using the existing GL readback/conversion/comparison and fences. The SAME
boot then reached pinned FreeLoader entry. Causal logs prove all three surface
hooks were requested for removal, actually unlinked and freed by the CPU actor
before the second marker. These frees occurred while the CPU was RUNNING:
stopped-CPU callback execution is not proved.

| Actual finite evidence | Result |
| --- | --- |
| Lifecycle records |13648|
| Callback insert/remove/unlink/free chains |23/23/23/23|
| Preserved target hooks retired before FreeLoader marker |3/3|
| Natural surface flush begin/end |1/1|
| Complete frontend loan/selection/glFinish/release chains |1744|
| Accelerated / fallback completed frames |1496/248|
| Active frontend loans at Xromwell / final markers |0/1|
| Sync empty-surface returns |0|
| Native GPU ownership / display quiescence |FALSE/FALSE|

The final marker sampled an actual loan in flight. A prior completed fence does
not close that later loan or prevent future frontend frames. The readonly paired
census still retains texture/current-unit/shader/module/vertex/display references
after preservation, including the modeled texture/surface alias. Actual surface
GL deletion return and CPU-hook free do not prove complete shared-context
object destruction. No cleanup, new fence, queue drain or native permit was added.
Dirty flags/latest contents at the later natural invalidation were NOT logged.
Earlier readback does not prove that no new draw occurred before disposal; the
existing flush path with its disabled download remains an unresolved boundary.

The marker observes actual pinned Xromwell11100 after its finite snapshot and
before preservation; the second observes actual pinned FreeLoader200a20 after
200ms outside actor locks. Hooks retire during the natural transition, not by
a debugger-induced disposal. All GDB points were removed, memory mode0 verified,
guest resumed and trace events disabled. No memory/register writes or RAM
captures were used. Surface bytes use the SAME GL conversion path as oracle,
not an independent pixel reconstruction.

Actual245 native CPU workload PASS:65 allocations/releases/exposure refusals,
3194880 verified bytes and four joined workers, with retirement-model refusal.
Normal shutdown6006=1, dashboard return and orderly HMP stop/quit host exit0;
full allocation6724 files/320 directories/321 directory clusters, zero errors/
orphans; five structural hives, protected/staged hashes, startup, actual device
policy and event/SetupAPI history PASS. Application event delta empty.
Strict qualification remains FALSE for sole Ftdisk49 type1. Ordinary, physical,
complete-reference retirement and native acceleration qualification remain FALSE.
This is not all-file-content, power-loss or repeat-boot durability evidence.

Actual compiled binary is244/build005, SHA
acae1c8123ba1e040049f1a58aacf72fc0c4f9aa54fe898662d36ca70a40394b.
Fresh run nt5-phase245-preserve001 uses the same immutable239 seed and native
224/219/211 captured core, with no synthetic null bindings or driver change.
Compiled source parent_obj stays first with an actual offset-zero static
assertion. The negative layout test detects244's bad compiled header; callback
body O0/O2 ASan/UBSan each4096 cycles/102405 checks PASS. Host causal parser20,
pair54, guard72, close25 and connection12 checks PASS.1036 frozen pins unchanged.

Failed244 and every preliminary build/setup failure remain separate. Full raw
log, complete pairing JSON, source capsules, protected binaries and disks remain
private; the public compact lifecycle report pins the full private analysis.
All root244/245 actors are closed; no guest queued. Physical baseline, rollback,
0.1.0 and peer work unchanged. Closed portable copies were verified on E with
original paths retained, and no backing chain moved.

Next: design a bounded frontend loan-close protocol with finite completion
evidence outside locks needed by the UI/renderer. Observe actual GL/context/
texture/shader/vertex ownership before reference disposal or any native grant.
Do not infer stopped-CPU queue completion from this running-CPU trace, or patch
the earlier static sync-null branch: that branch had zero actual hits here.

#280 — proposed three-boundary worker passes host checks

No renderer/native build or guest preparation/launch occurred. No release is
installed, and no shared source, SDK or physical console changed. All owned
subprocesses closed. This is an implementation/testing step toward runtime
integration, not evidence of an actual texture release or video acceleration.

The proposed worker uses distinct immutable pre-release, post-release and
post-resume slots with actual epoch rules1/2,3/4,5/6. Its candidate state validates
refs1/cache1/unit0 after release without rewriting fields for the old277 contract.
It checks the deadline again after observer arm, requires fresh CPU acknowledgments
and the post-release graph before guest resume, and preserves partial mutation masks
on refusal. Failed scalar publication is never retried. Initial records stay
immutable during the final transaction.

Results:

- worker-host004:186 proposed actual orchestration/capture paths,27366 assertions,
  ASan/UBSan clean. CPU/GL/graph authorization, release and snapshot interfaces are
  explicitly modeled; the production orchestration/validation bodies are compiled.
- graph-host001:385 collector checks across both modes and all three stages,
  ASan/UBSan clean. Saved identities require a current live cache edge; absent,
  duplicate, over-capacity or changed objects refuse. QEMU/GL objects are modeled.
- publication-host001:512 real pthread publication races with1024 competing writers;
  actual record writer, modeled atomic caller/getter, no repeated publication or
  alteration of the initial record. ASan/UBSan clean.
- transport-host001:2138 independent changed/missing/ambiguous transport mutations
  rejected across both modes and three stages. Inputs are actual host test output,
  not guest evidence. Unknown row kinds and truncated binary records refuse.

worker001 failed compilation on two misleading-indentation diagnostics; its exact
inputs/result remain frozen.002 passed184 paths/26103 assertions before the explicit
timing rows.003 passed184/27186 with timing rows.004 adds the post-arm deadline and
quiescence check and two associated failure paths. All earlier capsules/results
remain preserved and are not rerun. The unchanged279 helper and original277
contract are retained byte-exact; the new stage/ref rules are separate.

Missing integration is explicit: actual complete graph/UI proof provider, texture.c
release/snapshot wrappers, QOM request/getters and real complete transport tests.
No worker PASS authorizes a guest by itself. A fresh matched control/candidate with
unchanged guest contents and full cold audit remains necessary after implementation.

278 remains closed: scoped unchanged no-release reuse PASS, strict whole-disk
equality FALSE for the reserved byte.279's counter-field match is only an inference;
the writer remains unproved. No old evidence, audit, gate, run or fixture was changed.
Physical demo/recovery256, immutable0.1.0,0088 and all rollbacks remain untouched.

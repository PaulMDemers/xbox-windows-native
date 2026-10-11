#265 ownership-ledger implementation; first runtime failed in host recording

The read-only diagnostic compiled, but emu001 is a CLOSED FAILED attempt. One
native kernel/process/driver/handle/four-page attestation completed. Actual UI
capture returned1807 rows, eight pages, error0/overflow0 at the closed frontend
boundary. The host recorder then failed its immutable-page comparison. It had
written HMP CRLF text through Windows text-mode newline conversion and read it
back through universal newline decoding. The original failure is reproduced by
266's transport test. The second comparison response was not saved, so there is
no retrospective claim of actual immutable-page equality for265.

No ledger request reached the renderer, no texture was disposed and no native
GPU grant was attempted. The controller removed its breakpoint, restored physical
memory mode0, requested frontend reopen and quit the owned emulator. Guest normal
shutdown did not occur. The once-only cold audit found322directories,6726files,
323directory clusters,13orphans and four WBEM chain errors. Integrity, diagnostic,
orderly-host and strict qualification are FALSE. Preserve the interrupted disk;
never repair, reboot, recollect or use it as a parent. Controller86523 is CLOSED.
Run accepted22:12:31UTC; trace closed22:13:34; controller/cold audit22:14:16.

## Compiled and tested artifacts

- Renderer003: E:/Codex-archive/xbox-windows-native/ledger265-build003/
  xemu-ledger265.exe,191652402bytes, SHA256
  b52c671e6f5ea643eaac1e1a8970cf5454fa776fdb763debfba5030b43b41624.
  Exact263 source parent, seven changed files,15 private source snapshots;
  all borrowed sources restored.78 inherited warning instances, no new messages.
- Observation-only native probe001:35205e9ac65af98ccc04ca7ea39c98cb91451b2c2e32f2f694107e5bc414cb0d,
  11483bytes. Imports, cdecl checkpoint ABI and both actual optimized callsites
  verified. Uses unchanged258 reboot-held driver. This probe expects CPU seed0
  twice, not renderer-injected pixels; it cannot be substituted for263's protocol.
- Exact bounded ledger core:195138 ASan/UBSan checks. Independent row decoder:
  19 negative controls plus an accounted unit-only positive case. These are host
  tests, not runtime GL or disposal evidence.
- 1993 frozen inputs,108 invoked host dependencies. Fresh standalone preparation
  is readback-verified and remained unchanged; it is separate from the failed
  runtime disk. No physical hardware access or deployment occurred.

Renderer001 failed compilation due to missing qemu_strtou64 declaration;
renderer002 failed an exact source anchor before compilation. Both have separate
private input/source capsules and retained records.003 corrects the include at
the actual nv2a.c anchor. Preflight001 also failed before launch because the host
review expected the entire source manifest in the15-file capsule. The corrected
review compares the full parent manifest and hashes every saved source. Original
preflight script and failure record are retained.

See DESIGN.md for actual locking, epochs, bounds and unresolved completeness.
Shader actor completion remains unknown, UI names are retained, indexed bindings
and container attachments require later review. No comprehensive backend
retirement, performance improvement, ordinary qualification or physical promotion
is claimed.263's separate scoped pixel preservation remains unchanged; Ftdisk49
remains a strict event failure. The physical audio004/video118/shared158/FATX0101
demo, private256 recovery and immutable0.1.0/0088 rollbacks remain unchanged.

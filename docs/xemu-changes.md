# Local xemu changes

Audited October 26, 2026. The latest Windows fixture, 639, uses the retained
322 candidate executable (`ea3473314e6c0ea0...`). That build carries **four
logical changes across seven source files** relative to recorded base
`e72e76bd1f12ce45c6c63b4196c6918ea2cc705d`.

| Change | Purpose | Qualification boundary |
| --- | --- | --- |
| NVNET access-size alignment | Permit aligned byte/halfword MMIO writes used by Cromwell | Partial-register side effects still need dedicated hardware comparison |
| Optional NV2A resource/BAR experiment | Environment-selected 128 MiB BAR1 alias and optional BAR2 | Synthetic resource experiment, not a faithful-hardware claim; compiled presence does not mean enabled in every run |
| Guarded CPU-write surface eviction | Preserve GPU contents before discarding/recreating cached surfaces after CPU writes; retain bindings during an open primitive | Later build003 corrects the earlier draw regression; scoped native/Windows evidence is not general game/performance qualification |
| PRAMDAC timing-register storage | Retain VTOTAL, VSYNC_START and HTOTAL writes, with reset and migration fields | Register storage only; no raster/field simulation. Actual migration save/restore remains untested |

[679's source audit](../outputs/preparation679/xemu-audit001.json) verifies all
11,340 retained parent file hashes and reconstructs the complete candidate
manifest hash. It does not rebuild or reopen a closed runtime. The source delta
is independently distinguished from the executable selection in
[639](../outputs/windows480p639/runtime.py).

The shared Linux project also has a **separate NVNET TX-batch draining fix**.
Thus five named functional/experimental patch families appear across the two
projects, but only four are in this Windows baseline. The TX patch has its own
matched Linux evidence and is not silently attributed to Windows. See the
[earlier upstream inventory](../outputs/upstream-xemu/README.md); its upstream
status was checked then, not refreshed by this local audit.

Historical renderer ledgers, ownership queries, HMP bridges, wait snapshots and
other diagnostic builds are retained separately. They are not additional patches
in the 322 executable. Their file/attempt count would overstate the maintained
functional delta. Stock xemu (`7da537938ea2ac09...`) is also retained and was used
for standalone native mode tests in 633; stock and patched results must stay
distinct.

These are emulator-side changes. They are not included in the native Windows
package copied to physical Xboxes, and none establishes native NV2A acceleration.

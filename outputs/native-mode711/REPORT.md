#711: baseline-only transaction call before display blanking

710's cyan hold established the larger native handoff/PCI/timer checkpoint on
one physical run.708/709 remain closed blue-to-black failures; their exact native
failure stage is unknown.711 adds the real transaction call and baseline checks,
then returns a distinct diagnostic code0x711 immediately BEFORE blank(g).

The source differs from704 transaction003 only by that checkpoint insertion.
Argument/layout/IF/baseline rejection and indexed-selector restoration are
preserved. Later mode/encoder programming remains retained source but is
unreachable. The linked baseline calls only bounds704 and has no port I/O.
Other retained helper functions exist in the linked image but are never called
by711; instruction-model execution rejects entry to those helpers.

The fresh raw payload is5080 bytes, padded with0xCC to the existing9916-byte
extent to retain the32KiB page partition.15 relocations are decoded, including
four internal absolute32 entries; the exact-count guards and all rejection tests
were updated accordingly. The32KiB allocation/alias/stack/table contracts remain.
The compiler and all source/binary hashes are pinned in build records.

Fresh checks:131379 ownership cases; ASan/UBSan page construction at four
placements;12 diskless CPU fixtures, all closed;114 exact relocated baseline-call
models at two addresses;23 nxdk page-builder cases and372 ownership cases.
The models cover all request fields, null arguments, IF rejection, PCI/timer
refusals, baseline register mismatches, selector restoration, bounded result and
stack writes and independent whole-framebuffer/guard checks. Only index-selector
writes and CF8 save/restore are allowed: no encoder/ACPI-control/mode writes.
These tests do not prove physical CPU/cache/device behavior.

## Physical observation guide

BLUE is the initial kernel picture, shown for five seconds. The thin TOP bar
becomes GREEN after native entry. The SECOND bar becomes CYAN after PCI/timer
checks, then GREEN if the baseline-only call returns0x711; ORANGE means another
return code. Other pre-call refusals: RED GPU PCI, YELLOW SMBus PCI, MAGENTA LPC
PCI, WHITE timer. Native code deliberately holds, requiring manual reset only
after the result is recorded. The short cyan transition need not be visible.

A GREEN second bar qualifies only this pre-blank checkpoint; no native mode
initialization or Windows1.6 support is claimed. No startup hook, Windows launch
or console C access. Read launch/observation/collection receipts for actual state.

## Closed physical result

One SITE accepted at2026-10-27T05:41:57Z. User reported "Green, holding" in
response to the final second-bar color question. The diagnostic GREEN result
requires return0x711 from the real baseline checks before blank(g). Both bars
were not separately enumerated and no photo/native RAM capture was supplied.
This is observed checkpoint evidence, not native mode initialization.

After confirmed manual power-cycle, nine preparation reports were double-read
and audited. Last persisted phase is handoff_armed; it remains pre-transfer file
evidence. Kernel PCI/CRTC/sequencer/geometry and allocation mappings match710.
Independent alias/disjoint-range checks and all source/binary/report pins pass.
Unrelated directory entries are unchanged.711 is CLOSED; no normal Windows
shutdown is claimed. No hook/owned host child; console at dashboard.

The call/baseline boundary is now observed on this run.708/709's exact failure
phase and possible intermittency remain unresolved. Next review a bounded
blank-and-restore-only probe before any encoder or geometry changes.

## Exact executed-source preservation

Publication whitespace checking rejected two unchanged inherited files:
gpu_legacy.c had an extra final blank line; gpu_types.h mixed spaces and a tab.
source-preservation001.json retains their exact executed UTF-8 bytes and hashes.
Only publication whitespace was normalized; all original build/test receipts
remain unchanged. Reconstruct those two inputs from that snapshot when replaying
the recorded build into a NEW private directory. Neither binary was rebuilt or
substituted after physical launch. The current published hashes are recorded too.

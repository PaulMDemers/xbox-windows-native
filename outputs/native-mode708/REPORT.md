#708: integrated native480p transaction candidate

This watched experiment combines the larger705 bridge with the unchanged
9,916-byte704 video transaction. Kernel preparation follows the watched707
allocation/context checks. It is a constrained transition from kernel-prepared
720p, not a from-reset driver or Windows1.6 qualification.

The new bridge requires LPC BAR0=0 and configuration84=8001, matching706/707,
instead of705's permissive OR. GPU/SMBus/LPC identities, commands and bases are
captured again natively; CF8 is restored. A bounded PM interval must progress
at least1688 and at most33750 ticks within100000 additional reads before the
transaction. Kernel3375000Hz is required. This repeats the nominal699 timing
assumption; it is not independent frequency calibration.

## Launcher and validation

The launcher requires the observed64MiB GPUd3/MCPd5 console, HDMI/HDTV settings,
both480p and720p capability, expected PCI/VGA baseline and checked framebuffer.
It allocates and validates the1MiB source,32KiB native region and all eight low
virtual alias pages. Full physical/virtual copies are compared before entry.
The actual nxdk page builder matches the tested host pages byte-for-byte.

Pre-file-write and pre-arm CPU snapshots are persisted. Final CPU values are
RAM-only at8e8..900, within the bridge's excluded mutable scratch. The source
template remains unchanged. No kernel API is called after the final capture.
After native entry, failure holds; there is no firmware return or retry.

- host-plan001:131379 ownership cases; ASan/UBSan page construction and43
  output-preserving rejections per placement.
- cpu-run001:12 fresh diskless QEMU fixtures, four mappings and eight failure
  paths. Only bounded expected status-bar writes occur; all VMs are closed.
- integration001:38 post-transition bridge/transaction model cases, including
  strict PCI refusal, stalled/backwards native timer, encoder/setup/enable
  failures, exact wire sequence, every successful pixel, and stack/guard checks.
- page-review001:45 actual nxdk compiled page-builder cases, including two
  byte-exact matches with tested host pages and43 rejection cases.
- plan-review001:372 actual nxdk compiled ownership cases.
- build001:exact bridge and payload each appear once in the linked executable.

Host models do not prove physical mode timing, encoder internals or output gating.
The payload preserves clocks/PFB/interrupt state and refuses locked CR11; it never
writes CR11. Post-blank failure makes a bounded reblank request and stays held.
Black output may leave the exact failure phase unknown; it is not counted as
success or repaired by borrowing firmware state.

## Expected observation

The kernel first shows a720p picture with a BLUE top bar for five seconds.
Native entry paints a thin GREEN top bar. Early refusal uses a second bar:
red GPU, yellow SMBus, magenta LPC, orange request/baseline, white timer.
Cyan briefly marks timer completion before the transaction.

Success should replace that picture with a720x480 pattern: white border, GREEN
top region, red/green/blue/white quadrants and a black/white checker patch near
the bottom. That checker patch is absent from the kernel picture. The result
deliberately holds for observation/photo and manual power-cycle. A green native
entry bar alone is not transaction success. No Windows or startup hook is used.

Read stage/launch/observation/collection receipts for actual hardware state.
Retain all old failures and closed runtimes; do not relaunch an accepted attempt.

One SITE was accepted at2026-10-27T05:13:07.663033+00:00 after exact staging.
Native result/photo is pending. No reset or collection has been requested;
no physical success is inferred from host tests or launch acceptance.

Publication whitespace check found one trailing space in the CPU harness.
The exact executed harness is preserved in cpu-source001.json with its original
SHA256; cpu.py differs only by that removed space. Original CPU/build receipts
are unchanged. Reconstruct that exact source from the snapshot when verifying
those closed receipts. No executable or payload bytes changed.

## Closed physical result

User reports BLACK; initial blue-picture sequence and input signal status were
not observed. User requested a watched rerun. After confirmed manual power-cycle,
nine preparation reports were double-read and audited. Last persisted phase is
handoff_armed, with admitted allocation and both copies exact. This does not prove
native entry, encoder completion or the failure phase. No visible mode success.
Staged bytes and unrelated entries unchanged. Runtime708 CLOSED; never recollect
or relaunch. A fresh709 namespace is being prepared solely for the requested
watched repeat. No functional fix is inferred or applied.

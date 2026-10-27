#704: integrated480p transaction passes host tests

The final candidate combines blanking, source-backed GPU setup, checked geometry,
the Xcalibur encoder sequence, VGA setup/readback, a bounded framebuffer pattern,
settling and conditional output enable. It is a constrained native720p-to480p
transaction candidate, not a qualified1.6 driver. No XBE was built, staged or
launched; the console was not accessed and remains last known at the dashboard
after closed703. Ordinary720p Windows is untouched.

## Current candidate and validation

Use **transaction003.c / build004**. The raw9916-byte payload SHA256 is
`126594c9ae628e7920667339aaf5963fe86984816749c03085424a98370f125c`.
Build003 has identical bytes; build004 retains the relocation metadata needed
for a future owned native allocation. GCC12 and all source inputs are pinned.

`cpu004.json` passes880 linked-instruction model cases and32,770 allocation
boundaries. Cases include every encoder transfer failing through four different
status paths, every table delay going backward, finite stalls/timeouts, short
reads, dropped GPU/VGA writes, preserved-field drift, failed pixel readback,
settle failure and failed output enable followed by reblank. Exact wire bytes
use the independently retained681 table oracle. Successful paths verify every
pixel against a separately constructed image. No interrupt/clock/PFB writes are
allowed by the model; selectors, IF, code/request bytes and allocation guards
are checked. CR11 writes are explicitly forbidden.

`cpu005.json` passes12 linked cases at four relocated payload addresses plus
nine invalid-relocation/placement cases. It confirms absolute function pointers
and table addresses move with the payload. It does not test real page tables,
cache transitions, NV2A scanout, external clocks or ACPI physical gating.

The build and tests used the shared build/emulator leases and projected20GiB
reserve checks, including the WSL backing drive. No VM or host child remains.

## Preserved failures and superseded candidates

- cpu001 failed after75 cases: the fault affected both a read-modify-write and
  its readback, so the harness expected the wrong failure stage. cpu002 restricts
  that injection to post-geometry readback and passes878 cases. Code unchanged.
- review001 rejected build001's kernel-high-alias contract for a paging-off
  handoff. Build002/cpu003 use physical framebuffer addresses;879 cases and
 32,770 boundaries pass. The old code and receipt remain intact.
- review002 rejected writing CR11 merely to unlock it. Build003 requires the
  base already unlocked and never writes this shared register. cpu004 passes.
- sources001 preserves three429 source-download responses. Versioned primary
  source pages were read; compiled retained local inputs are hash-pinned.

The final candidate preserves all known limitations in SOURCE-REVIEW.md. The
primary remaining work is integrating its larger payload into a checked native
handoff and independently validating every page, relocation, stack and table
extent. Only then prepare a fresh watched physical pattern attempt.

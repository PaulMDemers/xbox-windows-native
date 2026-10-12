# 278: complete unchanged texture reuse control

The no-release standalone control passed its scoped ownership and unchanged
texture-reuse gates. Overall strict qualification remains **false**: one byte in
reserved disk sector 1536 changed. Complete 8 GiB mapping and 65,536 overlay-byte
comparison establish that filesystem bytes are inherited unchanged, without
attributing or waiving the reserved-area write.

`emu001` ran once from 2026-10-12 01:38:04 UTC to orderly closure at 01:39:06 UTC.
All owned processes are closed. Never relaunch, recollect or parent this runtime.
No release helper, native driver, SDK or physical-console change was installed.

## Actual evidence

- Three native checkpoints (11, 22, 33) validated the owned XBE, full text,
  caller, kernel-export identity, allocations, vertices and 15 RAMHT descriptors.
  Native reads matched 49,152 source/guard bytes, 384 vertex bytes at each stop,
  and two independent 720-byte framebuffer captures. Kernel identity is not a
  symbol-matched full-kernel pin; not every mutable graphics descriptor bit or
  executed command is decoded.
- Initial and final PFIFO transactions each collected 55,660 rows / 218 pages.
  CPU-exclusive epochs 1/2 and 3/4 acknowledged four actual surface callbacks;
  their mutation clock was 40 at every boundary. Complete tuples and locked
  surface graphs matched within each transaction. No callback was removed,
  downloaded or cleared. Both actual context fences and owner checks passed.
- Four disabled units initially had exactly two references: one cache edge and
  one unit edge. Each original live generation was reused by the normal guest
  binder. Eight snapshots independently matched source and RGBA bytes (8,192
  bytes total), with identical keys, identities and GL names in each pair.
  The sealed terminal records eight events in four runs: one normal bind and
  one decrement per generation, no final frees, capture mask 15 and no errors.
- The final owner actor sealed on the original PFIFO worker after fresh CPU
  acknowledgments. Both graphs show 48 original shader work functions returned;
  that does not mean OS-thread exit or joining. The older base graph parser's
  `unknown` summary is superseded only for this specific work-return evidence by
  its independent actor extension, not by a general idle/retirement claim.
- Frontend reopened once, breakpoints were removed and physical-memory mode
  restored. After phase 33 the controller allowed the 18-second halt window,
  then orderly host stop/quit exited 0 without fallback. HalHaltRoutine entry
  itself was not traced. This is not a Windows shutdown/event/hive result.
- QCOW checks and EEPROM equality passed. All 83 frozen dependencies and 1,022
  private captures were rehashed. Private pixels and system binaries remain
  outside Git. `emu001/final-review.json`, `reuse-proof.json`, `audit.json` and
  `disk-delta.json` retain the separate scoped and strict outcomes.

## Implementation and validation

Exact 276 child build002 is
`E:/Codex-archive/xbox-windows-native/boundary278-build002/xemu-boundary278.exe`,
191,818,097 bytes, SHA256
`dcc08133f6627f387da3a584ba9eed2bdbac73e3cb3fcb19d1edb78c05e1ac93`.
Only renderer.c and physmem.c change. The new opt-in texture transaction uses
the byte-identical 277 pure admission core and mutation clock; legacy zero-count
capture and end-admission bodies reconstruct exactly. All 19 borrowed source
files were restored. There are 79 inherited warning instances, no new messages.

Actual extracted worker host tests cover 57 paths / 4,788 assertions. Collector
and canonical request tests cover 78 cases. Independent scalar transport rejects
308 mutations; full graph/native linkage rejects 68 + 4 mutations. CPU jobs,
GL and graph objects are explicit models in those host tests. Runtime supplies
the separate actual evidence above. Post-run analysis rejects 278 mutations of
the actual graphs and all 8,192 single-byte source/RGBA mutations; originals
remain unchanged. In `actual-controls.json`, the poorly named field
`strict_disk_gate_unchanged: false` records the still-false strict result; it does
not change the original audit gate. Original analysis output is preserved.

Build001 compiled but failed warning review because of a shadowed local name;
it was never launched. Build002 only renames that collector iterator. Initial
controller generation failed an exact CRLF anchor before runtime preparation;
`prior-controller001` retains its inputs. The next preflight rejected newline
normalization of the bounded atomic writer; `preflight001` preserves it. Exact
qualified writer bytes were restored before freezing the sole runtime. The
prelaunch `source-review.json` remains an immutable prelaunch record; its
`guest_launched: false` is not the final runtime state.

## Limits

This proves a bounded unchanged four-texture no-release control, not disposal,
backend retirement, Windows GPU ownership, acceleration, performance or hardware
qualification. Two unbound dirty surfaces retain unresolved native provenance;
they stay untouched outside this narrow texture operation. Scanout, UI holders,
native PTE/cache aliases and deferred release remain separate obligations.
The reserved-area disk failure remains open. Historical Windows Ftdisk49 is a
different fixture result. All prior failures and immutable 0.1.0/0088 rollbacks
remain intact; the physical audio004/video118/shared158/FATX0101 demo is unchanged.

#241 Xromwell dirty-pixel preservation succeeded; ownership still unproved

The concrete failure in CLOSED240 was a disabled-pusher refusal before its empty-queue check: state4/reason21/consume_stop5, GET=PUT=0/parser0/waits0, no commands or readback. New241 changes only the diagnostic consume function in pfifo.c. A live unexpired request with no waits and an empty completed parser skips pusher invocation; outstanding work, parser errors and waits retain existing bounded paths. No pusher enabling, register/wait clearing, fake completion, reference disposal or native-driver change.

Build001 reconstructed the exact238 source under the build lease, changed only pfifo.c and restored all borrowed source bytes. Toolchain is the unchanged pinned gcc image. Actual candidate executable `f1dc067d2edd1c1536bcd35d1a15be344709d6169c8e7a4f6cbb05395a9e1e7f`, 191399354 bytes; source manifest `bb456696386192ff481a6827a1d912cbac684661fb0ce45e048a572b24c7645d`. Compiled artifacts were created on E and exposed through the original workspace junction, with no disk backing chain move.

Fresh241/preserve001 paired with CLOSED239/control001 on the exact SAME verified immutable239 seed, native224/219 payload and211 captured-core device policy. No synthetic null binding or physical access. Both pin executing Xromwell11100 and FreeLoader200a20, with exact32-byte resident matches; FreeLoader magic2badb002/IF0. Each removes both breakpoints, verifies virtual mode0 and resumes. No debugger register/memory-write packets or native GPU commands.

At pinned Xromwell, each passive238 snapshot observed three dirty non-overlapping surfaces3072000 bytes, empty FIFO/parser, no waits/frontend batches/framebuffer/flush/sync work. FIFO and PG observations have distinct times, not simultaneous locks. In241 the actual preservation setter closes producer admission; its worker rechecks under FIFO/renderer/PG lock ownership, fences and downloads real GL pixels, compares every byte of all three expected buffers against VRAM and fences again. Immutable terminal3 reports surfaces3/dirty3/downloaded3/bytes3072000/error0/reason0/old_halt0/consume_stop0/steps0/words0/waits0. Request/gate vectors match; no FIFO commands consumed. This qualifies the bounded debugger preservation scope, not native ownership or hardware acceleration.

Primary qmp_pmemsave -> cpu_physical_memory_read -> flatview_read_continue invokes GPU read callbacks. No control/before RAM capture was performed. Only after worker success were these three exact post-preservation RAM buffers captured and privately retained:

- Physical RAM 0x3c64000, 614400 bytes: `61df6107d07deba62c052a53294ec0959a7dc0e203becee1e64923833eb51453`.
- Physical RAM 0x3e30000, 1228800 bytes: `2cebba2283e01a13623d4f65a38d4dda7b5bf12530a5a1df9e0fb57eacd300f0`.
- Physical RAM 0x3d04000, 1228800 bytes: `009ab2ef22949a0cfde035b824b5e6cc6f99eafff56e65d6718bd3cb3c5a7351`.

These callback-bearing RAM captures do not independently prove GPU pixels. The compiled worker's actual full byte comparisons supply that scope. Its expected buffers preserve existing padding bytes as well as the downloaded pixels. Existing finish restores previous producer admission on success. Bindings/callbacks/textures are retained by the reviewed implementation; complete post-preservation runtime reference inventory and retirement remain unproved. `references_retired=0/native_grant=0` are contract fields, not a new comprehensive runtime inventory. See RETIREMENT.md for the next separate gate.

Both runs completed65 CPU allocations/releases/exposure refusals,3194880 verified bytes and four joins. Eight retirement rounds/128 sequential MMIO reads correctly retain UNMODELED_BUSY/NO_OWNERSHIP. One normal EventLog6006 shutdown/dashboard return and orderly host stop/quit/exit0, no Kill fallback. Complete allocation, five structural hives, protected/staged hashes, startup/device policy/SetupAPI and event history passed:

| Case | Files | Directories | Directory clusters | Orphans |
| --- | ---: | ---: | ---: | ---: |
| outputs/gpu-preserve-entry239/control001 | 6725 | 320 | 321 | 0 |
| outputs/gpu-preserve-empty241/preserve001 | 6725 | 320 | 321 | 0 |

Existing directory captures show identical control/candidate paths and no baseline path missing. This is selected-content/full-allocation scope, not all-file or power-loss/repeated-boot durability. Application event deltas empty; sole Ftdisk49 type1 remains a strict failure in both. Overall strict/ordinary/physical/native GPU ownership remain FALSE; no gate waived and no physical baseline changed.

Actual compiled consume/wait functions tested at O0/O2 with real QEMU atomics and ASan/UBSan:18432 cases/110593 checks per build, zero sanitizer stderr/leaks. Cases cover empty parked queues, outstanding methods/errors/work, all wait masks, request states, deadline boundary and delegation under explicit clock/FIFO/pusher adapters. These models are not GPU scheduling/readback proof. Actual host experiment/parser62, guard72, single-connection12 and bounded closure25 checks PASS.661 frozen inputs unchanged. Runtime records are reviewed in review001.json; all239/240/241 root identities are closed, no root guest queued.

Preserve239 successful control, pre-VM capacity refusal and all host setup guards; preserve240 accepted safe refusal/normal cold recovery, without retry/recollection. Success reviewers authored for failed earlier cases were not executed on them; actual failure review scripts retain negative gates. Generic inherited helper print labels239/238 and protocol232 remain historical names: actual case paths, compiled sources/binary pins and runtime records identify241. Closed build/portable offloads were hash/readback verified and original paths preserved; physical0101/video0093,0088rollback,immutable0.1.0 and peer branches unchanged.

Next: new bounded SAME-intervention post-preservation reference inventory with producer admission still closed, then actual retirement/completion proof including asynchronous CPU callbacks and display/texture/shader references. Only then consider native ownership and accelerated fills/blits, followed by a separate hardware comparison with rollback. No root process remains running.

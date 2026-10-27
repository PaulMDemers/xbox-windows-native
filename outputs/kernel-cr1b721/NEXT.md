# 721 CLOSED: CR1b mismatch reproduced under Xbox kernel

One launch accepted at2026-10-27T16:24:19.552163+00:00. User observed orange and
automatic dashboard return. Seven fresh reports collected ONCE with identical
double-read; staged owner/XBE hashes and unrelated E-root/apps unchanged.
Source/build/model/link pins and preparation audit passed. Kernel PCI/CRTC/
sequencer/geometry match closed720. No startup hook, owned process or VM;
build/emulator leases released, hardware ticket retained. Console at UnleashX.

Durable kernel control: code7218; before85/prewrite85/request85; direct05,
reselected05, after-output05; exactly one attempted write. Index before/after1b;
CR11 before/after09; sequencer restored01 and selectors restored. EFLAGS
entry282 -> critical082 -> restored282. Recorded CR0=80010031 (PG remains set),
CR3=f000, CR4=610. No native handoff, paging/cache-register write or Windows.
Kernel pre-file context and critical context are separate snapshots; no claim
all control-register bits remain identical across kernel file APIs.

This physical result rules out native handoff or post-write index reselection
being necessary for this mismatch in721. It does not define bit7, prove every
85 write behaves this way, establish harmlessness, or explain full-mode708/709.
The same-value control FAILED; preparation/collection verification PASSED.
Kernel post-write data is file-backed here, unlike720's optical-only native
result. Dashboard return is firmware restart, not normal Windows shutdown.

Next: use the combined719/720/721 evidence to review CR1b readback semantics and
separately inspect full-mode failure predicates. Do not keep repeating the same
85 write, infer bit7 writability, mask mismatches, or promote a functional fix.
Any next probe must isolate a different question with fresh source namespace,
bounded host validation and watcher/reset availability. Preserve708/709 black
screens and717/718 failures. CR22 stays untouched; networking, bootintermittency,
1080i and acceleration remain tabled. Never rerun/recollect/parent721 runtime.

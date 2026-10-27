# 721 staged: kernel-context CR1b comparator; awaiting watcher

720 is CLOSED: one native saved85 write read05 immediately and after output
restore, error7208. Preparation audit passed; no retry or recollection.
The compiled720 instruction sequence contains no bit7 mask. Current primary
sources describe indexed FIFO/arbitration access but do not define NV2A bit7.

721 retains the Xbox kernel paging/cache context. It performs the established
blank/unlock sequence, one saved85 write, direct data read before reselecting1b,
then indexed read, output restore and final read. Entry flags are saved and
interrupts explicitly disabled only for this bounded no-API sequence; original
flags restored before file APIs. CR0/3/4 are recorded without modification.
No native handoff, Windows launch, CR22/encoder/clock/timing writes or CR1b retry.

916 tests of the actual compiled probe object passed; maximum modeled critical
path532 instructions. Control-register reads and device behavior are modeled,
not physical proof. Probe instruction bytes verified in PE and XBE outside
relocation operands. Source/layout/pins reviewed; fresh source manifest frozen.
No failed build or test in721. Legacy720 XBE title719 is cosmetic and retained;
new721 title is correct. No historical executable/source modified.

Staged owner/default.xbe at E:/Applications/XWNMode721, both read back exact.
XBE SHA256 197e7c1f76aff58dabdad5e2e068e07cc43596c999a075e65a2df2b573f857bd.
No launch requested. Watcher/reset availability question pending. No startup
hook, owned host process or VM; build/emulator leases released, hardware ticket
retained. Console at UnleashX during successful staging; C untouched.

Next after explicit watcher Ready: verify frozen sources/build/stage, create
ready001 exclusively, send ONE SITE request with20second reply bound. No repeat
accepted/uncertain launch. Observe top color for15seconds then expected dashboard
return. Green=same raw reads (ignored write possible); orange=mismatch;
red=refusal/restoration failure; magenta=post-write report save failure.
Collect once on dashboard return and audit raw control words plus preparation.
Expected successful lifecycle has7 reports: start,before_kernel_mode,
allocation_checked,kernel_context_captured,write_control_armed,
write_control_returned,restart_requested. Refusals produce fewer; preserve all.
Kernel reports can contain post-write evidence here;720 files were pre-handoff.
Dashboard return is not Windows normal shutdown. If hung, ask for manual recovery.

If both direct/indexed reads05, native handoff and index reselection are not
necessary for this mismatch in this control. If direct85/indexed05, access
sequence or timing remains a hypothesis. If both85, kernel mismatch was not
reproduced; ignored write still possible. No outcome alone defines bit7 or
qualifies full-mode/Windows1.6. Keep networking/bootintermittency/1080i tabled.

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

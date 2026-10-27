#726 CLOSED: 630-only transition retains CR1b85

One accepted launch18:13:46UTC2026-10-27. Green held result/photo001:
7260000d,4,5,726,2,30085,30085,20085,30085,30085,30085,0,22007.
6303->2->3; CR1b85 throughout six displayed stages and zero changes in32
late pairs. Two writes and final cleanup/selectors pass; no CRTC data writes.

User power-cycled. Collected nine preparation records once/double-read;
audit001 passed exact sources/binaries/photo, allocation/alias bounds and
unrelated E entries. PCI/CRTC/SEQ/geometry/allocation preparation matches725.
Last file phase handoff_armed; native values are optical only. Manual reset
is not normal Windows shutdown. Console UnleashX; no hook/process/VM.
Preserve integration001 harness expectation failure. Runtime726 CLOSED.

NEXT outputs/native-630726/NEXT.md: fresh minimal interaction control combining
6302, oneCR1b05 write and saved6303 restoration, with raw stage samples.
No new build/staging/launch. Do not reopen726/older runtimes or infer bit7
semantics, a full-mode fix or Windows qualification. Ordinary720p protected.

#726 STAGED: 630-only control, CR1b unwritten

New726 is staged and read back; no launch yet. Watch/reset readiness pending.
Probe725 bracketed CR1b05->85 after630 restoration, not causality. New control
writes only6302 then saved3, plus output blank/restore and selector traffic.
Six630/CR1b pairs and32 late reads distinguish blanking and transition behavior.
No CRTC data writes; full-width/byte restoration checks retained.

Fresh payload/host/build,12 CPU cases (all VMs closed),44 integration cases,
76 optical,20 nxdk page and372 nxdk ownership cases passed; exact linked bytes.
Preserve integration001 harness expectation failure; fresh integration002
corrected CR19 low-bit baseline expectation, binary unchanged.

Console UnleashX, no hook/owned process/VM. Only /E/Applications/XWNMode726
staged. NEXT outputs/native-630726/NEXT.md: readiness, one SITE, full13row
photo, power cycle, collect once. No full-mode/Windows/GPU claim. Closed725
and earlier runtimes remain closed. Ordinary720p protected.

# Engineering handoff: native Windows on Xbox

The platform/FATX essays below originated with the 0.1.0 physical milestone.
For current work read [CONTINUATION](CONTINUATION.md) first, then [STATUS](STATUS.md)
and the [maintained guide map](../../docs/current-status.md). Historical next-step
statements are not current launch instructions. These notes consolidate the main
lessons; the linked patches, reports and retained private artifacts are the
detailed lab record. Findings from Windows/ReactOS are not automatically bugs
in any Linux FATX implementation. No external project has been contacted.

- [FATX findings and Linux-oriented review checklist](FATX.md)
- [Current overall status and remaining gates](STATUS.md)
- [1080i investigation handoff and resume criteria](../../docs/1080i-investigation.md)
- [128GiB dump correction and complete emulator recovery](../atapi-dump-lba48/REPORT.md)
- [Boot, memory, display, network and validation notes](PLATFORM.md)
- [Video performance and modes plan](../video-next/PLAN.md)
- [Video diagnostic lifecycle and emulator/hardware divergence](VIDEO-DIAGNOSTIC-LIFECYCLE.md)
- [Live framebuffer mapping audit](../video-mapping-audit/README.md)
- [Direct-RAM video prototype and remaining lifecycle work](../video-direct-map/README.md)
- [Detached startup and strict shutdown audit](../video-startup-detached/README.md)
- [Experimental display replacement and failure cleanup](../video-surface-lifecycle/README.md)
- [Ordinary device-installer isolation experiments](../video-installer-isolation/README.md)
- [GPU installation and second-boot evidence](../shutdown-device-install/README.md)
- [Paired first-install idle/shutdown test](../shutdown-install-idle/README.md)
- [Observed popup owner in the idle installation test](../shutdown-idle-trace/README.md)
- [Emulator device research and non-stopping lifecycle recorder](../native-event-recorder/README.md)
- [Installer window observations](../shutdown-installer-windows/README.md)
- [Completion, restart questions and pending-install guard](../shutdown-installer-completion/README.md)
- [Explicit configuration of xemu's unused test function](../shutdown-null-placeholder/README.md)
- [Concurrent file/volume-flush investigation](../fatx-shutdown-concurrency/README.md)
- [Current physical PnP snapshot, read-only](../physical-pnp-followup/README.md)
- [Preserved baseline and recovery](../release-0.1.0/README.md)

Evidence vocabulary: **physical** means this console; **user-observed** means
the user's report; **emulator** means a named fixture; **compiled test** is a
targeted ABI/behavior test; **hypothesis** is not a root-cause finding. Do not
collapse those into a single PASS. Historical failures remain useful even when
the current candidate passes a later bounded workload.

#727 CLOSED: minimal interaction reproduces CR1b05->85

One accepted launch18:47:11UTC2026-10-27. User green and photo001 decode:
7270000d,4,5,727,10102,30085,20085,50005,30085,30085,30085,0,1022007.
Baseline6303/CR1b85; prewrite6302/CR1b85; direct05/indexed05 after oneCR1b05
write;85 after6303 restoration/output/late.32 late pairs, zero changes.
Two630 writes, oneunlock, oneCR1b write; final restoration/selectors pass.

Other prefix writes are not required for this observed transition in727.
Timing/context and bit7 semantics unresolved. No full-mode/Windows/GPU claim.
User power-cycled; nine records collected once/double-read. Audit001 passed
pins/photo/ownership/unrelated E entries; preparation exactly matches726.
Last persisted phase handoff_armed; native data optical only. Manual reset
is not normal Windows shutdown. No727 failures. Runtime727 CLOSED.

Console UnleashX; no hook/process/VM. NEXT outputs/native-interaction727/NEXT.md:
fresh matched kernel-context interaction comparator, unchanged register body
and raw samples; preserve kernel CPU context. No new build/staging/launch.
Never reopen727/prior runtimes. Protected720p and deferred work unchanged.

#727 STAGED: minimal CR1b/630 interaction; readiness pending

New727 reduces725 to6302, unlock1f57, oneCR1b05 write, saved6303 restoration,
plus output/selector handling. Captures direct data read then reselected read,
prewrite pair, after6303/output/late pairs and change count. Full baseline
restoration checks retained; no retry, repair, mask or other prefix data writes.

Fresh payload/host/nxdk build and exact linked bytes passed.12 CPU VMs closed;
50 integration,76 optical,20 nxdk page,372 nxdk and131379 host ownership cases
passed. No727 failed build/test. Source frozen, remote stage/readback verified
at /E/Applications/XWNMode727. NO launch yet; watcher/reset question pending.

Console UnleashX; no hook/process/VM. NEXT outputs/native-interaction727/NEXT.md:
Ready, one SITE, full13row photo, power cycle then one collection/audit.726 and
prior runtimes stay CLOSED. No full-mode/Windows/GPU qualification. Ordinary720p
protected; network/boot/1080i remain tabled.

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

# Native Xbox audio207 development status

Updated 2026-10-10 01:14 UTC. Hardware package is NOT ready. No physical access,
deployment or launch has occurred. Work remains on codex/xbox-native-audio at
base47fe46f; no commit/push yet. Canonical evidence and shared toolchains remain
read-only. Physical0101/video0093, original0088 rollback and immutable0.1.0 remain
preserved.

## Results

| Case | Result |
| --- | --- |
| control001 | Host dependency failure before Windows launch; integrity passed; closed. |
| control002 | Historical driver: scoped audio, normal restart and cold integrity passed. Strict whole-boot failure: Ftdisk49. |
| candidate001 | Build001 lifecycle changes: same scoped pass and Ftdisk49 strict failure. Closed. Build001 has a subsequently discovered all-ones halt-status defect; do not deploy. |
| candidate002 | Build002 fixed-codec changes: 360-second host bound, no helper logs, no test tones, no new events or normal shutdown. Cold integrity passed. Closed permanently. |
| candidate003 | Build003 render-connection correction: 360-second host bound, no helper logs, no test tones, no new events or normal shutdown. Cold integrity passed. Closed permanently. |
| diagnostic001 | Observer dependency failure before any monitor read; integrity passed; closed. |
| diagnostic002 | Read-only paused diagnostic: bugcheck1E/C0000005 in SysAudio+74B5 reading address4, build003 loaded. Cold integrity passed; closed. |
| candidate004 | Build004 single WaveCyclic PCM-DAC-speaker filter: full scoped audio/restart/cold integrity PASS. Strict whole-boot failure remains Ftdisk49. Closed. |
| install001 | Genuine SetupAPI replacement succeeded; exact xwnaci207 service/driver/oem3.inf persisted, normal restart and cold integrity PASS. Strict whole-boot failure remains Ftdisk49. Closed. |
| installed001 | First subsequent installed-driver boot returned normally; cold audit waiting for global build lease. No verdict yet. |

The successful cases independently produced eight complete stereo segments and
four reset-shortened segments, with left400Hz/right600Hz distinguished. Twelve
open/write/reset/unprepare/close cycles, exact96000-sample full-buffer completion,
one EventLog6006 and dashboard return were required. Cold checks cover all five
hives, protected bytes, typed service/device policy, event/setup history and full
FATX allocation. Known201 cancellation handles only its identified prompts, then
observes real installation idle. It installs nothing and proves no prompt-free
boot. Ftdisk49 is never waived by a scoped audio result.

Candidate003's post-timeout HMP screendump was unsupported by this xemu build;
no screenshot resulted. The cold audit was inadvertently invoked directly rather
than through its build-lease wrapper; audit004-host-deviation.json records this.
It read an already closed owned disk; this deviation cannot qualify the failed
run. All future audits use their leased wrapper.

## Source and tests

Owned source replayed ReactOS afc0127e8f937ab68503d715d948844973756aa1 plus historical
0016 tree5c302cf16ce08e7f2748be580e3d2e60d7d2441b. Microsoft/Intel/ReactOS notices are
retained. Primary references and licenses are recorded in RESEARCH.md.

- Build001: incremental0207 fixes descriptor lifetime/free length, bounds reset
  and position reads, and checks DMA addresses. Host actual-method tests passed
  31,081 cases; later review found its all-ones halt-status defect.
- Build002: cumulative0208 adds all-ones rejection, real resource validation,
  codec identification, Wolfson fixed-stereo handling, bounded inherited DMA
  quiescence and render-only topology. Both targets compile; actualNT5 imports
  resolve. ASan/UBSan tests passed31,082 lifecycle and297 resource/codec/link cases.
- Build003: cumulative0209 prevents registration of the absent microphone pin.
  Both targets compile and native imports resolve. The first host extractor
  failed; corrected extractor tests004 pass six actual-source connection cases.
  This host result does not establish the cause of the guest regression.

Cumulative0209 replaces0208/0207; never apply them together. Exact source/binary
hashes are in source-build001/002/003.json and build-review*.json. Frozen manifest
families preserve each experiment's inputs. Failed extractors and host attempts
are retained. The waveform oracle also rejects silence, mono, swapped channels
and missing-cycle input. No physical codec behavior is claimed from host mocks.

## Installation and hardware boundary

Installer001 and state001 helpers compile; their imports and dynamic export
chains resolve against the actualNT5 fixture DLLs (install-review001.json,
state-review001.json). Genuine installation passed in install001; subsequent installed-driver playback remains pending. The exact-ID INF and
installer target only10DE:01B1, revisionB1/subsystem00000000. The state helper will
require a started xwnaci207 device, one loaded xwnaci207.sys module and no legacy
ac97xnt5.sys before single-device playback. A precompile escaping error in the
state generator was rejected and preserved before corrected compilation.

Physical evidence distinguishes ACI00:06.0, IRQ6, D001/D201/FEC00000 from separate
APU00:05.0,10DE:01B0, IRQ5,FE800000. No APU or01B4 match, device disabling, null
binding or event suppression is introduced. Unsupported APU remains unresolved.
Initial scope is analog stereo PCM; actual Wolfson identity/audibility and digital
output are unproven. Coordinator alone owns physical deployment after reviewed
package, preflight, collection and rollback gates.

## Active ownership

At this checkpoint every guest is closed. Session75487 waits to audit installed001,
then will prepare installed002 only on a scoped PASS. Source archive44051 also
waits for the global build lease. No second playback boot or package is qualified
by a dashboard return alone. Preserve the completed runtime and pending audits.

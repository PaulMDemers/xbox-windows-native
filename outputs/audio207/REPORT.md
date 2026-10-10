# Native Xbox audio207 experimental package

The native ACI analog stereo package is ready for a coordinator-controlled first
physical trial. Genuine Windows SetupAPI installation and two subsequent playback
boots passed in xemu. Physical audio remains untested; this chat performed no
physical access, deployment or launch. Separate APU01B0 remains unsupported.
Ftdisk49 remains a strict whole-boot failure. Known unrelated wizard cancellation
was recorded, so these results do not establish an integrated prompt-free boot.

## Deliverables and exact identity

- audio207-aci-experimental.zip: driver, exact-ID INF, physical-mode install and
  playback helpers, trial/rollback instructions, licenses, manifests and evidence.
- audio207-corresponding-source.zip: complete historical0016 source tree,
  cumulative0210 patch, helper source and rebuild instructions.
- package001.json: package sizes and SHA256 hashes, copied with readback checks.

Driver version0.0.4.207, service xwnaci207, targets only the observed ACI10DE:01B1,
subsystem00000000, revisionB1. Driver SHA256:
`c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75`.
Apply only0210-waveonly-cumulative.patch to historical0016 tree
`5c302cf16ce08e7f2748be580e3d2e60d7d2441b`; do not stack earlier patches.
Source archive verification read all31,256 members and replayed the final patch,
matching all33 driver source files to the compiled source manifest.

## Qualification evidence

| Case | Scoped result |
| --- | --- |
| candidate004 | Twelve playback cycles, stereo capture, normal restart and cold integrity PASS. |
| install001 | Genuine SetupAPI installation, persisted xwnaci207 binding and exact driver/oem3.inf bytes, normal restart and cold integrity PASS. |
| installed001 | First subsequent boot: started device, one native module, no legacy module, one WinMM device, playback and cold integrity PASS. |
| installed002 | Second subsequent boot without reinstall: same device/module/playback/persistence checks PASS. |

Each playback case produced eight complete two-second stereo segments and four
reset-shortened segments, independently distinguishing left400Hz/right600Hz.
The checks require twelve successful open/write/reset/unprepare/close cycles,
exact96000-sample full-buffer completion, joined helpers, EventLog6006 and normal
dashboard return. Cold checks cover all five hives, protected file hashes, typed
device/service policy, preserved event/setup history and complete FATX allocation.
All four qualifying cases are closed. No debugger or paused observation was used
for ordinary qualification. No offline binding edit substitutes for installation.

Both AC97 build targets compiled and the native driver's imports resolved against
the actual NT5 fixture. The unchanged stream/resource paths passed31,082 lifecycle
and297 resource/codec/link cases under ASan/UBSan. The capture oracle rejected
silence, mono, swapped-channel and missing-cycle inputs. Physical-mode runners
passed actual NT5 import checks; their only source difference from tested emulator
runners is the known wizard mode. They have not been physically executed.

## Driver behavior and limits

Build004 exposes one WaveCyclic PCM-DAC-speaker graph with two pins and one actual
DAC node. It does not publish fictitious hardware mixer or capture controls.
DMA lifetime, free length, address bounds, position reads and reset waits are
checked; memory is retained if hardware halt cannot be confirmed. All-ones status
reads are rejected. The fixed Wolfson path validates real resources and codec IDs
and quiesces inherited PCM/S/PDIF engines before publishing a new ring.

Physical evidence identifies ACI00:06.0, IRQ6, D001/D201/FEC00000, distinct from
APU00:05.0,01B0, IRQ5,FE800000. xemu's STAC codec is not proof of the physical
Wolfson path. Analog48kHz16-bit stereo is the initial scope. Physical audibility,
S/PDIF/HDMI adapters, capture, hardware mixer controls and protected-content
playback remain unqualified. No APU/01B4 matching, device disabling, null binding,
event suppression or change to dump policy is introduced.

## Preserved failures and provenance

Control001 failed a host dependency before Windows launch; control002 and
candidate001 passed scoped playback with Ftdisk49 strict failures. Build001 later
proved to have an all-ones halt-status defect and must not be deployed.
Candidates002/003 reached their360-second bounds without helper completion,
test tones, new events or normal shutdown; both are closed failures with cold
integrity passes. Diagnostic001 failed its observer dependency before monitor
access. Diagnostic002's separate paused, read-only capture found a SysAudio null
dereference (bugcheck1E/C0000005, RVA74B5, address4) with build003 loaded. Build004's
single-filter graph then passed ordinary testing. Diagnostics are not ordinary
qualification, and symbol lookup failures were retained without substitutions.

Candidate003's cold audit was inadvertently called outside its build-lease
wrapper. audit004-host-deviation.json records that read-only audit of a closed
owned disk; it does not qualify the failed guest run. Later audits used the lease.
Failed extractors, generated-source draft, CRLF shell attempt, source-archive
lease timeout and all failed guest evidence remain preserved.

The source archive retains original licenses. The AC97 directory carries MIT
notices, but linked stdunk and support components retain their original licenses;
the complete binary is not represented as MIT-only. Historical sources, canonical
artifacts and shared toolchains were not intentionally edited. Physical0101/
video0093, original0088 rollback and immutable0.1.0 remain preserved.

## Handoff boundary

The coordinator must use PHYSICAL-TRIAL.md, including fresh hashed rollback,
one-launch installation, a separate subsequent playback boot, audible channel
checks, evidence collection and exact rollback. Do not deploy solely because a
package exists. This audio chat has no remaining guest session or physical task.
Repository work is confined to codex/xbox-native-audio; publication status is
recorded separately after remote verification. No main branch or tag was changed.

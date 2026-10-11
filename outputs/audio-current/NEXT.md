# Current Xbox audio qualification and next work

Updated October 10, 2026, after the closed dedicated channel trial.

The new helper passed host waveform/import checks, an ordinary emulator boot
with independently verified captured left/right/both PCM, and a physical boot
with six complete phases, normal restart and cold integrity checks. Physical
speaker mapping remains unverified: no listening observation for this dedicated
sequence was received before closure. The earlier user-observed Windows login
sound remains a separate positive analog audibility result.

All audio physical tickets are closed. The incoming baseline was restored and
verified with 1,202 file readbacks and zero final allocation errors/orphans.
No audio-owned emulator or physical session remains active.

## Current evidence and limits

- Emulator capture verified masks 1,2,3,1,2,3, roughly two-second tones and
  one-second encoded silence, followed by normal restart and cold integrity.
- Physical installation and subsequent runtime passed: xwnaci207 loaded, legacy
  module absent, six complete 144,000-frame phases and normal restart.
- Physical left/right mapping and measured quality remain unverified; no
  instrumented physical capture was made.
- Ftdisk49 remains a strict whole-boot failure. Known unrelated wizard cancellation
  means prompt-free startup is not established.
- APU, digital output, capture, mixer controls, protected content, suspend/resume,
  general repeated-boot storage safety and future video integration remain
  unsupported or unqualified by these results.

## Next step

Record the user's observation of the completed sequence: left-only 400 Hz,
right-only 600 Hz, both, repeated once. Preserve missing, swapped or distorted
output as reported; absence of a reply means unknown, not silence or success.
The helper is already implemented and tested. Do not repeat a closed case.

Any further physical replay requires a new serialized ticket, fresh actual
baseline capture, unique paths, normal restart, cold checks and verified rollback.
Do not reopen audio220, audio-listen001 or audio-channel001, or silently install
the candidate permanently. External capture is needed for measured signal quality.

## Fixed candidates and constraints

The driver remains xwnaci207 version 0.0.4.207, SHA256
c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75.
The new helper build002 SHA256 is
5ddf733be56e5bbffbcf1ad69f69a6fe31584d4635683a37dd18a0b5c912db77.
Driver source/package remains 7cdb191bd2ef72e24001370726f97a7383a7250b,
using cumulative0210 alone on its documented base.

Bind only exact ACI01B1/subsystem00000000/revisionB1. Preserve translated MMIO,
PortCls synchronization and DMA ownership. Initialization resets PCM and S/PDIF
engines; future digital support needs coordinated ownership. Preserve physical
FATX0101/video0093, original0088, immutable0.1.0 and all failed cases. No HAL,
GPU, APU or other device candidate was introduced.

The first helper link attempt failed for missing user32 and is retained.
Corrected build002 passed sanitizer waveform checks, six independent capture
cases and actual NT5 imports before guest or physical use. Older reports remain
historical evidence with original hashes. Root GPU-observer results do not
qualify audio.

## Records

- [Dedicated physical trial](../audio-channel-physical001/REPORT.md)
- [Physical review and observation state](../audio-channel-physical001/review001.json)
- [Closed physical ticket](../audio-channel-physical001/queue-close.json)
- [Emulator audit](../audio-channel001/emu001/audit.json)
- [Captured emulator sequence](../audio-channel001/emu001/capture.json)
- [Helper imports and source review](../audio-channel001/helper-review001.json)
- [Earlier login-sound observation](../audio-listen001/user-observation001.json)

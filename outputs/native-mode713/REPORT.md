#713: extended-register unlock/CR11 check with bounded restoration

712 visibly blanked and restored the retained720p picture.713 adds only the next
704 boundary: one CR1f57 unlock-key request, followed by an exact comparison of
CR11 with the admitted baseline. CR11 is never written. If it changes,713 records
0x7135 and uses the existing single restoration path. No common PRAMDAC/CRTC
setup, geometry, encoder, clock or interrupt programming is included.

The underlying712 baseline, sequencer1=1 admission, nominal one-second bounded
PM delay, single blank/restore pair and selector save/restore remain. Unlock is
requested only after successful blank readback. CR1f is not read as a write-key
oracle, and its captured read value is never written back as a supposed lock
restoration. The probe holds for manual power-cycle afterward.

The184-byte result fits the existing256-byte slot and adds unlock-attempted and
post-key CR11 words. Success0x713 means the key request/check and restoration
checks completed; it does NOT prove extended writes are enabled. Models include
an ignored key that software cannot detect without a subsequent changed-register
readback. A future setup test must establish write access explicitly.

The pinned Cromwell unlock helper and704 guard are documented in source-review001.
The fresh raw5120-byte payload is padded to9916;17 relocations include four
internal absolute32 entries. All executed sources and binaries are pinned.
Host tests and actual launch/observation/collection are separate evidence classes.

## Observation guide

After the five-second BLUE kernel picture, expect a brief black interval and
then the existing picture with GREEN top/second bars, held. ORANGE indicates a
returned rejection; other pre-call refusal colors remain. A black screen that
stays black does not identify the failure phase. Record the visible sequence and
final color before requesting manual reset. No Windows, startup hook or console C
access. No native mode/Windows1.6 qualification or functional driver fix claimed.

## Fresh host validation

131379 ownership cases and four ASan/UBSan construction placements passed.
Twelve diskless CPU fixtures passed and all closed.160 exact relocated instruction
models passed, including changedCR11, ignored unlock key, restore failure after
unlock rejection, prior baseline/timer failures and whole-framebuffer guards.
The trace oracle permits exactly one CR1f57 request, no CR11 write and one
restoration pair.23 compiled nxdk page cases and372 compiled ownership cases
passed. These do not qualify physical extended writes or native mode setup.

## Launch state

One SITE accepted at 2026-10-27T06:06:34.528479+00:00. User reported "Green, holding". This supports the distinct0x713 success
indication; the brief blank interval was not separately reported for713.
Manual reset and collection subsequently completed; see closeout below.
No repeated launch or startup hook; no host child remains.

## Closed physical result

User reported "Green, holding". After the requested manual power-cycle and Ready,
nine preparation files were collected once and double-read. audit001 passes
source/binary/report pins, allocation and independent alias checks, unrelated
entry checks; PCI/CRTC/SEQ/geometry/allocation match712. Last persisted phase is
handoff_armed, not a native result. The optical green separately supports0x713.
The blank interval was not independently reported for713. No extended-register
write-access proof, native mode initialization or Windows1.6 qualification.
Manual reset is not normal Windows shutdown. Runtime CLOSED; console dashboard,
no startup hook or host child. Never relaunch or recollect this attempt.

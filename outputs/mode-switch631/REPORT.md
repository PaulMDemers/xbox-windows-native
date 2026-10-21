#631 stock-API low/high/low emulator sequence completed

Build001 and emu001 are retained; emu001 is CLOSED and must never be relaunched,
recollected or used as a runtime parent. No physical-console contact, remote
write, Windows launch, startup hook or functional loader/driver patch occurred.
The original720p launcher and delivery packages remain unchanged.

The exact compiled XBE completed720x480 →1280x720 →720x480 at32bit60Hz in the
stock xemu fixture. Pitch was2880,5120,2880; H/V valid ends matched719/479,
1279/719,719/479. All stages used format3 and CRTC39=ff. The23 captured CRTC
values and three config/PLL words matched between the first and final low mode.
Independent full-frame comparisons covered1,382,400 /3,686,400 /1,382,400 bytes;
CRCs were7bd98b37 /dfa8cb56 /7bd98b37. Every framebuffer page translation and
physical scanout address was checked. Exact XBE/text/checkpoint/caller pins were
checked at the stops. This is emulated stock-API evidence, not a Windows mode
switch, a physical cable test, a complete native profile or acceleration proof.

The native build reused the pinned shared nxdk without modifying it. The sole
linker warning is the inherited reviewed export-section merge warning. Static
review of the actual compiled interrupt-disabled interval finds23+3 bounded
reads,24 selector writes, no calls, and saved selector/flags restoration. The
strict result decoder accepted one synthetic sequence and rejected300 malformed
sequences. Synthetic data is not presented as a physical result.

All owned emulator/controller processes exited0 without fallback kill. Hardware
breakpoints were removed and physical-memory mode was restored.42 private
captures remain under C:/xwn631/emu001/private. No firmware capture was added.
The optical D launch could not create its output log, so log_ok=0 in emulator;
GDB captured the mode evidence independently. Physical log creation, flush and
close have not been qualified by this optical run.

Strict whole-disk equality FAILED: one byte changed in reserved sector at byte
offset1536, with the same before/after sector hashes as historical307. The
complete overlay analysis finds all filesystem bytes inherited unchanged and
the first FATX header unchanged. No writer is inferred and the failed equality
result is not converted to PASS. QCOW structure, immutable source/input pins,
dependencies and EEPROM identity passed. This result does not qualify storage
persistence or permit promotion of the emulator disk. See emu001/audit.json and
emu001/disk-delta.json. Physical admission and protected-file audit still need
their own review; no hardware launch is admitted solely by this emulator result.

Original-console availability/watch question remains pending. Next: prepare the
separate physical transition with an owned writable output path and review its
admission/collection limits; then gather watched output on the supported console.
The measured lower-mode timing is useful but does not justify reusing the old
unchecked Conexant480p initialization path. See NEXT.md and the display roadmap.

Physical controller preparation now exists in physical.py. Mocked tests verify
20second reply timeout, one request even after reply loss, duplicate refusal,
and owned-directory limits. The first host import attempt failed because an
inherited helper changed Python's search path; its failure and frozen source
copies are retained. The corrected controller loads and pins its own oracle
before importing those helpers. No physical admission or connection occurred.

#739 source/access review, host-only

The safe-prefix rejection is established by733 and738. The requested next step
was to review access contracts, not repeat that experiment. This review made no
console connection, new executable, VM, driver edit or register access.

## Findings

Pinned original Cromwell source includes CR1b05, CR22ff and CR3311 writes, with
CR22/CR33 comments marking their purpose unknown. Authored704 adds full-byte
readback requirements. A write recipe alone does not establish those readback
semantics. Recorded working kernel722 modes (720p,720x480p,720p) containCR1b85
andCR22fe;731 independently measured CR22 FE/E7/5A/FF with GR04 plane selection.
This does not prove how CR22 responds to a write or identify708/709's failure.

Pinned upstream xemu dc10b4cea96e403d30c17ed53551fdaf023bc17f delegates PRMCIO to
vga_ioport_read/write. The CRTC read branch returns a byte-array entry; the write
branch stores one for indices1b/22. Its CR22 read has no GR04/latch selection.
This source path does not represent the physical plane-dependent reads. It also
contains no CR1b time-dependent read behavior. This is a static access-path gap,
not a new executed emulator result, complete scheduler audit or tested fix.
Do not use this behavior to qualify hardware predicates. No fork was modified.

Haiku a12d4cd1a5bd457078cb3a53ce265a364c5528b7 calls1b FIFO and33 LCD. Its inspected
FIFO setup is limited to older card paths, not an NV2A specification. The already
retained NVIDIA NV3 header calls bit7 UNDERFLOW_WARN. Neither establishes NV2A's
bit7 access contract. A guessed CR1b mask or CR22 FE substitution remains unjustified.

## Next bounded question

Prepare740 as a separate kernel-context preservation control: retain733's11
MMIO writes and first3 CRTC writes, omit its CR1b data write, and checkCR1b against
its admitted, actual saved full byte. Continue recording full cleanup comparisons
including CR22/CR33 without writing them. This asks whether the setup prefix can
preserve the already-working FIFO/latch/routing state. It does not weaken704's
predicate, execute geometry/encoder programming or qualify a mode switch.
No use of captured firmware values as programming writes is introduced.

Build fresh, test emitted instructions with mismatch and cleanup faults, audit
linked bytes and file lifecycle, then stage under a unique E path. The intended
kernel control writes its own reports and returns automatically. A native
counterpart or modeset is a separate decision after the measured result.

## Sources and limits

URLs, commit pins and hashes are in references001/002.json and audit001.json;
third-party files are retained privately at C:/xwn739. Initial broad searches
returned unrelated chips; they were excluded. The guessed Haiku nv_std.c URL
returned404 and was not used. No candidate/build/launch failure occurred.
Earlier730/732/734/735 reviews and all closed physical records remain unchanged.

Primary project sources:
- https://github.com/xemu-project/xemu/blob/dc10b4cea96e403d30c17ed53551fdaf023bc17f/hw/xbox/nv2a/prmcio.c
- https://github.com/xemu-project/xemu/blob/dc10b4cea96e403d30c17ed53551fdaf023bc17f/hw/display/vga.c
- https://github.com/haiku/haiku/blob/a12d4cd1a5bd457078cb3a53ce265a364c5528b7/headers/private/graphics/nvidia/nv_macros.h
- https://github.com/haiku/haiku/blob/a12d4cd1a5bd457078cb3a53ce265a364c5528b7/src/add-ons/accelerants/nvidia/engine/nv_crtc.c

Console last confirmed UnleashX after738. No hook/process/VM, no739 hardware kit.

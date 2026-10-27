# 700: Xcalibur sequence review and linked component tests

Host work only. No XBE, console staging, encoder write, maintained driver change,
or Windows launch. The physical timer699 result remains closed and unchanged.

## What now passes

The new encoder-only path combines the pinned 698 bus helper, 681 table/order,
and 685 bounded timer algorithm. It keeps the exact legacy reset and table byte
order, records the failed register and complete bus/timer trace, and stops at the
first error. It rejects incompatible requests before any I/O. It still requires
the old 55 MiB framebuffer/9 MiB reservation contract; this is NOT a ready
pattern-probe allocator or a complete video initializer.

`cpu001.json` records 608 executions of the newly linked 32-bit code:

- Full 148-transfer sequence with 144 delays and timer rollover.
- Bus error, dirty final status, and entry host-busy at each of 148 transfers.
- Backwards-clock rejection at each of 144 delays, plus a stalled-clock bound.
- Timeouts in the reset/read/write/table phases and both short reads.
- Nine invalid requests and interrupt-enabled refusal before any I/O.

An independent wire-byte oracle verifies every output port, width, value and
order. Guard bytes and IF remain unchanged. These are modeled ports, not
physical block-write, elapsed-time, GPU or display qualification.

`gpu001.json` executes a fresh build of the exact pinned legacy SetGPURegister
function across all 256 uniform initial CRTC byte values. All produce 720x480,
2880-byte pitch, format3 and totals779/524. It also demonstrates that index39
(interlace) is untouched, seven written CRTC bytes preserve inherited bits, and
the function does not establish clocks, framebuffer start or output conversion.
Uniform seeds are not an exhaustive test of all combinations of initial state.

## Full-sequence findings

The immutable source is recorded in `sources001.json`. The local recipe was
compared with the primary [Cromwell initialization source](https://github.com/XboxDev/cromwell/blob/master/drivers/video/BootVgaInitialization.c)
and [xemu NV2A register definitions](https://github.com/xemu-project/xemu/blob/master/hw/xbox/nv2a/nv2a_regs.h).
The downloaded register snapshot is private and hash-pinned; this is source
evidence, not proof of hardware register behavior.

1. The legacy framebuffer helper writes PCRTC+0x8000 and PMC+0x8000. The defined
   PCRTC START offset is +0x800, which earlier direct writes in the same source
   already use. Do not import the helper. This inconsistency does not establish
   the cause of any earlier physical boot failure.
2. NVVertIntrEnabled writes 1 to interrupt-enable and status offsets. Its name
   describes enabling, despite earlier conversational shorthand about disabling.
   Do not import its status acknowledgments into a probe that must preserve
   inherited pending state.
3. The legacy path changes PFB memory configuration, disables output, programs
   output conversion and geometry, writes the encoder, initializes VGA state,
   then enables output. The encoder calls ignore failure. The new encoder-only
   path fixes failure propagation in isolation; full output sequencing remains
   to be implemented and tested.
4. Correct geometry alone leaves inherited state. The common routine does not
   set the interlace byte, framebuffer start, clock selection or PLL. The PM
   timer observed in699 is a different clock; it does not qualify pixel timing.
5. The current native checkpoint draws into a kernel-owned 720p framebuffer.
   The encoder-only profile's fixed Windows reservation cannot be substituted
   for that allocation. A pattern-only initializer needs an explicit owned
   framebuffer contract before any GPU scanout change.

## Required complete transaction

| Stage | Required behavior | Current evidence |
| --- | --- | --- |
| Admission | Independent revision/encoder evidence, cable and mode flags, CPU/bus ownership, owned framebuffer bounds | Separate physical checkpoints and source policies; not combined |
| Clock contract | Establish source-backed clock selection and required initial state without copying firmware programming values | Open;699 only qualifies a bounded PM wait in its observed context |
| Blanking | Disable output before mutation; retain a reliable failure indication outside the changing scanout | Source order reviewed; native integration open |
| GPU setup | Explicit format, stride, dimensions, interlace, framebuffer and output conversion; exclude interrupt-status clearing and unexplained memory-controller writes | Common geometry function tested; complete setup open |
| Encoder | Two reads, two reset writes,144 ordered table writes and144 bounded waits; stop on failure |608 linked modeled cases; physical writes unqualified |
| Verification | Bound latch/settle checks; independently read geometry/format/stride/scanout before output enable | Not implemented for Xcalibur |
| Finish/failure | Enable only after checks; otherwise hold without retry, pending-bit repair or Windows handoff | Design requirement; no physical candidate yet |

## Process and limitations

Both freestanding builds and both Unicorn suites exited. No QEMU VM or host
process remains. Build/emulator leases were released. Private artifacts are in
C:/xwn700; the capacity guard included the WSL backing volume. No console access
occurred, so the last confirmed physical state remains dashboard after699.

The initial WSL text search failed because the argument crossed shell quoting
and rg was absent there. A bounded Python source scan then completed. A later
long shell command intended only to write the review receipt was rejected by
automatic policy before execution; this report was saved through the file-edit
tool instead. No hardware operation was involved or retried.

Read NEXT.md before advancing. Networking,1080i and intermittent boot work remain
tabled; the original Conexant720p installation and ordinary launcher are intact.

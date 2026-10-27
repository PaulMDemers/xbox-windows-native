# 702: checked480p geometry component and clock review

Host-only component, not a complete initializer or a maintained driver patch.
No console access, XBE, encoder programming, output enable or Windows launch.
The closed701 observation remains the last physical result.

## Clock selection

The pinned Envytools PRAMDAC definitions identify separate TV pixel-clock and
VPLL controls. Captured701 selection100a0400 has TV_PCLK bit17 set and VCLK_DB2
bit28 set; VPLL_PROG bit9 is clear. This supports investigating a TV-clock path,
not treating the raw VPLL coefficient as the active display clock. Several
nearby definitions have chipset restrictions; their names alone do not prove
all NV2A/Xcalibur routing, external frequency or480p suitability.

The pinned Cromwell Xcalibur HDTV helper ignores its dotClock argument and
copies the480p table. Its initialization path does not establish VPLL/selection.
The pinned xemu PRAMDAC implementation stores the VPLL coefficient but does not
handle selection offset50c and reports lock flags directly. Therefore emulator
success cannot qualify this physical clock selection or lock timing.

`sources001.json` pins exact revisions, URLs and private downloaded-file hashes.
Primary references:

- [Envytools PRAMDAC definitions](https://github.com/envytools/envytools/blob/master/rnndb/display/nv3_pramdac.xml)
- [Cromwell Xcalibur helper](https://github.com/XboxDev/cromwell/blob/master/drivers/video/xcalibur.c)
- [xemu PRAMDAC implementation](https://github.com/xemu-project/xemu/blob/master/hw/xbox/nv2a/pramdac.c)

No speculative PLL write is added. The observed701 values are equality checks
only, never a firmware-derived target table. A kernel-prepared480p/native capture
is the next useful physical comparison before combining the encoder component.

## Geometry substage

The new32-bit wrapper reuses exact700 SetGPURegister source. It admits only a
checked64MiB context with an existing1280x720x32 framebuffer,5120-byte stride,
page-aligned base, enough allocation and checked coverage, and caller-supplied
contiguity/native-alias/blanking confirmations. It checks the entire allocation
against RAM bounds, source/stub space below32MiB and the legacy38-40MiB range.
Those flags are caller obligations; this function does not prove allocation or
blanking itself and has no physical caller.

The new target is720x480x32,2880-byte pitch and1,382,400 visible bytes, within the
same owned allocation. No fixed55MiB framebuffer or9MiB reservation is borrowed
from the future Windows profile. Correct PCRTC_START600800 and explicit CR39ff
replace reliance on the old tail helper/inherited interlace value. All owned
timing fields are read back; stride includes CR25 bit5. The index selector and
IF remain unchanged. Unexpected context is refused before geometry mutation;
failed readback returns an error without an output-enable path.

Clock, PFB, output-conversion and interrupt registers remain untouched. This
component does not blank output, unlock protected CRTC registers, initialize
preserved CRTC fields, program the encoder, settle clocks or enable display.
A complete transaction must provide those reviewed stages and remain blank on
failure. In particular, successful modeled field readback is not a display.

## Evidence and preserved failures

`build001.json` pins the fresh GCC12 freestanding build and exact component
sources. `cpu.py` and `cpu001.json` preserve the first test failure: the harness
incorrectly expected dropping a redundant CR28=83 write to fail. The baseline
already has83, so final state correctly still passes. No C code changed.

`cpu002.py` corrects that expectation, includes another redundant framebuffer
start write, and seeds every timing register before fault injection. Its receipt
records randomized mixed CRTC states, individual readback faults, context drift,
rejected inputs, dropped effective writes and protected low CRTC behavior, plus
every page-address boundary in64MiB with ordinary/overflow-sized allocations.
These are linked instruction tests with modeled registers, not device emulation.

Early file lookups used nonexistent build001.py/policy.h/check_repository.py
names; inventory resolved the actual files. Two initial upstream documentation
URLs returned404 and were corrected through the repository tree. No runtime or
hardware action failed in those lookups. Closed700/701 runtimes were not reopened.

The second run was explicitly stopped after more than three minutes without a
final receipt; its per-call Unicorn timeout imposed excessive sweep overhead.
`cpu002-interruption.json` records the owned PID and closure. No result from
that incomplete run is promoted. Fresh `cpu003.py` uses an instruction bound
per short bounds call and a120-second outer limit. It passed354 geometry cases
and32,770 page/extent cases. All host processes are closed and leases released.

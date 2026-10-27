# 701: read-only native GPU context

One launch accepted at 2026-10-27T03:26:07.159806+00:00. Bar observation and
photo are pending; no reset or collection yet. The previous physical runtime699 is closed and must not be repeated.

The kernel prepares the same checked1280x720 framebuffer and records additional
PCRTC, pixel-clock/selection, PFB and CRTC39 observations before transfer. The
unchanged minimal native handoff then captures a separate set of GPU values into
RAM and ten optical rows. Kernel preparation is not read-only; the subsequent
native diagnostic does not program a mode, encoder, clock or memory controller.

Native admission checks PCI01:00.0, ID02a010de, memory decoding enabled, and
BAR0 exactlyFD000000 orFD000008. It restores CF8 before either refusing or reading
MMIO. The CRTC index is saved and restored around four byte reads; no CRTC data
register is written. Native writes otherwise target the owned diagnostic page
and framebuffer. No SMBus, timer, pending-status clearing or Windows entry.

The addresses follow the pinned700 legacy sources and primary
[NV2A register definitions](https://github.com/xemu-project/xemu/blob/master/hw/xbox/nv2a/nv2a_regs.h).
The values are observations, never a firmware table to copy into another mode.

## Display

Top green means the native handoff checks completed. The second bar is green
when the reads complete, red for GPU identity refusal, cyan for disabled memory
decoding, or yellow for an unexpected BAR. It deliberately holds for a photo and
manual power-cycle. A completed read does not establish that its values are
appropriate for480p.

Ten32-bit rows, most significant bit on the left, white1 and black0:

1. GPU PCI vendor/device ID.
2. PCI command/status.
3. GPU BAR0.
4. PCRTC configuration, offset600804.
5. VPLL coefficient, offset680508.
6. Raw clock selection, offset68050c.
7. Raw output control, offset680880.
8. Packed CRTC bytes:39 in bits31:24,28 in23:16,19 in15:8,13 in7:0.
9. Framebuffer start, offset600800.
10. PFB configuration, offset100200.

On PCI refusal the seven unread GPU rows remainFFFFFFFF. Result code lives in
RAM at page offset5cc and is conveyed by bar color, not a separate optical row.
Photograph before reset: persisted files contain only preparation context.

## Validation and state

- Exact linked template passed18 modeled PCI/MMIO/CRTC/pixel cases, including
  refusal before MMIO, selector restoration, relocation and differing raw values.
- Ten fresh diskless CPU fixtures passed: three mappings reach the expected PC
  PCI refusal, seven malformed/fault contexts do not paint the success header.
- Actual nxdk objects passed9 page-builder and19 allocation-policy cases.
- Code1019bytes fits below GDT4c0. Scratch ends5d0 before IDT600. Source/binary
  pins and unchanged transition/allocation components are in review001.json.

All host VMs/processes exited; build/emulator leases released. Hardware ticket
retained. Stage path is E:/Applications/XWNNative701, no startup hook or dashboard
C access. The ordinary launcher and original Conexant720p installation remain
unchanged. The frozen transport's inherited observation string mentions697;
the actual last completed physical run is699, followed by user-confirmed reset
and verified collection. Current readiness must be recorded separately.

## Optical observation

Both bars green. Ten optical rows:02a010de,02b00007,fd000000,00000003,
0003c20d,100a0400,21101100,ff835180,03c5c000,03070003. All320 bits
threshold/offset checked; middle256 independently cross-row checked. Native
CRTC13/19/28/39 =80/51/83/ff. Raw readings are NOT programming values.

Photo captured before requesting manual power-cycle. Await Ready/dashboard;
then record collection-ready001 and collect once. No reset confirmation or
collection yet. No repeat launch, startup hook or Windows. Host processes closed.
Read native-gpu701/NEXT.md. Original720p unchanged.

## Closed result

Photo decodes02a010de,02b00007,fd000000,00000003,0003c20d,100a0400,
21101100,ff835180,03c5c000,03070003. Both bars green. All320bits checked
with thresholds/offsets; middle256 cross-row verified. Six shared MMIO values
and CRTC13/19/28/39 match kernel snapshot exactly. Framebuffer matches owned
allocation/scanout. This does not qualify480p initialization or clock selection.

User power-cycled after photo capture and confirmed Ready. Eight preparation
records read twice; source/binary/private pins, staged XBE/owner and unrelated
entries verified. Runtime701 CLOSED: never relaunch/recollect. No hook, Windows
or native mode/encoder/clock programming. Kernel prepared720p. No host processes.
Console at dashboard; hardware ticket retained; automation paused.

Next: source-backed complete480p transaction design and linked failure-path tests,
using observed state only as a precondition, not copied firmware programming.
Resolve pixel-clock selection and owned framebuffer contract before encoder writes.
Read native-gpu701/NEXT.md. Original720p unchanged; networking/1080i/boot tabled.

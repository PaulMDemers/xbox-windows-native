# 694 launch accepted; physical observation and recovery pending

At2026-10-27T01:35:46.988119Z, one SITE request received200 EXEC command
succeeded. Fresh user watch/reset availability is recorded in ready001.json.
No repeat request. Actual top-bar/screen result is pending; acceptance does not
prove native execution. Do not collect while the console may be held. First
record the user observation, then request power-cycle if held and confirm the
dashboard before collection. No startup hook; no Windows intended. No owned host
process. Hardware ticket retained, automation paused. Follow694/NEXT.md.

# Native checkpoint694: prepared and staged, not launched

The next question is whether a checked, owned one-page transition can leave the
Xbox kernel's paged environment and write a visible checkpoint into the retained
framebuffer on the incoming 1.6. This is a diagnostic handoff, not an Xcalibur
initialization sequence, Windows boot, or ordinary launcher replacement.

## Memory and transition contract

The kernel-side allocation policy retains693's separate physical target, returned
virtual reservation base, and high allocation pointer. It verifies containment,
mapping, allocation extents and disjointness before copying and comparing the
entire4096-byte page through both execution addresses. The low virtual target
and physical target have the same numerical address but may have distinct backing
pages before paging removal. The rounded reservation base is only ownership data.

The page contains468 bytes of code, owned GDT/IDT, descriptor/context storage and
512 bytes of stack reserve. It explicitly disables maskable interrupts, flushes
writes, disables caches with CR0.CD=1/NW=0 and WBINVD, installs its own flat
selectors and stack, clears paging and CR3, then checks that context before writing
the green header and holding. CR4 is preserved. The native stub performs no port,
MSR, PCI, encoder or GPU-register writes. Kernel-entry accesses rely on the nxdk
flat ABI; the preflight requires the recorded8/16/16 selectors and non-PAE paging.

The persisted CPU sample is **before file-writing**. A later final sample is put
in RAM in both page copies, without another kernel API call before transfer.
Native context is also RAM-only. Neither final nor native context can be recovered
from the pre-transfer JSON or after a power-cycle.

## Host evidence

- `build002.json` passes with the pinned nxdk SDK. `extract001.json` verifies the
  complete template against the actual linked PE, not a separately assumed stub.
- `cpu-run003.json` passes ten fresh diskless CPU fixtures: three mapping layouts
  reach the native hold with the exact green header and preserved surrounding
  pixels; seven malformed/fault cases stop without changing the framebuffer.
  Descriptor, stack, paging, interrupt and neighboring-memory checks pass.
- `page-review001.json` passes nine actual nxdk-object page-builder cases and
  matches the fixture pages. `plan-review001.json` passes nineteen actual
  nxdk-object memory-policy cases. `review001.json` records code/layout review.
- All eleven invoked VMs are closed. These CPU models do not prove physical
  cache visibility, DMA/NMI behavior, NV2A operation or Xbox kernel services.

Preserved failures: `build001.json` lacks SafeSEH metadata (fixed with normal nxdk
metadata in build002); `cpu-build001.json` rejects an assembler label named flat
(renamed in fixture002); `cpu-run002.json` reaches the modeled native hold but its
HMP memory-dump command fails, so it supplies no framebuffer qualification. The
new cpu003 fixtures use structured QMP memory dumps. No closed fixture was rerun.

## Staging and expected physical observation

`stage001.json` completed with exact readback at the unique owned path
`E:\Applications\XWNNative694\default.xbe`. XBE SHA-256:
`1883abd943741cd71ecb78d328fc3c0d134ae56f1bdd2aa0d30d68fbb62cfcbd`.
No startup hook, Windows payload or dashboard C access. No launch has occurred.
Fresh watch/reset availability is pending.

The kernel prepares the reference panels with a BLUE top bar and waits about five
seconds. Successful native execution changes that header to GREEN and deliberately
holds. An allocation refusal shows RED and can return automatically; a later
CPU/final-context refusal can return with blue. A black/frozen picture by itself
does not locate failure. LED colors are not the checkpoint for this probe.

After the observation, a held console needs a power-cycle. Collect new records
only after the user confirms the dashboard. Retained scanout and a green header
would establish this limited native write, not native encoder setup or a working
Windows1.6 video driver. Original Conexant720p and all closed attempts are unchanged.

# 695 CLOSED: native PCI/status read photographed, recovered and collected

Read outputs/native-status695/analysis001.json, REPORT.md and NEXT.md.
Both bars photographed GREEN. Four optical rows independently decode01B410DE,
00B00001,0000C001,00000000 at three thresholds: expected PCI identity, IO enabled,
exact SMBus BAR and zero entry status after native transition. No bus transaction
or encoder initialization attempted; no Windows1.6 qualification or689 cause claim.

User manually power-cycled and confirmed dashboard. Eight reports each twice read
matched; independent local hashes verified. Final persisted phase handoff_armed;
allocation and both4096-byte copies passed. Staged files and unrelated E/apps
entries unchanged. Persisted CPU is pre-file-write; native values are optical,
not a recovered register dump. No normal Windows shutdown claimed. Incoming1.6
at HDMI dashboard; no hook or owned host process. Hardware ticket retained;
build/emulator leases released, automation paused. Ordinary launcher unchanged.

All695 physical/host runs CLOSED; no rerun/recollection. Ten CPU fixtures,16 IO
models,9 page-builder and19 policy cases passed. Preserve photo001 failed screen-
corner projection and successful independent component decoder photo002; private
photo not committed. Next: fresh single bounded native byte-read with visible
phase/outcome and strict entry/owned-status gates; prove layout and actual code
in new models before hardware. No next candidate built or staged. Preserve all
prior failures; networking679,1080i and historical boot intermittency tabled.

# Native status695: green observed, optical status zero; collection pending

One launch was accepted at 2026-10-27T01:47:14.635499Z. The user reported green
and supplied a photo. Both the handoff header and the separate result bar are
green. Independent optical decoding of the four rows gives:

| Native observation | Value | Interpretation |
| --- | --- | --- |
| PCI ID, bus 0 / device 1 / function 1 | `01B410DE` | Expected controller |
| PCI command/status | `00B00001` | I/O enable bit set |
| BAR at offset 14 | `0000C001` | Expected I/O address |
| SMBus entry status | `00000000` | No busy or terminal bits present |

This supports native controller visibility after the checked transition. It is
not a bus transaction, encoder identification/initialization, or Windows test.
The user has been asked to power-cycle and confirm the dashboard. File collection
is pending; no automatic return or normal Windows shutdown is claimed.

## Source and actual build

The kernel-side allocation, page builder and transition through the first green
header are unchanged from694 after the namespace change. The new native code
saves CF8, selects and reads three PCI dwords, then restores CF8 before any result
branch. It reads one16-bit status word at C000 only after matching identity,
I/O enable and BAR. Busy0800 takes precedence over terminal0036. No device
configuration, SMBus status, SMC, encoder or controller-command write occurs.
There is no poll or retry loop: a fixed number of I/O instructions is executed.
This bounds software work, not a hardware I/O-cycle timeout.

The linked page contains855 bytes of code before the GDT at400. Additional raw
values occupy5a0..5b8, disjoint from context, IDT and stack. The added routine uses
at most8 bytes of its512-byte owned stack in the IO models. The persisted CPU
sample remains pre-file-write; the final/native records remain RAM-only.

`build001.json` and `extract001.json` pin the source, toolchain and actual linked
template. Staging readback matched the unique owned path
`E:\Applications\XWNNative695\default.xbe`, SHA-256
`8b1e2aefeb5398d2da27b48c53adca5e945944059b39aefdb79783b2f154757f`.
No startup hook, Windows payload, dashboard C access or ordinary launcher change.

## Validation and observed display

- Ten fresh diskless CPU fixtures execute the actual linked template. Three
  mappings reach the native result display; the PC's different PCI identity
  produces the expected red refusal. Seven malformed/fault cases stop without
  changing the framebuffer. Whole-frame pixels and neighboring guards match.
  All ten VMs are closed. No Xbox PCI device was substituted into these fixtures.
- Sixteen explicit Unicorn I/O models execute the linked read/render bytes after
  the handoff. They cover clean/unknown status bits, busy, terminal combinations,
  absent/wrong device, disabled I/O, wrong BAR and relocation. Exact port sequences,
  CF8 restoration, bounded stack, complete pixels and guards pass. No forbidden
  device/status write is accepted by the harness. These are models, not hardware.
- Nine nxdk-object page-builder cases and nineteen allocation-policy cases pass.
  `review001.json` records the source/layout review and model limits.
- `photo002.json` decodes32 independent bit cells per row without supplying the
  expected values. Three different black/white thresholds produce the same four
  numbers. Bar samples and direct visual inspection agree on green. The photo
  stays private; only its hash, sampling geometry and derived evidence are public.

The initial screen-corner projection in `photo_decode.py` failed its sampling
robustness check before completing a row. Preserve `photo001.json`. The separate
component-based decoder removes that calibration assumption; it does not replay
the physical test. Optical decoding is not a captured native register dump.

The display retains the green handoff header at y8..79. The second wide bar at
y96..159 reports: green=clean entry status, red=wrong PCI ID, cyan=I/O disabled,
yellow=wrong BAR, orange=busy, magenta=terminal status pending. Four rows below
show ID, command/status, BAR and SMBus status, MSB first, white=1 and black=0.
An unread status would show FFFFFFFF. The red/green/blue/white quadrants behind
these cells are the inherited reference pattern, not additional failure codes.

## Remaining work

Record the user's manual recovery, collect695 files once, and verify pre-transfer
phases and staged-file custody before closing this runtime. Then prepare a new
bounded native byte-read probe with persistent phase/error/readback display.
Retain dirty/busy refusal gates and never acknowledge inherited unknown status.
Do not infer the old689 failure cause or general boot reliability from this pass.

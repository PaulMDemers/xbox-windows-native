# Graphics sample ladder

Start here before using games as diagnostics. Each rung adds one capability and
has an explicit result to check. The samples are original project code, target
32-bit Windows 2000, and run as ordinary applications. They do not install a
driver, change resolution, reboot, or initialize the Xbox GPU.

**Rungs 00–02 are implemented and have passed their six allowed cases on a modern
Windows PC, a Windows 2000 SP4 PC control, and the installed Xbox at 720p.**
The three pixel cases each matched 43,008 independently expected bytes on NT5
and Xbox. These runs checked memory operations with the preview disabled;
they do not qualify DirectDraw presentation, Direct3D or GPU acceleration.
**Rung 03 also passes default/HEL windowed presentation on Windows 2000 PC and
Xbox**, with exact source and GDI-observed primary pixels through cover/move/
uncover stages. Physical scanout, D3D and acceleration remain unqualified.
Rung04 is under validation; later rungs are planned, not stubbed-out passes.
The [game/D3D roadmap](graphics-roadmap.md) remains the larger goal.

## The ladder

| Rung | Sample | Check before advancing | Status |
|---|---|---|---|
| 00 | GDI reference copy | Two owned 32-bit DIBs; exact source and copied rectangle, unchanged destination border; GDI flush and cleanup | PC/NT5/Xbox pixel controls passed |
| 01 | DirectDraw inventory | Independently request default, HEL and HAL-only objects; record HRESULTs, hardware/HEL caps and current mode | All three inventories completed on PC/NT5/Xbox |
| 02 | DirectDraw system-memory copy | Explicit RGB32 offscreen surfaces; write/lock/unlock, rectangle blit, exact source and destination readbacks | Default and HEL controls passed on PC/NT5/Xbox |
| 03 | Windowed DirectDraw presentation | Primary surface plus window clipper; cover/uncover and move the window without damaging adjacent GDI content | NT5 PC/Xbox default and HEL pixel controls passed |
| 04 | Palettes, formats and sprites | 8-bit palette changes, supported 16/32-bit formats, color-key sprites, clipping and overlapping copies in both directions | NT5 indexed8/RGB565 pass; RGB32 failure retained |
| 05 | Surface lifecycle and memory budget | Focus changes, lost-surface handling where applicable, repeated create/release, failure recovery and bounded memory use | Planned |
| 06 | Legacy D3D discovery | Query the chosen D3D interface, enumerate actual devices/caps; distinguish software and hardware choices | Planned; begin with the installed legacy runtime, not a DLL upgrade |
| 07 | Clear and triangle | Offscreen render target, clear, pretransformed colored triangle, independent interior/background pixel checks | Planned |
| 08 | Textures, depth and blending | Known texture orientation/filtering, overlapping triangles with depth, transparent quads and alpha reference pixels | Planned |
| 09 | Transforms and scene stability | Rotating textured object, camera/projection, resize/activation handling and repeated resource teardown | Planned |
| 10 | Small game-like scenes | Scrolling isometric tiles and moving sprites, then a textured room; controls, audio and save/reload | Planned; precedes the actual game acceptance tests |

Do not require hardware acceleration for a software-compatible rung. An inventory
success is not a rendering test, and a system-memory blit is not a GPU benchmark.
Full-screen tests come after windowed correctness and use only actually supported
modes. 720p is the Xbox baseline; 1080i remains paused.

## Build

Source: [ladder.c](../src/samples/graphics-ladder/ladder.c),
[Windows runner](../src/samples/graphics-ladder/run.cmd).
After the [RosBE setup](building.md), run this on Linux/WSL from the repository:

```sh
python3 tools/build-graphics-samples.py \
    --rosbe "$HOME/xwn-rosbe-001/RosBE-2.2.1" \
    --output "$HOME/xwn-graphics-samples-001"
```

Choose a fresh output outside the repository/toolchain. The build checks the
20 GiB reserve on the output filesystem and WSL backing volume. On a shared
development host, use its build lease. Outputs include:

- `ladder.exe` and `run.cmd`: the runnable sample and exit-code recorder.
- `ladder.c`, `headers.d`, `ladder.map`, `pe.txt`, `build.log`, `build.json`:
  source, dependency information, import inspection, commands and hashes.

The executable uses PE subsystem 5.0 and no C runtime. Its static imports are
Kernel32, User32 and Gdi32; DirectDraw is loaded dynamically. The recorded build's
43 static imports match the exports of the pinned owned NT5 DLLs. That static
check is not a Windows 2000 execution result. Keep the build receipt with tests.
The builder neither downloads Windows DLLs nor deploys the executable.

## Run one sample at a time

Copy `ladder.exe` and `run.cmd` together into a dedicated directory on the test
Windows installation, for example `C:\xwnsamples`. This is the **Windows** drive
letter; do not confuse it with dashboard C. Use a disposable PC Windows 2000
control before a new Xbox trial. Do not replace any system DLL or driver.

From a Windows command prompt in that directory:

```bat
run.cmd 00 default r00a view
run.cmd 01 default r01d quiet
run.cmd 01 hel r01s quiet
run.cmd 01 hal r01h quiet
run.cmd 02 default r02d view
run.cmd 02 hel r02s view
```

These are separate commands: run one, inspect its result, then continue. Use new
prefixes for every attempt. `view` shows a small GDI preview for five seconds;
`quiet` leaves the window hidden. Rung 01 only records inventory. Closing a
preview early records cancellation, not success. No test moves the mouse or
changes the desktop mode. The optional preview is **GDI presentation of the
captured pixels**, separate from rung 03 DirectDraw presentation.

The three backend requests mean:

- `default`: DirectDraw's default device selection; do not infer hardware use.
- `hel`: request the software emulation layer explicitly.
- `hal`: request hardware-only capability discovery in rung 01 only. Reported
  capabilities are not proof that an operation executes on the GPU.

Rung 00 accepts only `default`. Rung 02 accepts only `default` or `hel`. An early
hardware-only system-memory creation attempt on the modern host exited with an
access violation before the first surface-creation return was recorded. Its
cause is unresolved; the current sample refuses that combination before loading
DirectDraw. It is not retried or relabeled as a pass. See [436's evidence](../outputs/graphics-ladder436/REPORT.md).

## Collect and check the result

For prefix `r02s`, keep:

```text
r02s.txt          API results, requested backend, OS API version, terminal status
r02s.exit         actual process exit code saved by run.cmd
r02s-source.bin   64 x 48 RGB pixels, four bytes each
r02s-dest.bin     96 x 80 RGB pixels, four bytes each
```

Rung 01 produces only `.txt` and `.exit`. Copy results back to the PC and run:

```sh
python3 tools/graphics_sample.py --prefix /path/to/results/r02s \
    --exit-file /path/to/results/r02s.exit
```

The independent Python oracle checks all 10,752 source/destination pixels in
rungs 00 and 02, including pixels outside the copied rectangle. It requires
the expected API steps, a complete terminal record and a successful external
exit code. Captures use little-endian B,G,R,zero bytes; the unused X byte is
normalized, not an alpha-channel test. Surface pitch is checked but padding
bytes outside the logical image are not captured or claimed as allocation guards.

The pattern is a deterministic RGB ramp. A 48×32 rectangle is copied from
source `(3,4)` to destination `(8,10)`; the surrounding destination stays dark
blue. Source and destination captures must match the independent calculation,
not a screenshot chosen after observing the result. Visual presentation and
screen movement require separate human observations.

| Exit | Meaning |
|---|---|
| 0 | Sample finished its stated inventory or pixel operations; still run the PC checker |
| 1 | API, layout or cleanup failure; inspect the last recorded operation |
| 2 | Invalid/unsupported arguments or output collision; choose valid arguments and a fresh prefix |
| 3 | Pixel mismatch |
| 4 | Report/capture I/O failure |
| 5 | Preview cancelled |
| Other / missing terminal record | Crash, termination or incomplete run; preserve it as failed/incomplete |

The samples use non-waiting DirectDraw blit/lock flags and report busy errors
without retrying. This does not bound every DLL/driver call. The host control
uses an external 30-second process watchdog; the Windows batch runner does not
provide a watchdog. Preserve a hung/crashed attempt and resolve it before
advancing. Never rerun over the same output files or use an incomplete capture.
[Microsoft lock semantics](https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdrawsurface7-lock).

The reported OS API version may be compatibility-adjusted on modern Windows.
Record the actual OS separately, plus the executable hash, console revision,
driver/runtime versions, mode and visual observations. The checker deliberately
does not infer NT5, physical-console or acceleration qualification from pixels.

## Presentation results and next implementation

### Rung 03: primary presentation

The separate [present.c](../src/samples/graphics-ladder/present.c) sample uses
the current desktop mode. Build it with the same command above, adding
`--sample present` and choosing another fresh output. Copy `present.exe` and
`present.cmd` together, then run one case at a time:

```bat
present.cmd default r03d
present.cmd hel r03s
```

Keep the desktop visible and leave the sample unobstructed. Its own magenta
sibling window deliberately covers part of the target. Four stages check the
visible target, cover, move while covered, and uncover. The blit rectangle extends
beyond the target; the HWND clipper must protect the blue surrounding GDI region
and the cover. GDI paint handlers never draw the expected DirectDraw pattern.

Each case produces `.txt`, `.exit`, `-source.bin`, `-before.bin`, and `-after.bin`.
The binaries contain four consecutive top-down BGR0 frames: source 128×112,
before/after 256×192. They total 1,802,240 bytes per successful case. Keep these
private desktop readbacks with the test, then verify on the host:

```sh
python3 tools/graphics_present.py /path/to/results/r03d --backend default
python3 tools/graphics_present.py /path/to/results/r03s --backend hel
```

The verifier checks the full clip region, exact independent pixels, position,
occlusion and API/cleanup results. It accepts the tested RGB565/RGB555/RGB32
layouts only. The sample does not switch modes or lock the primary surface.
These are GDI-observed desktop pixels, not a physical scanout or GPU completion
measurement. The owned NT5 test controller bounds each case at 90 seconds;
`present.cmd` itself does not provide a watchdog. Rung03 pixel/API failures use
exit 1; preserve partial captures as well as successes.

Host verifier tests: `python3 tests/test_graphics_present.py`.

The [440 NT5 presentation control](../outputs/presentation440/REPORT.md) and
[442 Xbox control](../outputs/presentation442/REPORT.md) each verify 3,604,480
bytes across both backends and reject 468 actual-evidence mutations. The same
sample runs on PC RGB565 and Xbox RGB32. Both restarted normally; the physical
test hook is removed and 720p/code are unchanged. The first PC test's missing
sibling-order precondition and a physical preflight manifest error are retained
as separate failed attempts. The Xbox again logged Ftdisk49 and two shutdown
rundll32 popups; a presentation pass does not qualify the whole system.

The [437 NT5 control](../outputs/graphics-nt5437/REPORT.md) and
[438 Xbox control](../outputs/graphics-xbox438/REPORT.md) establish the initial
baseline. Both used the same sample executable; the Xbox driver and 720p mode
were unchanged. Each retained 402 rejected evidence mutations. The physical
run restarted normally but retains Ftdisk49 and two shutdown-time rundll32
initialization popups, so it is not a clean overall system qualification.

Rung 04 now has an implementation; its qualification is recorded below.
Keep default/HEL distinctions, independent destination/neighbor checks and
every refusal. Use a fresh PC control before a distinct Xbox run.
Advance to D3D rendering only with actual capability and surface evidence; do not
change `DrvEnableDirectDraw` to advertise support without implementing its contract.

Host verifier tests: `python3 tests/test_graphics_sample.py`. The initial control
and negative tests are [recorded separately](../outputs/graphics-ladder436/REPORT.md)
from Windows 2000/Xbox testing. The original games remain untested.

### Rung 04: palettes, formats and sprites

Build [sprites.c](../src/samples/graphics-ladder/sprites.c) from Linux/WSL:

```sh
python3 tools/build-graphics-samples.py --sample sprites \
    --rosbe "$HOME/xwn-rosbe-001/RosBE-2.2.1" \
    --output "$HOME/xwn-sprites-001"
```

Choose a fresh output directory. Copy `sprites.exe` and
[sprites.cmd](../src/samples/graphics-ladder/sprites.cmd) together. Run each
combination separately, using a new prefix:

```bat
sprites.cmd default index8 r04di
sprites.cmd hel index8 r04si
sprites.cmd default rgb565 r04d6
sprites.cmd hel rgb565 r04s6
sprites.cmd default rgb32 r04d3
sprites.cmd hel rgb32 r04s3
```

This sample leaves its window hidden and uses only owned system-memory surfaces.
It does not create a primary surface or change the desktop palette or mode.
Four stages check a transparent color-key sprite through two disjoint clip
rectangles, a palette-only update, then overlapping self-copies in both directions.
The palette stage must change converted colors while preserving the raw indices.
RGB cases retain their pixels at that stage. The source remains unchanged.

Each prefix produces `.txt`, `.exit`, `-source.bin`, `-dest.bin`, `-rgb.bin` and
`-palette.bin`. Each pixel file contains four consecutive frames. Source is
16x12, destination and converted RGB are 32x24. Every raw pixel or index is
stored as a little-endian 32-bit integer, including the 8/16-bit formats.
The RGB capture is BGR0 after conversion through the surface's GDI DC.
The indexed palette file contains four sets of 256 actual four-byte
`PALETTEENTRY` records (red, green, blue, flags); flags must be zero. RGB cases
have an empty palette file. Successful captures total 31,744 bytes per indexed
case or 27,648 bytes per RGB case. Surface padding is not an allocation guard.

Verify one case after copying its files back to the host:

```sh
python3 tools/graphics_sprites.py /path/to/results/r04di --backend default --format index8
python3 tests/test_graphics_sprites.py
```

The checker calculates expected indices, packed pixels, palette entries and
converted colors independently. It requires a complete report and external
exit receipt. Exit 1 includes API, pixel, layout and cleanup failure; 2 is invalid
arguments/output collision and 4 is I/O failure. Preserve partial outputs.
The owned test controller bounds each process at 90 seconds; the batch file
alone supplies no watchdog. Busy/unsupported operations fail without retry.
This does not qualify presentation, scanout, GPU use or a game.

The [first NT5 control](../outputs/sprites443/REPORT.md) failed: indexed/RGB565
pixels matched, but the sample detached its clipper twice during cleanup. RGB32
also omitted 16 red pixels during the clipped keyed copy. The
[corrected control](../outputs/sprites444/REPORT.md) passes indexed8 and
RGB565 through both backends: 118,784 exact bytes and 1,718 rejected evidence
mutations. With colors varying in both axes, RGB32 still omits 12 pure-red pixels
at varied positions; non-red clip-edge pixels copy correctly. A low 16-bit-only
key comparison explains those bytes, but the actual faulty component is not
identified. This occurs on the PC control's 16-bit desktop.

A [separate mode diagnostic](../outputs/sprites445/REPORT.md) requested a 32-bit
desktop without changing the sample. The pinned Cirrus driver rejected that
mode before any sample case ran. It also retains a host preflight-ordering
limitation and is not deployment qualification. No rung04 Xbox test has run.
Expected pixels and all failed results remain intact; the installed Xbox driver
and 720p baseline are unchanged.

### RGB32 color-key diagnostic

[keyprobe.c](../src/samples/graphics-ladder/keyprobe.c) narrows the RGB32 failure
without modifying the rung04 sample or changing the desktop mode:

```sh
python3 tools/build-graphics-samples.py --sample keyprobe \
    --rosbe "$HOME/xwn-rosbe-001/RosBE-2.2.1" \
    --output "$HOME/xwn-keyprobe-001"
```

Copy `keyprobe.exe` and `keyprobe.cmd` together. From Windows, run each backend
with a fresh output prefix:

```bat
keyprobe.cmd default keyd
keyprobe.cmd hel keys
```

The hidden-window test enumerates supported display modes, then performs twelve
independent RGB32 copies: three keys, with/without keying, with/without clipping.
It tests exact keys and near-colors that differ only in their red byte. Each
operation resets its destination. Pixel mismatches are recorded while later
operations continue; API or layout failures stop the diagnostic.

Keep `.txt`, `.exit`, `-source.bin` and `-dest.bin` for each prefix. The two binary
files contain twelve consecutive frames of little-endian DWORD pixels: source
16x12 (9,216 bytes total), destination32x24 (36,864 bytes total). Copy them back
to the host and check:

```sh
python3 tools/graphics_keyprobe.py /path/to/results/keyd --backend default
python3 tools/graphics_keyprobe.py /path/to/results/keys --backend hel
python3 tests/test_graphics_keyprobe.py
```

Exit0 means all expected pixels matched; exit1 records pixel failures, exit2
includes API/layout or argument failures, and exit4 is an I/O failure. Complete
diagnostic records do not make failing pixels acceptable. The batch wrapper has
no watchdog; the owned validation controller separately bounds each process at
90 seconds. There is no display-mode change, primary surface, scanout test or
hardware acceleration claim.

The [NT5 diagnostic](../outputs/key-semantics446/REPORT.md) completed both backends:
all plain copies matched, while keyed copies failed with three distinct keys,
both with and without clipping. Full keys were retained by `GetColorKey`.
All destination captures match a low16-bit comparison model; the responsible
implementation is not traced. The current16-bit desktop enumerates24-bit modes
but no32-bit mode. These failures are recorded, not accepted as compatible.

The [24-bit comparison](../outputs/key-depth447/REPORT.md) runs that exact binary
on an enumerated 640×480×24 desktop. Both backends pass every operation and all
92,160 captured bytes, then the controller verifies restoration to 16-bit mode.
The difference supports desktop-depth dependence in this PC configuration; the
responsible implementation remains untraced. The same probe is prepared for the
Xbox's existing 720p/32-bit desktop, but has not yet been deployed there. This
focused result does not qualify the remaining full rung04 RGB32 sprite stages.

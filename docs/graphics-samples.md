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
uncover stages. Those checks do not qualify physical scanout or GPU acceleration.
Rung 04 also passes all six cases on NT5 PC and Xbox, and rung 05 passes its
bounded lifecycle controls. Rung 06 now passes complete default/HEL inventories
on NT5 PC and Xbox, reporting the RGB software renderer. Rung 07 now creates
that software device and passes offscreen clear/triangle pixel checks on both.
Rung 08a passes owned point-sampled texture controls on NT5 PC and Xbox. Rung 08b
depth controls pass on NT5 PC and Xbox. Two earlier Xbox launches returned without
Windows receipts; the later 483 run completed both depth cases and a normal restart.
Rung 08c now has matched selected-input alpha arithmetic on NT5 PC and Xbox,
with the endpoint precision limitation retained. Rung 08d now passes windowed
D3D presentation on NT5 PC and Xbox. Rung 09a adds six XYZ transform controls
on both. The combined offscreen scene also passes on PC and Xbox; combined
windowed presentation now passes on both. Resource and performance measurement
remain the next steps before game trials.
The [game/D3D roadmap](graphics-roadmap.md) remains the larger goal.

## Start here

These programs run **inside an already working Windows installation**. They do
not create that installation or boot the Xbox. If you have only component
builds, follow [build to boot](build-to-boot.md) first. Source and matching
checkers are indexed in the [sample directory](../src/samples/graphics-ladder/README.md).

| Where | What to do |
|---|---|
| Linux/WSL on your PC | Build one sample with `tools/build-graphics-samples.py`; retain its build receipt |
| Windows 2000 PC control, then the prepared Xbox Windows installation | Copy the sample's `.exe` and `.cmd` together into an owned test directory; run one case with a fresh result prefix |
| Your PC | Copy back every file with that prefix and run the matching Python checker |
| Test report | Keep the checker output, original files, executable hash, hardware/runtime identity and screen observations together |

For a first test, start with rungs 00–02 below. For a first D3D rendering test
after those controls, use [the triangle sample](#offscreen-software-triangle).
The offscreen samples intentionally show no picture: a brief console window or
a return to the desktop is not the result. Their saved pixels and reports are.
Use [windowed D3D presentation](#windowed-d3d-presentation) when testing visible
rendering; follow the section's cover/move/uncover instructions.

An exit code of zero still requires the host checker. If Windows never starts
or the result files are missing, record an incomplete launch rather than a
graphics pass or pixel failure. Keep the ordinary boot configuration and use
720p on Xbox. The batch wrappers neither install a startup task nor restart
Windows automatically, and they do not impose a process watchdog.

## The ladder

| Rung | Sample | Check before advancing | Status |
|---|---|---|---|
| 00 | GDI reference copy | Two owned 32-bit DIBs; exact source and copied rectangle, unchanged destination border; GDI flush and cleanup | PC/NT5/Xbox pixel controls passed |
| 01 | DirectDraw inventory | Independently request default, HEL and HAL-only objects; record HRESULTs, hardware/HEL caps and current mode | All three inventories completed on PC/NT5/Xbox |
| 02 | DirectDraw system-memory copy | Explicit RGB32 offscreen surfaces; write/lock/unlock, rectangle blit, exact source and destination readbacks | Default and HEL controls passed on PC/NT5/Xbox |
| 03 | Windowed DirectDraw presentation | Primary surface plus window clipper; cover/uncover and move the window without damaging adjacent GDI content | NT5 PC/Xbox default and HEL pixel controls passed |
| 04 | Palettes, formats and sprites | 8-bit palette changes, supported 16/32-bit formats, color-key sprites, clipping and overlapping copies in both directions | All six cases pass on NT5 PC at24-bit and Xbox at32-bit |
| 05 | Surface lifecycle and memory budget | Focus changes, lost-surface handling where applicable, repeated create/release, failure recovery and bounded memory use | Bounded churn/focus/memory controls pass on NT5 PC and Xbox; actual loss/restore remains unqualified |
| 06 | Legacy D3D discovery | Query the chosen D3D interface, enumerate actual devices/caps; distinguish software and hardware choices | NT5 PC/Xbox default/HEL inventory passes: RGB software device found; no draw qualification |
| 07 | Clear and triangle | Offscreen render target, clear, pretransformed colored triangle, independent interior/background pixel checks | RGB software path passes on NT5 PC and Xbox; no presentation/GPU claim |
| 08a | Point-sampled texture | Enumerated texture format, exact upload/readback, known orientation and interior sampling | Default/HEL RGB software controls pass on NT5 PC and Xbox |
| 08b | Depth buffer | Enumerated depth surface, both draw orders, depth-disabled and clear-zero controls | Default/HEL RGB software controls pass on NT5 PC and Xbox |
| 08c | Alpha blending | Transparent, partial, opaque and blending-disabled triangle controls | Selected-input arithmetic matches on NT5 PC/Xbox default and HEL; exact ideal endpoints remain failed |
| 08d | Windowed D3D presentation | Render-target readback, exact clipped presentation through cover/move/uncover, unchanged source after blit | NT5 PC/Xbox default/HEL pixel controls pass; no GPU or performance claim |
| 09a | XYZ transforms | Identity, world/view translation, rotation then view translation, perspective divide and displaced viewport; independent pixel checks | NT5 PC/Xbox default and HEL controls pass |
| 09b | Combined offscreen scene | XYZ textures, transforms and depth/order controls | PC/Xbox default and HEL pass |
| 09c | Combined windowed scene | Native-format CPU staging, clipped primary blit, cover/move/uncover and exact GDI readback | PC RGB565 and Xbox RGB32 default/HEL pass |
| 09d | Repeated scene process costs | Three separate scene processes per backend, exact pixel checks, CPU time and working-set/commit counters | PC and Xbox six-run process-cost controls pass; not FPS or in-process leak proof |
| 09e | Sustained scene in one process | 2,560 repeated frames, calibrated API phase timings, five checked endpoints and memory before/after release | PC/Xbox scoped controls pass; PC QPC durations unqualified; Xbox clock cross-checks pass |
| 09f | Perspective texture interpolation | Fixed projected outlines with constant, increasing, decreasing and scaled W; swapped UV control | NT5 PC default/HEL pass; Xbox attempt returned without test receipts |
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
as separate failed attempts. The Xbox again logged Ftdisk 49 and two shutdown
rundll32 popups; a presentation pass does not qualify the whole system.

The [437 NT5 control](../outputs/graphics-nt5437/REPORT.md) and
[438 Xbox control](../outputs/graphics-xbox438/REPORT.md) establish the initial
baseline. Both used the same sample executable; the Xbox driver and 720p mode
were unchanged. Each retained 402 rejected evidence mutations. The physical
run restarted normally but retains Ftdisk 49 and two shutdown-time rundll32
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
limitation and is not deployment qualification. Expected pixels and all failed
results remain intact.

The [full 24-bit PC control](../outputs/sprites-depth450/REPORT.md) now passes all
six cases, including RGB32 and both overlapping-copy directions: 174,080 exact
bytes and 2,520 rejected evidence mutations. The sample executable is unchanged.
Its controller verifies the supported 24-bit mode and restoration to the original
16-bit desktop before normal shutdown. The checker accepts 24-bit desktop metadata
without changing surface formats or expected pixels.

The [matched Xbox attempt](../outputs/sprites-xbox451/REPORT.md) returned to the
dashboard without a result directory. Its test hook is disabled; the launcher,
normal startup and 720p settings are unchanged. Full physical rung04 qualification
remains pending a boot-path comparison and a fresh instrumented attempt.

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
responsible implementation remains untraced.

The [watched Xbox retry](../outputs/key-retry449/REPORT.md) also passes both
backends on the existing 1280×720×32 desktop: all 24 stages and 92,160 captured
bytes match. The same executable, runtime and driver were used, followed by a
normal restart and removal of the test hook. The earlier
[no-receipt launch](../outputs/key-xbox448/REPORT.md) is retained separately.
This focused key diagnostic does not qualify the remaining full rung04 RGB32
sprite/overlap stages. Ftdisk 49 and a shutdown-time rundll32 popup remain separate
system issues; no hardware acceleration or D3D result is implied.

The [complete Xbox sprite retry](../outputs/sprites-retry452/REPORT.md) now
qualifies all six rung04 cases, including the remaining palette and overlap
stages:174,080 exact bytes,2,520 rejected actual-result mutations, normal restart
and test-hook removal. It leaves the720p mode, runtime and driver unchanged.
This is system-memory correctness, not GPU acceleration or game qualification.

## Bounded surface lifecycle sample

[lifecycle.c](../src/samples/graphics-ladder/lifecycle.c) checks repeated
system-memory allocation, exact copies and release without changing display mode.
The bounded control passes on [NT5 PC](../outputs/lifecycle453/REPORT.md) and
[Xbox](../outputs/lifecycle-xbox454/REPORT.md):12,582,912 exact bytes per platform
and4,718 rejected actual-result mutations. Actual lost-surface restoration remains
unqualified.
Build it in a fresh directory:

```sh
python3 tools/build-graphics-samples.py \
    --sample lifecycle \
    --rosbe "$HOME/xwn-rosbe-001/RosBE-2.2.1" \
    --output "$HOME/xwn-lifecycle-001"
```

Copy `lifecycle.exe` and `lifecycle.cmd` together. Run each backend with its own
fresh output prefix, using a disposable Windows 2000 PC control before an Xbox:

```bat
lifecycle.cmd default life-d
lifecycle.cmd hel life-s
```

Two small owned windows appear briefly. With two surfaces still allocated, the
sample checks activation/focus between its own windows using thread-local handles
and focus messages. It does not dismiss other applications' dialogs or assert
that its window is globally in the foreground. Eight warm-up iterations precede
64 measured iterations. Each holds two 128×96 RGB32 system-memory surfaces, checks
a copied rectangle and untouched borders, then releases both objects.

Keep `.txt`, `.exit` and `-pixels.bin` for each prefix. Each complete pixel file is
6,291,456 bytes, containing 64 consecutive source/destination pairs of tightly
packed little-endian DWORDs. The file includes every source and destination pixel;
no guest checksum substitutes for the independent host oracle. Validate with:

```sh
python3 tools/graphics_lifecycle.py /path/to/results/life-d --backend default
python3 tools/graphics_lifecycle.py /path/to/results/life-s --backend hel
python3 tests/test_graphics_lifecycle.py
```

The sample records PSAPI process commitment and working-set measurements. Its
predeclared commitment-growth limit is 1 MiB above the post-warm-up baseline.
Passing this finite bound does not prove the absence of leaks or account for all
kernel/driver memory. It also requires refusal of a malformed surface descriptor,
followed by successful valid allocations; this does not test out-of-memory recovery.

In this unchanged-mode test, `IsLost` must return `DD_OK`. It does not force a loss
or call `Restore`, so actual lost-surface recovery remains a separate unqualified
scenario. Exit0 means the scoped checks completed, exit1 means a check/API failed,
exit2 is an argument/initial-output failure, and exit4 is a recorded I/O failure.
The batch wrapper has no watchdog; the private validation controller separately
bounds each process at 90 seconds. No primary-surface, GPU or D3D support follows
from this sample.

## Direct3D 7 device inventory

The [NT5 PC control](../outputs/d3d-discovery455/REPORT.md) and
[physical Xbox control](../outputs/d3d-marker473/REPORT.md) enumerate Microsoft's
RGB software device through both default and explicit HEL paths. Neither reports
hardware rasterization or hardware transform/lighting. Both Xbox cases exited 0
at the unchanged 1280×720/32-bit desktop, followed by a normal restart. Their full
236-byte capability descriptors match the PC control's recorded hashes, and 566
mutations of the actual Xbox records were rejected.

This qualifies device discovery only: no D3D rendering device was created and no
triangle was drawn. Five registry hives passed integrity checks; Ftdisk 49 remains
an overall-system qualification failure. Earlier no-receipt attempts, including
[458](../outputs/d3d-direct458/REPORT.md), remain failed/incomplete attempts and
are not retrospectively qualified. The temporary test startup entry was removed;
the normal boot installation and 720p configuration remain unchanged.

[discovery.c](../src/samples/graphics-ladder/discovery.c) queries the installed
Direct3D 7 interface and enumerates device capabilities. It does not create a
rendering device, draw, replace runtime DLLs or install a driver. Build it with:

```sh
python3 tools/build-graphics-samples.py \
    --sample discovery \
    --rosbe "$HOME/xwn-rosbe-001/RosBE-2.2.1" \
    --output "$HOME/xwn-discovery-001"
```

Copy `discovery.exe` and `discovery.cmd` together. Run default and explicit
software-emulation DirectDraw paths separately:

```bat
discovery.cmd default d3d-default
discovery.cmd hel d3d-hel
```

Keep each prefix's `.txt`, `.exit` and `-caps.bin`, then validate on the host:

```sh
python3 tools/graphics_discovery.py /path/to/results/d3d-default --backend default
python3 tools/graphics_discovery.py /path/to/results/d3d-hel --backend hel
python3 tests/test_graphics_discovery.py
```

The report retains the QueryInterface and enumeration results, device GUIDs,
names, descriptions and selected capability fields. The binary contains the full
236-byte little-endian descriptor for every returned device, up to 16 records.
The checker joins both representations, including the complete descriptor bytes,
and rejects duplicates, overflow, truncation, missing completion and failed cleanup.
Names/descriptions are hex-encoded in the raw report to preserve their bytes.

A complete inventory can truthfully report an unavailable interface or zero
returned devices. That outcome is distinct from a failed/incomplete probe.
Hardware capability flags are the runtime's declarations; they do not prove a
working accelerated driver or successful draw. The next rendering test must use
an actually enumerated device and independently check its output. The sample's
exit0 means a complete scoped inventory, not Direct3D rendering support.

## Offscreen software triangle

The [fresh NT5 PC control](../outputs/d3d-triangle474/REPORT.md) and
[physical Xbox control](../outputs/d3d-triangle476/REPORT.md) pass both default
and explicit HEL cases using the same executable. Each creates the enumerated
RGB software device and verifies 4,096 clear pixels, 561 triangle-interior pixels
and 2,199 exterior pixels. The remaining boundary band contains only the two
prescribed colors. Both processes exit 0 and the controller restarts Windows
normally. Each actual 11-module snapshot matches independently checked files.

The preceding [475 boot attempt](../outputs/d3d-triangle475/REPORT.md) returned
before producing Windows/sample evidence and remains failed. The successful
Xbox run still records Ftdisk 49 and a shutdown-time `rundll32.exe` initialization
popup; overall system qualification therefore remains false. Rendering success
does not resolve those issues or the intermittent boot path.

[triangle.c](../src/samples/graphics-ladder/triangle.c) is rung 07. It selects the
enumerated RGB software device and creates a private 64×64, 32-bit system-memory
render target. It clears the target, draws a solid pretransformed triangle, and
captures the pixels after each operation. It does not change the desktop mode or
display the triangle on screen. This is a rendering diagnostic, not a benchmark.

```sh
python3 tools/build-graphics-samples.py \
    --sample triangle \
    --rosbe "$HOME/xwn-rosbe-001/RosBE-2.2.1" \
    --output "$HOME/xwn-triangle-001"
```

Copy `triangle.exe` and `triangle.cmd` together to Windows 2000. Run each request
with a fresh result prefix:

```bat
triangle.cmd default triangle-default
triangle.cmd hel triangle-hel
```

Copy each prefix's `.txt`, `.exit`, `-clear.bin` and `-draw.bin` back to the host:

```sh
python3 tools/graphics_triangle.py /path/to/results/triangle-default --backend default
python3 tools/graphics_triangle.py /path/to/results/triangle-hel --backend hel
python3 tests/test_graphics_triangle.py
```

The checker requires a successful external process exit, complete API/cleanup
records, the actual enumerated device identity, and the prescribed vertices.
It checks every clear RGB pixel, a triangle interior well away from raster edges,
and a predefined exterior region. The remaining band may contain either of the
two prescribed colors; exact edge coverage is not qualified. The unused X byte
is retained in the capture but is not a color channel and is not compared.

`CAPTURED` and exit 0 mean the sample finished its API calls and wrote its files.
Only the host checker establishes the scoped pixel result. Exit 1 means an API
or check failed, exit 2 means arguments or initial output creation failed, and
exit 4 means recorded I/O failed. The batch wrapper has no watchdog; private
validation runs additionally impose a 90-second process deadline. Keep failed
results and choose a new prefix instead of overwriting them.

The sample also records a bounded snapshot of loaded modules while its D3D
device exists. This helps identify the installed software runtime; it does not
trace helpers that were loaded and unloaded before that snapshot. A successful
triangle does not establish textures, depth, blending, presentation, hardware
acceleration, game compatibility or useful game performance.

## Offscreen point-sampled texture

The [fresh PC control](../outputs/d3d-texture479/REPORT.md) and
[Xbox comparison](../outputs/d3d-texture478/REPORT.md) pass both default and HEL
cases with the same executable. Each enumerates ten formats and uses an actual
RGB32 format. The source bytes remain unchanged after drawing, all 576 interior
texture checkpoints match, and Windows restarts normally. This qualifies this
small software-rendering case; game compatibility and performance remain open.
The Xbox still logs Ftdisk 49 and shutdown-time rundll32 initialization popups,
so overall system qualification remains false despite the scoped rendering pass.

[texture.c](../src/samples/graphics-ladder/texture.c) is rung 08a. It enumerates
the software device's texture formats, uploads an owned 8×8 color pattern, and
draws a textured quad into a private 64×64 target. Each texel has a distinct RGB
value; this checks orientation as well as checkerboard parity. It uses nearest
filtering with no mipmaps, depth testing or blending. Nothing is shown on screen
and the desktop resolution is unchanged.

```sh
python3 tools/build-graphics-samples.py \
    --sample texture \
    --rosbe "$HOME/xwn-rosbe-001/RosBE-2.2.1" \
    --output "$HOME/xwn-texture-001"
```

Copy `texture.exe` and `texture.cmd` together to Windows 2000, then run:

```bat
texture.cmd default texture-default
texture.cmd hel texture-hel
```

Copy all six files per prefix back to the host: `.txt`, `.exit`, `-clear.bin`,
`-draw.bin`, `-source-before.bin` and `-source-after.bin`. Validate them with:

```sh
python3 tools/graphics_texture.py /path/to/results/texture-default --backend default
python3 tools/graphics_texture.py /path/to/results/texture-hel --backend hel
python3 tests/test_graphics_texture.py
```

The checker requires the actual format enumeration and selected format, complete
API/cleanup records, exact upload bytes unchanged after drawing, all clear RGB
pixels, 576 predefined samples inside the 64 texel cells, and exterior background.
Other pixels must contain source-palette or background colors; exact texel and
raster edge selection is outside this test. The unused render-target X byte is
not a color channel. An unsupported texture format is a refusal, not permission
to change the expected image. `CAPTURED` still requires host validation.

Use fresh prefixes and retain failures. The public batch file has no watchdog;
private qualification adds a 90-second process deadline and normal shutdown
checks. This rung does not qualify presentation, depth, blending, acceleration,
game compatibility or performance. Runtime results are recorded separately in
the [479 PC control report](../outputs/d3d-texture479/REPORT.md). The earlier
[477 malformed-floppy attempt](../outputs/d3d-texture477/REPORT.md) remains
failed and produced no texture result.

## Offscreen depth buffer

The [PC480 control](../outputs/d3d-depth480/REPORT.md) and
[Xbox483 comparison](../outputs/handoff-witness483/REPORT.md) pass both default
and HEL with an enumerated 16-bit depth format and all five fixed image controls. The
[Xbox481](../outputs/d3d-depth481/REPORT.md) and
[Xbox482](../outputs/d3d-depth482/REPORT.md) attempts returned to the dashboard
without Windows receipts and remain failed. The fresh483 diagnostic records a
later boot-handoff boundary and completes the depth workload and normal restart.
It does not establish a fix for intermittent boot failures.

[depth.c](../src/samples/graphics-ladder/depth.c) is rung 08b. It enumerates depth
formats for the actual RGB software device and attaches a private 64x64 depth
surface to an offscreen color target. It draws the same overlapping triangles
in both orders, then repeats with depth disabled and with depth cleared to zero.
This isolates depth comparison, depth writes, clear and draw-order behavior.
Nothing is shown on screen; the desktop mode is unchanged.

```sh
python3 tools/build-graphics-samples.py \
    --sample depth \
    --rosbe "$HOME/xwn-rosbe-001/RosBE-2.2.1" \
    --output "$HOME/xwn-depth-001"
```

Copy `depth.exe` and `depth.cmd` together into Windows 2000. Use fresh prefixes:

```bat
depth.cmd default depth-default
depth.cmd hel depth-hel
```

Retrieve all seven files per prefix: `.txt`, `.exit`, `-clear.bin`,
`-far-near.bin`, `-near-far.bin`, `-no-z.bin` and `-zero-z.bin`.

```sh
python3 tools/graphics_depth.py /path/to/results/depth-default --backend default
python3 tools/graphics_depth.py /path/to/results/depth-hel --backend hel
python3 tests/test_graphics_depth.py
```

A successful process only means its captures are ready. The checker requires
complete API/format/attachment/cleanup records, prescribed vertices and states,
and independently expected RGB pixels. Both depth-enabled draw orders must show
the nearer triangle; the depth-disabled control must show the last triangle;
clearing depth to zero must reject both triangles with LESS comparison. Exact
raster edges and the unused X byte remain outside the claim. This is not a
stencil, depth-precision, presentation, acceleration or game-performance test.
The public batch wrapper has no watchdog; private validation uses a 90-second
process deadline. Keep failures and use a fresh output prefix for each run.
Runtime evidence is recorded in the [480 PC report](../outputs/d3d-depth480/REPORT.md)
and [483 Xbox report](../outputs/handoff-witness483/REPORT.md). The Xbox retains
Ftdisk 49 and two shutdown-time application popups; the scoped depth pass does not
qualify the whole system or game compatibility.

## Offscreen alpha blending

**The public `blend` sample retains the original exact-endpoint checks, which
failed on the tested PC runtime.** The separate selected-input characterization
below is a different diagnostic; its pass does not make `graphics_blend.py`
accept those failed endpoint captures. Keep the original expected pixels.

[blend.c](../src/samples/graphics-ladder/blend.c) is rung 08c. It draws a
magenta triangle over a green background using the enumerated D3D7 RGB software
device. Six captures distinguish a clear target, alpha 0, alpha 85, alpha 170,
alpha 255, and alpha 85 with blending disabled. Each stage records the actual
blend enable and source/destination factors. The private 64x64 RGB32 surface
never changes the desktop mode or displays a preview.

Build with the documented RosBE toolchain and a fresh directory:

```sh
python3 tools/build-graphics-samples.py \
    --sample blend \
    --rosbe "$ROSBE" \
    --output "$HOME/xwn-blend-001"
```

Copy `blend.exe` and `blend.cmd` together into Windows 2000, then use two fresh
output prefixes:

```bat
blend.cmd default blend-default
blend.cmd hel blend-hel
```

Copy each prefix's `.txt`, `.exit` and all six `.bin` captures back to the host:

```sh
python3 tools/graphics_blend.py /path/to/results/blend-default --backend default
python3 tools/graphics_blend.py /path/to/results/blend-hel --backend hel
python3 tests/test_graphics_blend.py
```

The independent oracle requires exact background, transparent, opaque and
blending-disabled colors. Partial blends allow at most one level per 8-bit RGB
channel around the calculated color; this tolerance was fixed before execution.
It checks every pixel, with a separate boundary region that permits either
background or foreground because exact raster-edge coverage is not qualified.
The unused X byte is ignored. Missing captures, failed API calls, unexpected
states and incomplete cleanup fail validation even if the process exits zero.

The public batch wrapper has no watchdog. Private validation uses a 90-second
process deadline. Destination alpha, texture alpha, depth/blend interaction,
presentation, acceleration and game performance require separate tests.

The [first PC alpha control](../outputs/d3d-blend484/REPORT.md) completed both
processes and restarted normally, but failed its exact transparent/opaque endpoint
checks: a drawn channel expected to remain 255 became 254. Partial blends fit the
predeclared one-level allowance, and blending disabled is exact. This is a failed
pixel qualification despite successful API calls.

The [separate mixed-color control](../outputs/blend-precision486/REPORT.md) matches
`(source * alpha + destination * (255 - alpha)) // 256` per channel for its selected
inputs on both software paths. Explicit ZERO/ONE and ONE/ZERO factor controls
remain exact. That distinguishes the observed result from the ideal divide-by-255
calculation and from separately truncating each product. It characterizes these
inputs without changing the original failed oracle or proving the runtime's
internal implementation. The [Xbox comparison](../outputs/blend-precision487/REPORT.md)
returned before any Windows test receipts; it provides no alpha qualification.
The later [490 Xbox comparison](../outputs/context-adapter490/PHYSICAL.md)
completed both default and HEL cases with all sixteen captures matching the
predeclared486 oracle, followed by a recorded normal restart. This characterizes
those selected inputs on the RGB software renderer; it does not remove the
endpoint limitation or qualify windowed D3D presentation, GPU use or games.

The later [526 repeat attempt](../outputs/blend-context526/REPORT.md) produced no
Windows results. It adds no alpha measurement and leaves boot repeatability
unresolved; it does not replace the earlier 490 result. A new matched run is
still needed to assess repeatability after the launch problem is diagnosed.

## Windowed D3D presentation

[d3dpresent.c](../src/samples/graphics-ladder/d3dpresent.c) adds a D3D-rendered
triangle to the owned window/clipper arrangement from rung03. Build it with
`--sample d3dpresent` and a fresh output directory. Copy `d3dpresent.exe` and
`d3dpresent.cmd` together, then run one case at a time on a visible desktop:

```bat
d3dpresent.cmd default r08dd
d3dpresent.cmd hel r08ds
```

The sample keeps the current mode and requests the enumerated RGB software
device. Supported targets use the primary's RGB565, RGB555 or RGB32 format.
It renders four differently colored triangles while the owned window is
visible, covered, moved while covered, and uncovered. Blue GDI surroundings and
a magenta cover check that the clipper protects neighboring content.

Keep `.txt`, `.exit`, `-source.bin`, `-post.bin`, `-before.bin` and `-after.bin`
for each prefix. Source captures are taken before and after presentation; the
second capture must be unchanged. Check the files on the host:

```sh
python3 tools/graphics_d3dpresent.py /path/to/results/r08dd --backend default
python3 tools/graphics_d3dpresent.py /path/to/results/r08ds --backend hel
```

Each complete case has 2,031,616 captured bytes. The independent checker requires
the declared triangle interior/background colors, allows only those two colors
in a narrow predefined edge band, and then checks exact source-to-screen mapping
and GDI guards. It also checks clip rectangles, vertices, render states, module
inventory and cleanup. Exact triangle-edge placement, padding bytes, physical
scanout and GPU acceleration are outside this test. Do not adjust expected
pixels to match a failed capture.

The batch file records the process exit; it has no watchdog. The owned test
controller bounds each process at 90 seconds. Synthetic decoder tests are in
`tests/test_graphics_d3dpresent.py`; they do not establish guest correctness.
See the [491 design](../outputs/d3d-present491/DESIGN.md) for the control scope.

The [491 PC control](../outputs/d3d-present491/REPORT.md) passes both cases at
640×480 RGB565, including 4,063,232 captured bytes and normal restart. An independent
cold reader agrees on the results. The matched
[492 Xbox comparison](../outputs/d3d-present492/REPORT.md) passes both cases at
1280×720 RGB32 with the same oracle, exact source preservation and normal
restart. Ftdisk 49 and three shutdown-time rundll32 popup events remain recorded;
this scoped graphics pass does not qualify overall system stability.


## World, view and projection transforms

[transform.c](../src/samples/graphics-ladder/transform.c) starts rung 09 with
six unlit, offscreen D3D7 controls. It submits XYZ vertices, sets and reads back
world/view/projection matrices, and captures the actual rendered pixels. It
does not draw a visible scene or change the display mode.

Build with the same command above, adding `--sample transform` and choosing a
fresh output directory. Copy `transform.exe` and `transform.cmd` together into
an owned Windows test directory. Run one case at a time:

```bat
transform.cmd default r09ad
transform.cmd hel r09as
```

Keep each prefix's `.txt`, `.exit`, `-clear.bin` and `-draw.bin` together. Each
pixel stream is 98,304 bytes: six 64×64 RGB32 images. Check on the host:

```sh
python3 tools/graphics_transform.py /path/to/results/r09ad --backend default
python3 tools/graphics_transform.py /path/to/results/r09as --backend hel
```

The checker calculates screen coordinates using rational arithmetic and a fixed
two-pixel edge band. Interior and exterior colors must match; the edge band may
contain only the two declared colors. It also requires exact matrix, viewport
and vertex records. The unused high color byte and pitch padding are excluded.
Matrix readback alone is insufficient. The sample covers identity, separate
world/view translation, rotation followed by view translation, perspective
and an offset viewport. Raster clipping, lighting, combined scenes, frame rate,
GPU use and games remain separate work.

The initial host oracle tests found two insufficiently distinct geometries;
those failures are preserved. Stronger geometries passed before the first PC
launch. See the [493 design](../outputs/d3d-transform493/DESIGN.md). Runtime
qualification is recorded separately in that attempt's report.

The [493 PC control](../outputs/d3d-transform493/REPORT.md) passes both default
and HEL paths, with normal restart and independent cold-file agreement. The
[494 matched Xbox comparison](../outputs/d3d-transform494/REPORT.md) also passes.
This establishes six software transform cases, not general D3D compatibility or hardware acceleration.


## Combined XYZ, textures and depth

[scene.c](../src/samples/graphics-ladder/scene.c) combines two owned 8x8 textures,
actual XYZ vertices, world/view/projection transforms and an attached depth
buffer. Its five 64x64 offscreen cases compare both draw orders, depth disabled,
a zero-cleared depth buffer, and a small world-space movement. The final case's
record label is `camera_move`; it changes the **world** matrix, not the view matrix.

Build using the same RosBE command, selecting `--sample scene` and a fresh
output directory. Copy `scene.exe` and `scene.cmd` together into Windows. Run:

```bat
scene.cmd default r09bd
scene.cmd hel r09bs
```

Each result prefix produces a text report, exit receipt, two framebuffer streams
(`-clear.bin`, `-draw.bin`) and two texture-source streams (`-source-before.bin`,
`-source-after.bin`). Copy all six files per prefix back to the host and check:

```sh
python3 tools/graphics_scene.py /path/to/results/r09bd --backend default
python3 tools/graphics_scene.py /path/to/results/r09bs --backend hel
```

The checker requires exact matrices, state readbacks, format selection, owned
surface capabilities, draw order and completed cleanup as well as pixel data.
The [495 oracle](../outputs/scene-oracle495/REPORT.md) was fixed before this
sample was compiled: safe RGB regions must match exactly; predefined two-pixel
geometry/texture boundaries allow only the specified colors. Texture source
bytes must remain exact. Framebuffer X bytes and pitch padding are excluded.
Both triangles have constant W individually, so this does not yet test
perspective-correct interpolation across varying W, visible presentation,
lighting, acceleration or game performance. See the [496 result](../outputs/d3d-scene496/REPORT.md)
for the actual tested build and qualification status.

The [496 PC control](../outputs/d3d-scene496/REPORT.md) and fresh
[545 Xbox comparison](../outputs/d3d-scene545/REPORT.md) pass all five offscreen
cases through both default and HEL software paths, followed by normal restart.
The Xbox comparison uses the exact 496 executable and unchanged oracle, with
independent source/pixel and live/cold module checks. Ftdisk 49 and a shutdown
popup remain; the scoped graphics pass does not qualify the whole system.
The [497 Xbox attempt](../outputs/d3d-scene497/REPORT.md) produced no launcher or
Windows test receipts and remains a separate failed attempt. Its hook and the
545 hook were removed after collection. The combined windowed PC and Xbox results
are described below.


## Combined windowed scene (rung 09c)

`scenepresent` combines the five offscreen scene cases with an owned window,
DirectDraw clipper, GDI occluder and exact screen-pixel readback. It uses
the existing RGB32, RGB565 or RGB555 desktop and never changes the display mode.
The RGB32 rendered scene is explicitly copied into a native-format staging
surface before the clipped blit; this CPU conversion is part of the test. The window
moves, is covered and uncovered, then closes. Software rendering only.

Build in WSL using the same RosBE setup as the earlier samples:

```sh
python3 tools/build-graphics-samples.py --rosbe "$ROSBE" \
  --sample scenepresent --output "$HOME/build/xwn-scenepresent-001"
```

Copy `scenepresent.exe` and `scenepresent.cmd` together to Windows. From that
folder, run each mode with a fresh output prefix:

```bat
scenepresent.cmd default scene-default-001
scenepresent.cmd hel scene-hel-001
```

Retrieve each prefix's `.txt`, `.exit`, `-clear.bin`, `-draw.bin`,
`-source-before.bin`, `-source-after.bin`, `-screen-before.bin`,
`-screen-after.bin`, `-post.bin`, `-native-before.bin` and `-native-after.bin`.
From the repository on your PC:

```sh
python3 tools/graphics_scenepresent.py /path/to/scene-default-001 --backend default
python3 tools/graphics_scenepresent.py /path/to/scene-hel-001 --backend hel
```

A zero process exit means the capture completed; the host checker must also
pass. It checks the independent scene expectations, exact clipping/occlusion,
GDI readback and unchanged RGB source pixels. This sample does not establish
performance, acceleration, game compatibility or varying-W interpolation.

The [547 PC comparison](../outputs/d3d-window547/REPORT.md) passes both software
paths on RGB565. The [546 attempt](../outputs/d3d-window546/REPORT.md) refused
an unsupported 32-bit desktop prerequisite before running the sample; it remains
a separate failed attempt. The matched [549 Xbox comparison](../outputs/d3d-window549/REPORT.md)
passes both modes at protected 720p/RGB32, with normal restart supported.

The [548 Xbox attempt](../outputs/d3d-window548/REPORT.md) returned without
Windows test receipts; it does not qualify the new windowed scene on Xbox.
The subsequent 549 cold-start comparison passes, preserving the existing 720p
setup. Both modes check 64,000 native screen samples, source preservation and
live/cold module identity. Ftdisk 49 and a shutdown popup remain; this scoped
graphics result does not qualify the whole system or resolve intermittent booting.

## Bounded scene process costs (rung 09d)

`scenebench` launches the unchanged windowed scene three times in sequence for
one software mode. Each child has a 50-second deadline. It records elapsed
and process CPU time, sampled working-set/commit usage, reported peaks and
page-fault counters. Every child still needs all of its pixel checks to pass.
The wrapper never changes display mode, installs drivers or restarts Windows.

Build under the same WSL/RosBE environment:

```sh
python3 tools/build-graphics-samples.py --rosbe "$ROSBE" \
  --sample scenebench --output "$HOME/build/xwn-scenebench-001"
```

Copy `scenebench.exe`, `scenebench.cmd` and `scene.exe` from the output root
into the same folder on Windows 2000. `scene-build/` contains the supporting
scene's source/build receipt; it is not needed to run. Open a command prompt
in the copied folder and use fresh, short prefixes:

```bat
scenebench.cmd default cost01d
scenebench.cmd hel cost01s
```

Use letters, digits and hyphens only. Keep Xbox prefixes at 16 characters or
fewer to leave room for capture suffixes on FATX. Leave the windows alone;
manual interference can intentionally cause the pixel checker to fail.
After each command finishes, retrieve **all files starting with its prefix**,
including the wrapper `.exit`, `-bench.txt` and each `-c0`, `-c1`, `-c2` child's
`.txt`, `.exit` and nine binary captures. Validate on your PC:

```sh
python3 tools/graphics_scenebench.py /path/to/results/cost01d --backend default
python3 tools/graphics_scenebench.py /path/to/results/cost01s --backend hel
```

Keep every repetition, including the first. Elapsed times include process
startup, deliberate window pauses, CPU conversion and capture I/O; they are
**not FPS**. Emulator timing cannot predict Xbox speed. Available system RAM
can change for unrelated reasons, and separate child processes do not prove
that repeated work in one process is leak-free.

The [550 PC control](../outputs/scene-cost550/REPORT.md) passes all six scenes
and telemetry checks, with normal restart and independent cold readback.
Whole-process elapsed times were 15.2–16.4 seconds; all children reported a
1,980 KiB peak working set. These are baseline measurements, not performance
targets. The [551 Xbox comparison](../outputs/scene-cost551/REPORT.md) also passes
all six scenes, module/counter checks and normal restart. Its first process took
22.455 seconds and the other five took 7.350–8.145 seconds; reported peak working
sets were 1,988–1,996 KiB and peak commit was 656 KiB. The fixed test order and
startup/system activity prevent attributing the first-run difference to a
specific cause or comparing backend speed. Ftdisk 49 recurred; earlier alpha,
shutdown-popup and boot-reliability limitations remain. The next rung will
separate repeated rendering within one process from capture I/O and pauses.


## Sustained scene (rung 09e)

`sceneloop` holds one software D3D7 context, two textures, and the existing
windowed presentation surfaces across five batches of 512 frames. The five
batch endpoints retain the independent geometric and clipped-screen checks.
Timing intervals separate render/state API work with target completion,
CPU readback/native pixel conversion, and primary blit plus `GdiFlush`.
Captures, report writes and deliberate display pauses are outside those intervals.
The presentation interval measures API completion, not when pixels reach the TV.
Two longer intervals check the high-resolution counter against coarse elapsed
time. When they disagree, QPC-derived durations are explicitly unavailable;
raw counter readings and independent `GetTickCount` phase totals remain. Those
coarse totals include counter-call overhead and are limited by clock-tick
quantization: a zero phase duration means unresolved, not zero work.

```sh
python3 tools/build-graphics-samples.py --rosbe "$ROSBE" \
  --sample sceneloop --output "$HOME/build/xwn-sceneloop-001"
```

Copy `sceneloop.exe` and `sceneloop.cmd` together. Use a fresh prefix each time
and leave the scene window untouched:

```bat
sceneloop.cmd default loop01d
sceneloop.cmd hel loop01s
```

Retrieve all files beginning with each prefix, including nine `.bin` captures,
the `.txt` report and `.exit` receipt. Check them on the host:

```sh
python3 tools/graphics_sceneloop.py /path/to/results/loop01d --backend default
python3 tools/graphics_sceneloop.py /path/to/results/loop01s --backend hel
```

The sample bounds each repeated batch to 30 seconds at frame boundaries; that
cannot interrupt a blocked API call. The public command wrapper has no external
watchdog. The private validation fixture additionally bounds each owned process.
The checker requires 2,560 completed frames and five valid image endpoints, checks
counter ordering against coarse elapsed time, and applies an 8 MiB limit to each
reported working-set and commit peak. Memory is observed before graphics setup,
before/after each batch, and after graphics resource release. Windows and PSAPI
still exist at the final snapshot. Runtime caches and system activity mean a
nonzero final memory delta is not automatically a leak. This bounded workload
cannot prove long-run leak freedom, FPS, GPU acceleration, or game compatibility.

The [552 initial attempt](../outputs/scene-loop552/REPORT.md) passed its image
endpoints but failed the original counter-frequency gate; it remains failed.
The revised sample adds explicit clock calibration and independent coarse
phase counters. The [553 revised PC control](../outputs/scene-loop553/REPORT.md) passes both
2,560-frame runs, ten image endpoints, resource/counter checks and normal restart.
The long clock checks reject QPC durations on this fixture, so only coarse phase
measurements are retained. Batch commit stayed constant and dropped by 64 KiB
after graphics release, without returning to its pre-graphics value. These
observations do not establish leak freedom.

The [554 matched Xbox comparison](../outputs/scene-loop554/REPORT.md) passes both
2,560-frame software runs and all ten endpoints at 720p, followed by a normal
restart. Its 1,125,000 Hz QPC agrees with both longer clock checks, so API phase
measurements are retained. Commit stays 667,648 bytes across batches and drops
to 577,536 bytes after graphics release; peak working set is 2,068,480 bytes.
These bounded observations do not qualify game FPS or leak freedom. Ftdisk 49
persists, so strict system qualification remains false. The temporary startup
hook is removed and ordinary startup is unchanged. Next is independent coverage
of perspective-correct texture interpolation across varying W.

## Perspective texture interpolation (rung 09f)

`perspective` renders two disjoint XYZ triangles into a 64x64 offscreen target.
Five cases keep their projected outlines fixed while changing vertex depths or
texture coordinates. The independent reference computes perspective-correct UV
and cross-checks it using object-space ray/triangle intersections. It fixes the
two-pixel boundary tolerance before a runtime capture; robust interior regions
reject affine interpolation. No lighting, blending, visible presentation,
acceleration or game-performance claim is made by this sample.

Build into a fresh directory with the same pinned RosBE setup:

```sh
python3 tools/build-graphics-samples.py --rosbe "$ROSBE" \
  --sample perspective --output "$HOME/build/xwn-perspective-001"
```

Copy `perspective.exe` and `perspective.cmd` together. Run once per fresh prefix:

```bat
perspective.cmd default persp01d
perspective.cmd hel persp01s
```

Collect each prefix's `.txt`, `.exit`, `-clear.bin`, `-draw.bin`,
`-source-before.bin` and `-source-after.bin`. On the host:

```sh
python3 tools/graphics_perspective.py /path/to/results/persp01d --backend default
python3 tools/graphics_perspective.py /path/to/results/persp01s --backend hel
```

The sample requires Windows 2000 and selects the enumerated RGB software device.
It explicitly sets and reads back texture perspective state. Each screenshot
stream has five 64x64 RGB32 frames; source streams contain two 8x8 textures.
The wrapper does not impose an external watchdog or restart Windows. Private
qualification bounds each process separately. The [host oracle](../outputs/perspective-oracle555/REPORT.md)
is synthetic evidence only. The [556 Windows 2000 control](../outputs/perspective556/REPORT.md)
passes all five cases in both software backends, unchanged texture bytes and
normal restart. Independent cold readers and live module checks agree. The
[557 Xbox attempt](../outputs/perspective557/REPORT.md) returned to the dashboard
without a runner receipt or graphics captures; it does not qualify Xbox
perspective rendering and does not invalidate the PC result.

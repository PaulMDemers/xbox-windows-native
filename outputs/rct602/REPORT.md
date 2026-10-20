# PC602: RCT's windowed GDI presentation calls observed

RCT Deluxe reached its title menu and Forest Frontiers under the qualified
paired-call recorder. All five private captures were inspected, including the
options panel showing Window mode and the unobstructed park. The guest then
closed the game, restored the temporary registry values and restarted normally.

The trace contains393 matched call/return pairs:272 with return addresses in the
RCT executable and121 from other modules. Unlike599's lookup-only inventory,
these records include actual invocations and return values:

| Call from RCT | Observed result |
| --- | --- |
| DirectDrawCreate | One successful call returned an interface; Release later returned0 |
| CreateDIBSection | One successful call returned a bitmap and a pixel-buffer pointer |
| StretchDIBits |32 sampled calls used that same pixel-buffer pointer; all returned768 |
| BitBlt | No direct main-image call observed;26 calls came from other module callers |

The32 StretchDIBits calls comprise22 destination rectangles of640x480 and ten
64x480 strips spanning that width. All use `00cc0020` (SRCCOPY) and usage0.
This establishes a GDI DIB presentation path in this instrumented PC windowed
run. It does not establish where the game spends most of its time.

The recorder armed the returned DirectDraw object's Release, SetCooperativeLevel
and CreateSurface entries. It saw Release, with no invocation of the other two
covered methods. Other DirectDraw interfaces and methods were not followed, so
this is not a universal claim that DirectDraw or GPU work is absent.

Sampling stopped after32 StretchDIBits entries. That early sample is not a frame
count and is not tied to a specific park phase. The game continued to render and
the later park image was inspected, but the capped calls do not prove its exact
presentation sequence. CreateDIBSection header bytes were not captured; the DIB's
dimensions, orientation and pixel format remain unmeasured. The return value768
is retained as observed, not converted into an assumed480-line copy or FPS.

See [drawing summary](drawing-review001.json), [paired trace review](trace-review001.json),
[cold checks](review001.json), [visual review](visual-review001.json) and
[final closure](final001.json). The recorder's shared core is byte-identical to
the qualified [original PC601 control](../rct601/REPORT.md); only the main target,
fixed IAT addresses, PID receipt and360-second bound were adapted.

The independent prelaunch verifier checked all502 game assets. Cold readback
enumerated7001 files, verified copied tools and protected OS binaries, and checked
five clean hives with independent raw-reader agreement. Only the expected
CSS0.DAT and Game.cfg game files changed. The temporary game registry subtree is
absent. One new EventLog6006 and VM exit0 confirm the normal restart; no host quit,
termination or deadline was used. The existing DRM typed-value decode limitation
remains explicit. This is not an allocation-bitmap or full filesystem health audit.

Setup problems were preserved in [input review](input-review002.md) and
[setup review](setup-review001.json): a stale dispatcher ID, text delivery and
backslash loss, the original retail UDF warning, and a rejected post-close screen
request. None caused a second game launch or a closed-runtime reopening.

All601/602 host processes are closed. No Xbox connection or console changes were
made. The ordinary launcher,720p baseline, saves and both transfer ZIPs remain
unchanged, and the ZIPs still exclude RCT.596's offline SOFTWARE cleanup has not
yet received another Windows boot. No matched pristine game control, debugger
overhead, game FPS or Xbox acceleration result is claimed.

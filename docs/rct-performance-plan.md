# RCT performance measurements after input qualification

Deluxe rendered Forest Frontiers and accepted a building action on the Xbox.
That establishes a useful compatibility starting point, not a frame-rate or
hardware-acceleration result. The current [compatibility record](rct-compatibility.md)
separates the watched Xbox result from PC controls and unresolved inputs.

## Save/load checkpoint and next measurement

The user confirmed repeated manual Xbox saves/loads in
[596](../outputs/rct596/REPORT.md), with a new park file collected and both prior
saves unchanged. [594](../outputs/rct594/REPORT.md) verified the new paused save
across normal restart. Treat the manual compatibility check as complete for the
current scope. The planned `XWN593.SV4` moved-view/reload image pair was not captured;
qualifying the exact loaded scene remains part of measurement preparation.

The first request recorder passed a known Windows 2000 control in
[PC597](../outputs/rct597/REPORT.md): 25 expected requests across two threads,
with the subject's own checks passing with and without tracing. The adapted
recorder reached the title and Forest Frontiers in
[PC599](../outputs/rct599/REPORT.md), with normal close, registry restoration
and restart. The earlier [598 display-setup failure](../outputs/rct598/REPORT.md)
remains recorded separately.

The paired-return recorder subsequently passed an original NT5 control in
[PC600](../outputs/rct600/REPORT.md): 45 matched calls/returns, including20
recursive probe invocations across two threads and five expected failed lookups.
Both pristine and traced subjects passed; normal restart and cold checks passed.
That qualified the scoped return recorder. The subsequent
[PC601 graphics control](../outputs/rct601/REPORT.md) verified exact GDI pixels,
failed/successful creation results and returned DirectDraw/surface methods with
106 paired calls. Its pristine and traced subject outputs matched.

[PC602](../outputs/rct602/REPORT.md) now supplies actual game invocations and
returns: successful DIB creation and32 sampled StretchDIBits calls from RCT,
plus DirectDraw creation/release. Title and Forest Frontiers rendered; normal
close, registry restoration and restart passed. Next, qualify the exact saved
scene and compare a fresh uninstrumented game control with the instrumented case
before interpreting costs. The original subject is a recorder control, not a
matched game-performance control. Current Xbox registry cleanup is cold readback
verified but has not received a subsequent Windows boot.

The [PC603 scene control](../outputs/rct603/REPORT.md) subsequently restored the
exact retained PC593 park view, with all165600 checked scenery pixels matching
its reference after a deliberate camera move. [PC604](../outputs/rct604/REPORT.md)
qualified bounded bitmap-header reads. [PC605](../outputs/rct605/REPORT.md) then
qualified a single explicit phase transition after recorded calls drain, including
exhausted startup sampling and duplicate requests:32 StretchDIBits samples per
phase,192 total pairs and84 header records on an original NT5 control. Its offline
checker naming collision and corrected002 review are preserved. The next actual
RCT trace can use this mechanism to delimit the verified saved park. Actual game
layout, process costs, clock qualification and observer overhead remain unmeasured.

[PC606](../outputs/rct606/REPORT.md) captured an early RCT1024x768 top-down8-bit
BI_RGB DIB, with32 sampled StretchDIBits calls using its returned bits pointer.
It failed before saved-park sampling: an internal GDI call returned a bitmap with
NULL ppvBits, which the recorder rejected and then terminated the game. Cleanup
and normal restart passed. A new absent-output recorder control is required before
the next game attempt. Early layout evidence is retained separately from this
failed saved-scene objective; no game costs or acceleration result is available.

## Establish a repeatable scene

The automated input comparison is qualified on [PC584](../outputs/rct584/REPORT.md):
arrows and right-button dragging moved the view in both modes; edge scrolling
moved it only in Full Screen mode. The matching Xbox583 launch produced no
runner output, so those physical input checks remain pending. The watched
Xbox565 building result remains the physical compatibility baseline.

The first cross-restart save helper stopped at its asset-verification gate
before starting the game ([PC585](../outputs/rct585/REPORT.md)). Its corrected
[PC586 control](../outputs/rct586/REPORT.md) subsequently ran after verified
capacity recovery. It saved a paused Forest Frontiers scene, restarted Windows
normally, and loaded that exact save after a deliberate camera change on the
second boot. The checked 165600 scenery pixels matched the saved scene exactly.
This is a PC control, not Xbox save persistence or a performance result.

[PC603](../outputs/rct603/REPORT.md) now qualifies the retained **PC593** save
on a fresh uninstrumented game fixture. After a deliberate camera change, loading
restored all165600 checked scenery pixels exactly to the matching PC593 reference
and held them unchanged ten seconds later. The save stayed byte-identical; native
Window mode, normal exit/restart and registry cleanup passed. This supplies a
repeatable scene, with no timing or acceleration result. The physical594 save has
the same filename but different bytes/hash and must not be substituted into this
PC comparison. User-confirmed physical manual save/load remains accepted.

For subsequent measurement scenes, retain the same discipline:
After the window/fullscreen input comparison, create one uniquely named park
save and record its hash, game executable, settings, actual display/client
size, camera position, zoom, pause state and visible scenery. Reload that exact
save after a normal Windows restart and verify the same scene. Preserve a
failed save or reload; a file existing is not proof that the game can reload it.

Use separate bounded cases for a paused stationary view, an unpaused stationary
view and a defined camera movement. Keep construction out of the baseline.
Record focus and pointer bounds; don't count an injected key as camera movement.
Use images to establish the scene before and after measurement, with capture
and report writes outside the timed interval. Sound remains deferred.

## Identify the actual rendering path

PC599 captured 332 API-entry requests: 237 from the RCT executable image and
95 from other DLL callers. RCT requested `DDRAW.DLL`, `DirectDrawCreate` and
`DirectDrawEnumerateA/W`, as well as GDI exports such as `BitBlt`, `StretchDIBits`,
`CreateDIBSection` and palette operations. The request names/counts match the
earlier failed-layout run, showing why startup lookup inventories alone cannot
identify rendering behavior.

Those599 records are `LoadLibraryA`/`GetProcAddress` arguments only. PC602 extends
them to393 paired invocations:272 from RCT and121 from other modules. All32 sampled
StretchDIBits calls used the pixel pointer returned by CreateDIBSection and
returned768. Their destination rectangles were22 full640x480 rectangles and ten
64x480 strips.26 BitBlt calls came from other module callers, with none directly
from the RCT image in this trace.

RCT successfully created a DirectDraw interface and later released it. The
recorder observed no calls to that interface's armed SetCooperativeLevel or
CreateSurface entries. Other interfaces/methods were outside coverage. Thus a
GDI DIB presentation path is observed in this PC windowed run; complete rendering
costs and physical acceleration remain unknown. The32-entry cap is an early
sample, not a frame count or a park-specific trace.

[PC604](../outputs/rct604/REPORT.md) qualifies the bounded header reader on an
original NT5 graphics control: 123 paired calls and 19 header observations,
including real inaccessible-page/truncated-header failures, with identical
pristine/traced result logs. It reads at most four plus forty bytes and interprets
only the bounded 40-byte BI_RGB policy; palette, masks and pixels are not captured.

Next apply that qualified reader to actual RCT headers to establish format,
dimensions and orientation.602 recorded the header pointer, not its contents;
neither return768 nor client640x480 establishes the bitmap layout. Its early
32-call cap also does not establish saved-park coverage. Qualify any new phase
signaling or delayed arming on an original control before using it in the game,
and preserve explicit phase/sampling limits when measuring selected calls.

The [PC586 static import inventory](../outputs/rct586/api-inventory001.json)
finds `LoadLibraryA` and `GetProcAddress` imports, with no static
`DirectDrawCreate` import. The602 trace follows selected resolved function
pointers and the returned DirectDraw interface. Neither the static inventory
nor this bounded invocation trace identifies a rendering cost.

Keep pristine and instrumented controls separate. A debugger pause or wrapper
can change scheduling and behavior; a call-count trace must not be presented as
an uninstrumented performance result. Check the resulting game images and
normal cleanup before considering the same observation on Xbox. Do not change
the functional display driver merely to make a tracing experiment pass.

## Measure costs with stated boundaries

Capture process CPU time, working-set/commit bounds and page-fault deltas for
each fixed workload, alongside elapsed time. Cross-check the guest clocks on
every platform before retaining high-resolution durations. Preserve failed
clock checks rather than rescaling them into a pass.

Only after the call trace identifies meaningful boundaries should timings be
assigned to game computation, software drawing, copying/conversion or
presentation. A Blt may update a dirty rectangle rather than a whole frame;
call counts and API completion do not establish physical scanout or game FPS.
Measure instrumentation overhead and retain the uninstrumented comparison.

The [Xbox554 software-scene results](../outputs/scene-loop554/REPORT.md) already
separate render, CPU upload and presentation-API phases, with guest-clock
cross-checks. They concern a small synthetic D3D7 sample and cannot be converted
into RCT performance. Its inherited Ftdisk49 and shutdown limitations remain.

Choose an optimization only when the game measurements identify a substantial
cost and a reproducible visual baseline can detect regressions. Native NV2A
acceleration remains a separate capability milestone; successful game startup,
module presence or a faster host model cannot qualify it.

[PC607](../outputs/rct607/REPORT.md) qualifies the narrow recorder fix for606's
absent CreateDIBSection output address. Original pristine/traced controls agree,
including independently inspected returned bitmap objects and expected failure.
The actual saved-park trace still needs a fresh game run;607 is no new game or
performance result. Non-NULL reads and DirectDraw checks remain strict.

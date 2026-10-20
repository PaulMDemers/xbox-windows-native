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
This qualifies the scoped return recorder, not game drawing or COM observation.

Next, observe actual graphics invocations and returned interfaces. Keep a new
unmodified game control separate from the instrumented case and measure trace
overhead before using timings. The synthetic subject is a recorder control,
not a matched game-performance control. Current Xbox registry cleanup is cold
readback verified but has not received a subsequent Windows boot.

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

These game records are `LoadLibraryA`/`GetProcAddress` arguments. They do not prove
successful resolution, invocation, surface types, renderer choice or acceleration.
PC600 now covers paired returns and actual original-probe entries. Qualify graphics
output pointers, calling conventions and module lifetimes in a new control before
following the game's DirectDraw objects. Record resolved module identities,
creation results, requested interfaces, cooperative level, display mode, surface
descriptions/capabilities and the methods actually used to update surfaces.
Include actual GDI drawing calls rather than assuming DirectDraw owns every update.

The [PC586 static import inventory](../outputs/rct586/api-inventory001.json)
finds `LoadLibraryA` and `GetProcAddress` imports, with no static
`DirectDrawCreate` import. The new request trace supplies a dynamic discovery
boundary, but does not yet follow returned function pointers or interfaces.
Neither inventory identifies a rendering cost.

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

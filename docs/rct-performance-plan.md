# RCT performance measurements after input qualification

Deluxe rendered Forest Frontiers and accepted a building action on the Xbox.
That establishes a useful compatibility starting point, not a frame-rate or
hardware-acceleration result. The current [compatibility record](rct-compatibility.md)
separates the watched Xbox result from PC controls and unresolved inputs.

## Establish a repeatable scene

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

PC568 observed DDRAW.DLL loaded in the game process. Module loading does not
identify the calls made, surface types, renderer or acceleration used. First
validate a bounded user-mode API observation on a fresh PC fixture. Record
resolved module identities, DirectDraw creation/interface requests, cooperative
level, display mode, surface descriptions/capabilities and the methods actually
used to update surfaces. Include GDI calls if the observed path uses them.

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

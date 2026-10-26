# RCT performance measurements after input qualification

Deluxe rendered Forest Frontiers and accepted a building action on the Xbox.
That establishes a useful compatibility starting point, not a frame-rate or
hardware-acceleration result. The current [compatibility record](rct-compatibility.md)
separates the watched Xbox result from PC controls and unresolved inputs.

## Latest measurement and next step

[PC628](../outputs/rct628/REPORT.md) completed the matched paused-park caller
measurement after the original-code controls. The scenery matched all 165,600
checked pixels before and after. RCT used 19.890625 CPU seconds over 20.016 guest
seconds / 20.025054937 host seconds. All 87 captured fixed-version WINMM timer
frames led to the same RCT return address, with the captured caller targeting
`timeGetTime`. These bounded observations identify a caller, not call frequency,
a percentage of CPU cost, game FPS or a demonstrated polling defect.

The next performance experiment remains a bounded physical Xbox process-cost
comparison with fresh clock/counter sanity and the same independently verified
scene. The separate [recording626](../outputs/rct626/REPORT.md) confirms windowed
play and arrow/right-button scrolling, but provides no game performance number.
No game pacing patch or functional driver change is justified by these samples.
Other-console hardware tests are deferred; native acceleration follows that
compatibility work. [Current status](current-status.md) records the intervening
display and timer/UDP diagnostic work.

## Measurement history and save/load checkpoint

The following sections retain the sequence of bounded measurements. A next-step
statement in an earlier result describes its stage; 628 above is the current
measurement boundary.

[PC623](../outputs/rct623/REPORT.md) now qualifies the original busy-versus-paced
timer comparison. Busy `timeGetTime` and `GetTickCount` loops used nearly one
emulated CPU; the `Sleep(10)` cases made 1,284 payload calls in about twenty
seconds and registered no CPU increment at coarse resolution. Both sampled and
unsampled cases passed. The call counts cover separately bounded subject windows,
exclude setup/deadline calls, and are not game FPS or pristine API-latency figures.

Busy `timeGetTime` produced many locations in its WINMM body/helper; paced cases
landed at the `NtDelayExecution` return. Busy cases also produced ntdll wait-return
locations from zero-timeout checks, so a wait API name alone does not establish
sleeping. [PC622](../outputs/rct622/REPORT.md) remains a failed qualification:
logging extended the subject window beyond its declared bound. PC623 moved the
subject release ahead of logging without changing the workload or relaxing gates.

This supports the timer-polling lead below. Next validate runtime code and callers
with original controls before applying the method to a fresh RCT fixture. It does
not yet justify pacing the game, replacing timer APIs or changing drivers.

[PC621](../outputs/rct621/REPORT.md) completes the matched saved-scene location
milestone after [PC620](../outputs/rct620/REPORT.md)'s original workload controls.
RCT used 20.046875 CPU seconds over 20.094 elapsed, all accounted for by its main
thread; the 165,600-pixel scene stayed exact. 240 saved-user locations comprised
73 RCT, 88 WINMM, 78 ntdll and 1 GDI32. Exact protected DLL address analysis places
the WINMM samples in timeGetTime and its direct arithmetic helper. This makes
timer polling a concrete next lead; it does not prove the source of all CPU use.
The ntdll samples are syscall returns and do not establish sleeping or kernel
costs. Location counts are not CPU-time percentages, game FPS or Xbox results.
Normal restart, cold audit and all nine private capture inspections passed.

Next qualify busy versus paced timer polling with original code before changing
the game or drivers. Any packed game address attribution needs validated runtime
bytes/callers. [PC619](../outputs/rct619/REPORT.md)'s prelaunch serial-reader failure
and every corrected preparation failure remain retained; no failed runtime was
rerun. The physical Xbox and distributed packages were untouched.

[PC618](../outputs/rct618/REPORT.md) completes the matched saved-scene cost
milestone, using [PC617](../outputs/rct617/REPORT.md)'s qualified continuous-work
coordination. Over20.062 seconds, the game used19.3125 CPU seconds, the recorder
0.375 seconds (1.87% of one emulated CPU), and the observer0.015625 seconds.
The165600-pixel scenery matched exactly before and after; independent host
elapsed was20.044836489 seconds. All processes closed normally and cold checks
passed. Compare pristine615's19.859375 CPU seconds over20.016 elapsed seconds.
These are single PC intervals under capped32-pair recording with ongoing entry
handling. Recorder process CPU is measured, but total instrumentation overhead,
FPS and Xbox acceleration are not established. The paused game dominates CPU;
next attribute that time to waiting, rendering and copies before optimizing.

[PC616](../outputs/rct616/REPORT.md) qualified the next measurement setup on
original Windows 2000 code: distinct subject/recorder/observer identities,
host-correlated twenty-second intervals, exact pixels and all recorded-phase
call/return timestamps inside the interval. It counted40 measured entry hits,
including8 beyond the32-call cap. The cap leaves breakpoints active; it does not
make execution uninstrumented. This tiny paced control registered no CPU
increment at coarse resolution, so it supplies no recorder-overhead estimate.
Normal restart and cold checks passed. PC617 subsequently qualified continuous work; PC618 completed the matched retail
saved-scene measurement.

[PC615](../outputs/rct615/REPORT.md) completed the first host-clock-checked,
uninstrumented paused saved-scene cost baseline. Over20.016 seconds, RCT used
19.859375 seconds of process CPU (99.2% of the single emulated CPU), while its
working set stayed33.684MiB. The165600-pixel scene remained exact. Normal restart,
registry restoration, saved-file and cold checks passed. This is one PC interval,
not game FPS or Xbox throughput. It does not identify the cause of the CPU use.
PC618 now aligns actual recorder activity with a matched timed interval and
measures game, recorder and counter-observer processes separately. Recording that finishes before timing starts cannot establish sampled-call
costs. PC616 confirms capped entry breakpoints still incur debugger handling.

[PC613](../outputs/rct613/REPORT.md) exposed a timing problem in the PC fixture:
a two-second sleep appeared as about 0.286 seconds through QPC/frequency. It failed
qualification; the short busy workload also fell below the sampling interval.
[PC614](../outputs/rct614/REPORT.md) then checked longer original workloads against
independent host timestamps delivered through virtual COM1. Guest tick elapsed
agreed within 12.8 ms, and busy/idle CPU accounting behaved as expected. QPC remains
unreliable for elapsed time in these fixtures; no correction factor or driver
patch was applied. The observer recorded no CPU increment at coarse resolution,
which is not zero-overhead proof. These are synthetic controls, not game FPS or
Xbox measurements. PC615 subsequently included host clock agreement on its own verified saved-scene
interval. PC618 supplies the matched traced comparison above.

[PC610](../outputs/rct610/REPORT.md) qualifies recorder DLL unload/reload using
original code at a reused address with different instruction bytes. Pristine
and traced behavior matched; unsafe pending/active states remain rejected.
[PC611](../outputs/rct611/REPORT.md) was stopped by host disk-space protection;
it supplies no game outcome. Historical leaf disks are now losslessly archived
with full verification. [PC612](../outputs/rct612/REPORT.md) then passed with
larger capacity headroom: the loaded park matched all165600 reference scenery
pixels and remained unchanged ten seconds later. Its571 paired calls include32
RCT StretchDIBits samples in each phase, linked to a1024x768 top-down8-bit BI_RGB
DIB. Normal restart and cleanup passed. This establishes the sampled GDI path;
PC615 subsequently measured pristine game costs; PC618 supplies separate recorder process costs, with the limitations above.
Neither capped API counts nor these PC observations establish FPS or Xbox GPU
acceleration.

The user confirmed repeated manual Xbox saves/loads in
[596](../outputs/rct596/REPORT.md), with a new park file collected and both prior
saves unchanged. [594](../outputs/rct594/REPORT.md) verified the new paused save
across normal restart. Treat the manual compatibility check as complete for the
current scope. The physical `XWN593.SV4` moved-view/reload image pair was not captured. The
separate PC593 scene is now qualified by PC603 and instrumented PC612; do not
substitute the differently hashed physical save into that PC comparison.

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
close, registry restoration and restart passed. The exact saved scene is now qualified by PC603/612. PC615 provides a clock-qualified uninstrumented cost baseline; PC618 supplies the matched instrumented case and bounded recorder process costs. The original subject is a recorder control, not a
matched game-performance control. At that stage Xbox registry cleanup had only
cold readback verification; the later626 interactive session passed its own
registry-restoration and normal-shutdown checks.

The [PC603 scene control](../outputs/rct603/REPORT.md) subsequently restored the
exact retained PC593 park view, with all165600 checked scenery pixels matching
its reference after a deliberate camera move. [PC604](../outputs/rct604/REPORT.md)
qualified bounded bitmap-header reads. [PC605](../outputs/rct605/REPORT.md) then
qualified a single explicit phase transition after recorded calls drain, including
exhausted startup sampling and duplicate requests:32 StretchDIBits samples per
phase,192 total pairs and84 header records on an original NT5 control. Its offline
checker naming collision and corrected002 review are preserved. PC612 subsequently used this mechanism to delimit the verified saved park and
record its actual DIB layout. PC613/614 subsequently qualified host-correlated timing, and PC615 measured
pristine process costs. Recorder overhead remains unmeasured.

[PC606](../outputs/rct606/REPORT.md) captured an early RCT1024x768 top-down8-bit
BI_RGB DIB, with32 sampled StretchDIBits calls using its returned bits pointer.
It failed before saved-park sampling: an internal GDI call returned a bitmap with
NULL ppvBits, which the recorder rejected and then terminated the game. Cleanup
and normal restart passed. PC607 subsequently qualified absent-output handling, and PC610 qualified DLL
lifetimes before the successful PC612 saved-scene trace. Early layout evidence is retained separately from this
failed saved-scene objective; no game costs or acceleration result is available.

## Establish a repeatable scene

The automated input comparison is qualified on [PC584](../outputs/rct584/REPORT.md):
arrows and right-button dragging moved the view in both modes; edge scrolling
moved it only in Full Screen mode. The matching Xbox583 launch produced no
runner output and remains a failed attempt. Later physical590 and626 confirmed
windowed arrows and right-button movement; fullscreen remains unqualified.
The watched Xbox565 building and594/596 save/load results are separate evidence.

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

That reader was subsequently applied in612, establishing the sampled saved-park
format described above.602 recorded the header pointer, not its contents;
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
The subsequent612 run supplied the saved-park trace;607 itself is no game or
performance result. Non-NULL reads and DirectDraw checks remain strict.

[PC608](../outputs/rct608/REPORT.md) stopped at copy admission because of a stale
uppercase tool name; no game launched. [PC609](../outputs/rct609/REPORT.md) corrects
that with a checked copy contract and confirms607's absent-output handling in the
actual game. Its Load dialog accepted the save path, but a tracked DLL unload
triggered deliberate recorder termination before scene verification.536 calls and
returns pair; no park sample or timing result was obtained. Qualify module lifetime
and address reuse on an original NT5 control before the next game retry; keep
active/pending/stepping checks strict. Existing manual Xbox save/load remains valid.

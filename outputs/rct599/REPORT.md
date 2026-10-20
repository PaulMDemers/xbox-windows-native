# RCT API-request discovery reaches Forest Frontiers

Fresh PC599 displayed the RCT title and paused Forest Frontiers while the API
request recorder was active. Five valid640x480captures include the objective
dialog explicitly naming Forest Frontiers and the final unobstructed park. The
desktop was1024x768,16bit, selected through the native Display panel and checked
by the helper before any game launch or setup-registry change.

The recorder captured332entries:237from the RCT image and95from other DLLs. RCT
requested DDRAW.DLL, DirectDrawCreate and DirectDrawEnumerateA/W, plus GDI exports
including BitBlt, StretchDIBits, CreateDIBSection and palette operations. The
requested library/export names and counts match the failed-layout598 discovery.
This is evidence of lookup requests, not successful return values, drawing calls,
surface placement, GPU acceleration or frame rate. Startup resolves a broad API
set; a name appearing once does not establish that it draws each frame.

The game and debugger both exited0 through the helper's WM_CLOSE path. No forced
termination occurred. Registry restoration passed independently on the cold
SOFTWARE hive, and a new EventLog6006 plus VM exit confirmed normal restart.
The disk audit verified protected OS binaries, all3tools, five system hives and
the immutable seed. Guest copy verification covered502game assets before launch;
only CSS0.DAT and Game.cfg differ afterward. All owned processes are closed.

The scheduled host screenshot at VM exit recorded FileNotFoundError with
process_exit0; it remains in ntfs-phase1.json. All five guest captures are complete.
The earlier598bad-mode attempt and597first compiler failure are preserved.
No Xbox access, startup hook, package update or physical cleanup qualification
occurred. The current Xbox SOFTWARE cleanup still awaits a subsequent Windows
boot; saved parks and delivered ZIPs remain untouched.

Next: extend the known synthetic recorder control to pair function returns and
observe actual DirectDrawCreate plus GDI drawing invocations. Follow the returned
DirectDraw interfaces/surfaces only after that recorder is independently checked.
Then qualify the saved fixed scene, paired pristine/instrumented game controls
and overhead before measuring CPU, copying or presentation costs. Sound, other
consoles, fullscreen, boot intermittency and1080i remain deferred.

Evidence: [final001](final001.json), [cold/capture checks](review001.json),
[visual observations](visual-review001.json), [request inventory](trace-review001.json),
[598 comparison](request-comparison001.json), [597 recorder control](../rct597/REPORT.md).

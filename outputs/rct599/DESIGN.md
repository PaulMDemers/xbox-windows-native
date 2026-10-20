# RCT599: correct the598 display preflight, retain request-discovery scope

598 requested800x600x32 and received DISP_CHANGE_BADMODE(-2). It nevertheless
started the game at640x480; the strict visible-client guard refused input. That
failed harness attempt is retained, with its useful early API requests, normal
close/restart and pending cold audit. No game failure is inferred.

Fresh599 returns to the native Display control panel used by PC593. Select and
verify1024x768 before launching. The helper now refuses to create the debugger or
touch game registry values unless the actual desktop is1024x768. No guessed bit
depth or ignored mode-change result. Game remains640x480windowed. Other recorder,
asset, input/capture, cleanup and shutdown behavior inherits598; read its design.
Only a NEW immutable404 child, never reopen598. No physical access or startup hook.

Require a captured title and paused Forest Frontiers, game/debugger normal exit,
normal Windows restart, exact assets/tools and restored game registry. Parse
entry requests separately from successful resolutions and method invocations.
There is still no matched pristine game control/overhead measurement, fixed-save
baseline, FPS or acceleration result. Sound and other hardware tests stay deferred.

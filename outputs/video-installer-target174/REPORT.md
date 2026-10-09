# Outer failure captured; popup producer still unresolved

SINGLE fresh launch2026-10-09 00:56:35UTC→dashboard00:58:58 (actual launch.json).
Owned runner7809,tracer37642,supervisor10514,cold audit31724 CLOSED; all breakpoints
removed/resumed, no pending returns.63events/62 independently verified resident
pins,29 creation entries+29 exact ETHREAD/48byte return pairs,1 kernel shutdown.
432 excluded early-loader/termination address-lead hits retained;7 unreadable
hits (4 target loaders,3 Explorer creation entries), no pages forced or weakened
identity gates. Capture completeness PASS for declared scope, not child startup
or ordinary/performance/physical qualification.40 frozen input/source pins exact.

Actual pinned UMP caller and ADVAPI inner caller, current services.exe PID208:

-01B0: outer+innerTRUE; returned child844/TID840. Three verified child thread
  loader entries; two current-child command reads name exactly the01B0 instance,
  one command remains nonresident. Loader entry is not completed initialization.
-01B4: outer+innerTRUE; child840/TID844. Inner/outer returns tick7118, actual child
  loader entry7119 with exact01B4 command. No hard-error/termination hit decoded.
-1B36/0005: outer supplied token1868 at tick7121; innerTRUE tick7126 returned
  process/thread handles1876/1868 and child864/TID840. OuterFALSE tick7127 with
  LastError6. Input token numeric value equals output child thread handle; this
  suggests reuse but neither token type/failing API nor closing actor captured.
  Additional device is an emulator observation; no hardware-device claim.

Winlogon PID180 NtShutdownSystem action1 at tick7295. Capture continued through
dashboard, yet no user/kernel NtRaiseHardError hit. Cold logs containONE rundown
DLL-initialization popup26/type4 (“window station is shutting down”). Thus error6
is not established as popup producer; absence of the hooked error API does not
mean no error occurred. Window-station teardown can precede final kernel shutdown;
the after_shutdown_entry field only names that captured API ordering.

Guest5samples/20 pixel-copy checks/25timedloops/50 RAM-versus-scanout fullscan RGB
coherence, normal shutdown/dashboard PASS. Full cold322dirs6721files323dirclusters,
zero errors/orphans;5 structural hives/protected binaries/startup exact. Workload/
integrity PASS. StrictFALSE inheritedexactFt49+ONEpopup; application delta empty.
No event waiver, physicalFTP/deploy/test, driver/settings/device/UI change.173
failed capture retained unchanged, new174 narrowed observation scope only.

175 NEW bounded current-thread native API observation inside services rundll32
outer calls is the next discriminator. It retains raw statuses and buffers to
identify the first token failure; no global close tracker or speculative fix.
Physical0101/video0093,0088rollback,immutable0.1.0 preserved.

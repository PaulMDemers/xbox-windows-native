#699 native timer prerequisite

A separate watched diagnostic uses697's checked owned-page transition and inherited
720p scanout. The kernel sets the diagnostic720p mode through its supported API,
as in697. The subsequent native path measures one timer interval and performs no
SMBus access or encoder programming. It does not initialize a native video mode,
boot Windows or resume networking. Staged owner labels refer to this native scope.

The kernel must report3375000Hz and CPUID must advertise TSC/SSE before handoff.
That frequency matches the earlier684 kernel-context observation; this is not an
independent post-handoff frequency calibration. The native code checks the same
PCI identity/I/O/BAR expectations, restoresCF8, then reads port8008 as32 bits.

Starting from one sample, it permits at most100000 additional reads. Unsigned
subtraction accepts32-bit rollover. A backwards/large jump or elapsed interval
above33750 ticks refuses the result. Success requires at least1688 ticks, the
rounded-up500us interval at the recorded kernel rate. RDTSC brackets the timer
loop; its raw64-bit difference is diagnostic and not serialized or an independent
clock calibration. No clock, interrupt, cache or mapping change is added to the
existing transition.

## Display

Top green bar means the checked native handoff was reached. The second bar is
blue during sampling, then green=interval reached, orange=read budget exhausted,
magenta=discontinuity. PCI refusal remains red=identity, cyan=I/O disabled,
yellow=BAR. Result deliberately holds for a photo and manual power-cycle.

Ten MSB-left bit rows, white1/black0: PCI ID, command/status, BAR, first tick,
last tick, elapsed ticks, read count, result code, TSC delta low, TSC delta high.
Result codes:1 success,2/3/4 PCI refusal,5 budget,6 discontinuity. Failed PCI
admission leaves timer samples/TSC unread (FFFFFFFF) and read count0.

## Validation and preserved failures

Build001 failed because the new frequency check used the PC-style counter API
signature. Correct Xbox KeQueryPerformanceFrequency is used in frozen build002;
failed source/script/log pins remain. No failed payload was staged.

The linked template passed22 timer/pixel models: progressive/stalled/backwards
clocks,32-bit rollover,24-bit wrap rejection, threshold/upper bound, last-read
success, timeout, PCI refusal, relocation and64-bit TSC subtraction. These use
explicit input/RDTSC models, not actual Xbox timing.

Ten fresh diskless CPU fixtures pass the full transition: three mappings reach
the expected PC-PCI refusal and seven invalid/fault inputs leave the framebuffer
unchanged. All VMs closed.19 allocation-policy cases pass. Page-review001 ran too
early, before its dependent CPU pages existed; it failed without hardware access.
Fresh page-review002 passes all9 cases against those completed fixture pages.

Code1067 bytes fits below GDT4c0. Timer scratch ends5d4 before IDT600; stacke00.
Frozen source/binary pins, layout and scope are in review001.json. Source licenses
are retained. No startup hook, dashboard C access or ordinary launcher change.
Native results are RAM/display only; persisted CPU remains pre-file-write.

Read NEXT.md and stage/launch/observation records for current physical state.

One SITE accepted2026-10-27T02:58:09.306075Z after current watch/reset confirmation.
The timer result/photo is pending; no native success or reset is inferred.

User subsequently reports "Green, holding" (observation001.json). This is the
interval-reached indication; raw timer measurements/photo remain pending.
No reset requested or collection started. Top bar not separately confirmed.

## Closed physical result

Photo independently decodes first FEB2F2E5, last FEB2F98E, elapsed1705 ticks,
87 timer reads, result1 and raw TSC delta375617. Both bars green. At the recorded
kernel3375000Hz rate this is nominally505.185us; no independent calibration or
serialized TSC claim. All320 bits threshold/offset checked;256 cross-row checked.

User power-cycled after photo capture and confirmed Ready. Eight preparation
records read twice; private hashes, source/binary pins, staged XBE/owner and
unrelated directory entries verified. Native context remains RAM/display only.
No native SMBus/encoder programming, Windows or startup hook. Kernel prepared720p.
No owned host process/VM. Hardware ticket retained; automation paused. Console
at dashboard. Runtime699 CLOSED: never rerun/recollect. Original720p unchanged.

Next: complete480p GPU/output/encoder sequence review and linked failure tests
using isolated698 status handling before a watched configuration-writing probe.
Read native-timer699/NEXT.md. Networking/1080i/boot intermittency remain tabled.

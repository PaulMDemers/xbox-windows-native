# Counter boundaries and interpretation

CALLS counts selected timer calls inside the payload loop only. The initial
selected-timer baseline read is outside this count. GetTickCount also supplies
subject START/END and deadline checks; those control calls are not counted as
payload calls. Busy modes check release/deadline once per4096 payload calls;
paced modes check once per call and then Sleep(10). No timeBeginPeriod request.

Subject START precedes SetEvent(ready); observer measures its own20s interval
after ready/module/identity setup. Subject END follows observing the release
set after end counters/module capture, before logging. The reviewer requires enclosing subject
bounds within1s of each observer boundary and total subject20..22s. CALLS is not
an exact20s count or a game FPS/call-frequency measurement. Returned selected
timer values must advance and agree with the full subject duration within100ms.

The620 sampler loop and elevated observer priority remain unchanged. Busy/paced
CPU contrast is tested independently from location distribution; no chosen
proportion of WINMM samples is required to pass. Saved-user syscall returns do
not identify kernel execution or prove sleeping. Call-loop counters, batching
and conditional branches add diagnostic costs; this is not pristine API latency.

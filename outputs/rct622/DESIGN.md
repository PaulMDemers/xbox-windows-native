# PC622 original timer polling qualification

Fresh immutable404 only. Reuse620 external sampling loop, module/identity,
balanced suspension and host serial clocks unchanged apart from owned namespace.
Four original modes:0 busy timeGetTime,1 timeGetTime with Sleep(10),2 busy
GetTickCount,3 GetTickCount with Sleep(10). Run each once without sampling then
once with sampling. Each observer window20s; bounded subject deadline40s.
Busy modes issue4096 timer calls between release/deadline checks. Paced modes
issue one call then Sleep(10). Both count calls and changing returned times.
Call counts cover the subject's entire reported START/END window, including
startup and final log overhead outside observer timing; never label them exact
20-second counts. No output writes occur inside workload loops.

Require advancing clocks, plausible monotonic timer progression, busy CPU>70%,
paced CPU<10%, main-thread coverage, independent host timing, balanced snapshots,
exact tools, normal restart and cold audit. Samples identify saved-user locations,
not CPU-time percentages/kernel costs. No prerequisite proportion of timer-site
samples: report actual locations, preserving qualification failures. Compare
WINMM offsets to exact protected DLL identity from621 seed export. No game,
physicalXbox, driver patch, FPS claim, timer-resolution request or priority
change in subjects. Observer elevated priority is inherited620 diagnostic state.

22GiB fixture admission and20GiB reserve includingWSL. Do not reopen any closed
runtime. Keep all failures; immutable404 and protected packages unchanged.

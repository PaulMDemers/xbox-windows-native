# 550 PC scene process costs: scoped PASS

A fresh child of the original404 Windows2000 NTFS seed completed three separate
scene processes through each default and HEL software path. All six processes
passed the unchanged five-stage pixel oracle, native CPU staging, window
clipping/occlusion/movement and source-preservation checks. The original
547/549 scene executable is unchanged; the new wrapper observes process CPU
FILETIMEs and PSAPI working-set/commit counters at a nominal50ms cadence.

| Mode | Run | Elapsed seconds | Process CPU seconds | Reported peak WS KiB | Reported peak commit KiB |
|---|---:|---:|---:|---:|---:|
| default | 1 | 16.375 | 3.750 | 1980 | 624 |
| default | 2 | 16.437 | 3.938 | 1980 | 624 |
| default | 3 | 15.375 | 3.406 | 1980 | 624 |
| hel | 1 | 15.172 | 2.844 | 1980 | 624 |
| hel | 2 | 15.328 | 3.219 | 1980 | 624 |
| hel | 3 | 15.562 | 3.422 | 1980 | 624 |

These are whole-process emulator measurements. They include startup, deliberate
window pauses, CPU staging and flushed capture writes; they are not frame-rate
measurements or physical-Xbox speed. All runs are retained, including each
first run. Global available-memory changes include unrelated system activity.
Three separately terminated processes do not establish in-process leak freedom
or a long-run resource trend. No GPU, games, varying-W or ideal-alpha claim.

One VM boot/runner invocation only. Both wrapper exits and six child exits are
zero, normal restart was requested, the VM exited without host stop/deadline,
and cold EventLog6006delta is one. Five hives were audited; inherited SOFTWARE
typed DRM limitations and lack of independent full NTFS allocation audit remain.
No new error/warning records in the selected system-event delta. Source seed
and floppy bytes unchanged; original OS executables unchanged.

Two independent cold readers agree. Eleven live module records per child match
cold bytes and PE image sizes. Exact cold PSAPI exports GetProcessMemoryInfo;
its hash also agrees after the run. Actual telemetry controls reject372mutations.
Four host receipt tests pass, including tick wrap and missing/invalid fields.
The first host test failure was a malformed synthetic fixture with the end
marker before child fields; host-tests001/failed-test001 preserve it.
No guest was launched for that failure. Corrected host-tests002 passed.
38 malformed floppy controls passed before launch;157inputs were frozen and
are archived privately. All owned processes/mounts are closed; never rerun,
recollect or parent550. See final-review.json and runtime-review002.json.

The public builder now compiles the wrapper and sibling scene.exe. Public
source/import checks pass, but rebuilt executable bytes are not independently
runtime-qualified; public-build001.json distinguishes that result. Matched551
Xbox packaging uses the exact550 binaries and awaits a new cold-start confirmation.
Boot diagnosis remains tabled; no physical launch was performed for550.

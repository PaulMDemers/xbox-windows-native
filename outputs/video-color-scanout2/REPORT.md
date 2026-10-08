# Independent color cursor lifecycle PASS

Fresh candidate001 used the exact ordinary probe123 and unchanged RAM0109 DLL.
All 104 raw framebuffer captures matched: 26 original color cursor states,
26 hidden states, 26 replacement states and 26 restored backgrounds. This is
10,223,616 RGB comparisons with zero mismatches. Visible phases covered 35,898
cursor pixels, of which 21,989 differed from the background. Nonzero hotspots,
top-left desktop clipping and clipping at the tested rectangle are covered;
desktop right/bottom clipping is not claimed.

All runtime DIB references exactly matched their 26 cold reference SHA256 values.
Raw marker arguments, process/thread identities and stage ordering were checked.
355 resident byte pins include all 11,668 relocated display.text bytes. The
display header's E14 remains explicitly recorded, with loader identity, complete
resident code and cold binary hash required instead. No guest register/memory
forcing or UI intervention. Full breakpoint teardown and resume succeeded.

The added journal records 111 stops and 110 single-steps. All 103 stepped cursor
and restoration marker entries advanced one byte, with no process change. Two
entry demand-fault deferrals and two unrelated process API hits are retained.
The earlier ordering failure did not recur. This does not establish its cause
or show that logging fixed an observer bug; timing and unrelated activity differ.

Normal shutdown count 1 and dashboard return. Full allocation: 325 directories,
6,785 files, 326 directory clusters, zero errors/orphans. All five structural
hives, protected/payload/startup hashes, unchanged 96MiB pagefile and inherited
configuration passed. No warning/error or application events. Five mutations of
the actual framebuffer oracle were rejected, including wrong shape/hotspot,
hidden/visible confusion and one background RGB bit.

See verification.json, oracle-tests.json and candidate001/audit.json.
strict_diagnostic_passed=true; ordinary_qualified=false; physical_qualified=false.
The separate ordinary video-color-cursor run passed independently. The first
video-color-scanout remains strict FAIL for its incomplete sequence, despite
its clean guest workload and cold audit. history-review.json checks all three
outcomes without relabelling that failure.

All owned processes CLOSED. Never relaunch or recollect these attempts. No
driver, cache, policy or physical-console changes were made. Alpha/animated
cursors, ShowCursor display counts, lifetime races, display-mode transitions,
boot-video/crash ownership and hardware performance remain unqualified.

Probe123 SHA256: c00a46bbf5391532ad43e8a0c29c1475439b47800f0972f6e1dd262cd350ef57.
RAM0109 SHA256: ed901376d61e70a125fce834e20b366e49a1d632879debbcfedd621c18b6a440.

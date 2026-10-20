# PC616 closed: original recorder-cost coordination passed

Fresh immutable404 PC fixture ran 2026-10-20 18:48:27–18:51:02 UTC.
No retail assets, physical console, GPU driver changes or closed runtime reuse.

An original subject copied an 8x8 DIB and verified every destination pixel,
first directly and then under the recorder. Each case completed 75 copies:
35 before the timing gate and 40 paced copies inside the measurement window.
Both subject self-checks and exit codes passed. The observer opened the actual
subject process and checked its PID, creation time and executable path.
Subject, recorder and observer remained distinct in the recorded case.

| Case | Guest ticks | Host elapsed | Samples |
| --- | ---: | ---: | ---: |
| Sleep sanity | 5.000 s | 4.990316 s | endpoints |
| Direct subject | 20.016 s | 20.013171 s | 183 |
| Recorded subject | 20.015 s | 20.010241 s | 183 |

Both subject workloads occupied 5.000 seconds within their twenty-second
intervals. Subject, observer and recorder CPU increments were zero at coarse
15.625 ms accounting resolution. This deliberately tiny, paced workload does
not quantify recorder overhead and cannot establish zero cost. Stable sampled
working sets were 794624 bytes direct, 819200 bytes recorded subject and
1032192 bytes recorder. These are process working sets, not game memory costs.
QPC again reported incorrect elapsed time and remained diagnostic only.

The recorder retained 69 paired calls overall, including 32 StretchDIBits pairs
per phase. All 35 startup and 40 measured entry hits were counted; respectively
3 and 8 exceeded the sample cap. All measured call/return timestamps lie within
the observer interval and finish before subject DONE. This confirms that hitting
the cap does **not** remove the breakpoint: subsequent entries still pass through
the debugger. A capped recorder is not equivalent to uninstrumented execution.

Cold readback hashed 6492 files in 310 directories, checked five clean hives,
matched all three installed executables, preserved protected OS/seed bytes and
confirmed one new normal EventLog shutdown with independently checked raw event
timestamps. No forced process termination or host reset occurred. VM, serial
reader and owned audit/build processes are closed.

Host tests rejected 19 invalid identity, clock, completion and alignment cases;
the shared timing store passed address/undefined-behavior sanitizer bounds tests.
Build001 failed a function-pointer cast warning and remains preserved; build002
uses the typed lookup and passed. Source reviewer001 omitted the explicit quoted
VM-number substitution and failed on actions002.py; corrected reviewer002 passed
against unchanged sources. Both failures remain public.

Before admission, the already-closed612 raw leaf was archived, fully decompressed
and hash-verified before its raw file was removed. See archive001.json for the
exact E:/xwn616 archive mapping; restoration is evidence-only, never boot/parent.
Existing archive maps, failure evidence and private assets remain intact.

This qualifies timing and process coordination on original NT5 code. The matched
RCT traced measurement is next; PC615 remains the pristine game baseline.
No game FPS, Xbox throughput, acceleration or release claim follows from PC616.
Xbox remains untouched, last known at the dashboard with no owned hook;
596 SOFTWARE restoration remains cold-only. Packages, protected720p and deferred
hardware/audio/fullscreen/boot investigations remain unchanged.

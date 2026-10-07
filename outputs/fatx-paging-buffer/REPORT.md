# Full-run trace observes separate persistence of the two warning fragments

Case002 launched05:54:30UTC7October2026 and returned at06:00:34UTC. The driver
consumed59 mapped SetupAPI.log buffers; every complete captured range matches
the cold file. Both parts of the220-byte warning at270225 are now covered.
No source mismatch, filesystem corruption or driver failure was reproduced.

| Observed write | UTC | Process | File offset | Effective bytes | Target bytes covered |
|---|---|---|---:|---:|---:|
| First suffix |05:55:17.716165|rundll32.exe|270336|109|109|
| Later preceding page |06:00:12.247911|winlogon.exe|266240|4096|111|

The host interval is294.531746s and includes debugger pauses; it is not an
ordinary latency benchmark. The earlier page was observed near the normal
shutdown. All target-overlapping requests returned success and the exact
effective information count. This closes the first attempt's missing-prefix
capture. Its partial result is preserved independently in001/REPORT.md.

The final disk contains the entire warning exactly, including111+109 bytes.
The corresponding physical range in the immutable input was all zero: all220
bytes changed, so the result cannot be explained by prefilled matching slack.
Complete F allocation, selected binaries, five hives, installation, normal
shutdown and event checks passed. All breakpoints were removed and the guest
resumed before owned teardown. Both attempts are closed and collected once.

This is debugger evidence only. Source buffers precede lower disk/DMA submission;
correct emulator bytes do not explain the hardware anomaly. The original first
hardware reboot method is unknown. Different persistence times make an
interrupted-guest experiment worthwhile, without assuming a power interruption
actually occurred on the console. No driver patch, hardware deployment, recovery
replacement or release-tag change follows from this observation.

The reviewed unchanged0101 binary and compiler-derived frame/structure offsets,
source snapshots and instruction bytes are pinned. Case002 removed unrelated
cache-call traps and observed until dashboard return instead of the early hit
bound. ordering.json, per-case buffer-analysis.json and before-target.json retain
the exact evidence and limits. Raw buffers remain private under artifacts.

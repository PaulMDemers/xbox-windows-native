# Test753 CLOSED: clock-reference refusal

One SITE accepted01:04:54UTC; authenticated dashboard01:05:25UTC. Two reports
collected once/double-read: start, clock_reference_refused. Actual reported low
frequency3375000; compiled comparison incorrectly3375300. No video mode change
or CR03 probe reached. No native/full mode/Windows proof.

Root cause: broad750->753 namespace replacement also changed literal3375000.
The review repeated that replacement in its expected source and missed it.
138 probe cases do not exercise main's clock gate. Build/link checks accurately
matched the erroneous main. Audit001 failed required seven-phase sequence;
refusal-audit001 separately verifies the retained refusal and compiled constant.
The initial hypothesis of an unlogged high32-bit frequency was not established;
actual object disassembly identifies the wrong comparison constant instead.

All failures retained; no repeated launch, no hook, no owned process/VM. Console
at authenticatedUnleashX. Fresh754 must use token-aware namespace replacement,
restore exact3375000, log both halves and validate main's actual clock-gate code.

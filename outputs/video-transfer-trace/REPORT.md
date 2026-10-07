# Closed partial transfer trace

trace001 is CLOSED. Route capture failed E14 after the two small samples, with
26 events and10 paired calls. Exact failing read address was not logged, so no
specific page or cause is established. All breakpoints were removed, Windows
resumed, and the helper completed54 cases/162pixel stages with normal restart.
Cold allocation324dirs6755files325clusters, five hives/protected binaries,
pagefile/configuration and strict event checks pass. Those gates do not waive
the incomplete four-sample trace. Ordinary qualification is false.

The two complete samples follow BitBlt -> NtGdiBitBlt -> EngCopyBits before
returning success; GdiFlush -> NtGdiFlush follows in its own bracket. The screen
surface is a1024x57632-bit engine bitmap with4096-byte stride; upload source
is80x80 with320-byte stride. No drawing fault was observed. The failure was in
the host observer's read. See trace001/trace.json, audit.json and closure.json.

The new observer kit preserves exact failed-read context and validates module
headers once per fixed process lifetime while still requiring every observed
code site's resident bytes. Header eviction is a hypothesis for this first E14,
not its proven cause. No guest page-in, register patch or driver change is used.

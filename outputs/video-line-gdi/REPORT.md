# RAM0110 broader ordinary regression passes

candidate001 is CLOSED and strict ordinary emulator qualification passed. All26
real GDI cases matched both their live independent DIB references and the pinned
RAM0109 cold reference files: 2,555,904 RGB pixels with no mismatches. The sequence
included78 authored cursor phases and successful CDS_TEST/CDS_RESET at the current
1024x576x32 mode between cases12 and13. Geometry and revision110 remained correct.

Observed callbacks: BitBlt10,CopyBits247,TextOut2,StrokePath4,LineTo1,
StretchBltROP3,PlgBlt2,AlphaBlend2,GradientFill2,TransparentBlt1.
FillPath,StrokeAndFillPath,Paint and StretchBlt hooks were not observed and remain
unqualified as distinct callbacks; the corresponding GDI requests may be handled
through other observed paths. Cursor phase checks are guest observations, not an
independent raw cursor-pixel capture in this run. API reset success is not new
surface-lifetime tracing or proof of a recreated primary.

Normal shutdown and dashboard return were observed. Full allocation is clean:
326 directories,6786 files,327 directory clusters,zero errors/orphans. Five hives
parse structurally; protected and installed payloads,startup,96MiB pagefile mapping
and expected inherited configuration are unchanged. No warning/error/application
event deltas; prior event history is preserved. Gates were not relaxed.

The exact same reviewed91335-byte RAM0110 binary used in the matched line runs is
installed. Driver SHA256:
a1d5cf1eea27729a23c06e177f89f862eedcff0a1d0aa002815f4456279b4e98.
There is no debugger,no device policy change and no physical access. The historical
RAM0109 cold references are pinned in reference-pins.json and verified before the
run. oracle-tests.json uses explicitly retagged earlier log data for host protocol
tests; it is not new guest evidence. Actual guest results are in candidate001.

Preparation47550,runner79660,supervisor16014 and audit63330 are CLOSED. Accepted
2026-10-08T03:36:49.377433UTC; returned03:38:18.898910UTC. Initial local FTP
connection retries occurred before the single accepted launch; no duplicate launch.
Never relaunch or recollect this case. No FPS,physical scanout,additional mode or
hardware qualification claim. Read ../video-line-upload/NEXT.md for continuation.

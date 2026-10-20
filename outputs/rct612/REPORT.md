# PC612: saved-park graphics trace passed

PC612 completed a fresh, instrumented Windows 2000 RCT Deluxe run. After a deliberate
camera move, loading the retained PC593 save restored all 165600 checked scenery
pixels exactly to the reference and held them unchanged ten seconds later. All
nine private captures were visually reviewed. This is PC evidence; the existing
user-confirmed physical Xbox save/load result remains separate and accepted.

## Observed graphics path

The recorder completed 571 paired calls/returns, with no pending calls. It sampled
32 RCT StretchDIBits calls before the saved-park phase and 32 in that phase. The
headers describe a 1024 by 768 top-down, 8-bit BI_RGB DIB, stride 1024 bytes and
extent 786432 bytes. Each sampled bits pointer links to successful DIB creation.
The 640 by 480 game view includes full-view and narrower-region presentation calls;
64 sampled calls must not be interpreted as 64 frames. DirectDraw creation and
release were also observed; they do not establish hardware acceleration.

The exact PC610 lifetime-qualified observer was inherited. Six mutations of the
actual game lifetime records and ten trace/phase/header mutations were rejected.
The source, binary/import, media, tool-copy, scene-negative, lifetime-inheritance,
retry-inheritance and independent layout checks passed. The copied closure helper
prints an old609 label; its actual paths and final001.json belong to612. Historical
helper labels are not alternate runtime identities.

## Execution and cleanup

One fresh immutable404 child ran from 2026-10-20 16:28:28UTC to16:36:21UTC. One
runner launch followed verified display setup and ejected media. Exit0 accompanied
one new EventLog6006 and normal shutdown, with no host quit, deadline or space stop.
The cached cold audit contains7005 files/315 directories, five clean hives with raw
value agreement, restored temporary registry, unchanged save/tools/OS/seed and the
recorded allowed CSS0.DAT/Game.cfg changes. All owned612 processes have exited.
An automatic screenshot raced process exit and failed with FileNotFoundError;
that error is preserved in ntfs-phase1.json/final001.json, not hidden or interpreted
as game failure. No runtime was reopened or recollected.

611 remains a separate failed host-space attempt.612 changed capacity admission to
22GiB with a2GiB projected allocation allowance, retaining the20GiB reserve. The
lossless archives of closed602/606/608/609 remain mapped in ../rct611/archive001.json;
2717122560 source bytes were recovered from host C without discarding their bytes.

## Scope and next work

CLOSED PASS: saved-scene bounded graphics tracing and cleanup. No timings, FPS,
complete frame count, palette/accessibility proof, Xbox acceleration or game CPU
bottleneck is established. Next compare fresh uninstrumented game costs with the
observer using independently qualified clocks and the same saved scene. Do not
optimize a driver or infer GPU support from this result.

No physical access this turn. Xbox last at dashboard, no owned hook;596 SOFTWARE
cleanup remains cold-only. Protected720p, ordinary launcher, accepted saves and
transfer ZIPs remain unchanged; ZIPs exclude RCT. Other-console tests, sound,
physical fullscreen/input follow-up, boot intermittency and1080i remain deferred.
Private captures, game/OS assets and hives stay outside the public repository.

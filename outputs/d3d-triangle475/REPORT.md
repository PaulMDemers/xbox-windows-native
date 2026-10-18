# 475: physical boot attempt closed without a rendering result

One launch was sent at 02:56:05 UTC on 2026-10-18. Dashboard FTP returned by
02:56:30 UTC. The 176-byte preparation report proves the payload and high/low
loader copies at phase 6. It does not prove paging transition or Windows entry.
No refusal record, Windows result directory, sample receipt or new Windows event
was produced. All five hives, both event logs and the video trace remained exact.
The root cause of the early return remains unresolved.

The temporary startup hook was removed first during collection. The original
launcher, normal startup, 720p protected code and staged payloads were unchanged.
Five cold hives parsed clean with raw-value agreement; no new event records or
normal-shutdown count change. Console C was untouched. This selected audit is
not a full FATX allocation scan and does not qualify Windows boot or D3D.
All owned subprocesses are closed. Never relaunch/recollect this case.

The new diagnostic was a namespace-only child of qualified471; its Windows
payload is byte-identical. The triangle executable is byte-identical to PC474.
Host001 caught stale numeric X473/R473 tag expectations in the harness/decoders
while the actual binary correctly contained X475/R475. Preserve host001 and its
sources. Host002 corrected those constants and passed 104 modeled-kernel wrapper
cases; 171 complete records decoded and 37 truncated records rejected. The
binary did not change. Eight actual dispatcher paths passed with modeled FTP.

[Cold review](cold-review001.json), [closure](final-review.json),
[host failure](host-failure001.json), [package](package001.json).
A distinct476 attempt is permitted; later success must not rewrite this failure
or be described as a boot reliability fix.

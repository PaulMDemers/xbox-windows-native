# RAM-primary0108 ordinary emulator pair passes

Both fresh ordinary runs completed54drawing cases and162exact pixel stages,
normal shutdown/dashboard, full allocation325directories6759files326directory
clusters with no errors or orphans, five structural hives and protected/payload
hashes. No new warning/error/application events. Configuration and96MiB pagefile
remain as prepared. Neither run had breakpoints or debugger pauses.

The candidate additionally passed54 full-visible RGB self-comparisons between
its RAM image and the permanentUC framebuffer. This is useful internal evidence,
not independent scanout proof. The following callbacks were actually observed:

| Callback | Calls |
| --- | ---: |
| BitBlt | 11303 |
| CopyBits | 48483 |
| TextOut | 65 |
| StretchBltROP | 4 |
| AlphaBlend | 2 |
| GradientFill | 11 |
| TransparentBlt | 1 |

StrokePath, FillPath, StrokeAndFillPath, LineTo, Paint, StretchBlt and PlgBlt
had zero calls. Incidental desktop callback activity is not a pixel oracle for
those operations. Candidate counted30983uploads/769149104bytes. There is no
physical speed claim; full-clip fallbacks may be slower.

The unchanged direct0107 control and RAM0108 candidate have identical payloads
except their expected-driver marker and exactly two bound display selector values
in SYSTEM. Other nodes/values and Microsoft framebuf bytes were preserved. Both
recorded shared-pointer acquisition SUCCESS atFCED6000→03C00000,44records0drops.
All prior physical/release/crash evidence remains unchanged and distinct.

Fresh reconstruction tree0cb24809fa673421024b4a409d7a9fc08d40d8d0 produces
xwnram.dll SHA25651d98cf9ee2d2f42c360d96152877491b32773471ef8a0680d40264b49f6efc5.
The actual source passed46host lifecycle/upload/substitution cases plus65,536
ROP4 dependency truth tables, ASan/UBSan/leak detection. Imports match the owned
Windows2000 binaries. Draft001 and the host shim assertion failure are retained.

Control launch22:04:47UTC; candidate22:07:24UTC, returned22:09:13UTC. Both are
CLOSED, audited and immutable; never relaunch or recollect them. pair-review.json
pins the evidence. One HMP screendump request returned unknown-command; a later
non-pausing framebuffer-copy attempt was refused because candidate had already
closed. Neither produced an image, pause, breakpoint or guest write. Do not claim
a visual capture from these attempts.

Independent video-ram-scanout3 subsequently passed twelve physical snapshots:
1,794,048pixels,267runtime pins including the complete11940byte display .text,
full teardown and all cold gates. It is a separate debugger diagnostic. The two
earlier observer failures remain preserved and failed. verify-evidence.py checks
all five closed disks, frozen source snapshots and unchanged backing chains.
Broader callback/ownership/cursor/mode/crash qualification is still required
before any hardware promotion; see NEXT.md.

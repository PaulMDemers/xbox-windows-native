# RAM0112 reduces traffic in native window movement and repaint

Both matched ordinary emulator runs pass. Eighteen native child-window moves and
18 forced repaints per driver each compare3,538,944 live pixels. All18 reference
images and36 actual readbacks per run also pass independent cold composition.
The guest-generated font bitmap is identical across runs and passes its separate
color/bounds/nontext checks. Same immutable parent,compiled probe138,paint counts,
callback counts,settings and protected binaries; only RAM0110 vs RAM0112 differs.

| Measured interval | RAM0110 bytes | RAM0112 bytes | Reduction |
| --- | ---: | ---: | ---: |
| 18 native moves | 1,099,128 | 1,047,360 | 4.71% |
| 18 full repaints | 8,711,232 | 7,186,368 | 17.50% |

Upload calls increase87 to117 during movement and72 to180 during repaint.
Callback totals are identical:18 BitBlt,117 CopyBits,27 TextOut. All counter quiet
checks pass. Pair verifier rejects6 altered evidence records and4 malformed live
protocols. Geometry model independently predicts BOTH old bounding-box bytes and
new visible-region bytes for all18 full repaints; altered byte count rejected.
For this scene no extra full-repaint gap copying remains beyond the declared
visible bitmap/fill/text-bound operations. This is not a claim about every hook.

Measured GetTickCount medians are7.5/15ms for old/new movement and15/15ms for repaint.
They are NOT qualified speed comparisons:15ms clock granularity,shared functional
resource and overlapping host preparation/audit activity. More rectangles mean
more copy calls,so reduced bytes alone cannot establish lower latency or physical
FPS. The next discriminator is area versus rectangle-count/transfer cost.

The real scene is a128x80 bitmap/text child moving behind a96x144 fixed child,
six positions repeated3times. Pixel ROI is384x256 on1024x576. Position4's mover
extends20rows below the ROI but remains onscreen; traffic model includes those
bytes. Cursor positions are exercised during moves,then hidden for readback;
independent raw cursor pixels and whole-screen pixels are not newly qualified.

Both normalshutdown/dashboard,zero new warning/error/application events,cleanfull
allocation (327directories,328directoryclusters;6816control/6817candidatefiles),
zero allocationerrors/orphans,5structuralhives,protected/payload hashes,startup,
pagefile and inherited configuration checks pass. Native reset/restart is ordinary,
no debugger,register edits or physical access. RAM0112 binary unchanged:
ba6e37ddb2bdaad05cc12585fe9c986bdb5203c94101443500ebf1c547c81da8.
Inherited configuration text still contains older108/109 captions; actual payload
hashes and guest revisions establish110/112. Synthetic null/unsupported-device
policy remains emulator-only and unchanged.

All sessions CLOSED. Control prepare94574/runner37151/supervisor21089/audit83378;
candidate prepare39514/runner98227/supervisor61525/audit72060. Actual timestamps,
source snapshots,hashes and closures are in each attempt directory. No repeat.

Preserved failures: video-window-move/control001 and video-window-observe/control001
both failed pixel gates because Getting Started covered x270..383/y100..255.
The second run saved pixels proving this; outside that rectangle pixels match.
This kit raises only its owned parent before measured intervals. It does not
close or cancel another app/dialog or alter startup/device policy. Neither old
failure was converted to PASS. Initial move candidate remains prepared but NEVER
launched. Host indentation-build failure and prelaunch cursor-stats correction
are retained; no failed/preliminary binary was launched.

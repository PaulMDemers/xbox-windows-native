"""Record completed601/602 state without changing frozen experiment files."""
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
header='''# PC602 closed: actual RCT windowed GDI calls observed

PC601 original graphics control passed106 paired calls, exact GDI pixels and
returned DirectDraw/surface checks. Its compile failure, incorrect copied6016
audit predicate and corrected cached-raw6006 review are preserved explicitly.
PC602 then reached title/Forest Frontiers with393 pairs (272 RCT/121 other).
RCT successfully created a DIB, made32 sampled StretchDIBits calls with its same
pixel pointer, and created/released DirectDraw. No call to the armed cooperative
level or surface creation methods was observed; other methods are outside scope.
26 BitBlt calls came from other module callers. StretchDIBits hit its32-entry cap;
this early sample is not frames, park-phase coverage, cost or Xbox acceleration.

Both runs are CLOSED, all owned VM/build/cold processes exited.602 normal restart,
one new6006, exact tools/OS bytes,502 prelaunch assets, five clean hives with raw
agreement and temporary registry removal passed. Five private game images were
inspected. DRM typed decode limitation and input/setup failures remain recorded.
Do not reopen/recollect/parent closed runtimes. Read outputs/rct602/NEXT001.md.

Next: qualify the exact retained593 saved scene on a fresh pristine fixture;
qualify bounded DIB header reads in an original control; then matched scene/cost
and observer-overhead measurements before any optimization or Xbox promotion.
No game FPS, pristine game performance control or physical acceleration claim.

Xbox untouched this turn; last dashboard, no owned hook.596 offline SOFTWARE
cleanup remains cold-only. Launcher/720p/saves/transfer ZIPs unchanged; RCT still
excluded. Other consoles/sound/fullscreen/boot intermittency/1080i deferred.
Automation remains paused and old overnight cutoffs are inactive for this request.

'''
for name in ['CONTINUATION.md','STATUS.md']:
 p=W/'outputs/engineering-notes'/name
 old=p.read_text(encoding='utf-8')
 marker='# PC600 closed: returned-value transport qualified on the original control'
 assert marker in old
 p.write_text(header+old[old.index(marker):],encoding='utf-8',newline='\n')
print('Continuation and status updated to closed602')

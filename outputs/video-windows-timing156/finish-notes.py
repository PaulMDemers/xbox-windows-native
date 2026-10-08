"""Close continuation/status using explicit UTF-8; no guest action or stage replay."""
import json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
note=ws/'outputs/engineering-notes/CONTINUATION.md';status=note.parent/'STATUS.md'
old=note.read_text(encoding='utf-8');previous=status.read_text(encoding='utf-8')
assert old.startswith('# Windows156 isolated timing ACTIVE')
assert json.loads((k/'series-closure.json').read_text())['timing_qualified']
history=k/'running-note-history.md';assert not history.exists();split=old.index('# Windows155 ordinary')
history.write_text(old[:split],encoding='utf-8')
header='''# Windows156 isolated timing PASS; all CLOSED; offline bundle158 prepared

Read outputs/video-windows-timing156/REPORT.md,NEXT.md,timing-comparison.json,
verification.json,series-closure.json,owned-sessions.json and actual case records.
Same RAM0112/compiled141/immutable parent; ONLY unchanged xemu build003 differs.
Both fixtures/preflights/config/maps complete before runtime,actual build+xemu
lock conflicts before/after,no screenshot/state/debugger/build/prep/audit during
runs. Cold collection only after BOTH guests/leases close. QPC/coarse/quiet gates
PASS. Bottom192x96 primary median4387.35 to98.20us,44.678x; equal-area top/top-offset
~0.10ms. Other affected layouts13.670..39.439x; unaffected/memory paths near1x.
One control-first pair/3rotated reps,cooperative isolation: emulator microbenchmark
latency ONLY,no physicalFPS or hardware guest-driver speed claim.

Both ordinary strictPASS45cases/13271040pixels/45refs+45RGBreadbacks,normalshutdown1,
327dirs6851files328dirclusters,zeroerrors/orphans,5hives/protected/startup/config/maps,
no warning/error/application deltas. RAM0112 movement/repaint bytes4.71%/17.50% lower
in earlier real-window138; hardware latency remains unmeasured. Extra modes,
including1080i,and WC/GPU-transfer acceleration remain separate implementation work.

ALL sessions CLOSED: preparations73970/32755,control6648/61626,candidate63186/12166,
cold58914/63155,Windows verifier80410 and candidate/pair/timing/closer88005,test32883.
Actual timestamps,source snapshots/36pins/private raw hashes preserved; never
relaunch/recollect.754geometry/8protocol/36RGB/7lifetime/24timing host checks PASS.
Borrowed source restored. Original155 timing exclusions and all failures retained.
First notes update used Windows locale decoding and failed before any notes write;
UTF-8 retry changes documentation only,not runtime evidence or closed stages.

Offline outputs/video-hardware-candidate158/package-review.json PASS for THREE
exact emulator-tested display files plus readback-verified rollback private ZIPs.
Attempt157 preserves guard failure:0.1.0 miniport is older than physicalvideo0093.
158 uses physical-qualified0093 artifact matching last installed-state hash;
Microsoftframebuf matches too. Historicalbootvid has no latest physical hash:
require fresh read-only physical check and CURRENT rollback before deployment.
deployment_readyFALSE/physical_qualifiedFALSE: exact real physical binding/settings/
geometry review,NEW emulator reconstruction with only display chain/binding changed,
strictcoldgates,then bounded hardware trial. Do not copy emulator device-policy hive.
This turn emulator/offlineONLY,no physicalFTP/deploy/test. Physical0101/video0093,
0088rollback,immutable0.1.0,128GiBend-to-enddump/recovery,unresolved111nonASCIIhardware
anomaly unchanged.20GiBguard unchanged; C~24.4GB after runs. Upstream xemu uses
unchangedbuild003 and native145..154 plus ordinary155/156,explicit race/sample limits.

'''
note.write_text(header+old[split:],encoding='utf-8')
body=previous.split('\n',1)[1]
status.write_text('''# Native Xbox Windows 2000 status — 8 October 2026

2026-10-08: the reviewed xemu CPU-write surface eviction now has a qualified
isolated ordinary Windows timing comparison,with identical guest RAM0112/probe141.
Affected192x96 bottom draw median4.387ms to0.098ms (44.678x),while equal-area top
rectangles and memory-only paths stay near their former costs. Both runs pass
strict pixel/event/cold-integrity gates. This is an emulator microbenchmark gain,
not physical FPS or a guest-driver latency comparison. See
[Windows timing report](../video-windows-timing156/REPORT.md).

The guest display improvement is already written and functionally validated:
RAM0112 cuts actual window-movement copy bytes4.71% and repaint bytes17.50% with
exact pixels. Physical latency gain remains unmeasured. An offline three-file
shared-UC provider/miniport/display candidate and qualified0093/historical rollback
are bundled/readback-verified; deployment_ready remains FALSE pending fresh physical
state/binding/rollback review and a display-only emulator reconstruction. The older
0.1.0 miniport mismatch was caught/preserved,then the correct0093 artifact used.
No physical files/settings were changed. See
[candidate bundle158](../video-hardware-candidate158/README.md).

Additional video modes including1080i and WC/GPU-transfer acceleration remain
implementation work with separate geometry/encoder/ownership/physical validation.
The128GiB dump/recovery emulator closure remains complete. Physical0101/video0093,
0088rollback,immutable0.1.0 and unresolved physical SetupAPI corruption remain
explicitly distinct from the newer emulator stack.
'''+body,encoding='utf-8')
print('UTF-8 continuation/status updated; active note preserved')

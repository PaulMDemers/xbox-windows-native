"""Record349 closed failure and precise next discriminator; retain history."""
from pathlib import Path
K = Path(__file__).resolve().parent
P = K.parent / 'engineering-notes/CONTINUATION.md'
old = P.read_text(encoding='utf-8')
assert not old.startswith('#348/349 CLOSED')
prefix = '''#348/349 CLOSED: primary-copy pixels PASS; largest fast-byte coverage FAIL

Read primary-copy348 REPORT/NEXT/build001/source-review001/binary-review001/host002 and primary-runtime349 REPORT/NEXT/coverage-diagnosis001/pair-results/closeout002. New bounded same-primary32bpp overlap path targets RAM engine copy only; upload/mapping/cache/lifetime/other DDIs unchanged. Matched RosBE tree f9adc6373a147add130c8e619bd88ff726d80738 PRIMARY_COPY OFF/ON, profilingON both. Control162143cf... candidatef5329b0f...; probe60aa2545.... Host00253291checks/13299pixelcases per mode; weaker periodic host001 preserved. Source/binary/import/residency reviews PASS. No physical access or promotion.

349 fresh never-executed339 seed, control16:57:20->17:02:56UTC and candidate17:07:37->17:13:47UTC Oct13. Both CLOSED:5drawing samples/6audio phases/normalshutdown1/orderlyhostexit0, cold341dirs6809files358clusters0errors/orphans,5hives/protected/startup/policy/history pass. Smaller256x128/640x360 overlaps fully fast; largest960x540 has8fast+5fallback calls/op,2067564fastbytes versus2073600requested, exact6036deficit inall10intervals. Independent pixels pass; incompletecoverage is NOTcorruption. ScopedmatchedFALSE, strictFALSEFt49HarddiskVolume1; no gatewaiver or speedclaim. Apparent timing difference largely unchangedupload, no causalhardware benefit established.

Original344adjacency parser didnot accept new348packets; originalaudit/closure remainunchanged. Separate protocol decoder validates66lineblock placement/fullcoverage then unchanged344projection;1051actual mutations and5originalgate controls. Control correctedscopedTRUE; candidateFALSE actualcoverage. Supplemental pins unchanged. Originalfinal-review.py failed candidate sample0; nooutput. closeout002 verifies failed evidence without requiringPASS:178frozeninputs/case,30privatecaptures/case,fixture/driver/probe hashes and22hostprivatefiles. Never rerun/recollect either consumedcase; no runtimeparenting.

NEXT NEW bounded actual-call trace of existing348candidate withfreshunusedfixture: pair actual XwnTryPrimaryCopy entry/return, module/code/operands/rectangles/clip/translation/rejectionconditions. Account8fast/5fallback and6036bytes; don't infercursor/window cause fromcounts, don't lowergate. Boundevents/thread-framepairs, fullbreakpoint/modecleanup andnormalcoldaudit. No newhelperpatch untilactualcalls explaincoverage. No hardwaretest queued. PhysicalE remains originalb23b94ac.../normalstartup, originalFrollback/immutabletags retained; XboxC staysoutside all toolaccess. PhysicalSrv2013/Ft49 separate; automationPAUSED/demo251ticketretained,keyboardunplugged/hardwareauthorization standing.

ALLowned sessions CLOSED:348build5150;349prepare32467/35231,control30118/supervisor63639/audit93087,candidate39448/supervisor45909/audit49443. No xemu process atcloseout.20GiBguard unchanged; C~74.4GB/E~29.7GB, no cleanup/backingmoves. Initial WSLstagingPermissionError beforemutation preserved. This source/report closeout is being committed; verifyHEAD/origin beforework. Existinghistoricaluntracked files untouched.

# Historical continuation below
'''
P.write_text(prefix + old, encoding='utf-8')
print('Recorded closed349 result and next evidence requirement')

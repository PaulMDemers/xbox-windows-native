"""Prepend current status without rewriting historical continuation bytes."""
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
header='''# Current: PC480 depth PASS; Xbox481/482 incomplete launches closed, retries stopped

Read outputs/d3d-depth480,481,482 REPORT/DESIGN/NEXT/final-review and482
closed-handoff-review001.json. New work pending commit/push; previous pushed
bd12a2df. No test queued; Xbox at UnleashX. Both temporary hooks removed FIRST;
normal6240 launcher/da47 startup/protected720p unchanged. ConsoleC untouched.
Never relaunch/recollect/parent480/481/482. Next unused experiment483.
All owned sessions CLOSED: host oracle63411, PC runtime75092, cold82021/95317,
actual controls15908, physical481 stage82551/observer31731,482 stage23089/
observer72887/collection4790. Build/import/module/closeout calls synchronous.

New original MIT depth.c/cmd, graphics_depth.py/tests; public build --sample depth.
Sample20,283B SHA00f6487c474420a2b84d60381d2915621c047e33eb2c3b27adc2c2ecd99c9d2f,
source995771930a2e8df49ffd368b700993049599dcb83d9b8ccaef31ca52f964da37.
Pinned RosBE, no warnings/import mismatches; sharedSDK/driver unchanged.
Rung08b: actual RGB device enumerates two depth formats, selects pureD16, owned
64x64system-memory Zsurface attached/queried before device creation. LESS+writes,
near/far same projection atZ.25/.75; near wins both orders, disabledZ last wins,
Zclear0 rejectsboth. Five captures/process,10captures163840B. Each561 safeinterior,
2199exterior,1336edge-zone prescribedpalette only; exactedges/Xbyte/depthprecision/
stencil/presentation/performance/GPU/games unqualified. No visible test pattern.
3synthetic tests20480pixelnegatives; actual PC513metadata+20480pixel changes/case,
41986total rejected. All originals exact; complete HRESULT/attachment/cleanup.

480 fresh404 reusable NTFSseed child, not477or479runtimeparent. Exact1474560B
FAT12 reviewed twice;39 host negatives preserve477malformedfloppyfailure.
Two default/HEL process0, normalrestart QEMUexit0 at03:52:13UTC2026-10-18,
nohostquit/kill/deadline. Cold6491files309dirs;5hivesclean/rawagreement,
source/floppy/protectedOSbinariesexact.31independentNTFS-3Gfilesagree,cleanunmount;
11actualmodule/PEimage identities each;149frozen inputs archived. Selected new
systemevents6006/6009/6005 only; NOT fullNTFSallocation/whole-systemqualification.
InheritedSOFTWARE DRMtype1004 limitation remains. Private480 underWSLhome/paul.

481 single accepted03:56:26UTC ->dash03:56:50;482 accepted03:59:58 ->04:00:22.
Neither produced Windowsresultnamespace/receipts/refusal/newWindows events or
normalshutdowncountdelta. Phase6 primary176B proves preparation ONLY; Windows
entry/pagingtransition unknown. All5hives/2eventlogs/videotrace BEFORE/AFTEREXACT,
hiveclean/header/rawagreement. Selectedcoldaudit only, nofullFATXscan (latest463).
Each33package inputs archived C:/xwn481or482/frozen001;allprivatecapturesrehashed;
176actualtruncationsreject. Existing successful478 does not requalify failures.
Each new471namespace wrapper:104hostMODELEDkernel paths,8actualdispatcherMODELED
FTPpaths,171complete37truncatedrecords,imports24/26; originalWindowspayloadexact.
481bootc51cdea443f4d41138ff51bb8d81070b3465f2f76a13ac36be3d68e6eac8651b;
482boot13a6dac524242722c370227a7a3ed9e49037d4822103ed749a6dafc8f7c359db.

READ-ONLY comparison: successful478 and failed481/482 all44preparationwords are
identical after removing ONLY magic/cookies atwords0,3,42. Exact482assembly/symbols
pinned in closed-handoff-review001. Gap covers final trailerflush/NtClose,
post-I/O payload/loader rechecks, secondboundedSMBusmarker, restoredjump,
paging-off/GDT/segmenttransition/payloadentry. Missingrefusal provesnoneofthose.
No newbootfix/diagnostic installed. STOP identical physical retries. Next review
bounded owned observation of firstunprovedboundary; preserve registers/flags,
bothcopies and nofileI/O afterprivilegedtransition. Host-test failures before
newbuild/boot. Physicaldepth requires lateractualfixedpixels/modules/restart.
Alpha blending is separatefuture08c; no speculation/refcount/bypass changes.

Public build/run/retrieve/check instructions and sourceindex updated. PC/runtime
artifacts and Windowsbinaries remain private. Physicalbootintermittency, Ft49,
priorrundll32shutdownpopups remain unresolved; noevent/service suppression.
All priorfailed475/477, frozeninputs, recovery256/0.1.0/0088/rollback preserved.
720pbaseline,1080iparityinvestigation paused, WMPdemo unchanged. No hardwareGPU,
PCI/USB/audio/prototype work. No games qualified. No new offload/backing moves;
C last25,168,506,880B free;E21,499,871,232B verytight. Recheck20GiBprojectedguard.
Historicaluntrackedfiles untouched. Explicitnewkit-textattributes and byte-exact
staging required; final repositorycheck and commit/push follow.

--- Previous continuation follows unchanged ---

'''
p=W/'outputs/engineering-notes/CONTINUATION.md';p.write_bytes(header.encode()+p.read_bytes())
status='''# Latest: depth passes on PC; two Xbox launches closed without receipts

The new D3D7 software depth sample passes both draw orders, depth-disabled and
clear-zero controls on a fresh Windows2000 PC fixture. Its source, build/run
instructions, independent image checker and negative tests are in the repo.

Two distinct Xbox attempts returned to UnleashX without Windows test receipts.
Both are closed, hooks removed and baseline files unchanged. No physical depth
result or boot-stability claim. The preparation trace is identical to the earlier
successful texture run except test IDs; it cannot identify the failing boundary.
Further identical retries stopped. Next: a bounded handoff observation beyond
preparation, then physical depth validation. Alpha blending follows separately.

No GPU acceleration, game compatibility or overall system qualification claim.
Ftdisk49, prior shutdown popups, boot intermittency and1080i remain open.
Console is at the dashboard with no test queued. Reports: d3d-depth480/481/482.

--- Previous status follows unchanged ---

'''
p=W/'outputs/engineering-notes/STATUS.md';p.write_bytes(status.encode()+p.read_bytes())

from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'engineering-notes/CONTINUATION.md';old=P.read_text(encoding='utf-8');assert not old.startswith('#350 CLOSED')
P.write_text('''#350 CLOSED:6036-byte deficit explained by actual bitmap fallbacks

Read primary-trace350 REPORT/NEXT/final-review/candidate001 trace-verification002,functional-scope001,audit/closure. One launch17:44:49->17:50:30UTC Oct13, existing348candidate f5329b0f.../probe60aa2545... unchanged, freshNEVER-executed339 seed. Two actual960x540 operations captured: each8primary fastcalls2067564bytes +3bitmap-to-primary6036bytes +2primary-to-bitmap2688bytes. Actualownerreturns0 onnonprimaryside, two31x27 bottom-up memorybitmaps,stride-124. Eightfast+threeengineoutput rectangles tilewhole960x540 exactly/nooverlap. CursorpurposeNOTproved/NOTrequired; legitimateineligibility proved.171residentpins/actualkernelIDT/process/module/pairedthread-frame evidence;549actualmutationsreject. Nohelperpatch orhardwareaccess.

Original349/350 full-requested-fast-byte gate remainsFAILED; doNOTretroactivelyrequalify. NEWeligible-plan-byte contractNEXT: saturatingeligiblebytes OFF/ON, ONfastbytes==eligibleplanbytes andfast+empty==eligiblecalls, OFFfastzero/eligiblepositive. Keepold348packetunchanged,newversion; no arbitrarybitmapfastpath orpercentagewaiver. Hosttestnewaccounting,compilematchedexact348children andfreshordinarypair beforephysicalpair. Driverplanner/upload/cache/mapping/lifetime unchanged. No performanceclaimfromdebugger.

350 fullfunctional pixel/copy/DIB/text/window scopePASS,150largepixelchecks/75legacyintervals,6captured audiophases/API/identity/joins,normalshutdown1/orderlyhostexit0. Cold341dirs6809files358clusters0errors/orphans,5hives/protected/startup/policy/historyPASS. StrictFALSEFt49HarddiskVolume1; combinedFALSEoriginalcoverage.189frozeninputs/30captures/full5providerbinaries rehashed. Allbreakpointsremoved,mode0verified,guestresumed;allowned sessionsCLOSED54049/63397/40098/24911/43641. Neverrelaunch/recollect/parentcase.

Preserve sites001provideromission/sites002, firstinlinePSextensionfailure(nofile), freeze.py missinggdi32 KeyError beforelaunch/freeze002 actualcoldproviderpins. Firstanalysis incorrectlyassumedpositive124stride/onebitmap; analysis002 matchesrawnegative124/twoidentities, originalchecker/failure receiptimmutable. No capturedbytes/oraclechanged. No xemu leftoncloseout. PhysicalEoriginalb23b94ac...normalstartup,Frollback/tagsunchanged,Cconsoleuntouched,nohardwarequeued,automationPAUSED/demo251ticketretained; keyboard/hardwareauthorizationstanding. C~74GB/E~29GB,20GiBguard,nooffload/backingmoves. Publicationinthiscommit; verifyHEAD/origin beforework. Historicaluntrackedfilesuntouched.

# Historical continuation below
'''+old,encoding='utf-8')

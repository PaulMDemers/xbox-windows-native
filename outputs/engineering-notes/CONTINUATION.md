# Matched HAL root dump-path comparison closed; later dump failure remains

2026-10-07 09:47UTC. ALL owned sessions CLOSED. Read outputs/hal-dump-path/REPORT.md,
NEXT.md,DESIGN.md,pair-review.json and actualrecords. Do not relaunch/recollect
control001 or candidate001. Previous pushed9b7ccad records completedlowertrace;
thisnew0102source/build/ordinarycomparison is readyfor reviewedcommit/push.

0102 adds independent bounded paging/dump counters, stop/remove protection and
not-disableable state; root remains fixedpowered/resident with no idle/parent
dependency. It does not fake lower completion or implement full dumpwriting.
Hostcountertest actualfunction passes400000concurrentpairs andboundary cases.
Matched freshbuildcontrol44a6d83116b3fc056c81159905f9c635bd1aebfda21a7da37cf7a4fc14826c45;
candidate7c6a3bfb9b6794c3b6fbce95fb76dc57d003843c19512b3ddb186604f668ed08.
Imports/residentdispatch/checksums verified, sameflags, only0102source difference.

Bothordinaryruns792appends/32shrinks/132reopens/11exactcoldfiles; normalshutdown/
dashboard,fullallocation323dirs6765files324clusters0errors/orphans,5hives/protected
hashes, HidServ4/0/0. ControlstrictFALSE49; candidatestrictFALSE44(error4)+49(error3).
Additional44 indicates laterfailure but NOT yetruntimeFSCTL/status proof. No
debugger/UI intervention. Frozeninputs/closeddisks/rawfiles/pair invariants pass.
Physical0101/video0093,0088rollback,immutable0.1.0 andinstalledHAL unchanged.

Next NEW bounded candidate diagnostic: paired IopConfigureCrashDump usage call,
IopCompleteDumpInitialization, actual reference/query/FSCTL inputs/output/status,
pending completion and callerbranch. Preserve pins/teardown/fullcoldaudits.
Never infer newFSCTLcause fromeventalone or patchspeculatively. No suppression or
silentgatewaivers. End-to-end controlleddump/recovery remains latergate. Original
physical111nonASCIIprefix/restart unresolved; interruptionmechanism separate.

Spaceguardblockedbuild001 beforecreation; oldPowerShellwrapper failedto propagate
Python exit, correctedretry. Fourclosedstandaloneoldruns036/041/042/043 copied/
hashverified toEwithjunctions preservingoldpaths. Manifesttask-storage-offload/
manifest-20261007.json. No backingchain moved. Candidatebuild002/controlbuild001
passedunchanged20GiBguard. Closedsessionslisted in hal-dump-path/NEXT.md. No
runningguest/build/observer. EmulatorONLYuntil13:00UTC; checktimefirst, atcutoff
cleanup/report/pauseautomation. No physicalFTP/deploy/test.

---

# Active matched HAL root dump-path experiment

2026-10-07 09:39UTC. Latest pushed9b7ccad closes dump-usage-trace. NEW uncommitted
outputs/hal-dump-path adds0102 bounded separate paging/dump counters and PnP
stop/remove/not-disableable protection. Root remains fixed powered/resident;
no fake lower completion or device policy change. Full dump support UNQUALIFIED.
Read DESIGN.md. Originalphysical111nonASCIIcorruption remains separate.

Candidate buildhal-dump-path-002 and matchedcontrolhal-dump-control-001 compiled
fresh with matchingpins/flags. Build001 was blocked beforecreation by20GiBspace
guard, retained in DESIGN; fourclosedstandaloneruns036/041/042/043 offloaded toE
with verifiedjunctions, manifestoutputs/task-storage-offload/manifest-20261007.json.
400000concurrent counterpairs andboundarytests passed; imports/residentfunctions
reviewed. PhysicalHAL/FATX0101/video0093 and0.1.0 untouched.

CURRENT owned: control001 runner85940, supervisor46209 launched09:38:28UTC;
candidate001 preparation9108 stillrunning. Controlprep88373/build26564/controlbuild
99884/offload57427/WSLread37398 closed. Do not duplicate launches. Aftercontrol
cleanup, cold audit/configuration/closure/evidence once; candidate preflight
requires closedcontrol workload+integrity. Candidate is notyetlaunched. Use
localhost4596 only with XWN_EMULATOR_FTP_USER/PASSWORD; neverphysicalFTP. Deadline
13:00UTC remains. Keepstrictgates; likely laterdumpinitialization issue is only
a staticlead untilactualruntime evidence. Alloldtracecases closed.

---

# Crash-dump rejection localized to the fixed-root HAL

2026-10-07 09:26UTC. ALL owned sessions CLOSED. Read dump-usage-trace/REPORT.md,
NEXT.md, trace-verification.json and hal-source-audit.json under outputs. Both
dispatch001/002 are closed and cold-audited; NEVER relaunch or recollect them.
Emulator-only authorization continues until13:00UTC. No physical FTP/deploy/test.

dispatch002 captured39events/13dispatchpairs/4IRPs/43residentpins. InitialIRP
goes FATX->Ftdisk->Disk->Diskperf->PartMgr->Disk->atapi; nested matching usage
IRPs go atapi->PCIIde->PCI->PCI_HAL. Firstcompletion is HAL+83d8 with inherited
STATUS_NOT_SUPPORTED. Exactbinary paging-only selector and0055source agree:
dump/hibernate were deliberately not implemented. Failure propagates to final
IopSynchronousCall. Ftdisk/FATX returnPENDING, not the origin of rejection.
No retrieval-pointer FSCTL reached. No asynchronous thread transition occurred
in this capture; four matching nested requests are not allocation-parent proof.
dispatch001 unpinnedDiskperf capture failure preserved, safely resumed.

Bothworkloads792appends/32shrinks/132reopens/11exactcoldfiles, normalshutdown/
dashboard,323dirs6765files324directoryclusters,0errors/orphans,5hives/protected
hashes. HidServ4/0/0; strictFALSEsoleFtdisk49. No driver/settings/policychanges.
All residentpins/frozeninputs/closeddisks replaychecked;5875repositoryfiles pass
payload/credentialchecks and102newkit stagedfiles preserveexactworkingbytes.

Next: review actual root HAL dump contract and reproducible build provenance;
NEW isolated genuine dump-path accounting/residency/PnP/power implementation
only if contract is satisfied. Do not just forceSUCCESS or suppressdumps/events.
Real dump-write/recovery validation required beforeclaimingcapability. Physical
0101/video0093,0088rollback,immutable0.1.0 unchanged. Original111nonASCIIphysical
corruption/restart remains unresolved and separate frominterruptionexperiment.
Inherited emulator syntheticnull/unsupporteddevicepolicy unchanged.

Closedrun sessions001 prep88284 runner71711 tracer6916 supervisor42911 audit54330;
002 prep49055 runner33212 tracer83531 supervisor29166 audit61427; evidence23117.
No runningguest/observer/build. Current findings readyfor privatecommit/push.

---

# Crash-dump usage request traced through FATX to Ftdisk

2026-10-07 08:58UTC. ALL owned sessions CLOSED, including evidence verification
43144. All five frozen-source/private-disk/raw-byte audits passed replay checks.
Read outputs/dump-config-trace/REPORT.md,NEXT.md and actual records. Emulator-only
until13:00UTC; check time before experiments; at cutoff cleanup/report/pause.
No physical FTP/deploy/test. Current work is not a new driver candidate.

New dump-config-trace serial002/003/004/005 captured4/20/23/26 resident-pinned
sites. Initial handle succeeds, disk queries and40-byte dump-pointer request
succeed, miniport dump driver loads. IopSynchronousCall's crash-dump usage
notification (major1b/minor16,InPath1,type3) returnsSTATUS_NOT_SUPPORTED. In005,
VfatPnp forwards the same request to Ftdisk and getsSTATUS_PENDING; ultimate
lower-driver status producer is unresolved. IopCompleteDumpInitialization and
its retrieval-pointer FSCTL are never reached. Do not patch that FSCTL or fake
usage success. The earlier static error-block assumption missed other incoming
branches. serial001 trace failed pairing and is retained; cleanup/resume passed.

All five diagnostic workloads completed792appends/32shrinks/132reopens/11exact
coldfiles, normalshutdown/dashboard, full allocation323dirs6765files324clusters,
0errors/orphans,5hives/protected hashes. Six storage binaries unchanged. Strict
FALSE soleFtdisk49 remains. HidServrunning4/0/0 and noSCM7000. No service/registry/
dump policy/driver changes. Debugger timing is not ordinary qualification.
Frozenpercase source/preflight, closure and private disk hashes retained.
Do not relaunch/recollect ANY completed case. Current kit launch IDs occupied.

Next: NEW bounded diagnostic observing this same IRP through Ftdisk/lower disk/
port dispatch and final completion before freeing, retaining pending/asynchronous
thread transitions, resident-code/binary/module identity and full teardown/cold
audit. Read NEXT.md before preparing. No speculative patches or silent event
gate waiver. Existing restored-HidServ ordinary pair is separate and also
strictFALSE49. Inherited emulator-only synthetic null-device/unsupported-device
policy preserved. Physical0101/video0093,0088rollback,immutable0.1.0 unchanged.
Original111nonASCII physical SetupAPI damage/firstrestart unresolved; intentional
111zero/109correct interruption mechanism and negative source search remain
separate. Source/evidence reviewed, checked and pushed as d198532. All5773 tracked files
passed repository payload checks; the index preserves exact diagnostic bytes.

Closed sessions: preparation58755/49232/70520/23805/97292; runners82475/49561/
97183/91135/76923; tracers31191/66641/50414/92354/91958; supervisors84231/31368/
62691/72576/28600; audits22760/11873/81865/93428/60615. serial003 premature audit
was blocked by cleanup guard before guestdisk access; completed once after exit.

---

# Restored missing emulator HID service; remaining event narrowed to dump init

2026-10-07 08:20UTC. ALL owned guests/supervisors/audits CLOSED. Pair comparison
86428 completed and pins passed; no owned process remains active. Emulator-only until
13:00UTC, check time; at cutoff cleanup/report/pause automation. No physical
FTP/deploy/test or driver/hive/device-policy change. Read baseline-hid-restore/
REPORT.md,NEXT.md and baseline-event-forensics/REPORT.md (under outputs).

Read-only exactcold registry/message analysis: automaticHidServ points to missing
hidserv.exe, SCM7000 %%2=file-not-found. Preserved0.1.0 system32/dllcache copies
identical19728bytes SHA031a1fb5ca4194284d6ecfbfe8afe63589700c1376873267f131ead06946dc6a.
New isolated baseline-hid-restore restores only this service executable plus
unique workload/status-query payloads. No settings/service-disable workaround.
Both serial001/flush001 now reportHIDSERV_START/END4,0,0 and noSCM7000. Both
pass792cycles/32shrinks/132reopens/11coldfiles, normalshutdown/dashboard,5hives,
protected/importedDLLhashes, fullallocation323dirs6765files324dirclusters0errors/
orphans. Concurrent799flushes,353append-overlaps,305dirty-overlaps,44rendezvous.
StrictFALSE soleFtdisk49 remains. All cases collectedONCE, never relaunch.
serial08:10:32->08:12:55UTC; flush08:15:35->08:17:58. Closedprep32329/32845;
serialrunner49325/supervisor47255/audit68697/config56932; flush4633/38870/99598.

Ftdisk49 exactmessage=pagefile crash-dump configuration failure, not delayedwrite.
C:\pagefile.sys96MiB exists, configured96/192; CrashDumpEnabled3. Presence/size
does not prove active paging/dump readiness. Pinned kernelstaticcandidate
IopConfigureCrashDump logs49(uniqueerror3) after IopCompleteDumpInitialization
negative return. Candidatefunction has handle reference/query/FSCTL0x9003b.
VFATsource lacksQUERY_RETRIEVAL dispatch but this branch would additionally log
44, absent in observed delta. Need actual runtimebranch/NTSTATUS beforepatching.
NEXT givesRVAs, thread/frame/pin/gap constraints for NEW diagnostic child; no
speculativeFSCTLhandler or CrashDumpEnabled suppression. Physical111nonASCII
corruption/firstrestart stillunresolved. Prior4be74ab pushed; currentkits/notes
await finalcheck/commit/push. Preservephysical0101/video0093,0088rollback/0.1.0.

# Bounded mapped-shrink/volume-flush pair complete

2026-10-07 08:02UTC. ALL owned sessions CLOSED. No guest/tracer/observer active.
Emulator-only until13:00UTC; check time before new work; at cutoff cleanup/report/
pause automation. No physical FTP/deploy/test or driver/hive/release change.
Read outputs/fatx-map-rendezvous/REPORT.md,comparison.json,NEXT.md. Serial and
concurrent each pass792 appends,32 queried allocation-size decreases,132 exact
reopens,11 final cold files, normal shutdown/dashboard. Full allocation323dirs/
6764files/324dirclusters/zeroerrors/orphans,5structural hives/protected hashespass.
Concurrent810 successful flushes,347 inside append epochs,331 in dirty mapped
epochs,44 bounded rendezvous, positive coverage every file-round, successfuljoin.
Strict qualifications remainFALSE exactlySCM7000 HID Input Service/Ftdisk49.
Neither original physical corruption nor a driver fix is established.

serial launch07:52:45 return07:55:02; flush launch07:56:39 return07:58:57UTC.
Closed serial72749/18673/27289; flush4280/39796/34783; comparison79466. All
source/fixture/parent/disk/rawcold pins verified. Never relaunch/recollect.
Previous truncateflush001 overlap failure and post-timeout snapshot remain
separate; closed/pushed32d92a8 with prefix-forensics. New rendezvouskit and notes
currently awaiting finalcheck/commit/push; no recovery snapshot/promotion.

NEXT identifies the exact recurring event sources from owned message resources
and cold hive/file state (shutdown-diagnostics/event-message.py). No event
suppression, service-disable workaround, policy change or speculative patch.
Only concrete evidence may justify a NEW isolated fixture. Original physical
nonASCII bytes/firstrestart unknown; normal/intentionalinterruption distinct.
Preserve physical0101/video0093,0088rollback,immutable0.1.0 and allfailures.

# Concurrent rendezvous run active; revised serial control closed

2026-10-07 07:57UTC. outputs/fatx-map-rendezvous/serial001 completed and cold
audited:792 appends,32 queried shrinks,132 reopens,11 exact files, normal shutdown
count1, allocation323dirs/6764files/324dirclusters/zeroerrors/orphans,5hives and
protected hashes pass. StrictFALSE exactSCM7000/Ftdisk49. Closed72749/18673/27289.
flush001 launched07:56:39.893962UTC ONCE, runner4280/supervisor39796 active.
Deadline about08:11:40UTC; runner20min cleanup~08:16UTC. Inspect actual launch.json.
If timeout, use kit capture-timeout.py/decode-timeout.py and framebuffer tool
BEFORE auto-cleanup; do not infer crash. After cleanup audit/configafter/closure/
verify/compare ONCE. No source edits to pinned payload. Source frozen per case.
Prepared fixture83299 closed, before configTRUE. No physical access. Until13:00UTC.
Prior changes pushed32d92a8; newkit/notes uncommitted. Automation updated with
owned sessions, must update again after result. Normal and failure join waits
are each bounded60seconds; a failed normal join can enter abort's second wait.

# Bounded rendezvous pair in progress

2026-10-07 07:54UTC. Prior kit/reports committed and PUSHED32d92a8. New UNCOMMITTED
outputs/fatx-map-rendezvous built/reviewed,11 oracle negatives pass. Fresh
serial001 launched07:52:45UTC, runner72749/supervisor18673 active; do not duplicate.
Run work/runs/nt5-fatx-map-rendezvous-serial001, localhost4594/4595/4596.
flush001 PREPARED but NEVER LAUNCHED; preparation83299 closed, before configuration
passes. Wait serial return/cleanup, cold audit/config-after/closure/verify before
launching partner. First dirty append per44 cases requires10sec bounded overlap
rendezvous in concurrent mode; serial100ms dwell, remaining17 appends2ms. Every
failure signalsstop/boundedjoins; no drivers/hives changed. Read newREADME.
No physical access. Until13:00UTC; strict errors remainFALSE. Preserve oldfailed
flush coverage, all rollback/release artifacts. Update heartbeat and notes after
pair; review/check/commit/push. No new recovery snapshot/physical promotion.

# Serial allocation shrink complete; concurrent overlap gate preserved as failure

2026-10-07 07:49UTC. ALL owned sessions CLOSED. Emulator-only until13:00UTC;
no physical FTP/deploy/test. No driver/release change. Read outputs/fatx-map-truncate/
REPORT.md, NEXT.md and comparison.json. serial001 completed792 appends,32 queried
allocation shrinks,132 reopens,11 cold files, normal shutdown, clean full
allocation/five hives/protected hashes. StrictFALSE historicalSCM7000/Ftdisk49.
flush001 exited after two file-rounds: overlap12 then0 ->FAIL_NO_OVERLAP.
Timeout then post-timeout RAM/register/framebuffer capture showed desktop and
no workload process or contended FATX resources. Host closed; no normal shutdown.
Cold allocation/hives/protected files intact; both completed round0 files exact.
Full four-round workload/strict resultFALSE; no waiver or deadlock inference.
Sources frozen per case before collector classification amendment. Closed
runner4186/supervisor21706/audit82702/comparison83995. Never rerun these cases.

New host-only outputs/fatx-prefix-forensics/REPORT.md: physical111-byte span
has strong3-byte periodicity, NOT proof of pixels/video cause. No exact111 or
three24-byte fragments in6618 saved files; none among13159 decoded image frames
including12887 PE resources.109 decode gaps preserved. All searches CLOSED
(session99447 complete). Original physical restart method/source remain unknown.

Next NEW kit: bounded dirty-map overlap rendezvous plus freely racing shrink
appends, paired serial control, guaranteed stop/bounded join on every failure.
Keep actual overlap gate; no speculative FATX edit. Preserve0101/video0093,
0088rollback/0.1.0 and every failed case. Review/check/commit/push current new
reports first; update heartbeat from old5721ffe state. No current guest/tracer.

# Ordinary mapped-append pair complete; strict service errors retained

2026-10-07 07:13 UTC. ALL owned sessions CLOSED, no guest/tracer/observer active.
Authorized emulator-only work continues until09:00EDT (13:00UTC). Check time
before new work; at cutoff cleanup/report/pause existing heartbeat. Never use
physical FTP/deploy/test. Preserve physical0101/video0093,0088rollback,0.1.0 and
all failures. No driver, physical payload or release baseline changed this turn.

Current kit outputs/fatx-map-append-regression; read REPORT.md, comparison.json,
coverage.json and NEXT.md. Both settled0/settled1 completed936 mapping/seek/unmap/
EOF/close cycles,52 reopens and13 exact final cold files. Identical helper and
parent; mode1 adds explicit flushes. Both normal shutdown count1/dashboard return,
full allocation0errors/orphans, five hives, selected protected hashes pass.
Both STRICT qualifications FALSE: exactly recurring SCM7000(HID Input Service)
and Ftdisk49(HarddiskVolume6), retained as failures. No new popup/application
events. This bounded ordinary negative reproduction does not explain the physical
111-byte non-ASCII span or qualify a driver/release. No debugger/UI action in pair.

settled0 launch07:03:42,return07:05:44UTC; settled1 launch07:06:47,return07:09:05.
Closed0runner3852/supervisor3692/audit28751; closed1runner28213/supervisor28087/
audit63728; comparison3762 closed. Every launched case has closure.json, private
disk hash and cleanup metadata. All collection done ONCE; never relaunch/recollect.

Failures preserved: mode0 xemu host startup path expansion failure06:52:40,
no Windows launch. Copied/rebased actual-lifecycle002 parent and qemu-img compare
proved identical virtual contents, unchanged original (parent-copy.json).
mode0b launched06:55:07; Found New Hardware recurred. Initial pending-install
guard logged258 and ran ZERO workload operations. Owned stop06:59:32, no normal
shutdown; allocation/hives/protected files intact. Closedrunner17432/supervisor
63640/audit41425. mode1 is prepared but NEVER launched; not-launched.json records
why. Earlier harness versions remain mode0/source and mode0b/source.

For actual pair reused known settled fatx-directory-order001 immutable fixture,
same0101/video0093. No offline hive/policy edits; before/after configuration.py
records installed GPU, exact QEMU1B36:0005 null INF and inherited01B0/01B4 flags64.
This configuration is emulator-specific and must not be promoted to hardware.

Coverage: per mode168sector/20page/8cluster-crossing appends, four exact111/109
warning splits. ZERO cluster-releasing truncations and no concurrent flusher.
NEXT proposes a NEW kit with65290/65300/65315 prefixes so mapping allowance
crosses65536 while finalEOF is below, plus exactEOF/regrowth. Establish serial
control then paired concurrent volume-flush worker with overlap/stop/join gates.
Use existing reviewed worker contracts, not old wait-all==0 mistake. Preserve
any failure, trace it before speculative driver edits. No new kit/build yet.

Actual SetupAPI lifecycle and all interrupted-append attempts remain closed,
reported in previous note. Engineering FATX.md now records source/paging/cold
distinctions and interruption caveats for Linux/FATX readers. Source/raw/fixture/
disk evidence verifier and paired comparison passed. Commit/push after final
repository review; active automation must be updated to this new state.

# Actual mapped-append lifecycle verified; paired regression helper prepared

2026-10-07 06:44 UTC. ALL owned sessions CLOSED, no active guest. Authorized
emulator-only work continues until09:00EDT (13:00UTC). Check time before more
work; at cutoff stop new experiments, cleanup/report/pause existing heartbeat.
Automation xbox-emulator-development-until-10am staysACTIVE every10min until
then. No physical FTP/deploy/test. Preserve physical0101/video0093,0088rollback,
immutable0.1.0, every failed attempt. No filesystem driver change made.

Completed outputs/fatx-mapped-lifecycle001/002, collected ONCE.001 initial trace
failed GDB E14 before first verified hit; exact read location wasn't recorded.
Removed all BPs/resumed; normal cold run clean. Sources/sites/review preserved
inside001.002 fresh overlay uses32-byte resident-code validation, explicit
unreadable-hit gaps and independent complete DLL hash checks (before/after).
Four unreadable outer-entry hits retained;58 COMPLETE matched call lifecycles,
175 buffer references verified. All58 captured mapped appends equal cold bytes.
Target record40 confirms actual C:\WINNT\setupapi.log inrundll32: old270225,
mapping maximum270480, correct220-byte mapped source, seek270445, unmap,
mappingclose, SetEndOfFile, fileclose allsuccess; outerresult0. No driver/data
mutation. No explicit flush in examined cleanup, NOT a system-wide flush census
or proof of bug. Runtime path now established, unlike earlier unused loggerlead.

002 launch06:36:34UTC, dashboard06:39:40, traceended06:39:41. Allcold gatespass:
full220 warning/prefix,5300ASCII appended, normalshutdown1, events/installation,
selectedprotectedbinarychecks, exactsetupapi, fullallocation0errors/orphans,
fivehives. This is debuggerdiagnostic, notphysical/ordinaryqualification.
Closed002runner90665/tracer71201/supervisor87016/collector67074. Closed001runner
17488/tracer67471/supervisor22391. Do not relaunch/recollect completed attempts.
Prior interrupted-append001/002/003 allclosed;003 file-visible111zero/109correct
under intentionalstop remainsmechanism-only, originalphysicalbadbytes/reboot
methodunknown. Seepriornote andperkitreports; neverreinterpretthat asnormalPASS.

NEXT mainwork: outputs/fatx-map-append-regression/NEXT.md. Helperprobe.c BUILT,
Build.ps1 pinnedcompiler/import/PE reviewPASSED inbuild-review.json. NOT staged
into anyguest; NO fixture/run exists.13boundaryprefixes incl270225,4rounds,
18 observed append chunklengths=936map/seek/unmap/truncate/close cycles,52reopen
checks,13finalfiles. Mode0 actual observedlifecycle;mode1 explicit view/file
flushes. Firstpayloadactual220warning,rest deterministic. Waitsinstallqueueidle,
normalshutdownafter60s;holds/fails ifqueuebusy. NoautoUIactions ordebuggerneeded.
Constructpaired reproduciblechildfixtures fromclosedauditedmapped-lifecycle002
postinstalloutput, pinparenthash,stageonlyhelper/mode/startup withreadback, preserve
hives/boot/0101/video0093. Implementindependentcold936/52/13 exact-byte/event/
allocation/hive/binarygates BEFORE launching. SeeNEXT forprecisedirections.

Currentchanges beingcommitted/pushed afterfa2cada. Evidenceverifierspassboth
lifecyclecases;175buffers, repository5209filesclean. Allprivaterawfiles/disks
remainignored. InspectcurrentGitHEAD ratherthanolderheartbeatcommit hints.
No user action required; continueautonomouslyviaexistingheartbeat untilcutoff.

## Prior recorded state

# Controlled interruption reproduces a file-visible page-boundary split

2026-10-07 06:28 UTC. All owned emulator, tracer, supervisor and cold-reader
sessions CLOSED. Continue authorized emulator-only work until 09:00 EDT today
(13:00 UTC). Check time before new experiments; at cutoff cleanup/report/pause
xbox-emulator-development-until-10am. Keep ACTIVE every10min meanwhile. No
physical FTP, deploy or testing. Preserve physical FATX0101/video0093, original
0088 rollback, immutable0.1.0 and all failed evidence. No driver patch made.

NEW completed kit outputs/fatx-interrupted-append; REPORT.md and NEXT.md.
001: stop after successful109-byte suffix. Raw first111 zeros +109 correct,
but cold file EOF269718 doesn't expose target270225. Allocation fails with one
WMI backup invalid-chain terminal and one orphan. Not file-visible reproduction.
002: host atomic trace replacement PermissionError; cleanup removed BPs and
resumed guest. Final trace.tmp recovered verbatim after preserving last JSON.
Owned observer closed this failed attempt. Cold full warning intact, normal
shutdown event1, allocation clean. Never classify as checkpoint success.
003: new fresh run, tested bounded atomic writer. Stop after successful1524-byte
write at270336 including exact109 suffix, before any observed prefix write.
Cold file EOF271385 exposes first111 ZERO bytes and109 correct bytes at270225.
Full allocation consistent,0 errors/orphans; five hives parse; selected payloads
unchanged. No Windows normal shutdown (intentional). This is a mechanism and
boundary reproduction ONLY: physical damaged111 bytes were non-ASCII, not zero,
and original physical reboot method/raw first-write topology remain UNKNOWN.
Normal control fatx-paging-buffer002 retains all220 bytes correctly after normal
shutdown, with prefix page written much later near that shutdown.

003 launched06:22:09, checkpoint06:25:25.380, cleanup06:25:25.773 UTC. HMP quit
while paused/debug with GDB attached; no resume/step/detach after checkpoint.
All BPs removed and pending log writes0. Emulator exit0; generic runner exit1
because it reports Task emulator exited:0. Explicit socket disconnect recorded.
Closed sessions003 runner30331/tracer13547/supervisor88280;00241734/98777/61504;
00159633/65175/78447. All cold audits collected ONCE. Do not rerun these attempts.

Host recorder atomic_json.py now retries transient PermissionError for3seconds,
keeping old JSON and complete tmp if exhausted. Real Windows sharing-handle
test verified both transient recovery and permanent-block preservation. Exact
001/002 tracer source snapshots retained. Evidence verifier passes all3 cases,
151 source buffers total,67 kit files staged; repository check5140 files clean.
Source/reports being committed/pushed after prior HEAD78164bf; inspect currentGit.

NEXT: actual application mapped-append lifecycle, not another identical boot.
Use fatx-interrupted-append/NEXT.md with static candidate addresses and limits.
Owned setupapi.dll hash1d0a6e9d062a51e71eaae93d776746823834f5c518096d340f2b332fc059a23d.
Candidate outer77893f87/helper77893da6/cleanup77893cb5 statically maps/grows,
copies strings, seeks, unmaps, closes mapping, SetEndOfFile, closes file. Actual
use for SetupAPI.log is NOT yet runtime verified. A prior unrelated logger site
778cc5a8 had zero hits. Capture filename/strings/mapped bytes and API results,
pair by process/thread/frame, retain zero-hit/read failures without guessing.
Then consider focused writable-map append/truncate normal-shutdown regression.
Do not infer missing required flush or patch Cc behavior from static calls.

Private disks/buffers/hives stay outside Git. Existing owned ports4594HMP,
4595GDB,4596FTP (localhost only), pinned emulator and draw001 immutable input.
Use leases and fresh run IDs. HMP quit causes reader disconnect; record exact
owned exit. Preserve ordinary/physical qualification gates separately.

## Prior recorded state

# Full-run paging observation complete; next controlled interruption

2026-10-07 06:02UTC. All emulator/tracer/supervisor/cold-reader sessions CLOSED.
User authorizes emulator-only work until09:00EDT7October (13:00UTC). Heartbeat
xbox-emulator-development-until-10am ACTIVE every10min. Before new work checktime;
at cutoff cleanup/report/pause. No physical FTP/deploy/test; preserve physical
0101/video0093,0088rollback,immutable0.1.0.

fatx-paging-buffer002 CLOSED and collected/analyzed ONCE.59 actual mapped buffers,
all exact vs cold. FULL220-byte target source coverage:109-byte suffix observed
05:55:17.716165UTC inrundll32;111-byte prefix in4096-byte page at266240 observed
06:00:12.247911 inwinlogon near normalshutdown.294.531746hostseconds includes
pauses, NOT ordinary latency. All target returns complete; cold audits clean.
Both001/002 before-target audits show eventual220-byte disk region allZERO before
run, so matching slack is excluded.001 partial109-only result remains preserved.

Reports/ordering/NEXT in outputs/fatx-paging-buffer. Last pushed e849dac contains
reviewed source and001;002 completion being committed/pushed now. No driverfix or
physical cause established; firsthardware rebootmethod remainsunknown.

NEXT authorized independent work: follow fatx-paging-buffer/NEXT.md to build a
NEW single owned intentional guest-stop experiment after suffixwrite completes
but before prefixwrite, preserving normal002 control. Observe cold prefix/suffix
without a Windows orderlyshutdown. Label interrupted-state evidence, never
ordinaryqualification. No physical access. Do not relaunch completed attempts.
This tests a mechanism; it cannot establish how userrebooted originalhardware.
Afterward consider actual mappedappend lifecycle trace/normal regression.

002 runner23088/tracer22159/supervisor50522/coldreader77857 all CLOSED. Earlier
001 runner43634/tracer6024/supervisor7122 alsoCLOSED. Otherpriorattempts allclosed.
No user action required. Continue autonomously until13:00UTC via heartbeat.

## Prior recorded state

# Active handoff: paging002 continues through normal shutdown

2026-10-07 06:00UTC. User authorized emulator-only work through09:00EDT (13:00UTC).
Heartbeat xbox-emulator-development-until-10am remainsACTIVE every10min. Physical
0101/video0093/0088rollback/immutable0.1.0 untouched; no physical FTP/deploy/test.
At13:00UTC stop new experiments, clean owned processes, finalreport, pauseheartbeat.

fatx-paging-buffer002 is STILL ACTIVE: runner23088,tracer22159,supervisor50522.
Launch05:54:30UTC. Do not relaunch or duplicate observer. Trace pins roottrace.py;
001 original source preserved. Every trace snapshot is atomic. At05:59 it had
21062 write entries,58 mapped log buffers, no first111 coverage yet. Bound100000
hits/10min from prelaunch tracer start; test may take longer under debugger.
Traces of unrelated disk writes slow guest time. Supervisor waits for ended_utc
before signaling runner cleanup. Inspect actual sessions/trace/launch/cleanup.
Then collect002 ONCE via trial.py, analyze.py002 and audit-before-target.py002
underWSL. Do not read active disk. Preserve failures/coverage gaps, no driverpatch.

All earlier attempts CLOSED; don't repeat collection. Paging001 verifies52
buffers exact vs cold,109-byte suffix captured,111-byte prefix NOT captured;
complete cold warning intact. audit-before-target.py001 confirms eventual220-byte
physical range was allZERO in immutable input, every byte differs afterward.
Thus correct cold bytes are not a prefilled-slack false positive. Still no cause
for missing prefix observation; later writeback hypothesis remains unproven.

Completed cache/paging001 evidence and prepared002 source/manifest being reviewed
and committed. Active002 trace/launch not staged until closed. Prior pushed86a0880.
Run multi-case fatx-target-buffer/verify-evidence.py after staging finished kits.
Keep exact source/site/buffer/cold hashes and source coverage separate from normal
qualification. No other active emulator or required user action.

If002 still misses prefix, consider broader file-name/offset capture or lower
VfatWriteDiskPartial observation at the independently confirmed target LBA,
not another blind identical repeat. Existing filters only retain paths ending
\setupapi.log; partial capture cannot exclude other paths or unobserved writes.
Candidate SetupAPI mapped-append lifecycle addresses are in prior note; not yet
runtime-proven. Normal writable-map/extend/unmap/truncate regression may improve
coverage beyond earlier WriteFile append tests. Continue evidence-driven work.

## Prior recorded state

# Overnight investigation: full-run paging capture active

Authorized until09:00EDT7October2026 (13:00UTC), emulator-only. ACTIVE heartbeat
xbox-emulator-development-until-10am every10min. No physical FTP/deploy/testing.
At cutoff cleanup/report/pause. Preserve0101/video0093/0088rollback/immutable0.1.0.

2026-10-07 05:55UTC. Prior global/setup/cache traces and paging001 all CLOSED and
collected/analyzed once. Cold checks clean. Paging001 captured52 mapped buffers,
all exact versus cold file. Twelve target-overlapping writes verify109-byte
suffix at270336; the111-byte prefix at270225 is NOT captured. Last earlier-page
write ended at270225. Complete cold warning intact. Full coverage remainsfalse.
Later full-page writeback outside trace is a HYPOTHESIS, not established cause.

NEW fatx-paging-buffer002 ACTIVE: launch05:54:30UTC, runner23088,tracer22159,
supervisor50522. Do not relaunch. Same immutable draw001 input, no guest changes.
Removes cache_call/cache_return traps and raises bound100000hits/10min to observe
through dashboard. Uses actual VfatGetUserBuffer return buffers and effective
length/offset. Preserve001/trace-source.py; roottrace.py now002 source. Atomic
trace snapshots; supervisor waits for tracer cleanup. No cold reads whileactive.

After all owned sessions close: trial.py collect002 ONCE, analyze.py002 underWSL.
Require explicit evidence for first111 and next109; preserve any coverage gap.
Finish cache/paging reports, stage, run fatx-target-buffer/verify-evidence.py
fatx-cache-buffer fatx-paging-buffer and repo checks; commit/push private main.
Last pushed86a0880 includes completed earlier misses. Both FATX trace kits and
multi-case verifier changes uncommitted. No other emulator remains running.

Static next lead (not runtime-proven): owned setupapi.dll routine77893f87 calls
mapping helper77893da6, copies ANSI strings into a writable mapped view, seeks
actual length, cleanup77893cb5 unmaps/closes mapping, SetEndOfFile, closesfile.
Imports/call sites reviewed interactively; no saved lifecycle review yet.
If full-run source coverage closes, consider focused user API lifecycle trace
and a matched normal writable-map/extend/unmap/truncate regression. Prior
fatx-mapped-eof tests mostly read mappings and WriteFile output, so do not assume
identical mapped-append coverage. No speculative driverpatch.

## Prior recorded state

# Overnight investigation: actual mapped paging buffers captured

Authorized until09:00EDT7October2026 (13:00UTC), emulator-only. Heartbeat
xbox-emulator-development-until-10am ACTIVE every10min. No physical FTP/deploy/test.
Preserve physical0101/video0093,0088rollback,immutable0.1.0. At cutoff cleanup,
record final report,pause automation.

2026-10-07 05:49UTC. install-buffer001/002/003,setup-buffer001,target-buffer001
CLOSED/collected/analyzed/reviewed, committed+pushed86a0880. Trace misses retained.
cache-buffer001 also CLOSED, collected/analyzed once; cold checks clean. It saw52
setupapi.log paging writes (flags0x43), all returned success. No CcCopyWrite for
that file; entryMDLs flags2 unmapped, zero buffers. This is path evidence only.

NEW outputs/fatx-paging-buffer001 ACTIVE, accepted05:47:55UTC. Runner43634,
tracer6024,supervisor7122; do not relaunch. Same immutable draw001 input, no guest
changes. Actual VfatGetUserBuffer return12d43 now captures buffers plus clipped
Length EBP-124 and resolvedOffset EBP-96; context EBP-100. At05:48:42 already46
buffers captured, including270336 onward. Driver and relocated instruction bytes
verified live. Await debugger/helper/supervisor/runner cleanup; then trial.py
collect001 ONCE, analyze.py underWSL, exact source-vs-cold range/111+109 checks.
Do not read active disk. Tracer bounded20000hits/10min; no guest registers/data
modified. It removes breakpoints and resumes; supervisor then permits teardown.

cache/paging kits uncommitted. Complete reports/source review, use
fatx-target-buffer/verify-evidence.py fatx-cache-buffer fatx-paging-buffer after
staging, repo checks, commit/push. Next evidence-driven work should follow actual
paging/mapped append behavior, not assume earlier WriteFile probes matched it.
No user action needed. Continue autonomously before13:00UTC.

## Prior recorded state

# Overnight investigation: FATX paging path identified; debugger active

Authorized until09:00EDT7October2026 (13:00UTC), emulator-only. Active heartbeat
xbox-emulator-development-until-10am every10min. Preserve physical0101/video0093,
0088rollback, immutable0.1.0; no physical FTP/deploy/testing. Cutoff: cleanup,
concise report, pause automation.

2026-10-07 05:44UTC: install-buffer001/002/003, setup-buffer001, target-buffer001
all CLOSED, collected once and analyzed. Cold checks clean, no target source
capture. Target001 saw27104 NtWriteFile entries/99 unreadable buffers (20examples),
clean breakpoint removal/resume. Coverage limited to full marker/8192bytes.

New fatx-cache-buffer001 ACTIVE: accepted05:42:13UTC, runner11260/tracer8184/
supervisor21524. Do not relaunch. Actual log path reaches FATX as paging writes;
no observed CcCopyWrite call for setupapi.log. Entry MDLs mostly flags2 (locked,
not mapped), so their source buffers remain unobserved. Same unchanged draw001
input, no driver change. Trace reports must be read with retry until finished
(non-atomic original save); later paging tracer uses atomic snapshots.

Next fatx-paging-buffer001 PREPARED ONLY, allocation preflight passed, not launched.
Post-VfatGetUserBuffer site12d43 captures EAX, clipped Length EBP-124, resolved
Offset EBP-96, context EBP-100. Reviewed pinned0101 instructions/imports; no guest
mapping invoked by debugger. Launch only AFTER cache001 fully closes/collects.
Collect each kit once via trial.py collect001, then analyze.py underWSL.
Keep actual payload/offset evidence distinct from unobserved caller or DMA data.

Completed kits reviewed/evidence checked and staged, but NOT yet committed;
last pushedc26fa97. Finish reports/source review/staged byte checks/repo checks,
commit/push private main. No user action required.

## Prior recorded state

# Overnight investigation: selective syscall capture active

Authorized through09:00EDT7October2026 (13:00UTC). Emulator-only. Active heartbeat
xbox-emulator-development-until-10am every10min. No physical FTP/deployment/test.
Preserve0101/video0093, original0088 rollback and immutable0.1.0.

2026-10-07 05:36UTC: install-buffer001/002/003 and setup-buffer001 CLOSED, collected
once and analyzed. All cold checks clean; ALL target trace coverage false.
Setup trace had zero hits and disconnected during runner cleanup, retaining
breakpoint cleanup errors. No active processes from those four attempts.
Reports preserve misses; no driver cause/fix inferred. New evidence uncommitted.

New outputs/fatx-target-buffer001 accepted05:35:21UTC. Runner6319, tracer36308,
supervisor59631 ACTIVE. Do not relaunch. Same immutable draw001 control input,
no guest changes. NtWriteFile bounded250000 hits/12min; only matching warning
buffers retained, unrelated writes/error counts recorded. Stops after three
warning occurrences return, or dashboard/deadline. Supervisor waits for tracer
cleanup before closing runner. Source and stub bytes pinned. Debugger-only.

When all owned processes close, trial.py collect001 ONCE, then analyze-buffers.py
underWSL; improve coverage analysis without changing raw trace. Null offsets do
not identify exact log occurrence. Complete evidence checks/review/repo checks,
commit/push private main. At13:00UTC no new experiments; clean up, report, pause.

## Prior recorded state (superseded by current header)

# Overnight investigation: focused SetupAPI trace active

Authorized through09:00 America/New_York7October2026 (13:00UTC). Emulator-only.
Automation xbox-emulator-development-until-10am ACTIVE every10min, name Xbox
emulator investigation until9am. At cutoff start no experiments, clean owned
processes/preserve evidence, concise final report, pause automation. No physical
FTP/deployment/testing; preserve0101/video0093/0088 rollback/immutable0.1.0.

2026-10-07 05:28UTC: outputs/fatx-install-buffer001/002/003 all CLOSED and collected
once, buffer-analysis.json completed. All cold checks clean, all target capture
coverage false.001:1027 captured writes, hit limit.002:495 captured buffers then
unpaired unrelated-return guard.003:16000 write entries,15841 complete captures,
read errors retained; no target warnings before hit limit. No corruption inferred.
Three normal shutdowns, exact warning offset270225/220 bytes persisted. Original
trace sources001/002 preserved; currenttrace corresponds003. No processes remain
from these cases. write-layouts.json compiler-derived offsets verified against
0101 source/binary; FILE_OBJECT128 is header size, not verified native NT5 tail.

New outputs/fatx-setup-buffer001 single launch accepted05:27:42UTC. Runner99325,
tracer77823, supervisor12708 ACTIVE. Do not relaunch. Same immutable draw001 quiet
input, no guest changes; preflight clean. Exact owned SetupAPI routine at778cc5a8
seeks EOF, converts ANSI, WriteFile+flush. Five reviewed instruction sites capture
seek return, write call/return and flush call/return. Stop after three matching
warning occurrences reach flush return or10min/2000hits. Breakpoint timing is
exploratory, never ordinary qualification. No kernel/guest-argument edits.

After tracer and owned dashboard/runner cleanup: trial.py collect001 ONCE in
fatx-setup-buffer, add/run focused cold source/offset/WriteFile/Flush correlation
analysis. Require exact file offsets and source/cold bytes; do not treat global
trace failures as storage failures. Never read active disk. Then complete both
kits' reports, source reviews, staged byte/evidence checks and repository checks,
commit/push private repository (last pushedc26fa97). Both new kits uncommitted.
Maintain exact active state for later heartbeat, continue evidence-driven work
before13:00UTC. No user action currently required.

## Prior completed state

# Coordinated aligned installation/GDI pair complete

2026-10-07 04:37 UTC. outputs/fatx-install-draw001(control)/002(drawing)
both PASS and collected once after owned cleanup. The target post-copy warning
remains at270225; all220 bytes/first111 exact,5300 new ASCII bytes in each case.
Drawing began at observed EOF268485, before the target;4688 completed cycles,
activity in each30s interval, stopped/joined before restart. Control0 cycles.
Both normal shutdowns, idle install queues, three exact once-only UI actions,
GPU binding, selected binaries, five hives and full allocation passed. Before:
322dirs6739files323dirclusters; after322dirs6745files323dirclusters; zero errors/
orphans. No unexpected event deltas/popups/application records.

Same immutable aligned001 pre-install parent, helper
0ee803b0cd20c214caf4b532f53c26a493cb421159904212c40d2440ee588668,
0101/video0093/hives/startup/INF/padding. Only staged payload difference mode0/1.
Original8985-byte UI matcher/action prefix preserved after CRLF normalization.
001 launch04:28:02 return04:31:08;002 launch04:33:32 return04:36:31 UTC.
Runners32050/78729 and supervisors82068/36401 closed; preparations67937/97565,
build2725 and cold readers closed. Do not repeat recorded launches/collections.
comparison.json pins qualifications; REPORT.md and NEXT.md record actual limits.

No corruption reproduced. Coverage brackets log growth during drawing worker
lifetime, not exact syscall overlap, source-buffer correctness or pixels. Next:
identify the actual aligned installer write request/buffer in an owned debugger
diagnostic before designing bounded tracing. Do not infer a fix or power loss;
physical111-byte anomaly/first reboot method remain unresolved. No physical
access, driver edits, new recovery, tag or automation change. Physical0101/
video0093/normal startup/GPU registration, remaining devices/raw-C warning,
original0088 and immutable0.1.0 preserved. Private review/checks/commit/push
completing from f73d534. No user action required and no test remains running.

## Prior completed state

# Paired paced append/GDI diagnostic complete; no corruption reproduced

2026-10-07 04:08 UTC. outputs/fatx-draw-append001(control)/002(drawing) both PASS,
collected once after owned cleanup. Same immutable fatx-directory-order001
pre-run parent; same helper e0f8c13e48a99c0ca7731b7f486950ba94bca8c27ea9ce26b5a54139e2948fc8,
0101/video0093, startup and preserved hives. Only staged payload difference is
xwnidle/drawmode.txt0 versus1. No physical access or driver source change.

Each8192 appends/16 exact cold files; total16384/32 files/15977216 bytes. Drawing
1644 completed cycles,1583 overlapping append epochs; all16 cases positive.
Control0 cycles. Normal restarts, no unexpected events/popups/application records,
five parsed hives, unchanged SetupAPI, full F323dirs6769files324dirclusters,
zeroorphans/errors. Workload29400/51975ms are not video-performance comparisons.

001 launch04:00:22 return04:02:15;002 launch04:04:36 return04:06:47 UTC.
Runners86601/92151 and supervisors92800/25855 closed. Preparations6821/29407
and all cold readers closed. No owned process remains. Do not repeat completed
launches/collections. comparison.json and each qualification.json pin evidence.

NEXT.md: coordinated bounded drawing worker alongside the actual aligned
first-install helper. Keep exact GPU/placeholder handling, queue-idle gates,
log offset and cold evidence; stop/join worker before restart. This pair is
known-source I/O load, not actual installer source-buffer reproduction, pixel
correctness, GPU acceleration or hardware qualification. Physical111-byte log
anomaly and first-reset method remain unresolved. Actual-device and reserved
raw-C capacity policy work remains required for unattended hardware qualification.
Physical0101/video0093/normal startup/GPU registration, rollback0088 and immutable
0.1.0 unchanged; no automation or recovery change. Source/report checks and
private commit/push completing; prior a96e927. No user action required.

## Prior completed state

# Both aligned installer emulator runs passed; physical anomaly unresolved

2026-10-07 03:54 UTC. outputs/fatx-install-alignment001/002 completed, cold-collected
and qualified PASS. Both actual post-copy warnings start270225 (mod512401,
mod40963985), all220 bytes and first111 exact. Original135501-byte prefix and
131059-byte padding preserved;5300 newASCIIbytes each. Normal restart, queueidle,
no unexpected errors/popups/application records, five hives and fullF allocation
322dirs6743files323dirclusters0orphans/errors. These are UI-assisted diagnostics;
ordinary/physical qualification remain false. No driver source change warranted.

001 launch03:45:33 return03:48:32;002 launch03:50:41 return03:53:31 UTC.
001 runner19250/supervisor86930 and002 runner4466/supervisor14833 closed; owned
PIDs75508/75152 cleaned. Preparation82845/81030 and all cold readers closed.
Do not relaunch/recollect completed cases. No owned process or automation active.
Parent is immutable fatx-first-install-0101/fixture-001.json; both sibling fixtures
in native-windows-fatx-forensics/artifacts, run disks retained under unique runs.

Saved physical second-boot layout maps target LBA292691839 versus emulator
290163071; both high-address, different sectors. Physical first-write topology
not established. Original damaged111-byte span includes91 high-bit bytes plus
oneDEL, clarifying earlier label92non-ASCII; original records/logs unchanged.
First physical reboot method still unknown. NEXT.md specifies a paired bounded
GDI drawing/file-I/O load comparison with known-source and cold byte oracles;
no direct GPU access/debugger/reset injection or physical launch included.

Physical Xbox untouched:0101/video0093/normal startup/GPU registration, prompts,
raw-C warning, rollback0088 and immutable0.1.0 remain. No release/recovery/tag
or automation change. Reports and reviewed source checks/commit/push completing;
prior570715e. No user action required for these completed emulator diagnostics.

## Previous completed state

# Sequence and first-install emulator tests complete; physical anomaly unresolved

2026-10-07 03:23UTC. fatx-append-sequence001/002 both PASS:16,384 appends total,
32 exact cold files, normal restarts, no unexpected events, five parsed hives/run,
complete consistent F allocation. SetupAPI unchanged in these settled boots.
All runner/observer sessions closed; do not repeat completed launches or audits.

fatx-first-install-0101/001 launched03:19:25 and returned03:22:29. Targeted prior004
helper completed exact GPU Finish/No and identified emulator placeholder Cancel;
queue idle at120s, normal6006, no new unexpected errors/popups/application records.
Cold GPU class0001/XboxVnt5/oem2.inf/ConfigFlags0, Start3; binaries unchanged,
5 parsed hives, full F allocation322dirs/6743files/323dirclusters,0orphans/errors.
SetupAPI adds5300 ASCII bytes and preserves135501-byte prefix. No malformed span.
Diagnostic qualification PASS only; ordinary/physical qualification both false.
Runner86332, supervisor78400 and cold readers closed. No process remains active.

Actual unsigned-driver lines begin at138864/139166/139744 (sector offsets112/414/
480), unlike physical270225/401. Next controlled variant in first-install kit's
NEXT.md: recorded log-prefix alignment in a fresh pre-install child, verify actual
resulting positions. Original physical first-reset method still unknown. No cause
inferred and no driver source fix fabricated from negative reproduction tests.

Physical Xbox was not contacted or changed this turn.0101/video0093, normal
startup, GPU registration, prompts, raw-C warning, original0088 and immutable0.1.0
remain as recorded. No release/recovery snapshot or automation change. All three
new attempts and old failures retained. New source/reports reviewed and checks/
commit/push completing; prior daddee5. Kits include byte-preserving Git attributes
and staged evidence hash verifiers. No more manual action required for this turn.

## Earlier continuation (historical)

# Two append-boundary emulator passes; physical anomaly still unresolved

2026-10-07 02:53 UTC. outputs/fatx-append-boundary cases001 and002 both finished,
collected and qualified. Each completed96 serial append cases with exact live
and cold bytes (8,238,784 payload bytes), normal restart, five parseable hives,
full F allocation323dirs/6850files/324dirclusters and zero orphan/errors. No new
unexpected errors/popups/application events; inherited identical HID SCM7000
is explicitly classified. SetupAPI remains byte-identical144784bytes in both.

Same immutable fatx-directory-order001 parent, unchanged0101/video0093, exact
probe1be9096aeb48a2cdae6bedcff07037f8085dc434bddd0d58f89962009dc0258f.
No driver edit, debugger, recorder or physical FTP/change. Fresh sibling002
is NOT based on001 output. Both owned runners/supervisors and read-only audit
processes closed. No automation active/modified by this work; no process remains.
All completed JSONs retained; do not relaunch/recollect these cases.

REPORT.md gives results/limits; NEXT.md specifies repeated log-style append
with end-only versus per-append flush, then separately controlled first install.
Passing serial appends does NOT reproduce/resolve the physical malformed111-byte
span or qualify unattended hardware. Physical0101/video0093/normal startup,
GPU registration, remaining prompts, raw-C warning and all rollback/v0.1.0 remain
as previously recorded. No new physical run or recovery snapshot.

Exact source/evidence byte preservation is scoped in .gitattributes to this kit;
verify-evidence.py checks staged hashes and both immutable case reports. Source
and reports reviewed, checks/commit/push completing this turn; prior9a3a81f.

## Earlier continuation (historical)

# GPU registration verified after normal restart; all postboot audits complete

2026-10-07. User All set confirmed return after requested normal Windows Restart.
Second GPU boot collected ONCE. SYSTEM retains exactGPU class0001/XboxVnt5/oem2.inf,
ConfigFlags0,Start3. SetupAPI adds3224 ASCII-only bytes, no GPU installer; first
log remains exact prefix. EventLog one6005/6006 pair, no new popup/application
records. Only unexpected warningSrv2013 WindowsF(raw Xbox C/shadow image); old
G/H cache warnings absent. Remaining01B0/01B4/01C1/USBffff:ffff prompts persist.

Read-only postboot F scan at/E/Applications/XWNGpu102b launched/returned/collected
ONCE:6075dirs/122327files/6080dirclusters,0orphans/errors. Observer44062 closed.
audit-second.py session48938 finished3439 binary hashes exact and nine hives
structural/sequence/checksum PASS. finish-second.py completed final dashboard
hashes:0101/video0093, normal startup, exact OEM INF and SOFTWARE backup; collected
SYSTEM/SOFTWARE/SetupAPI unchanged. All stage JSONs complete; do not repeat them.
No owned background process, emulator or automation. Dashboard available last check.

outputs/physical-gpu-setup/002/qualification.json: configuration_verified=true,
strict_qualification_passed=false. This is user-assisted setup, not unattended
validation, accelerated graphics, full audio or a release/recovery qualification.
No new Windows run or recovery snapshot. All original rollback/v0.1.0 preserved.

Unresolved first-boot log anomaly:111-byte prefix at270225..270335,92 non-ASCII
bytes, ending exactly at512-byte boundary. Matching remainder of earlier intact
unsigned-driver line is evidence for a damaged prefix, not cause. First boot
has no6006. Optional user question PENDING: Windows Restart versus console power/
reset for that first reboot? No answer inferred. Second boot has no new malformed
bytes. Preserve raw logs; do not silently repair or blame filesystem/power/video.

Next steps in physical-gpu-setup/NEXT.md: explicit actual-device support/policy;
legitimate raw-C capacity integration without deleting softmod/silencing events;
bounded emulator reproduction of append offset401 versus first GPU setup, with
source-buffer/completion/flush/cold-readback evidence. Only then unattended soak.
Current source/reports being committed/pushed; prior6f5d6b5. No manual action needed
for this completed collection. Do not launch another physical test implicitly.

## Earlier continuation (historical)

# Second GPU boot collected; read-only postboot scan running

2026-10-07 02:29 UTC. User confirmed normal restart complete. second-boot.py
collect ran ONCE. Registry retains GPU class0001/XboxVnt5/oem2.inf/ConfigFlags0,
serviceStart3. New SetupAPI delta3224bytes is ASCII-only, original first log is
exact prefix, no new GPU installer. Same01B0/01B4/01C1/USBffff prompts remain.
Events: second boot has one6005/6006 pair, no popup/application event. Only new
unexpected warning isSrv2013 WindowsF(raw Xbox C shadow image); G/H warnings no
longer occur after X/Y cleanup. First boot lacks6006 and retains92 anomalous
non-ASCII bytes at offsets270225..270335, ending on512-byte boundary. Cause unknown;
no strict PASS or softmod deletion/event waiver.

Unique read-only F scan launched ONCE02:28:03UTC at/E/Applications/XWNGpu102b,
returned02:29:48, collected once:6075 directories/122327 files,0orphans/errors.
Observer44062 closed. audit-second.py session48938 is running,2800binaries checked
without mismatch so far;3439/nine-hive completion still required. Inspect JSON,
resume only an incomplete audit, then finish-second.py once. No repeated scan. No further Windows launch. All previous trials and
scans remain preserved. Full cold checks are outstanding. Current changes uncommitted,
prior6f5d6b5. No automation modified; no emulator running.

## Earlier continuation (historical)

# Second GPU boot reached UI without VGA wizard; remaining prompts persist

User reports second boot no longer asks for VGA installation; the other prompts
remain. This is user evidence consistent with first-run persisted GPU registration,
not collected second-run binding/idle-queue evidence. No need to install GPU again.
No further launch authorized or requested. No running observer/automation.

Next: user may cancel the same audio/generic PCI prompts previously identified;
inspect any unfamiliar prompt separately. Verify desktop and keyboard/mouse, then
use normal Windows Start > Shut Down > Restart to return to UnleashX. Only after
return run outputs/physical-gpu-setup/second-boot.py collect ONCE. Decode new events,
compare SetupAPI prefix and malformed span, inspect persistent GPU binding and
perform relevant cold integrity checks. Prior92 non-ASCII SetupAPI bytes and
raw-C Srv capacity issue remain unresolved; do not call this a strict PASS.
All installed driver/rollback/cache-cleanup details below remain applicable.

## Earlier continuation (historical)

# Second GPU setup boot accepted; GPU registration confirmed, log anomaly unresolved

2026-10-07 02:09 UTC. User rebooted after difficulty clicking the GPU driver and
explicitly requested relaunch. First run collected ONCE, preserving logs and
SYSTEM/SOFTWARE. SetupAPI identifies audio01B0, then generic PCI01B4 and01C1, then
GPU02A0, then USBffff:ffff. GPU installation actually finished successfully and
requested reboot after query-removal veto. SYSTEM confirms ConfigFlags0, class
0001, XboxVnt5, oem2.inf/Xbox.Install; service Start3. OEM INF is exact staged
package. Driver/baseline hashes unchanged. SYSTEM6001keys/18608values and
SOFTWARE26914keys/39260values traverse successfully.

CAUTION:92 non-ASCII bytes in a new SetupAPI span (delta offsets6046..6156),
preceded by intact original log prefix. Exact repeated FTP readbacks agree.
Cause unresolved; first boot is NOT clean qualification. Preserve raw bytes,
review-first.py and first-setup-review.json. First reboot method not independently
established; no normal-shutdown claim yet. Event decoding/full cold audits pending.

Second boot explicitly authorized and accepted02:09:25.348123UTC. Record:
outputs/physical-gpu-setup/002/physical.json; second-boot.py launch must NEVER be
repeated. No new physical file writes; all captured state and installed OEM INF
were rechecked before launch. Keyboard reminder delivered; prior readiness
confirmation retained, not falsely recorded as a fresh unplugged observation.
Normal idle startup, no timed workload/automatic restart; no background observer
or automation. User should reconnect keyboard at desktop and report remaining
prompts. GPU selection should no longer be needed, but actual boot unobserved.
After a normal user restart, second-boot.py collect ONCE, then review events,
SetupAPI changes/log anomaly, persistent GPU binding and storage integrity.

Cache cleanup/raw C findings preserved. No C files deleted; shadowc.img explains
legitimate nearly-full raw system partition.0101/video0093 unchanged,0098 rollback
and original0088/v0.1.0 intact. Latest prior ed5472d; current evidence being pushed.

## Earlier continuation (historical)

# GPU setup boot launched once; waiting for user desktop/prompt observations

2026-10-07 01:52 UTC. User confirmed Razer keyboard unplugged and authorized
launch. trial.py rechecked installed0101/video0093 baseline, normal idle startup,
SOFTWARE rollback, INF and staged SOFTWARE hash before requesting SITE EXEC
E:\Applications\XWNFBoot\default.xbe ONCE at01:52:08.908647 UTC.
Dashboard replied200 EXEC command succeeded. This proves launch acceptance only;
no desktop, GPU binding or shutdown result is claimed yet. No repeat launch.

User should reconnect keyboard only after Windows reaches desktop, leave Windows
running and report exact hardware/device prompts before dismissing them. This
setup boot uses normal idle startup, no automatic workload or restart. No active
observer, emulator or automation. When supported setup is complete, request a
normal user restart; then trial.py collect ONCE and review SetupAPI, GPU class/
service/INF binding, unchanged video/FATX binaries and event deltas. Do not infer
success from FTP return. First-install shutdown failure remains historical;
this configuration experiment is not an unattended soak or release PASS.

All cache cleanup/raw C evidence and GPU staging were committed/pushed f508c38.
The six X/Y cache files remain privately backed up;1.39GiB reclaimed. Raw C is
legitimately occupied by508.6MB softmod shadowc.img, intact. No warning gate was
waived. /F/xwninf102/software.bak preserves pre-setup SOFTWARE; FATX0101/video0093,
0098 rollback and original0088/v0.1.0 remain unchanged. Current launch record and
notes being committed/pushed. No further hardware action until actual observation.

## Earlier continuation (historical)

# Cache cleanup complete; raw C explained; GPU setup staged, awaiting keyboard readiness

2026-10-07 01:46 UTC. User authorized cleanup and continuation. Six exact X/Y
cache maps archived, locally reread/hash verified, remotely rehashed then deleted.
1,488,977,920 bytes reclaimed; all other root entries preserved. Session82145
completed. Private backups E:/Codex-private-artifacts/xbox-windows-feasibility/
cache-cleanup-20261007; manifests in outputs/physical-space-cleanup.

Read-only raw C probe passed emulator002 exact metadata/directory comparison and
no-C-write audit, then physical launch/return/collection ONCE at XWNRawC001.
33 directories,83 files, no orphan/error,179 free16KiB clusters=2,932,736 bytes,
matching Windows. /nkpatcher/shadowc/shadowc.img is508,559,360 bytes. Preserve it;
no C deletion or softmod modification. The legitimate nearly-full system volume
needs deliberate Windows integration. Do not waive/silence the strict Srv gate.
Host emulator001 failed before boot on backing path length; retained separately.
Owned002 and all backup/validation/observer processes are now closed.

GPU setup at outputs/physical-gpu-setup is staged/readback verified, NOT launched.
Exact existing video0093 binary and tested INF in /F/xwninf102. Current SOFTWARE
backup local artifacts/before-software and remote /F/xwninf102/software.bak.
Only DevicePath appends C:\xwninf102; all26914 keys/39260 values checked.
Staged SOFTWARE hash4b6e54f8aa7d6d0161917869236da41db61f767521dfd5ac7c425e415db62f9f.
FATX0101, installed video0093, SYSTEM and normal idle startup unchanged. No null
INF, failed-install flag or signing-policy change. First emulator setup shutdown
failed historically; subsequent installed boots passed, so this remains a
controlled configuration experiment, NOT an unattended/release qualification.

PENDING USER QUESTION: is Razer keyboard unplugged? Do not launch Windows until
actual confirmation. Once confirmed, trial.py launch --keyboard-unplugged ONCE
with supplied FTP environment; leave Windows desktop for GPU setup. Reconnect
keyboard only after Xromwell/at desktop. Identify actual wizard device before
any instructions, preserve user observations, use normal user restart. Then
trial.py collect once, inspect SetupAPI/GPU service/class/INF and event deltas;
full cold audits and a later unattended soak remain outstanding. Do not repeat
physical0101's completed trial/scan. v0.1.0/0088/0098 rollback untouched.
No automation modified; no owned process remains active. Current reports/source
are being reviewed and pushed, prior e6ee894.

## Earlier continuation (historical)

# Cache cleanup and raw C inventory in progress

2026-10-07 01:40 UTC. User authorized safe space cleanup and continuing device
setup. Six exact X/Y cache maps archived and locally SHA256 readback verified at
E:/Codex-private-artifacts/xbox-windows-feasibility/cache-cleanup-20261007.
cache.py remove session82145 is running, rehashing each remote file before its
single deletion; inspect cache-removal.json before any action. Preserve all other
entries, savegames, preferences, fonts and all C/dashboard/softmod files.
Dashboard C exposes only3.26MB, unlike raw C's nearly-full Windows reading.

New read-only Partition0 C metadata probe built under outputs/raw-c-inventory.
No physical launch yet. Emulator host attempt raw-c-inventory-001 failed to open
a deep backing chain before guest boot; closed cleanup recorded. Flattening a
NEW equivalent fixture (session74403), originals unchanged, for new attempt002.
Do not relaunch earlier physical0101 trial or scan. Normal startup and0101/video0093
remain installed. Next: finish cache removal, emulator validate raw C probe,
launch it once directly via nxdk/FTP, collect raw metadata, then GPU PnP work.
No new Windows launch; future Xromwell requires keyboard unplugged.

## Earlier continuation (historical)

# Physical0101 collected and audited; all owned processes closed

2026-10-07 01:21UTC. Single candidate0101 trial completed500 rounds on each of
five workers in62205ms, zero API errors. Helper held for pending install258;
automatic observer expired. User closed multiple hardware prompts for keyboard
registration and later requested a clean normal restart. Both are preserved as
manual intervention, not an automatic PASS. Collection restored normal startup
FIRST; raw log confirms photograph, three exact final files, meta.tmp absent.

Cold results: one orderly EventLog shutdown; no new popup/application events;
threeSrv2013 warnings on WindowsF/G/H. Unique read-only scan returned, collected
once: allocation consistent,0orphans/errors. All3439 binaries match; nine hives
structurally valid. Final read-only installed-state.json verifies0101/video0093,
normal startup and0098 rollback. Overall strict FAIL (installer-held protocol,
automatic return deadline, warnings). No PASS-gated recovery capture or new boot.

SetupAPI exact prior prefix; current log identifies unsupported/no-compatible
10DE01B0,01B4,01C1,02A0 andUSBffff:ffff prompts, then successful Razer1532:021E
keyboard/HID and mouse installs. Current keyboard binding persists (kbdhid,
keyboard.inf,flags0). PCI state unchanged; GPU serviceXboxVnt5/flags0x400 still
lacks completed Driver binding. Registry entries include history; do not infer
live bus population. No unsupported-device policy was transplanted from xemu.

Sessions48504(scan observer),9944(binary/hive audit) completed. Earlier83795
Windows observer closed. No owned background process. Never relaunch this trial
or scan; all stage JSONs complete. Candidate0101 remains provisional,0098 local
and remote rollback plus0088/v0.1.0 preserved. User screen/log questions resolved.

Next: supported GPU PnP registration, explicit unsupported-device handling, and
independent small-partition capacity investigation before a NEW unattended trial.
Do not waiveSrv warnings, silence unknown devices, or delete cache/system files
blindly. Keyboard must be unplugged for any later Xromwell launch. Current source/
reports reviewed and being pushed; prior9dc8c29. No automation modified.

## Earlier continuation (historical)

# Physical0101 awaiting user normal restart after installer hold

2026-10-07 01:11UTC. User reports multiple Found New Hardware prompts had to be
closed for the keyboard to register. Device identities unknown; do not ask user
to reproduce/reopen those dialogs. This is manual setup interaction, separate
from the photographed500-round workload completion. Guard remains indefinitely
held even if installation queue has since cleared. FTP refused connection.

Next user action: close open apps and use Start/Shut Down/Restart normally.
If shutdown stops on a prompt or hangs, preserve actual state; do not assume
normal shutdown or silently force it. On dashboard access physical.py collect
FIRST restores startup, then qualify, unique allocation scan once and full audits.
Read collected SetupAPI/hives for device identities. No new Windows test launch.
No remote writes this turn. Device-name question superseded by user's account.
Prior13787da pushed; observation/continuation being pushed now. No background
observer or automation active for this trial. Exact installed/rollback data below.

## Earlier continuation (historical)

# Physical0101 workers completed; restart held for pending installation

2026-10-07 01:10UTC. User photo of C:\xwncc01\probe.log shows WAIT_RESULT3,
62205ms; COUNTS500/500/500; NAMESPACE_COUNTS500/500; all errors0; COMPLETE;
RESTART_BLOCKED_PENDING_INSTALL258. Record log-photo-evidence.json pins the photo
and transcription. This is user photographic evidence, not cold file readback.
No worker timeout is shown. The helper deliberately sleeps indefinitely after
this guard; closing the wizard alone will NOT resume its restart sequence.

FTP still offline (read-only check timed out). Asked once whether the hardware
wizard remains open and for the exact device name; leave installation choices
unchanged pending identity. Screen/log questions answered; device question pending.
No launch, remote write, scan or collection this turn. Observer remains closed.

Host qualifier now reports worker completion separately from restart protocol,
without relaxing any gate: a pending-install hold still fails strict qualification.
Host checks cover both retained PASS logs and held/error/partial/malformed cases.
Normal restart, exact files, strict events, full allocation,3439 hashes/ninehives
remain required. Do not turn this photographed workload completion into full PASS.

After setup identification arrange normal return, not another workload launch.
On dashboard access physical.py collect FIRST restores normal startup; preserve
logs before rollback. Then qualify, unique read-only scan once, complete audits.
Original0098 rollback/video0093/0088/v0.1.0 unchanged from recorded state. Latest
push72159e7; current observation and diagnostic distinction being pushed now.

## Earlier continuation (historical)

# Physical0101 desktop photo received; test log needed

2026-10-07 01:05UTC. User photo confirms Windows desktop, an open Found New
Hardware Wizard welcome page (device name obscured), Getting Started and a cmd
window. This rules out Xromwell being the pictured state. It does NOT establish
responsiveness, workload completion or that the restart guard fired.

Read-only FTP check refused connection. No new launch or remote write. Original
screen question answered; now asked user to open notepad C:\xwncc01\probe.log
and report final lines, leaving wizard open. If already rebooted, do not relaunch;
collect on dashboard return FIRST restoring normal startup. The helper sleeps
indefinitely after a pending-install result; closing the wizard alone does not
resume its restart path. Preserve outcome as held if that is what the log says.

Single0101 launch and rollback details below remain authoritative. Observer83795
closed; no owned process running. No scan launched. Startup remains last verified
as one-shot enabled until dashboard access returns. Source/notes pushed e37821f;
photo observation and updated state being committed now. No hardware PASS claimed.

## Earlier continuation (historical)

# Physical0101 awaiting screen evidence; host observer closed

2026-10-07 01:03:35UTC. Single launch at00:50:29UTC accepted, FTP went offline,
and the13-minute observer completed with NO dashboard return. Session83795 has
exited. No owned process remains running. No crash, deadlock, workload completion
or installer hold is inferred. The screen question asked00:56UTC is still pending;
do not ask it repeatedly or relaunch Windows. No scan has been launched.

Installed0101 SHA ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9,
video0093 unchanged. Normal startup restoration remains pending dashboard access;
last verified startup invokes C:\xwn101a\probe.exe. Helper exclusively creates
C:\xwncc01 and holds on timeout or pending installation. User screen evidence is
required to distinguish boot state, pending wizard, or Windows failure.

All rollback/startup bytes preserved locally in outputs/fatx0101-physical/artifacts
and at /F/xwn101a/rollback.sys and startup.cmd. On dashboard return run
physical.py collect FIRST, then qualify.py. Preserve results before driver rollback.
The prepared read-only allocation scan has NOT launched; if proceeding with it,
scan.py launch ONCE, watch.py scan, scan.py collect, audit-binaries.py (resume only
incomplete), qualify.py. Strict event gates and3439 hashes/ninehives stay required.
Never fabricate a qualification from the timeout or earlier emulator passes.

Original0088, immutable0.1.0 and all prior failures preserved. No automation
created/resumed/modified. Trial source/launch pushed487e05c; this final observation
and notes are being reviewed and pushed now. See physical final-state.json.

## Earlier continuation (historical)

# Candidate0101 single physical concurrency trial active

2026-10-07 00:50:29UTC. Latest human Proceed accepted as readiness after the
keyboard-unplug request. Read-only ownership, installed0098/video0093, startup
and unique-path preflight passed. Exact emulator-qualified0101 and five-worker
helper deployed with readback. Original0098 and startup preserved privately and
at /F/xwn101a/rollback.sys and startup.cmd. Video/boot chain unchanged.

Single SITE EXEC accepted. outputs/fatx0101-physical/physical.json is authoritative.
Observer session83795 watches windows-return.json; never relaunch or duplicate it.
Helper creates /F/xwncc01 exclusively; do not precreate/reuse it. Five500-round
workers, ten-minute wait bound; host observer thirteen minutes. Pending installer
causes a held test, not a forced restart. No claim of hardware PASS yet.

On return run physical.py collect FIRST (restores normal startup), qualify.py,
scan.py launch ONCE at /E/Applications/XWNLock101a, watch.py scan, scan.py collect,
audit-binaries.py (resume only incomplete), qualify.py. Full3439 hashes/ninehives
and allocation required. Strict Srv/popups remain failures. A screen question was asked at00:56UTC while the observer continues; do not
repeat it. No dashboard return alone cannot identify a deadlock. Preserve before any rollback.
All earlier emulator runs closed. No automation modified. Original0088 and
immutable0.1.0 preserved. Trial tools and launch pushed487e05c. Screen question/status updates pending commit.

## Earlier continuation (historical)

# Candidate0101 qualified for controlled hardware trial; no owned run active

2026-10-07 00:45UTC. All planned0101 emulator gates PASS:
- directory-order001: five500-round workers,19260ms, normal return00:20:02UTC.
- full persistence soak004:527 mappings,16BMP API cases,50 exact files,34 absent
  intermediates,15 rounds900000ms, normal return00:41:06UTC.
- independent directory-order002: same five500-round workers,18060ms, normal
  return00:44:42UTC.
All three closed, collected and qualified ONCE. Strict event deltas, exact bytes,
selected payload/runtime hashes, five structural hives and full allocation passed.
No timeout snapshots/debugger/UI manipulation in these successful runs. Actual
Paint UI and physical hardware remain separate. candidate-eligibility.json PASS
pins tree8e12297ca0ed53383fe9aaebef152c26aee5a43b and driver
ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9.

Runner/supervisor sessions74791/64781,33070/47155,94813/53785 all completed.
Preparation9774,53669,41353 completed. No run/observer/build remains active.
Never relaunch or overwrite these records. Earlier0098 and0099 lock-cycle
failures and the separate first0099 wait-all helper hold remain preserved.
0100 prepared fixtures were NEVER launched and remain held.

Next: physical verification, with exact rollback/startup preservation and new
unique trial IDs. Keyboard-readiness question asked earlier remains unanswered;
Xromwell hangs with the Razer attached, so do not launch hardware until clarified.
Physical0098/video0093, original0088 and immutable0.1.0 have not changed. The
physical PnP popup and three Srv2013 warnings remain strict failures; emulator
PASS does not waive them or allow a new PASS-gated recovery capture. See
fatx-directory-order/NEXT.md and physical-pnp-followup/README.md.

Source/docs prior checkpoints aff0475 and5f10349 pushed. Final PASS reports,
continuation and final-state checks are being reviewed/committed/pushed now.
No automation was created/resumed/modified in this turn.

## Earlier continuation (historical)

# Candidate0101 full soak PASS; independent concurrency replay active

2026-10-07 00:43UTC. Full-soak004 returned00:41:06.722UTC, runner33070 and
supervisor47155 closed. Collected once and qualified PASS:527 mappings,16BMP
replays,50 exact files,34 absent intermediates,15 rounds900000ms, normalshutdown,
strict event deltas, package state, five structural hives and full allocation.
No timeout snapshot/debugger. Stress001 was already PASS (five500-round workers).

Fresh directory-order002 preparation41353 completed; now one launch in progress:
runner94813, supervisor53785. Inspect002/launch.json for acceptance/time. Never
relaunch. Same corrected helper, exact0101 binary and original settled parent.
On normal return wait cleanup, trial.py collect002, qualify.py002. If deadline
misses preserve/decode memory before signal/cleanup; then collect once. Same
900s supervisor/1200s runner. Eligibility requires001,002 and fullsoak004 PASS.

After replay: update reports/notes, repo checks, commit/push. Last push5f10349.
Physical0098/video0093 untouched; original0088/0.1.0 retained. Keyboard-readiness
question still pending, so no physical launch. Physical PnP popup/Srv2013 still
strict failures. See directory-order/NEXT.md for the separate hardware handoff.

## Earlier continuation (historical)

# Candidate0101 concurrency PASS; full persistence staging

2026-10-07 00:22UTC. Directory-order001 returned normally00:20:02UTC, runner74791
and supervisor64781 closed. Collected/qualified once: PASS. Five500-round workers,
zero API errors,19260ms workload, exact three4097-byte files, meta.tmp absent,
normal shutdown1, no popup or new disallowed warning/error, five structural hives
and complete allocation audit passed. No debugger/snapshot on this ordinary run.

Full15min original mapping/BMP soak004 preparation53669 completed. Single launch
accepted00:24:41.363UTC; runner33070/supervisor47155 active. Deadline~00:45:42UTC,
runner limit~00:49UTC. Do not relaunch. Wait normal return, closed cold collection
and qualify004; timeout requires retained memory/decode before signal/cleanup.

Directory-order fresh sibling002 preparation41353 completed; NOT LAUNCHED.
Same helper/driver and original settled parent, independent writable fixture.
Run only after soak closes (same ports4594/4596). Then collect/qualify002 once.
Candidate eligibility script requires stress001,002 and full_soak004 PASS.
Hardware keyboard readiness remains pending; physical unchanged.

Latest pushedaff0475 includes both deadlock diagnoses and0101source/build/launch.
New PASS reports and repeat tooling need commit. Physical baseline and keyboard
question unchanged. Prior strict physical failures are not waived.

## Earlier continuation (historical)

# Directory-stream candidate0101 preparing after second confirmed cycle

2026-10-07 00:18UTC. Cleanup-repeat001 captured/decoded/closed/collected/qualified
once, strictFAIL. Counters17/18/10, errors0/0/0. New exclusive cycle: WinMgmt rename
holdsDir and waits via CcFlushCache for parent repository directory Main; volume
flush owns that Main and waitsDir. See retained timeout analysis/deadlock summary.
First0099 run was instead the documented helper hold after all500 operations.

0100 namespace stress001 was prepared but NEVER LAUNCHED; launcher now held.
0101 corrects directory streams to Dir-before-Main while ordinary files retain
Main-before-Dir. Includes cleanup, enumeration, metadata and both flush paths.
Built in fresh fatx-directory-order-001; tree8e12297ca0ed53383fe9aaebef152c26aee5a43b,
driverba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9.
Format/checksum/import checks and exact structure-offset compilation passed.
Fixture preparation9774 completed. Single0101 launch accepted00:18:32.952UTC;
runner74791 and supervisor64781 active. Host deadline about00:33:33UTC, runner
limit00:38UTC. Do not relaunch. On recorded timeout preserve/decode snapshot
before signal/cleanup; on normal return await cleanup, collect and qualify once.
No physical access this turn.

Full persistence soak tools now target0101 (retarget.json), unlaunched and gated
on stress001 PASS. Hardware keyboard readiness question remains pending. Preserve
physical0098/video0093, original0088 and immutable0.1.0. Last pushf41d261; newer
source/reports/notes/skill references need final review/check/commit/push.

## Earlier continuation (historical)

# Cleanup removes observed cycle; corrected repeat active, broader stress prepared

2026-10-07 00:02UTC. Cleanup-order001 completed all500/500/500 operations in
16620ms, exact final files, errors0/0/0, no contended FATX resources or cycle.
Its helper erroneously held on legal WaitForMultipleObjects(wait-all) result2.
Captured/decoded/cleaned/collected/qualified once: historical strict FAIL (no
normal shutdown). This is a harness bug, not a second observed driver deadlock.

New fatx-cleanup-repeat001 corrects ONLY that helper predicate to accept0..2,
keeps the pending-install guard exactly0, and uses the same0099 driver. Accepted
23:59:58.688UTC; runner37537/supervisor79909 active. Deadline about00:10UTC;
do not relaunch. Normal return -> await cleanup, trial.py collect001, qualify.py001.
Timeout -> capture-timeout/decode, then signal, await cleanup and collect once.

Candidate0100 source tree1d90707d7be4393dd899df6e52f13919d1828bf8, driver
4b11ff313ff4b0abfe34f50e4ffe7c19d8fac1f17833245824b062e061bfd9ff built/reviewed.
It fixes enumeration/metadata order and retry-safe overwrite acquisition. Its
fatx-namespace-order001 fixture is prepared but NEVER LAUNCHED and explicitly
held for the old wait-all helper bug. Do not launch it. Instead use the new
fatx-namespace-stress001 fixture: corrected5-worker helper, driver0100,500 rounds
each including metadata/rename/enumeration. Preparation46548 COMPLETED. Run its
Run.ps1 Case001 then supervise after the active repeat cleans up.900s deadline,
1200s runner,600s helper; same retained-snapshot/cold-audit workflow. No run yet.

fatx-lock-order-soak tools are prepared, NOT staged or launched. Staging004 is
gated on namespace-stress001 qualification PASS. It runs the original full15min
mapping/BMP workload with0100 and the established event/binary/hive/allocation
gates. Qualify.py added. Inspect generated scripts before use. Its timeout
decoder uses0100 offsets; no physical qualification follows from emulator PASS.

Skills FATX/validation references updated locally and in tracked copy (wait-all
contract, observed lock-cycle and create retry lifetime/identity distinction).
Latest push f41d261 contains the original deadlock and first0099 build/launch;
newer results,0100, repeat/stress/soak tools and skills need review/check/commit.
Hardware keyboard question remains pending. Physical baselines untouched.

## Prior continuation (historical)

# FATX deadlock reproduced; cleanup candidate built, fixture preparing

2026-10-06 23:45UTC. Concurrency001 timed out and its retained64MiB snapshot
proves cleanup/volume-flush exclusive lock cycle on worker0.bin. The three
helper counters are1/1/1, errors0/0/0. Completed runner87577/supervisor58512,
cold collection and qualification: FAIL; hives/allocation intact, no normal
shutdown, new Messenger7022. See deadlock-summary.json. Do not relaunch.

Candidate0099 in outputs/fatx-cleanup-order changes cleanup to Main-before-Dir;
other reverse-order callers remain, so it is a causal candidate only. Fresh
build68811 completed, source tree1c92d31299f370bbbca346be54c3a8d23012296f;
driver c7e029096a70e36a300a2439dfdb0216d070710700ac89e282d0b59a03542e79.
PE checksum/import review passed. Fixture preparation43857 completed. Candidate
001 launched once at23:45:27UTC, runner40906/supervisor2013 now active. One earlier
premature launcher invocation stopped at missing manifest, no VM/run directory
created. Do not relaunch this accepted attempt.
Same600s deadline/900s runner, unchanged helper; retain/decode timeout before
signal and cleanup, then cold collection and qualification once.

Build preflight required more C: space. Four closed standalone runs051-054
were copied/hash-verified to E:/Codex-private-artifacts/xbox-windows-feasibility/runs,
old paths preserved by junctions, verified from Windows and WSL; originals
removed only after readback verification. Manifest in outputs/task-storage-offload.
Offload35602 completed; C: now about24GiB free. No baseline files discarded.

Hardware keyboard readiness question still pending. No physical writes/launch.
Full emulator null-placeholder004 passed all bounded15-minute gates; old physical
strict failures unchanged. Commit224848c precedes these newer reports and new
candidate work; review/check/commit/push still needed. No automation/subagent.

## Prior continuation (historical)

# Full emulator soak passed; concurrency diagnostic launched

2026-10-06 23:27UTC. Null-placeholder004 completed and all runner/supervisor
processes closed. Cold collection, inventory and qualification completed once.
PASS:527 mappings,16 BMP API cases,50 exact files,34 absent intermediates,
900000ms, normal shutdown/return, events, selected binaries,5hives/full F
allocation. Inherited01B0/01B4 flags remain; not a physical qualification.

Focused FATX concurrency001 runner87577 and supervisor58512 are active; launch
was accepted at23:27:30.866UTC. Inspect outputs/fatx-shutdown-concurrency/001/launch.json
for the accepted launch. Never relaunch. Three threads,500 iterations each,
ordinary file writes/flush/close plus volume flush, no raw-volume writes or
changed drivers. Monitor4594/FTP4596. Supervisor waits600s; runner900s. If it
returns, await owned cleanup then trial.py collect001. If timeout is recorded,
run capture-timeout.py001 and decode-timeout.py001 before capture-complete.signal,
then await owned cleanup and collect. Preserve raw64MiB snapshot privately.
The extended decoder was replay-validated against completion006's retained
snapshot, labels6volumes/732resources, and uses exact source/compiler offsets
plus matched kernel PDB layouts. Shared owners/other lock types remain unknown.

Hardware-ready keyboard question still pending. Physical read-only baseline and
PnP snapshot completed; no remote writes or new hardware boot. Commit224848c
was pushed before the long result; newer reports/decoder/FATX notes need final
review/check/commit/push. Physical FATX0098/video0093, original0088 and immutable
0.1.0 remain unchanged. No automation or subagent running.

## Prior continuation (historical)

# Full emulator soak running; focused concurrency test preparing

2026-10-06 23:15UTC. Null-placeholder003 passed its short workload and all cold
checks; qualification.json records the bounded emulator configuration result.
The inherited01B0/01B4 FAILEDINSTALL flags are now explicitly inventoried; this
is not a full clean device installation or a hardware-qualified package.

Null-placeholder004 launched ONCE at23:09:46UTC, runner79130/supervisor59746.
Original full15-minute workload, no recorder/debugger/UI helper. Expect return
around23:26UTC; deadline around23:31UTC. Do not relaunch. After cleanup collect004,
run inventory.py004 in WSL and qualify.py004. On recorded timeout use retained
post-deadline capture/decode before owned cleanup. No physical launch.

New outputs/fatx-shutdown-concurrency helper is built/import-reviewed. Preparation
session93899 completed; fixture-001.json is ready. NOT LAUNCHED.
It tests500 rounds each in two file write/flush/close workers and a volume-flush
worker. No raw-volume I/O, lock/dismount or driver changes. Use only after004
cleans up and reviewed fixture is ready. Run.ps1 Case001 then supervise.py001,
same exclusive monitor4594/FTP4596. Timeout600s, runner900s; capture-timeout.py
then decode-timeout.py retains RAM for lock-owner diagnosis. Read its README.

Static source review found conflicting Main/Dir lock order in several paths,
but the older stalled snapshot establishes only DirResource wait candidates,
not owners/cycles. Do not patch cleanup alone or claim a root cause yet.
Physical read-only snapshot is complete. Keyboard-ready question remains pending;
no console writes, new Windows boot or automation changes. Update this note as
processes finish. Preserve all physical baselines and release0.1.0.

## Prior continuation (historical)

# Settled emulator workload running; physical snapshot read-only

2026-10-06 23:05 UTC. Null-placeholder001 setup and002 ordinary subsequent boot
are collected, cleaned, and pass their bounded checks. Exact emulator-only null
INF persists with no function service;002 has no new SetupAPI activity. No
driver binaries changed. This is supported configuration for an unused synthetic
device, not a patch for the Windows shutdown race or the earlier FATX flush stall.

Null-placeholder003 launched ONCE at23:03:35UTC, runner33241 and supervisor86518.
Monitor4594/FTP4596. Original527-mapping/16-BMP short workload,15 rounds>=60s,
no UI helper, recorder or debugger. Inspect003/launch.json; never relaunch.
On return/owned cleanup run trial.py collect003 once. On recorded return timeout,
capture-timeout.py003 then decode-timeout.py003, retain raw snapshot privately,
signal owned cleanup and collect. Require workload, events, hashes, hives and
full F allocation; a normal subsequent boot alone is insufficient.

Physical console is reachable at dashboard. Read-only baseline preflight and
SYSTEM/SOFTWARE/SetupAPI/event capture are under outputs/physical-pnp-followup.
No remote writes or Windows launch. GPU PnP registration is still incomplete;
latest physical SetupAPI opens01B0 with no compatible driver. Registry contains
historical PC/emulator entries too; presence in the hive does not prove current
hardware presence. Awaiting user's keyboard-unplugged readiness answer before
any hardware boot; independent emulator analysis continues. FATX0098/video0093,
normal startup, original0088 rollback and immutable0.1.0 remain unchanged.

## Prior continuation (historical)

# Cancel is temporary; explicit null-package test preparing

2026-10-06T22:47:26.118245+00:00. Physical baseline untouched.
Completion006 is collected and cleaned up. Without UI actions, it again opened
the exact1B36:0005 installer; repeat.log blocked restart with258. Snapshot after
return deadline: shell running, no bugcheck, no exclusive resource-wait cycle
observed. No normal shutdown. Thus004's Cancel is not a durable setup solution.
Do not run the mapping/BMP workload on that unsettled state or claim it fixed.

New outputs/shutdown-null-placeholder/001 preparation completed. Runner97817 and supervisor28726 are active;
check001/launch.json for accepted time. Monitor4594/localFTP4596. Never relaunch. Adds an explicitly emulator-only null INF (specific1B36:0005/subsystem/rev),
no function service/binary and no device removal/ID change. Starts from clean
completed004 state, keeps physical and driver binaries unchanged. Read README.
The guest helper observes windows/pending status but takes no UI action and holds
restart while pending. After prep launch once, collect/check actual null binding,
logs, hashes/hives/allocation. Only after success proceed to ordinary subsequent
boot and original workload. All historical controls/held/host-failed cases remain.

## Prior continuation (historical)

# Targeted setup passes; subsequent boot preparation

2026-10-06 22:35UTC. No physical access or driver changes. Completion004 completed
GPU Finish/No and exact-command placeholder Cancel, pending API0 by120s, normal
restart/dashboard return, no popup/new unexpected events. Selected payloads,
runtime hashes, five structural hives and full F allocation pass. Placeholder
still enumerated without a function driver; not new supported hardware.

Subsequent case005 failed before monitor/Windows launch because xemu could not
open nested backing paths. Preserved host-launch-failure.json and cleanup; do not
retry005. Case006 preparation completed; copied only completed004 delta into the
artifact directory, verifies virtual-disk equality and unchanged original, then
stages a minimal repeat.log helper with no UI inspection/actions. Keeps installed
hives and video trace. 006 launch accepted22:36:59UTC; runner9976, supervisor35953, monitor4594,
localFTP4596. Do not relaunch. Deadline22:44UTC. Collect once after owned cleanup.
If ordinary subsequent boot passes, rerun the unchanged original527-mapping/
16-BMP/15-round short rehearsal workload from completed setup state; distinguish
that60-second workload from the physical15-minute soak. If pending gate holds,
retain actual UI/process evidence and investigate without forcing restart.

## Prior continuation (historical)

# Pending queue identified; guarded setup diagnostic continues

2026-10-06 22:26UTC. Completion003 collected, not relaunched. GPU Finish and No
succeeded; new installer is the exact emulator1B36:0005 placeholder. Guard logged
RESTART_BLOCKED_PENDING_INSTALL258 and left the shell running. At return timeout,
one paused read-only64MiB snapshot was retained privately, decoded offline,
and the owned runner cleaned up. No bugcheck, no exclusive-resource wait cycle
observed, no normal restart. Full F allocation/selected payload/hive checks pass,
but this held run is not a normal-shutdown qualification.

Completion004 launch accepted22:27:11UTC. Runner55120, supervisor60487;
monitor4594/localFTP4596. Do not relaunch. Return deadline22:34:12UTC. It adds Cancel only for exact process
command/device ID and observed welcome-page controls. Test device remains present
and unsupported. No null INF, ID change, driver update or physical access.
Inspect records before collection. Expected queue idle after explicit acknowledgement;
never claim a clean result proves functionality for an unsupported device.
Physical FATX0098/video0093/normal startup and original0088/v0.1.0 unchanged.

## Prior continuation (historical)

# GPU completion advances to normal reboot prompt

2026-10-06 22:14 UTC. Physical baseline unchanged; no hardware access this turn.
Read prior sections for preserved failed observer and001 text-matcher miss.
Completion002 launched22:09:18, returned22:12UTC, collected once, all owned
processes finished. One GPU Finish action succeeds; subsequent same-process
System Settings Change asks restart-now and keeps pending API at102 through120s.
No popup, normal shutdown/return, selected payload/runtime/hives and full F
allocation pass. Intended complete-queue gate FAILS: do not call this solved.

Completion003 launch accepted22:15:42UTC. Runner8242, supervisor46642;
owned monitor4594, localFTP4596. Do not relaunch. Return deadline22:22:43UTC. It adds one
No action for that exact same-process GPU reboot prompt and withholds final
restart if pending installations remain. Unknown dialogs receive no action.
Observe/cold-collect003; check stage JSON first.
If timeout, preserve memory with capture-timeout.py003 before owned cleanup.
Driver files and parent staged hives remain unchanged. No ordinary storage/GDI
qualification or physical deployment from these UI diagnostics.

## Prior continuation (historical)

# GPU wizard completion investigation in progress

2026-10-06 22:10 UTC. Physical Xbox untouched; FATX0098/video0093 and normal
startup remain installed. Original0088 rollback and immutable0.1.0 preserved.
No automation or hardware launch. Current work is recorder-disabled emulator
setup/shutdown diagnosis, not a qualified new driver candidate.

outputs/shutdown-installer-windows/001 proves the completed GPU installation
waits on its final Finish page through120secs. A popup occurred and the machine
failed to return within420secs. EventLog shutdown alone was insufficient. After
timeout a paused snapshot found no bugcheck and FATX resource-wait candidates
with winlogon in PopFlushVolumes; resource ownership/cycle is not yet proved.
Owned emulator cleaned up; cold payloads/hives/full F allocation checks pass.

outputs/shutdown-installer-completion/001 returned cleanly, but no completion
action occurred: the exact text matcher expected CRLF, actual control uses LF.
Preserve this non-intervention outcome. Pending102 persisted. Source and build
pins are saved under001. Corrected case002 is being staged independently; only
CRLF/LF normalization changed, all other strict successful GPU page checks stay.
No unknown dialog action. Same120sec restart diagnostic, not a production guard.
Run/launch/collection JSON records must be checked before any action; never
repeat an accepted launch. Case002 launch accepted22:09:18 UTC. Runner session50250, supervisor32049;
owned monitor4594, localFTP4596. Do not relaunch. Timeout is about22:16:19UTC.
Next: finish preparation, launch002 once, collect and inspect GPU_FINISH_ONCE,
subsequent UI/queue state, popup/event deltas and cold integrity. If timeout,
retain raw with capture-timeout.py002 before cleanup to investigate FATX locks.

## Prior continuation (historical)

# Fixed recorder batch complete: failing lifecycle captured

2026-10-06 20:28 UTC. outputs/native-event-recorder. Exactly three new independent
runs003-005 completed; no relaunch, hardware access, debugger, paused capture or
guest change. All owned runner/supervisor/audit processes finished. Physical
FATX0098/video0093/normal startup, original0088 rollback and immutable0.1.0 remain.
No new driver candidate, recovery capture or automation. Do not repeat this batch.

Same seed4c4b8155, immutable base9f51f2a3, recorder executable0ae9b99a in all cases.
003 launch20:16:32/return20:19:32:425 verified records, one popup (strictFAIL).
004 launch20:20:21/return20:23:16:424 verified records, no popup, creation error6.
005 launch20:24:04/return20:27:02:419 verified records, no placeholder create seen.
Every trace reaches kernel shutdown; zero invalid sites;48/50/47 owner commands
remain unknown. Each completes120000ms idle and one normal EventLog shutdown.
GPU installation, nine payload hashes, six runtime hashes, five structural hives
pass. Full F: allocation322 dirs/6742 files, zero orphans/errors. No explicit
mapping/BMP workload or other-partition/full archive audit. These are instrumented
observations; no hardware qualification and no claim of zero recording overhead.

Read FAILING-LIFECYCLE.md, batch-summary.json and batch-review.json. In003:
GPU termination324 -> wait327 -> placeholder creation329 -> resume boundary331
-> successful creation332 -> CSRSS resume boundary334 -> harderror336/337
(c000026b, ONE popup) -> win32k termination338 -> matching termination339
(c0000142) -> exit340 -> wait341 -> first PnP control5 at344 -> kernel shutdown424.
Placeholder ownerff9f9020/PID996, error threadff9a51e0. Token8ac at both creation
samples. Exact GUI shutdown transition and CloseHandle are not captured.
Resume boundaries are pre-call, not proof of successful returns. Installer's
later execution establishes it ran. Control5 arrives AFTER the hard error.

004 samples token8e0 at call329, PnP control331, false create/error6 at335 with
zero token.005 observes GPU wait333 followed by control5 at334 in the same tick;
no placeholder call/harderror. Do not describe005 as an invalid-handle attempt.
Original reviewer assumed one placeholder call per run and failed on005;
review-batch-initial.py and batch-review-initial-failure.json preserve it. Updated
review represents zero attempts explicitly; no launch or cold audit was repeated.
No extra batch launch followed that analysis failure; all three were complete.

Next: inspect why the first GPU installer remains outstanding until shutdown
despite successful SetupAPI installation and reboot-required/remove-veto records.
Use a bounded read-only wait/dialog inspection in a fresh owned fixture, then
choose a supported installation-completion flow before requesting restart. Do
not just extend sleeps, dismiss unknown dialogs, remove the emulator placeholder,
or suppress the hard error. A shutdown-control-only guard is too late for003.
Keep token lifetime separate from the successful-creation failure path. Any fix
needs ordinary recorder-disabled first-install and subsequent-boot checks.
Physical popup owner and Srv2013 remain unresolved; graphics work has own gates.

## Prior continuation (historical)

# Device identified; non-stopping host recorder validated

2026-10-06 UTC, outputs/native-event-recorder. User approved source research,
less-disruptive tracing and a reusable comparison workflow. Physical Xbox
untouched; FATX0098/video0093/normal startup, original0088 rollback, immutable
0.1.0 and previous strict failures remain. No new hardware candidate or recovery
bundle. All owned build, runner, supervisor and cold-reader processes finished.

Source finding: xemu e72e76bd unconditionally creates QEMU pci-testdev at00:00.3
under a memory-controller FIXME. PCI1B36:0005 is that placeholder. Local relevant
sources match the pinned upstream revision; old executable hash matches its
recorded build. This is not a device added by our launcher. Read RESEARCH.md and
device-research.json. Do not assign that identity to the physical console popup,
remove the device to manufacture PASS, or pretend assigning NVIDIA IDs models
the real controller. No device/model/guest-content change in this experiment.

New isolated executable SHA256
0ae9b99a526257a7734c1d5e1742c4eb4b24dc9320d99ee5b150eca5ac197a42.
Opt-in TCG helper records at11 reviewed addresses, no GDB stop/paused capture or
guest write. Low64MiB RAM-only page walks; owner commands use owner's CR3;
unreadable fields remain unknown. Fixed addresses/pinned non-PAE single-CPU
fixture only. Bounded4096 records, buffered exclusive host file. Compiler/source
pins and patch in build.json; borrowed sources restored, original nvnet edits
preserved. First build attempt failed pre-mutation ownership check; next used
per-command safe.directory only. Existing/unused-function warnings documented.

Identical first-install idle002 seeds used in both cases with same new binary.
001 recorder disabled: launch19:32:08, return19:35:07 UTC.
002 recorder enabled: launch19:35:58, return19:38:55 UTC.
Both finish120000ms idle, GPU installation, one normal shutdown, dashboard return,
no popup/new unexpected error, nine payload hashes, six runtime hashes and five
hives pass. Full F: allocation each322 directories/6742 files, zero orphans/errors.
No explicit mapping/BMP workload or other-partition/full archive audit. Case001
ordinary_run_valid=true, case002=false because instrumentation remains explicit.
The clean pair does not fix or waive previous failures and cannot measure zero
observer overhead. This is a new emulator build, not the old binary replay.

002 records423 events, zero invalid-site records, kernel-shutdown boundary seen.
48 owner command lines unknown. CSRSS requests GPU installer termination at326,
exit-handling entry328, wait return330. Placeholder Create call331/tick9696;
PnP control5 on another services thread333; termination request337 for
EPROCESS0xff9a49a0/PID740; Create return338 false/error6 and token0 (entry0x8dc);
matching-process exit handling339. No resume-site hit for that EPROCESS, no
harderror/popup. Termination request precedes return; exit entry follows return.
An earlier event334 reuses PID740 with DIFFERENT EPROCESS0xff9ca020; never merge
by PID alone. CloseHandle and exact GUI-shutdown state boundary are not observed.
This is a clean comparison lifecycle, NOT the earlier failed hard-error path.

Reusable collector: trial.py collect CASE adopts completed reports without
repeating scans; trial.py compare emits paired summary. Run.ps1 guards prior
attempts, supervise.py launches once. Prior-attempt preflight was added between
the two cases; actual emulator arguments/guest seeds were unchanged. Source and
decoder review, negative decoder tests, cold reports and evidence-review.json
are in the kit. Raw host event file/disks/hives stay local and private.

Next: use recorder for a small predetermined unchanged reproduction batch to
capture the actual failing lifecycle. Do not repeat unbounded clean traces or
infer a fix from them. Scope a faithful controller model separately from hardware
evidence. Graphics work can proceed independently where its own gates permit;
physical popup ownership and Srv2013 failures remain unresolved.

## Prior continuation (historical)

# Idle first-install failure: hard-error owner captured

2026-10-06 UTC, outputs/shutdown-idle-trace. Physical Xbox untouched;
FATX0098/video0093/normal startup, original0088 rollback and immutable 0.1.0
preserved. No physical launch, driver rebuild, guest data/register patch,
error suppression, recovery capture or automation. All owned runner,
supervisor, tracer and cold-reader processes finished; no live test remains.

One launch, nt5-shutdown-idle-trace-001, at 19:14:17 UTC; dashboard return
19:17:23. Exact shutdown-install-idle002 seed and base, no guest-content edit.
Read-only paused capture found kernel base 0x823df000. Initial tracer attachment
failed pre-arm reading with E14, zero events, guest resumed; exact source and
failed report retained as trace-early-source.py/trace-early.json. Its unreadable
address was not recorded. Second attachment to the SAME launch records an
unreadable initial site if present, but all kernel sites were actually readable
and verified. No unreadable hit or decoding error. Source snapshots match the
hashes in their corresponding trace reports.

Three retained events: ExRaiseHardError, ExpRaiseHardError, NtShutdownSystem.
First two observe ONE error 0xc000026b from rundll32.exe newdev.dll,DevInstall
for PCI1B36:0005, PID1004/EPROCESS0xff9a0540/thread0xff9dd020, tick9991.
Caller0xa007e406 matches captured win32k and its cold hash. At tick10249,
winlogon PID156 enters kernel shutdown action1. No creation/resume/token-close/
termination boundary was traced. Following win32k termination with0xc0000142
remains matched static evidence, not an observed termination in this run.

Cold event log independently reproduces the ordinary idle002 single rundll32
window-station-shutdown popup. Strict result remains FAIL; ordinary_run_valid
is false. Helper completed120000ms, no explicit mapping/BMP workload, one normal
EventLog shutdown, no other unexpected errors. Normal background I/O remains.
GPU installation succeeded with unchanged binaries and required-reboot veto.
Checked payloads/runtime binaries match; five hives traversable. Full F:
allocation:322 directories/6742 files, zero orphans/errors. Not a full archive
or other-partition audit. No hardware candidate promotion.

Evidence: README.md, review-evidence.py/evidence-review.json, fixture-001.json,
001/{runtime,trace,trace-early,audit,package-audit,allocation,launch}.json.
Exact executed tracer sources preserved; raw disks/hives/media remain private.
prepare.py was written after equivalent inline preparation; it is the reusable
recipe, not a claim of the literal preparation command originally executed.

Next: capture the identified installer's start/resume relative to GUI shutdown
in this smaller fixture with limited observation. Earlier broad/sparse traces
often altered the outcome; do not treat a clean trace as a fix or transfer its
lifecycle to this failed run. Review a proper device package or synchronization
change only with evidence; no device removal, FAILEDINSTALL edits or popup
suppression to manufacture PASS. Physical popup ownership remains unknown.

## Prior continuation (historical)

# Paired idle test reproduces first-install popup without mapping workload

2026-10-06 UTC, outputs/shutdown-install-idle. Physical Xbox untouched;
FATX0098/video0093/normal startup, original0088 rollback and immutable0.1.0 remain.
No hardware launch, driver rebuild, signing-policy change, FAILEDINSTALL edit,
error suppression, recovery capture or automation. All owned emulator runners,
supervisors and read-only NBD readers finished; no running processes remain.

001: original uninstalled rehearsal with common helper/startup only.
002: prior verified INF+unchanged miniport+DevicePath staging, same helper/startup.
Both helpers sleep120000ms then enable shutdown privilege and request restart;
no mapping/BMP workload. Normal Windows background I/O remains. SYSTEM/video trace
preserved during staging; shared payload hashes equal, SOFTWARE differences are
exactly inherited verified DevicePath edit. Parent/seed identities recorded.

001 launched once18:48:34 UTC, returned18:51:30. Cold idle log120000ms, one normal
EventLog shutdown, no popup, no unexpected errors: bounded control PASS. GPU
remains uninstalled (ConfigFlags1024/no driver key/Start1); installation-specific
checks correctly false.002 launched once18:52:28, returned18:55:27. Cold idle
log120000ms, one normal shutdown, but one same rundll32 window-station-shutdown
popup: strict FAIL. Successful full package install, exact oem2.inf, ConfigFlags0,
class0001, framebuf registration, Windows-set Start3, query-remove veto6/code23
requiring reboot. No claim of live stop/remove success.

Both preserve checked payload/runtime hashes, five traversable hives, and no
old mapping/BMP workload logs. F: allocation clean (zero orphans/errors):
control321 directories/6737 files; package322/6742. No other partition or full
archive audit. Both normal guest returns; no forced reset, debugger, capture or
manual dialog dismissal. Earlier first-install001 missed return; this run does
not establish why that prior return failed.

Interpretation: explicit storage workload is not needed to reproduce the popup;
120-second idle does not avoid it. One matched pair does not prove package
causality across all boots, and normal background I/O remains. No hard-error
process identity was traced in these runs; do not assign the owner from SetupAPI
or earlier PCI1B36:0005 traces. Existing three clean installed-state replays
remain distinct from first-install failure. No hardware candidate promoted.

Next: trace hard-error identity and installer completion/shutdown ordering on
this smaller package fixture (002), preserving ordinary vs debugger evidence.
Do not just lengthen waits or suppress installer/errors. Fresh unique attempts
only. See README.md, pair-review.json, per-case audit/package-audit/allocation/
runtime-state reports. Source/import/compiler pins are probe-review.json.

## Prior continuation (historical)

# Installed GPU state: three clean independent emulator replays

2026-10-06 UTC. Added shutdown-device-install003/004; physical Xbox untouched.
FATX0098/video0093/normal startup, original0088 rollback, immutable0.1.0 remain.
First-install001 FAIL and physical soak3 strict FAIL remain. No hardware launch,
driver rebuild, registry change, recovery capture or automation in this turn.
All owned emulator runners/supervisors and read-only NBD audit processes finished.

003 launched once18:28:11, returned18:30:37 UTC.004 launched once18:31:34,
returned18:34:00. Both use byte-identical seed copies backed by the immutable
pre-run002 fixture, separate writable runtime disks, and verified absent result
logs. They are independent second-boot replays, not consecutive reboot cycles.
No GDB attachment or framebuffer-capture intervention.

Both pass527 checks,16 synthetic BMP API cases,50 exact files,34 absent
intermediates,15 timed rounds>=60000ms, first-workload preservation, all checked
runtime/payload identities, five traversable hives, one EventLog normal shutdown,
no new popup and no unexpected event errors. GPU binding/INF/Start=3 remain.
Combined with002: three clean replays. Each new SetupAPI delta contains only
the emulator PCI1B36:0005 client installer (no compatible driver), no GPU
reinstallation. SetupAPI headings are not process lifetime traces; do not assign
popup ownership or the earlier token race to these runs.

Read-only full F: allocation audits: starting fixture6,795 files; each repeat
6,847 (50 payloads+two logs);322 directories/323 directory clusters, zero orphans
or errors.2,127,616 reserved marks retain identical positions. These are retained
emulator reservations, not physical bad sectors. Other partitions and the full
binary archive are outside this added scan. Previous001/002 scopes stay intact.

Evidence: outputs/shutdown-device-install/{003,004,before}, evidence-review.json,
installer-event-comparison.json and README.md. Preparation/run/audit tools refuse
reusing recorded launches/scan outputs. Raw disks/hives/metadata stay private.

Next is NEXT.md: isolate first-time GPU installation from the mapping workload
in a fresh owned fixture, with a matched unchanged/timing control. Let normal
installation complete and request shutdown; inspect events/SetupAPI/binaries.
No FAILEDINSTALL edits or installer suppression. Resolve first-install failure
and display lifetime qualification before proposing a hardware package. Clean
replays do not waive physical Srv2013 warnings or qualify accelerated graphics.

## Prior continuation (historical)

# GPU package installed; first boot FAIL, second bounded boot PASS

2026-10-06 UTC, outputs/shutdown-device-install. Physical Xbox untouched:
FATX0098/video0093/normal startup, original0088 rollback and immutable0.1.0 remain.
Physical soak3 strict FAIL remains; no new recovery snapshot or hardware candidate.
Automations remain paused. Both owned emulator runners/supervisors and cold disk
readers finished; no running processes from this experiment remain.

001 launched once at17:47:08 UTC on the exact previously failing rehearsal.
Authored INF copies only unchanged video0093; existing framebuf.dll referenced.
Only DevicePath is appended offline; no signing-policy or FAILEDINSTALL edits.
Full GPU installation succeeds, ConfigFlags=0, class0001, oem2.inf exact,
XboxVnt5 Start=3 as set by Windows. Query-remove veto6/code23 requires reboot;
no live stop/remove success claimed. Binary identities remain exact.

001 completes527 mappings,16 BMP API cases,50 exact files,34 absent intermediates,
15 rounds>=60000ms and logs one normal EventLog shutdown. It still records the
rundll32 window-station-shutdown popup and misses420-second dashboard deadline.
Read-only unpaused framebuffer capture also timed out; no image or crash claim.
Its effect on the stall is unknown. Owned host cleanup at17:54:21 is explicit;
normal EventLog shutdown was discovered later by cold audit. First run stays FAIL.

002 launched once at17:58:10 and dashboard returned18:00:36. It preserves installed
hives, video trace and first workload, changing only startup/new xwns99 folder.
The helper sources only replace xwns98 with xwns99 after newline decoding.
No GDB/capture intervention. Same bounded workload and first-run preservation,
exact payload/runtime hashes, five hives, normal EventLog shutdown and no popup
or unexpected errors all pass. Package metadata remains intact. SetupAPI now
shows the emulator PCI1B36:0005 installer without a compatible driver; no new
GPU installation. Do not infer a specific token race or physical device from it.

Read outputs/shutdown-device-install/README.md, evidence-review.json and per-case
launch/audit/package-audit/runtime-state JSON. Exact authored INF/compiler inputs
are pinned; fixture manifests distinguish inherited first-stage metadata.
No full allocation audit; recurring baseline SCM7000/Ftdisk49 diagnostic signatures
remain recorded. This cannot waive physical Srv2013 warnings or first-run failure.

Next: repeated bounded boots from independent clones of the retained installed
state; compare installer ordering/timing with unchanged failing baseline. Treat
emulator-only device support separately. Do not promote the INF after one clean
boot or suppress an installer to manufacture PASS. Finish repeated shutdown and
display lifetime qualification before hardware/performance changes.

Current broad project status and remaining release/graphics/network work:
outputs/engineering-notes/STATUS.md. Source/reports to private main only.

## Prior continuation (historical)

# Sparse shutdown traces confirm failed late creation; no popup fix yet

2026-10-06 UTC, outputs/shutdown-popup-workload/003 and004. Physical Xbox untouched;
FATX0098/video0093/normal startup, original0088 rollback and immutable0.1.0 remain.
No new driver, registry change, physical launch or recovery capture. Automation
stays PAUSED and physical soak3 strict FAIL remains. All owned processes finished.

003 reduces observation to seven sites/nine events. Existing GPU installer
creation succeeds (events0–1). Its wait returns0 at event2/tick7925. Services
calls CreateProcessAsUserW for PCI1B36:0005 at3/tick7926 with token0x8ac. Another
services thread enters PnP control5 at4/tick7930; the creation returns false with
error6 at5/tick7931, saved token0 and zero PROCESS_INFORMATION. No hard error.
This captures the shutdown/creation overlap on the exact failing workload, but
not the internal close/query operations. Do not infer those from this trace alone.

004 observes only create returns and kernel hard-error/shutdown sites: three
events. GPU creation succeeds, late PCI1B36:0005 creation fails with error6 and
saved token0, then kernel shutdown. No popup. Entry/token-close timing unknown.
Neither control supplies the lifecycle of001's actual failing installer. Do not
infer breakpoint count caused the difference or claim the popup is fixed.

Both cold audits pass527 mappings,16 BMP API cases,50 exact final files,
34 absent intermediates,15 timed rounds>=60000ms, matching payloads and system
binaries, five traversable hives and one normal shutdown/dashboard return.
ordinary_run_valid=false for both debugger runs; no full allocation audit.
Source snapshots and separate sparse-summary.json files are preserved per run.
review-sparse-sites.py verifies umpnpmgr imports/offsets against the owned DLL;
review-sparse-evidence.py accepts003/004 and asserts workload and capture evidence.

Next change direction from similar clean traces to a real device-installation
intervention in an owned fixture. Preserve001 (actual win32k popup) and all controls.
The earlier display package boot checksum failure was fixed by FATX0098 in
fatx-paging-eof; its ordinary001/002 runs booted the installed package. Start from
the exact failing rehearsal state, retain the same workload, and isolate package
installation/binding from driver rendering changes. Verify normal installation,
registry binding, exact binaries, first/second boot and cold events before any
hardware proposal. Do not copy protected framebuf.dll, suppress an installer or
set FAILEDINSTALL to force a pass. Treat any emulator-only system-device package
separately from physical support. Existing package0096/0097 and diagnostic audio
flags are not automatically approved for physical promotion by these findings.

## Prior continuation (historical)

# Actual shutdown popup reproduced and traced to win32k; separate control clean

2026-10-06 UTC, outputs/shutdown-popup-workload. Two owned emulator launches
finished on the exact previously popup-failing FATX0098 soak rehearsal input
(video0093, unchanged 60-second minimum helper). Physical Xbox untouched:
FATX0098/video0093/normal startup, original0088 rollback and immutable0.1.0 remain.
No patch, registry/device-policy change, hardware launch or recovery capture.
Physical soak3 strict FAIL remains authoritative; automation remains PAUSED.

Run001 reproduced the original EventLog popup exactly. Three captured events:
ExRaiseHardError, ExpRaiseHardError and kernel shutdown. Both hard-error entries
have0xc000026b, rundll32 PID1008/EPROCESS0xff9b4020/thread0xff9dd580. Its command is
newdev installation of PCI1B36:0005. Caller0xa007e406 is verified against matching
win32k.sys code/imports and cold before/after hashes. This is the actual GUI
window-station-shutdown hard error, not a guessed user-mode loader failure.
The following static code requests process termination with0xc0000142; that
following request was not separately traced. One popup, two hard-error entries.
This emulator device identity is not proven to be the physical popup's device.

Run002 added process creation/resume/termination/exit observation:312 events,
no hard error and no popup. Event66 is the PCI10DE:02A0 installer resume path,
PID828/EPROCESS0xff9df020. CSRSS requests its termination at217; exit handling
is observed at218. Services enters native creation at223, then requests
termination of PCI1B36:0005 installer PID884/EPROCESS0xffb3f020 at227, argument5;
exit follows at228. No resume-site hit for that late identity was captured.
Do not claim it executed user code, infer its original creation error from5,
or assign the earlier saved-token race to this run. This clean path does not
supply run001's missing lifecycle. Debugger scheduling remains a limitation.

Both runs:527 mappings,16 synthetic BMP API cases,50 exact final files,
34 absent intermediates,15 timed rounds totaling>=60000ms, matching payloads
and reviewed system binaries, five structurally traversable hives, one normal
shutdown and dashboard return. Run001 diagnostic FAIL; run002 diagnostic PASS;
both ordinary_run_valid=false. No full allocation audit or fifteen-minute soak.
Actual user application testing remains separate. Summaries/assertions in
review-evidence.py and summary.json; exact executed source snapshots under001/002.
All owned runner/supervisor/tracer sessions completed; no experiment running.

Next: narrow lifecycle observation around the identified win32k hard-error and
late installer on this exact workload, avoiding hundreds of unrelated resume
breaks. We now know the actual failing caller/process but have not captured its
creation/resume ordering during a failing run. Preserve this reproduced case;
do not repeat broad clean controls or change drivers to force a passing log.
Any shutdown integration must stop new installation and protect token lifetime
for its entire use. A device package needs explicit behavior/provenance and
separate validation. Do not suppress events or mark devices installed as a fix.
Graphics performance/modes remain separate; no new hardware test is ready.

## Prior continuation (historical)

# PnP token close/use interleaving captured twice; popup still unresolved

2026-10-06 UTC, outputs/shutdown-token-lifetime. Two owned emulator launches
completed, with76/75 events and matched source snapshots. Physical Xbox untouched:
FATX0098/video0093/normal startup, original0088 rollback and immutable0.1.0 unchanged.
No driver/system-binary patch, device-policy change, error suppression or recovery
capture. Soak3 strict FAIL remains authoritative; automation stays PAUSED.

Run001: first01B0 installer creation succeeds using saved token0x770. Later,
installer thread0xffb70da0 checks a nonzero saved token. A separate services.exe
thread0xff9a6580 enters umpnpmgr control5, successfully closes0x770 and clears
the saved global. The installer then loads/passes zero to CreateProcessAsUserW.
Native token queries return0xc0000008; inner creation succeeds but outer setup
fails with last-error6 and removes the child. Events49–66 prove this ordering
within the debugger run. Prior numeric-handle reuse is no longer the sole clue.

Run002 removes generic CloseHandle observation, reducing ignored hits25113→51.
The first01B0 launch again succeeds. The later01B4 call begins with token0x908
and its initial native query succeeds. While inner creation is active, another
thread closes0x908 and clears the global. After inner creation succeeds, a query
of the original handle returns0xc0000008 and outer creation fails with error6.
Events49–65 capture the second interleaving. Do not retroactively assign either
ordering to shutdown-createprocess/001's earlier nonzero reused-handle trace.

Both helpers completed normal restart, dashboard return and cold diagnostic
checks: exact payloads and reviewed kernel/user modules, five traversable hives,
no new popup or unexpected diagnostic event. Baseline SCM7000/Ftdisk49 signatures
are retained explicitly. No full allocation audit or ordinary boot qualification.
Both runners/supervisors/tracers finished; cleanup/source hashes are in summary.json.
An early001 runtime capture predates identifiable NT mapping and is preserved.

The lifetime failure is repeatable under two debugger configurations, at different
points. Breakpoint pauses still affect timing; neither reproduced the actual
DLL-initialization popup. No new hardware test or popup-fix claim is warranted.
Next: correlate the exact hard error and process identity using the previously
failing fatx0098-soak/rehearsal workload, rather than another identical two-minute
clean control. Preserve input hashes and one-launch ownership. Any proposed
shutdown integration must stop new installer work and keep its token valid for
the entire use; another nonzero check alone cannot close the demonstrated window.
Do not silently mark devices installed, suppress events, or patch Microsoft
binaries merely to remove a symptom. Graphics performance/modes remain separate.

## Prior continuation (historical)

# Late installer fails with invalid handle; popup still unresolved

2026-10-06 UTC, outputs/shutdown-createprocess. Two owned emulator boots and
five separately preserved debugger attachments completed. No physical access,
deployment, registry changes or popup suppression. Physical FATX0098/video0093,
normal startup, original0088 rollback and immutable0.1.0 remain unchanged.
Soak3 strict FAIL remains authoritative; no PASS-gated recovery capture.
Automation remains PAUSED. All owned processes finished; cleanup records and
source-hash checks are in shutdown-createprocess/summary.json.

Run001 final trace captures services.exe calling CreateProcessAsUserW for
PCI10DE:01B4 from umpnpmgr at0x767a66de. CreateProcessInternalW succeeds,
returning hProcess0x904/hThread0x8f4, PID736/TID900. The outer call then fails
with last-error6 (invalid handle), after terminating its child. Its input token
was also0x8f4. Matching advapi32 code proves termination argument5 is a fixed
cleanup constant, not the original error or proof of access denial. Matching
umpnpmgr code supplies a saved token at RVA15b64. Handle-value reuse and a
separate close-then-clear block are leads; they do not establish the responsible
close, synchronization failure or popup cause.

Run001 attachments:59 events then instruction-read E14;0 events then localized
E14;8 events through kernel shutdown after unreadable-site handling. Run002:
512-event bound with broad native token tracing; narrowed attachment captured
only kernel shutdown. No missing interval or token-query outcome is inferred.
All five source snapshots match their trace hashes and all resumed the guest.
The original001 CSR interior site's caller field is the stack top, not a return
address; use API-entry callers. Latest tracer fixes that reporting field.

Both cold audits show normal shutdown/dashboard return, completed five-sample
helper, exact payloads and matched kernel32/advapi32/ntdll/umpnpmgr/kernel binaries,
plus five structurally traversable hives. No new popup. Diagnostic checks retain
known recurring baseline SCM7000/Ftdisk49 signatures; these are not strict soak
qualification, full allocation audits or ordinary boots. Debugger effects and
the emulator's older queue/video0096 fixture remain explicit limits.

Next: observe umpnpmgr saved-token lifetime and native token-query/duplication
results around a failing late creation, including synchronization with logoff.
Inspect matched module code before adding narrowly scoped observation sites.
Capture the actual intermittent hard-error caller before claiming causality.
Do not repeat identical hardware soaks, change FAILEDINSTALL policy, suppress
the popup or deploy a driver based on this clean-branch observation.

## Prior continuation (historical)

# Installer queue transition captured; popup still unresolved

2026-10-06 UTC, outputs/shutdown-installer-trace. Three owned debugger runs
completed with normal shutdown, dashboard return, exact payloads and five
structurally traversable system hives each. No popup reproduced. These are
observations, not ordinary/physical qualifications or a fix. Source/reports
reviewed with recorded ordering and binary-identity checks; no physical access, deployment or recovery
capture this turn. Physical FATX0098/video0093/normal startup unchanged;
soak3 strict FAIL and immutable0.1.0 preserved. Automation remains PAUSED.

Run002 provides direct ordering evidence: CSRSS terminates PID916's newdev
installer for PCI10DE:01B0, then services.exe creates another rundll32 for
PCI10DE:01B4 and terminates it with status5 while shutdown is in progress.
Its parameters remain unnormalized and no initial resume was captured. This
establishes the late queue attempt, not successful installation or popup cause.
Run001 showed the same pattern but the next command was unknown. Do not import
002's command into001. PID reuse occurred; use EPROCESS plus PID identities.

New host decoder supports relative process-parameter pointers, verified against
the exact owned ntdll RtlNormalizeProcessParams code and actual002 observations.
It writes no guest memory. Kernel/PDB sites, trace source snapshots, source hashes,
logs and cold audits retained.001/002 captured394/433 events;003 only hard-error
entries plus NtShutdownSystem captured one shutdown event and no hard error.
The exact prior popup message is ntdll resource0xc000026b. Its runtime caller
remains unknown.003 verifies guest kernel/ntdll hashes against the reviewed
binaries; all three use one immutable input fixture with video0096, FATX0098
and the reviewed120-second helper. Preparation does not edit registry hives.

All three owned runners, supervisors and tracers finished; cleanup records are
in summary.json. No running processes or automatic follow-up remain.
Next: inspect the late CreateProcess failure/unwind and window-station shutdown
path in matched owned user-mode binaries, then capture caller/status on a failing
attempt with minimal observer effects. The observed clean branch terminates
with status5 before a captured resume. Avoid more identical hardware soaks,
silent FAILEDINSTALL changes, popup suppression or declaring causality from
clean traces. Video performance/modes remain a separate gated workstream.

## Prior continuation (historical)

# Continuation: shutdown/capacity diagnostics completed; baseline unchanged

2026-10-06, outputs/shutdown-diagnostics. One ordinary owned emulator001 and one
explicitly scoped physical diagnostic completed with normal restart and strict
bounded diagnostic PASS. No driver/device-state/registry-policy edits, no cache
cleanup, no alert suppression. Exact helper17341bytes SHA256
431b6b862aab6f8eb72aef9a342f3e8fd79515b104055c28d64c12483320aefb.
RosBE build/import/hash review and runtime evidence retained; all owned emulator,
supervisor and physical observer processes finished. Automation stays PAUSED.

Physical launch15:35:02UTC, dashboard15:38:03UTC; normal startup restored FIRST.
All5 samples completed,last120345ms,normal EventLog shutdown,no new popup/error,
baseline/helper exact. No fresh full allocation/hive scan was done for this short
observation: do not label it a15-minute storage qualification or replace soak3.

Warnings: owned netevent.dll maps Srv2013 to disk capacity. Captured physical
MountedDevices + pinned HAL map Windows F:/G:/H: to dashboard C:/X:/Y:. Both
Win32 free-space APIs report2.8MiB/21.7MiB/46.3MiB free (0.56%/2.89%/6.18%).
Windows C: (dashboard F:) reports100302127104 free bytes (41.44%). This explains
the reported capacity condition, not an independent raw FAT proof. No deletion
or threshold change. Short run without warnings does not resolve periodic alerts.
Shadow-C mapping beyond these native partition identities remains unverified.

Physical pending installer: PID724,rundll32 newdev.dll,DevInstall PCI10DE:01B0,
Multimedia Audio Controller with no Driver/Service; window is Found New Hardware
Wizard. Still active at last sample but shutdown clean. Emulator pending GPU
02A0 installer likewise remained present through clean restart. Open wizard by
itself is insufficient to predict popup; its specific cause remains unresolved.
Pre/post physical SetupAPI capture preserved, exact append verified. No silent
FAILEDINSTALL acknowledgments or disabled hardware used for a passing result.

Next: trace installer process creation/exit and the specific hard-error process
across a failing shutdown; test queue advancement after shutdown begins. Use
existing resolved-target debugger tooling in owned fixtures, keep debugger runs
diagnostic and retain clean controls. Do not launch another identical physical
soak as a purported fix. Prior soak3 strict FAIL and0.1.0 archives/tag unchanged;
no new PASS-gated recovery snapshot. New helper remains/F/xwnsd01; prior test
folders and manual saves preserved. Xbox at dashboard with baseline0098/0093.

## Previous completed soak (historical)

# FATX0098 timed workload and integrity pass; event gate fails

Completed follow-up2026-10-06 15:14UTC, outputs/fatx0098-soak3. User confirmed
dashboard return. Collected once, restoring normal startup FIRST. No Windows
relaunch. Probe has all15 timed markers ending900000ms, COMPLETE and normal
restart request;527 mappings,16 BMP API cases,50 exact final files,34 absent
intermediates pass. EventLog records one normal startup/shutdown pair.

Strict qualification FAIL: one rundll32 DLL-initialization popup at shutdown,
plus three Srv2013 warnings for guest F:/G:/H:. Exact signatures match prior
physical events; popup also matches prior emulator evidence. No new application
events. Recurrence does not prove cause or harmlessness. Event gates unchanged.
No recovery capture: its full PASS prerequisite is unmet;0.1.0 remains intact.

One readonly allocation scan at /E/Applications/XWNSoak98c launched15:08:16UTC,
returned15:10:07UTC and was collected once:122310 files,6071 directories,zero
errors/orphans. All3439 binary hashes match; nine hives pass header/checksum and
key/value traversal. Installed-state check passes: FATX0098/video0093/Microsoft
framebuf/HAL/loader unchanged, normal startup restored,0088 rollback preserved.
No new manual Paint/Notepad observations belong to this attempt. Prior user
files remain preserved in /F/xwns98-first; second bootloader attempt at
/F/xwns98-second. All current automated output remains /F/xwns98.

Post-run SetupAPI log preserved in artifacts/diagnostics/setupapi.log (capture
metadata setupapi-capture.json); no before-SetupAPI log exists for this attempt.
Investigate installer queue/shutdown sequencing and Srv warning sources next,
before another strict qualification or video change. Historical debugger device
installer findings are leads only. Don't suppress popups/clear failure flags to
manufacture PASS. See event-comparison.json and outputs/video-next/PLAN.md.

All owned observer/scan/audit processes completed; automation remains PAUSED.
Original windows observer ended without return/timeout record; exact dashboard
return time and its termination cause remain unknown. Do not overwrite that
observation with the later scan return. Results summarized in summary.json.

## Earlier state (historical)

# Third FATX0098 attempt awaiting screen report

2026-10-06 15:03 UTC: observer session84500 is no longer known to the tool and
no matching Python process is running. windows-return.json has only the initial
offline observation; no return or timeout marker. Observer termination reason
is unknown. One fresh FTP check at15:03:16UTC timed out. Screen state UNKNOWN.
Asked user ONCE what is displayed and to leave it as-is. No crash, successful
Windows boot, completed soak or automatic restart can be inferred from this.

Automation paused pending user input. No Windows relaunch, scan or recovery
capture occurred. Startup is still recorded ENABLED; it cannot be restored
without dashboard FTP. On return run physical.py collect FIRST to restore normal
startup and preserve results. Then follow the audits below without repeating
recorded stages. No independent console audit can proceed while unreachable.
observer-followup.json records the actual read-only check.

## Launch state (historical)

# FATX0098 third launch attempt running

2026-10-06 14:35:18UTC: new user-authorized retry launched once; FTP accepted.
Current kit outputs/fatx0098-soak3. Exact rehearsed helpers, unchanged drivers,
video0093, HAL and loader. Observer watch.py windows runs in exec session84500;
offline observed14:35:25UTC. No new emulator run or trace reseeding.

User reported Xromwell had hung on the keyboard again. Second attempt collected:
normal startup restored FIRST, all workload files absent, both event logs and
trace byte-identical to before launch. bootloader-outcome.json distinguishes
user report from collected evidence; no Windows workload execution observed.
All five staged files archived/readback-verified under /F/xwns98-second. First
attempt and actual user files remain untouched at /F/xwns98-first.

Current test startup enabled. Automation xbox-15-minute-soak-validation ACTIVE;
quiet until14:53UTC, then inspect sole observer; do not duplicate/relaunch.
On dashboard return physical.py collect FIRST, qualify provisionally, audit
manual files, launch unique /E/Applications/XWNSoak98c readonly scan ONCE,
observe/collect, audit binaries/hives, qualify and final-state if PASS, otherwise
verify-installed. No scan or recovery capture launched yet for this attempt.
If still offline after14:59UTC ask once for screen, do not infer a crash.
Recovery capture only on full PASS; strict warning gates unchanged. Preserve0.1.0.
Pause automation at completion or when blocked solely on manual screen report.

## Previous attempt (historical state below)

# FATX0098 second soak awaiting console screen report

2026-10-06 03:09 UTC: the sole windows observer (session64538) exited normally
after its25-minute timeout at03:08:27UTC without observing dashboard return.
One additional FTP check at03:09:22UTC timed out. Screen state is UNKNOWN;
do not infer a crash, failed workload, or successful automatic restart.
Asked the user ONCE what is displayed and to leave the console as-is for now.
No independent collection/audit work remains possible until dashboard return.
Follow-up automation paused; no observer process remains running.

IMPORTANT: physical.json still records startup_enabled=true. Normal startup
has NOT yet been restored because FTP is unavailable. On eventual dashboard
return run physical.py collect FIRST to restore startup and preserve evidence.
Never relaunch Windows for this attempt. No scan or recovery capture launched.
No qualification result exists for this attempt. Preserve all previous files.
The stage instructions below remain the resumption plan, not completed work.

## Launch record (historical)

# FATX0098 second timed soak launched once

New human authorization: Proceed with a fresh attempt after the interrupted run.
outputs/fatx0098-soak2/physical.json records accepted launch at
2026-10-06 02:43:17.685748 UTC. No driver, video, HAL, loader or trace reseeding.
All baseline hashes match. Exact previously rehearsed probe/matched binaries are
reused; no new emulator run. Prior strict emulator popup failure stays recorded.

All 59 prior test-folder files were captured locally and readback verified before
and after renaming /F/xwns98 to /F/xwns98-first. Both user-saved files are included.
New /F/xwns98 is this attempt's exclusive workspace; no old results were reused.
Original attempt reports remain untouched. Six verifier rejection checks pass.

Running: watch.py windows, exec session64538, started02:43:21UTC; offline observed.
Do not launch Windows again. Let its fifteen-minute workload request its own
normal restart. Follow-up automation xbox-15-minute-soak-validation is ACTIVE,
every five minutes; remain quiet before03:01UTC unless user reports trouble.
At return collect once (normal startup restored FIRST), qualify provisionally,
launch the new readonly scan once at /E/Applications/XWNSoak98b, observe/collect,
audit binaries/hives, qualify and final-state if PASS, else verify-installed.
If still offline after03:07UTC ask once for the screen, never infer a crash.

Do not waive recurring Srv warnings; strict gates unchanged. Capture-recovery.py
requires full qualification and final-state PASS, and includes both test folders.
Preserve0.1.0. Commit follow-up results and pause automation at completion/block.

## Previous attempt (retained)

# Continuation: FATX0098 interrupted soak audited; console on dashboard

Latest: outputs/fatx0098-soak. The user restarted during the final timed wait.
Normal EventLog shutdown is recorded. All527 mapping checks,16 synthetic BMP
save replays,50 exact automated files and34 deleted intermediates passed, but
only14 timed markers (840000ms) and no COMPLETE/automatic restart marker exist.
The full15-minute soak remains INCOMPLETE, not a driver failure or full PASS.
No Windows relaunch was made. Do not reuse these trial/scan IDs.

Post-return allocation audit:122248 files,6069 directories,zero errors/orphans.
All3439 manifest binaries match; nine hives pass header and key/value traversal.
No new application events/popups. Three Srv2013 warnings exactly match previous
records; strict qualification preserves them. No gate was weakened to claim PASS.

User-saved C:\xwns98\manual-apint.bmp (961x532 RGB,1534342 bytes) decodes fully;
C:\xwns98\manuel-note.txt (27 ASCII bytes) was read back after reboot. Exact
hashes and user observations are separate reports. User reports apps opened/
closed, saves, Pinball and an OpenGL application running, with apparently faster
window redraw still visibly filling top-to-bottom. Actual UI reopen success,
measured speedup and hardware OpenGL acceleration are not established.

Normal startup restored. FATX0098/video0093/framebuf/HAL/loader are unchanged;
original0088 rollback remains at/F/xwneof98/rollback.sys. installed-state.json
verifies these independently of the failed timed gate. All owned emulators,
observers, scan and audit processes are closed. New recovery capture was not run
because its full-soak PASS prerequisite was not met;0.1.0 bundles/tag intact.

Next: a fresh timed soak with its own completion and automatic restart evidence,
then updated recovery capture and the separate video plan. No additional Windows
run belongs to this attempt. Pause the follow-up automation after committing.

## Historical continuation

# Continuation: FATX0098 passes the bounded physical trial

Completed 2026-10-06 01:57 UTC. The Xbox is back at UnleashX; normal startup is
restored and no owned emulator, supervisor, scan or audit process remains running.
Latest evidence: outputs/fatx0098-physical-trial. Do not relaunch its used trial IDs.

The single physical Windows run launched at 01:46:56 UTC and returned normally
at 01:50:47 UTC. All 153 mapping checks and 136 output write/flush/reopen cycles
passed across 17 boundary sizes. All 34 final files match their expected bytes.
There are no new application events, popups or unexpected warning/error events.
Normal shutdown is independently recorded in the system event log.

The subsequent read-only F: allocation scan passed: 122,181 files, 6,066
directories, zero orphan clusters, no crosslinks or capture/chain errors.
All 3,439 manifest binaries match; nine registry hives pass header checks and
read-only reachable key/value traversal. These are structural checks, not a
claim about every registry setting's semantics. qualification.json and
final-state.json both pass.

Installed FATX0098 SHA256:
beeaf329f0446d3bdd2ed490fa8143888253115c0ff6c1662b67b82e6619eedd
Video0093, Microsoft framebuf.dll, HAL, loader and mode remain unchanged.
Exact payload hashes are in final-state.json. FATX0088 and original startup
remain preserved locally under artifacts/physical and on the console at
/F/xwneof98/rollback.sys and /F/xwneof98/startup.cmd. No trace reseeding occurred.

Keep emulator findings separate: rehearsal1 passed its probe and cold data but
required forced cleanup after host framebuffer inspection timed out. Rehearsal2
returned normally with correct storage but logged the old-control rundll32
shutdown popup. Its strict emulator gate remains FAIL. eligibility.json records
the bounded decision to proceed based on the prior clean paired0098 regression
and successful API/storage checks; physical qualification waived no popup.

Next: desktop application save/reopen coverage and a longer physical soak with
0098 and the established video unchanged. Use fresh trial IDs and independent
collection/audits; the current run was bounded and serial. Concurrent mapped
truncation/writes, display PnP, faster window movement and higher video modes
remain separate work. Release0.1.0, its tag and recovery bundles are unchanged.

## Historical continuation entries (installed states below are historical)

# Continuation: candidate0098 passes real mapped EOF and cold persistence regression

Latest: outputs/fatx-mapped-eof. Both ordinary owned emulator attempts, their
supervisors and read-only NBD exports are closed. Last emulator cleanup:
2026-10-06T01:30:24.2282173Z. No physical access or deployment. Hardware remains
video0093/FATX0088; release0.1.0 and recovery bundles are unchanged.

Same 0098 driver binary/source as the prior entry below; no new driver patch.
Paired children share a pre-INF fixture, avoiding 0088's registered-display boot
failure so both can run the same real user-mode mapping probe. Inputs cover 17
sizes around sector/page/64 KiB cluster boundaries with deliberately 0xD7 backing
slack. Eight rounds replace/reopen 17 output files with 997-byte WriteFile chunks.

- Old 0088: 153 mappings, 74 nonzero EOF-tail failures (12 input/62 output), zero
  in-file mismatches. Normal shutdown, exact persisted contents, clean allocation.
  One new shutdown rundll32 DLL-initialization popup means strict run gate FAIL;
  keep it separate from the expected mapping failures, do not waive it.
- Fixed 0098: 153 mappings, zero failures; 136 create/replace/flush/reopen cycles.
  Normal shutdown, 34 exact cold files, five traversable hives, unchanged boot/
  display payloads and original input disk slack. No new popup, application event
  or unexpected warning/error. Strict gate PASS.
- Full F: allocation scans before/after both runs: no crosslink/short chain/orphan
  or capture errors; 318 directories/6749 files after. All 2,127,616 inherited
  synthetic bad-cluster reservations retain exact positions. Read-only NBD
  transport cross-checked against existing qemu range reader; no host device.

Manifests pin probe/source/imports, fixtures, payloads and launch/cleanup times.
summary.json separates the negative control, mapping result and strict gate.
README.md and HARDWARE-NEXT.md describe scope, reproduction and next trial.
Source files, raw disk chains and private artifacts retained; do not relaunch
these used IDs or move QCOW parents. No debugger was attached to these runs.

Next: a controlled 0098 hardware storage trial with the established 0093 video
unchanged. Read actual baseline/rollback bytes again; adapt probe input creation
through normal APIs in a unique physical test directory (dirty raw allocation
slack is emulator-only); launch once, collect after normal shutdown, disable
one-shot startup, audit events/content/allocation/hives, then desktop/long soak.
No hardware deployment script or physical result was produced this turn.
Concurrent mapped truncation/writes and generic display PnP quiescence remain
separate gates. Higher modes and physical video performance remain later work.

# Continuation: candidate0098 fixes post-install image checksum failure in xemu

Latest work: outputs/video-nt5-load-trace and outputs/fatx-paging-eof.
All three debugger attempts and both ordinary emulator runs are closed. No owned
emulator/helper is running. No physical access or deployment occurred. Hardware
remains video0093/FATX0088; release0.1.0 is unchanged.

Evidence chain: GPU service was requested, but MmLoadSystemImage rejected
xboxvnt5.sys before DriverEntry. Verified NT5 kernel tracing exposed underlying
STATUS_IMAGE_CHECKSUM_MISMATCH (0xc0000221), converted to 0xc000026c. Both captured
42,215-byte miniport mappings match the exact file hash within EOF; their byte at
EOF is 0x97 from sector slack. NT5 sums a rounded-up word count. Isolated replay of
its checksum instructions returns false with that byte and true when only it is
zeroed. The image's stored checksum is already correct; do not patch/bypass it.
The tracer's last-image hint is not thread-aware; mapped-482.bin is another image.

0098-vfat-paging-eof-zero.patch zeroes only returned regular-file paging bytes
past logical EOF, within the caller's mapped buffer and under existing paging
resource protection. Directory/FAT/raw-volume streams and nonpaging reads are
unchanged. Completion length is retained. No disk-slack rewrite is introduced.
Fresh pinned RosBE build, FATX profile with _WIN2K_COMPAT_SLIST_USAGE:
source tree 873d6b4ff9505e71da119abd99aba301013e1749
xwnfatx.sys SHA256 beeaf329f0446d3bdd2ed490fa8143888253115c0ff6c1662b67b82e6619eedd.
Paired host compilation of the actual common-read functions: old fails 10/63,
fixed passes 63/63 with buffer guards, short/failure and metadata exclusions.
Host tests do not establish NT ABI/cache/concurrency behavior.

Ordinary runs (only FATX payload changed; miniport0096/display0097/INF retained):
- fatx-paging-eof001: Start=1 diagnostic parent; strict cold audit PASS.
- fatx-paging-eof002: actual installed Start=3 parent; strict cold audit PASS.
Both complete four graphics correctness stages and five timing loops, normal
restart, matching payloads, no new popup or unexpected event error. Binding/INF/
owned display file are intact. Start=3 works with the EOF fix. These fixtures
retain earlier audio failed-install flags and the synthetic xemu PCI model.
No full allocation audit or broad hardware/persistence qualification in this turn.

Next: poisoned-tail real mapped-file tests across sector/page/cluster boundaries,
then broader persistence stress and a controlled hardware trial. Do not deploy
0098 automatically from two short emulator passes. Continue display PnP stop/
remove/restart ownership and consumer quiescence separately; higher video modes
and physical performance remain later gates. Preserve the existing physical and
release recovery bundles.

Exact fixture/build/audit hashes and cleanup in fatx-paging-eof/summary.json,
fixture-001/002.json, inputs.json and build-report.json. Guest disks/backing chains
remain local and unmoved. Closed trace RAM and older CPU logs are hash-verified
under E:/Codex-archive/xbox-windows-native/closed-load-evidence-20261006; original
and archived paths are in video-nt5-load-trace/evidence-archive.json. The former
video-nt5-display-package crash decoder now supports --ram for archived captures.
Shared FATX engineering/skill notes contain the EOF/slack lesson; installed skill
matches the versioned source. Latest owned cleanup: 2026-10-06T01:05:25.4311025Z.

# Continuation: display INF installs, subsequent boot fails0xB4

Latest work: outputs/video-nt5-display-package. Five emulator attempts are closed;
all cold audits are complete. No owned test process remains running. No physical
access or deployment occurred; candidate0093, FATX0088 and release0.1.0 remain
unchanged by this work. Neither0096 nor0097 nor the new package is promoted.

The authored INF targets PCI10DE:02A0. Existing0096 miniport and0097 display bytes
are unchanged. It uses the NT5 SoftwareSettings contract and a project-owned
xwnfb.dll filename. Original xboxvnt5.inf is retained for failed-attempt replay;
xwnvideo.inf is the current experimental source. Both are original text; owned
Windows media/binaries, fixture disks and crash RAM remain ignored/private.

-001: updater startup reached a desktop with overlapping wizard/welcome/console.
 No installer log persisted. Guest input attempts had no visible effect; stopped
 for inspection, not normal shutdown. No installation success inferred.
-002: preloaded DevicePath selects the INF, but replacing protected framebuf.dll
 elevated signing policy to Warn. Graphics and normal restart passed, no popup;
 registration incomplete, strict FAIL.
-003: changed only package DLL name/token to xwnfb. SetupAPI completes full install,
 query-removal veto requires reboot, ConfigFlags=0, Driver points to display0001,
 oem2.inf matches staged bytes, Device0 selects xwnfb. Graphics/payload/restart
 checks pass, one shutdown popup makes strict FAIL. Service Start changed1->3.
-004: boot from003's installed state, no guest edits. STOP0xB4(0,0,0,0x50000).
 Kernel RAM decode has VIDEOPRT but no Xbox miniport/display in loaded modules.
 PnP service binding exists with problem0; this does not establish driver startup.
-005: isolated child restores only active-control-set XboxVnt5 Start3->1;
 all5725 keys/17547 values compared. Start1 persisted, but same0xB4 and missing
 loaded miniport. Reject the simple start-type remedy. No normal shutdown in004/005.

Next: trace the actual image-load/device-add path in a fresh owned diagnostic run.
next-probe-plan.json pins matching NT5 kernel hash, public RVAs and entry bytes for
IopLoadDriver, MmLoadSystemImage, IopInitializeSystemDrivers and IopCallDriverAddDevice.
Resolve the actual next-run kernel base; do not reuse prior absolute addresses.
Determine whether service/image loading is skipped, fails, or unloads before GDI.
Keep debugger evidence separate from ordinary validation. Do not deploy an INF
workaround or treat ConfigFlags/Driver presence as functional PnP qualification.
Generic stop/remove/restart ownership and consumer quiescence remain outstanding.

Artifacts: immutable fixtures/seed hashes in fixture-001..005.json; current
reproducible installed-state parent is video-nt5-display-package-004.qcow2;
005 changes one start value. Keep all QCOW parents. Failed boot RAM captures are
artifacts/reboot-crash.ram and artifacts/starttype-crash.ram. Offline decoded
kernel/module/PnP reports are004/crash.json and005/crash.json. Page directories
were recovered from self-references, not captured CPU CR3; shared kernel data only.
Latest owned cleanup:2026-10-06T00:40:11.9405634Z. Shared skill installation and
source/report checks passed; commits include the installation/protection lessons.

# Continuation: ordinary installer-isolation experiments

Latest work is outputs/video-installer-isolation. No physical access or deployment;
candidate0093 and normal startup remain the last hash-verified hardware baseline.
All three owned emulator runs completed normal restarts and are closed. Their
cold audits and comparison are complete; no owned test process remains running.

- audio003 changed only ConfigFlags for the observed01B0 failed installation.
  All5722 hive keys and17533 values were compared, allowing exactly one value
  addition. Graphics, hashes, UC mapping and restart passed; strict audit failed
  with one popup. SetupAPI advanced from01B0 to01B4.
- control003 used the identical immutable0096/0097 fixture and unchanged SYSTEM.
  It passed the strict ordinary audit with no popups, while01B0 installation was
  still pending. This confirms intermittency; it prevents calling the flag a fix.
- pair004 changes only01B0 and01B4 failed-install flags. It passed the strict
  audit with no popups and returned at2026-10-06T00:01:51UTC. Its next installer
  target was02A0, the GPU itself. SetupAPI reports no compatible driver, while
  baseline enum metadata has Service XboxVnt5 but no Driver value (flags0x400).
  Boot-time binding is working; complete PnP driver installation is missing.
- Prepare001/002 did not boot. Absent-value lookup and the shared output-path
  guard rejected those attempts before guest hive writes. Artifacts retained.

The registry flags are diagnostic interventions, not audio support, a driver
correction or a deployment recipe. Do not promote them based on a clean boot.
No cache/mode/storage changes. Free host C: space was20.28GiB after these runs.
Keep all QCOW backing parents. Full miniport PnP stop/remove/restart ownership
and consumer quiescence remain separate requirements before promotion.

Next concrete task: inspect/package a proper NT5 display INF for02A0, matching
the installed service/display binary contract, then test real installation in a
new owned fixture. Do not suppress installation of the GPU with FAILEDINSTALL.
Retain original boot bindings and rollback; installation may invoke the still
unqualified PnP stop/start paths. A clean control is not a reason to waive popup
checks. The shared skill now records this setup-vs-boot distinction and the
need for target-process address-space reads; structural validation passed.

## Previous display and shutdown work

Physical0093 remains installed with normal startup. No physical access occurred
in the work below; the last hardware hash verification is23:07:22UTC Oct5.
Release0.1.0 and FATX0088 are unchanged. Neither0096 nor0097 is promoted.

New emulator evidence, Oct5:
- video-startup-detached: unchanged0096,120-second settling, startup CMD exits
  before shutdown. One ordinary strict audit PASS, with four GDI copy checks,
  five timing loops, UC RAM mapping, payload hashes and clean normal restart.
- video-surface-lifecycle: new0097 ReactOS display replacement. Fresh source tree
  a0a3f8b6bbd9c4fb60042554dd6d24130b0afddf; compiled failure-injection tests PASS.
  DLL SHA2563d4c5c2659c06f9ae4c9a735a99ad972d4e773e02a0f1b7d4d8c2d18053e9db7.
  Ordinary GDI/payload/mapping/restart checks passed, but two rundll32 shutdown
  popups made the strict audit FAIL. Detaching startup is not a general fix.
  Run nt5-video-surface-lifecycle-001 closed at23:37:47UTC. Its fixture002 and
  failed unbooted fixture001 remain preserved. The full DLL uses two clusters;
  a stripped version lost nonpaged section flags and was rejected, never booted.
- The installed framebuf.dll is Microsoft5.00.2180.1, not the ReactOS source.
  provenance.json and baseline-ddi.json separate these implementations.0097 fixes
  source-level failure cleanup, not an established defect in the installed DLL.
  Its public baseline callback table has no BitBlt/CopyBits rendering callbacks.
- video-shutdown-exits captured25 NtTerminateProcess calls, but unresolved target
  handles; video-shutdown-targets watched the wrong PspTerminateProcess site.
  Both debugger runs had clean cold checks, but are explicitly unqualified for
  ordinary boot because pauses alter timing. Historical failures remain retained.
- video-shutdown-resolved-targets resolved a CSRSS termination target as
  rundll32.exe newdev.dll,DevInstall for PCI10DE:01B0. SetupAPI confirms PID932
  and driver-selection error0xe0000228; its registry description is Multimedia
  Audio Controller. This unfinished installer was alive at shutdown. The traced
  run had no popups and clean cold checks, but ordinary_boot_qualified=false.
  It does not prove the popup cause. Owned cleanup completed at23:42:59UTC.
  All owned emulator, supervisor, debugger, audit and build processes are closed.

Immediate next work: inspect the unfinished01B0 install queue and its shutdown
interaction in an ordinary reproduction before promotion; then
complete miniport PnP stop/remove/restart ownership and consumer quiescence.
0097 covers surface failure unwind and normal release, not full PnP lifetime.
Retain0093 and unchanged cache policy; no measured speedup or HD-mode change.
Host C: had about20.6GiB free after the build. Twelve closed owned CPU logs were
losslessly compressed; backing parents/source caches were not removed. Check
the actual host free space before another fresh20GiB-preflight build.

## Previous mapping investigation

Physical candidate0093 is restored. Final read-only FTP verification at
2026-10-05 23:07:22 UTC passed for video, FATX0088, HAL, loader, launcher,
pre-dim backup and normal startup. Evidence: outputs/video-mapping-audit/final-baseline.json.
No emulator, observer, debugger, build or automation remains running from this work.
All owned sessions have closed; backing chains and source caches remain in place.

0094 observed UC GPU-aperture mappings on both emulator and Xbox; known loader
alias endpoints were absent. Emulator strict audit passed. Physical graphics,
payload and normal restart checks passed, but strict qualification failed on two
rundll32 shutdown popups. Logs retained and0093 restored; no performance claim.

0095 direct RAM through VideoPortMapMemory failed before desktop in xemu:
STOP E0580001 (7,57,03c00000,00400000), ERROR_INVALID_PARAMETER.
This failure is preserved;0095 was never deployed to hardware.

0096 uses owned MmMapIoSpace(MmNonCached) with reference/unmap/unload cleanup.
Fresh reconstruction and compiled execution checks passed. Source tree:
eded91e06d6cac60a1cf66bc8a05117ebfa6a71a; miniport SHA256:
e8021879bd606eb9cfc6927fbf50565c41781779af86e56f4678fa890b6eb6ec.
Both ordinary emulator runs passed pixel, direct-RAM UC, payload and normal
restart checks, but strict audits failed on two rundll32 shutdown popups.
Changing settling from30 to120seconds did not eliminate the failure.
See outputs/video-direct-map and outputs/video-direct-map-settled.
No0096 hardware deployment or measured hardware speedup occurred.

Exploratory nt5-video-shutdown-probe-001 used the same binary and120-second
protocol. Initial debugger handshake timed out and paused the guest; the corrected
handshake resumed that same guest. No NtRaiseHardError event was captured before
the supervisor closed the returned emulator. Cold logs show the same two popups.
Debugger timing interference disqualifies this run as ordinary validation;
outputs/video-shutdown-probe preserves both attach failure and final observations.
Cleanup completed at23:05:47 UTC; no popup root cause has been established.

Immediate next work:
1. Trace the shutdown popup creation path; the NtRaiseHardError breakpoint did
   not capture it. Do not select a clean timing retry as proof of a fix.
2. Complete PnP stop/remove/restart mapping lifetime, including consumer quiescence
   and asynchronous completion. Normal unmap/unload alone is not a general driver.
3. Re-run strict ordinary emulator checks, then one bounded physical timing trial
   with rollback. Keep0093 and release0.1.0 intact. No HD-mode change yet.
4. C: last measured about19.7GiB free. Fresh source builds require20GiB preflight;
   review safe archival of closed artifacts before another build. Never remove
   QCOW backing parents or unreviewed source caches to make room.

0093 physical qualification: outputs/video-trace-reuse-settled/qualification.json
and physical.json, two clean cycles at22:15:47.892872Z and22:18:01.946565Z Oct5.
SHA256 3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf;
source tree329a29d61af1620a9fc005b0d8fcfb9e1a937d20. Normal startup restored.
Private verified overlay: E:/Codex-archive/xbox-windows-native/postrelease-video-reuse-20261005,
ZIP SHA256 44c613e74b8a82e1494cc60140e3ceee27d53df4762e1ede97e22800242857e5.
No archive restore test claimed. Retain0092 physicalSTOP0xB4 and prior0093
strict popup failures; later clean-start/reuse0093 passed without any waiver.

## Results

- Added one-command native reconstruction/package tooling. Pipeline002 completed
  fresh source replay, seven native components, Cromwell launcher and verified
  eight-file overlay. It is not a Windows installer. The complete overlay now
  passes one emulator boot/GDI/restart and cold byte/event checks in
  outputs/rebuilt-overlay-validation. Broader/physical qualification is pending.
- HAL reconstruction now explicitly enables FRAMEBUFFER_ONLY_PCI as required by
  the qualified physical artifact. The later live CMake cache was misleadingly
  OFF. Builds001-004 remain compilation evidence, not baseline-equivalent.
- Repeated package assembly from identical inputs is byte-identical. Fresh
  compilation is not yet byte-identical. FATX/video/network/boot-video .text
  matches captured baseline. Exact tested-package comparison attributes all HAL
  code differences to relocation slots; two rosload non-pointer differences are
  diagnostic line-number constants. Pointed data is not fully normalized.
- GDI v2 failed due to startup-dialog occlusion. V3 enforces visibility and
  passes all four copy checks, including both overlap directions. One emulator
  launch, normal runner restart, dashboard return and cold EVT6006 verified.
  Qualified FATX/video hashes unchanged. See outputs/video-next/probe-v3.
  Timings include host build activity and are not Xbox performance evidence.
- Shared xbox-native-bringup skill updated and structurally validated. FATX
  notes, public-release plan, and xemu patch inventory remain available from
  the root README. No upstream submissions or public visibility change.

## Host incident and retained artifacts

- Pipeline001 filled C:; WSL fell back to read-only. Archived 46 closed owned
  CPU logs to E:/Codex-archive/xbox-windows-native/trace-archive-20261005 with
  SHA256 verification. Original run folders contain cpu-trace.archive.json
  pointers. No QCOW backing chain was relocated. Ubuntu then mounted writable
  without filesystem repair or a global reset. C: had about24GiB free after
  that retry; the latest reading is about19.7GiB (see above). New builds check actual Windows backing-volume space,
  not only Linux virtual capacity. Keep watching host space before more fixtures.
- Failed pipeline001 checkout retained at
  /home/paul/xbox-windows-native/build/package-reconstruction-001.
- Successful one-command output:
  /home/paul/xbox-windows-native/build/package-reconstruction-002.
  Private overlay copy: E:/Codex-archive/xbox-windows-native/reconstructed-overlay-20261005.
  ZIP SHA256:5ada6fb5887227f4c4b50d2197bb7a498342b4cd2f4eab90d81716990d5d30e3.
- Earlier reconstruction001-005, launcher-reconstruction-001 and overlay001/002
  retained under the same native build root. Do not reuse attempt identities.
- Closed owned GDI runs: nt5-gdi-baseline-001 (old failure), -002 (occluded),
  -003 (PASS). Fixture parents and children remain at original paths.
- Verified 0.1.0 recovery bundles remain at
  E:/Codex-archive/xbox-windows-native/0.1.0; no restore was performed.

## Next actions

1. Repeat-boot maintenance is complete for two bounded physical boots. Keep0093
   installed and preserve the trace file. Do not deploy0092 or disable the broad
   trace/PnP flags. Further removal of file I/O is a separate unqualified change.
2. Use physical003 as one bounded baseline: fill/upload2.10/2.36ms, readback50.14ms,
   overlap56.67/29.71ms for256x128. Investigate cache aliases/stride/copy paths;
   this does not measure dragging FPS or prove a cache cause. Extend reconstructed
   overlay storage/network coverage in a new fixture. Its current emulator PASS
   does not establish hardware equivalence. Never reuse attempts001-003.
3. Complete local user-media assembly and toolchain environment pinning for a
   fresh reproducible installation; full OS packaging remains open.
4. Plan 720p then1080i after console revision and cable/HDMI adapter are known.
   Coordinate loader/HAL/framebuffer reservation/miniport. Current HAL BAR2
   suppression is a compatibility workaround, not an accelerated GPU contract.
5. Prepare sanitized public export with per-component licensing and private
   history review. Prepare focused xemu reproductions against current upstream;
   no submission until the concrete proposal is reviewed with the user.

UnleashX root Windows entry was installed previously with backup/readback.
Dashboard visibility is not user-confirmed; do not reinstall it to refresh notes.

Host C: free space is about19.7GiB after these builds. The20GiB fresh-build
preflight should block additional source builds until reviewed artifacts can be
archived safely; no backing chains or source caches were removed.

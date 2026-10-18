"""Prepend exact continuation after closing capture469 and host-only470."""
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
head='''# Current:469 CLOSED raw status0x0808; diagnostic busy-bit bug identified;470 HOST-ONLY

Read marker-capture468 REPORT/DESIGN/NEXT/final-review, physical-status469
REPORT/DESIGN/NEXT/status-source-review/final-review/actualrecords and
marker-busy470 REPORT/DESIGN/NEXT/host001/final-review. No launch queued.
Previous pushed b560abf5; review/check/exact-stage/commit/push current changes.

469 single physical launch01:28:03UTC2026-10-18, dashboard returned01:28:26UTC.
Actual primary176B phase6/copiesPASS, refusal192B reason12/result5. Full marker:
transaction0,startmask1,completed0,idle0,completion0x0808,2polls,4writes,0acks,
3TSCreads,start1967119314916,end1967119317860. Raw hardware status captured.
No second marker/original loader reached; later hardware completion UNKNOWN.
No new user screen observation. Original launcher/startup,5hives,2eventlogs,
video trace exact;5hives clean/rawagreement,zeroevents,229actualnegatives.
No full FATX scan;463Eclean remains latest. No consoleC/SDK/driver/startup changes.
Private C:/xwn469/physical001; consumed E:/Applications/XWNBoot468a NEVERrerun.

Pinned upstream Linux nForce status definitions identify0x8 hostbusy,0x800 busbusy.
Our465/466/468 helper wrongly rejects hostbusy. This diagnoses the NEW marker
refusal, NOT old intermittent Windowsboot. Upstream xemu transaction synchronous;
source-to-exacthistoricalbinary identity not requalified in this comparison.
PrimarysourceURLs/commits/hashes in469status-source-review, private source001.

470HOST-ONLY fouroperand correction: knownmask includesbit3; wait on0x808 in
idle+completion. Busy neverPASS, busy+done waits, busy+errors refuses. No extra
clear/retry/reset/IO. Existing4096reads/64millionticks, register/flags preserved.
51actualassemblycases+51immutable repeats, all32old+19new, privateC:/xwn470/host001.
PrivilegedIO/CLI/TSC MODELED. No XBE/emulator/physical integration of470 yet.
Next NEW integration of470 into468 wrapper and poststack payload, newnamespace,
fullrefusalcapture/newstrictdecoder, source reconstruction, actualwrapper/file
failure tests, freshownedemu/coldaudit, then watchedphysical. Preserveolddecoders.
Never call old467/469 failures success or claim originalboot/D3D fix.

468build001537170B SHA184c08709673d0b2a9128579dc248782b2b6e9431b816e43c0cb0ee860dd46bc.
Capture-only exact466child; payloadbyteidentical. Host85wrappercases73fullrefusals
243negatives. Freshemu001 normalbothmarkers/loader/stack/continuationPASS.
Freshemu002 EXPLICITdebugger injectedrefusal afternaturalfirstmarker;192Bmemory
anddiskexact. Notnaturalstatus/ordinaryboot.514actualrecordnegatives. Bothfull
BP/physicalmodecleanup,orderlyhostexit0,nofallback; stoppedbeforeWindows.
Cold10GBmaps,545/816changedbytes,strictFALSE,276dirs6554/6555files255clusters,
zeroerrors/orphans,5hives3binariesexact,EEPROM/seedunchanged. Preservefailed
decoder001 transitionlaststatus assumption, cold002 pathlookup, review001 invalid
handle mutation; correctedversions separate;no guest rerun. All ownedsessions
CLOSED:prepare50611,emu95776/75559/51052/99371,stage63034,physical62180,readsearch59449.
Newwork onC; lastC~25.3GBdecimal,E~21.5GBdecimal. Keep20GiBprojectedreserve.
No oldfailed/completedruntimeparents, backingmoves,offload/deletion, orrepeat IDs.
Normalboot E:/Applications/XWNEBoot/default.xbe6240...,normalstartupda47...,720p
protected. HistoricalphysicalCofflimits/D3D/1080i/WindowsFt49 limitations unchanged.

'''
p=W/'outputs/engineering-notes/CONTINUATION.md';s=p.read_text(encoding='utf-8');assert not s.startswith(head.splitlines()[0]);p.write_text(head+s,encoding='utf-8')
status='''# Latest: physical marker busy-state diagnosis captured

The capture-only469 diagnostic recorded0x0808 while its first LED transaction
was still busy, then deliberately refused before Xromwell. The normal boot
installation is unchanged; five hives pass integrity checks with no new events.
Primary controller source confirms our diagnostic omitted the host-busy bit.
This explains the diagnostic exit, not the historical intermittent boot issue.

The proposed470 correction passed51 actual assembly host cases and51 immutable
repeat checks. It waits on both busy bits under the old bounds and still refuses
errors. It is HOST-ONLY, not integrated or installed. Next is a new wrapper build,
emulator qualification and watched console trial. No hardware run is queued.
468's capture protocol passed normal and debugger-injected emulator paths; both
are closed and cold-audited. Evidence/failures and original files are preserved.

'''
p=W/'outputs/engineering-notes/STATUS.md';p.write_text(status+p.read_text(encoding='utf-8'),encoding='utf-8')
p=W/'.gitattributes';s=p.read_text(encoding='utf-8')
for name in ['marker-capture468','physical-status469','marker-busy470']:
 line=f'/outputs/{name}/** -text whitespace=cr-at-eol'
 assert line not in s;s+='\n'+line+'\n'
p.write_bytes(s.replace('\r\n','\n').encode())

from pathlib import Path
K=Path(__file__).resolve().parent;N=K.parent/'engineering-notes'
entries={
'CONTINUATION.md':'''# Current: 467 watched diagnostic CLOSED; first LED marker refused physical status

Read physical-marker467 REPORT/DESIGN/NEXT/final-review and actual stage/launch/
observation/collection/cold-review002/user-observation001. One accepted SITE at
2026-10-18T00:43:20.952578Z; user: "Amber, the screen changed but stayed black and
exited". Dashboard returned00:43:43.840994Z. Complete primary176B phase6/copiesPASS;
complete refusal96B reason12/result5/close2 proves NEW marker deliberate refusal
before original privileged handoff. RawSMBusstatus/transaction/counts UNKNOWN:
only volatile96B marker held them; this build didnot persist them. Do not infer
the historical intermittent launcher failure, second-marker PASS or bootfix.

Original6240launcher/startup,5hives,2eventlogs,video trace byte-identical; candidate
and owner exact.720p protectedbaseline verified.5hives clean/rawagreement, zero
new events/shutdown delta0;28actual refusal negatives. No full allocation scan;
latestphysicalEscan remains463clean. No consoleC access, driver/startup change,
SDK change or new D3D result. New folderE:/Applications/XWNBoot466a is consumed;
never repeat/reset it. Private captures C:/xwn467/physical001. Existingnormalboot
path E:/Applications/XWNEBoot/default.xbe remains original. No hardware queued.

466build001 unchanged537170B SHA74a479078f378b8f02c54d4bd146765a7d860031116f636a3658a6616c2bedf5.
The source uses safe pre-paging refusal file path; stage2 failure intentionally
halts, but this physical refusal never reached it. Emulator466003 stays separate.
Cold-review001 import failed missing process LD_LIBRARY_PATH for existinghivex;
source/failure retained. Fresh002 with explicitoffline-disk librarypath PASS;
no dependencyinstall. Owned43710stage/4824launch-observe/17949audit CLOSED, collect
and closeout exit0. Preserve all prior failures/rollbacks and originalbaseline.

Next NEW capture-only refusal extension: serialize whole96B marker beforecleanup,
versioned strictdecoder, boundedwrite/flush/close withfailures, no extraSMBuscall,
no statusmaskrelaxation. Host-test exactassembly/serialization and newownedemu
beforeanotherwatchedphysicaltest. C reserve20GiB; E margin tight, useCprivate.
Previous pusheecd114a; check/exactstage/commit/push thiscloseout.

''',
'STATUS.md':'''# Current: watched LED diagnostic returned through its own refusal path

The user saw amber and a black screen, then exit. The saved refusal identifies
the new first LED marker: it rejected a hardware status outside its accepted
mask before handing control to Xromwell. This explains this diagnostic exit,
not the older intermittent startup failures. The raw hardware status was not
persisted, so the next diagnostic must capture it before changing any predicate.

Original launcher/startup, all five hives, event logs and video trace are
unchanged; no Windows events were added. The console is back at the dashboard.
No further launch is queued. See [467 report](../physical-marker467/REPORT.md).

'''}
for name,prefix in entries.items():
 p=N/name;old=p.read_bytes();assert not old.startswith(prefix[:30].encode());p.write_bytes(prefix.encode()+old)
p=K.parents[1]/'.gitattributes';data=p.read_bytes().replace(b'\r\n',b'\n');line=b'/outputs/physical-marker467/** -text whitespace=cr-at-eol\n';assert line not in data;p.write_bytes(data+line)

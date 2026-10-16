# 420: diagnostic launched by FTP; dashboard return not observed

User explicitly authorized automated launching, superseding the manual launch
request. Physical-launch001 records ONE SITE EXEC at23:10:14.927824UTC, accepted
200. Before launch the diagnostic and original XBE, selected protected files,
and all frozen stage input hashes were exact; no trace or inventory report existed.
Physical-return001 observed12 timed-out connection attempts through23:11:58UTC,
closed23:12:03UTC. FTP return was not observed; screen and application-entry state
remain unknown. No repeat launch sent. User asked for screen state and, if black,
a manual restart to UnleashX. No collection has run. All host processes closed.

After dashboard return run collect-physical.py once with authorized FTP environment.
It preserves any trace/report bytes privately before decoding and verifies the
selected baseline. Missing/partial/invalid trace remains evidence, never an
ordinary inventory PASS. Older manual-pending paragraphs below are historical.

418 FTP and419 manual File Explorer launches both stayed black and left no final
report. Both were manually restarted; selected Windows files and original utility
bytes remained exact. Neither result establishes application entry or a failed
probe. No repeat of either closed attempt was made.

New420 build001 adds a native Partition1 create-only xwn-trace420.bin before the
original E mapping/query sequence. Records are32 bytes, maximum2048 records,
with sequence/stage/phase/argument/result/reserved/checksum. Each write and flush
must succeed to continue tracing; errors are sticky and terminal status exposes
them. Kernel calls themselves are not claimed cancellable or time-bounded. No
missing after-record alone proves the operation caused the stop: the following
trace write could also fail. A missing trace still leaves pre-entry versus trace
creation unresolved. Existing trace refuses rerun rather than overwriting.

Instrumentation brackets E preparation, memory/video settings, separate Conexant
and Focus SMBus reads, free-space query, each mode enumeration, all PCI ID/class
reads, final report save, display mode change, sleep and reboot request. The normal
inventory query text reconstructs exactly after the explicit additions are removed
(source-review001). No probe removed or made to return a fake result. Timing and
disk writes differ; this is a diagnostic, not ordinary utility qualification.

Pinned nxdk58427c prebuilt libraries; all SDK pins unchanged. Build lease held.
110592-byte XBE SHA2567347176aac86a8ea24aea4e0113680de30394fb260dfa50f0efd5f7e37a58931.
Private build E:/xwn420/build001. Only inherited edata merge warning; no C warning.
The independently implemented decoder rejects33479 modeled transport/coverage
mutations and keeps incomplete traces incomplete. No ThreadSanitizer/atomic-disk
guarantee. Binary trace is private; summaries and native source are public.

Fresh unused official blank8GiB fixture/private EEPROM/ports/config under
E:/xwn420/emu001, owned emulator lease and immutable executable hardlink. No
executed disk parent. One run ended with exit0/no fallback. Cold read found1074
complete trace records, all512 PCI ID query pairs,12 present PCI devices, saved
inventory report, successful display setup and terminal reboot request. Full E
allocation3dirs/2files/7clusters,0 errors/orphans; prior files unchanged, QCOW
checks pass and EEPROM unchanged. Reserved absolute byte1540 changed as before;
whole-disk unchanged gate FALSE, not waived. No physical/display screenshot or
Windows shutdown claim. Emulator is CLOSED, never relaunch/recollect/parent.

stage001 uploaded/readback-verified ONLY E:/Applications/XWNInfo420/default.xbe,
with original utility and selected Windows baseline unchanged; no C access,
Windows changes or416 loader activation. No launch command sent. User asked for
one manual File Explorer launch of the NEW path. Physical launch/result pending.
All host commands closed, no observer running. Do not duplicate accepted/manual
launches. On reported dashboard return retrieve trace and any new inventory report
twice, preserve original bytes before decoding, record invalid/partial/missing
traces as evidence, verify protected files. No physical PASS yet.

Interlace discussion/source review and discriminating future display test are
in INTERLACE.md. Existing720p demo unchanged; no1080p conversion or speculative
field/driver patch. Public utility hold remains pending physical diagnosis.

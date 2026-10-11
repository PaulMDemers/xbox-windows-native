#234 CLOSED: worker journal publication succeeded, ownership still refused

Head before turn1624710. Fresh emulator trace002 CLOSED 2026-10-10T23:59:58.917659+00:00.
Controller112984/runner116228/tracer113124/
observer113988 CLOSED; cooperative leases released. Never relaunch,
recollect or audit closed trace002. No physical access, device merge or tag change.

ONE live worker request reached state3/tuple_published1; immutable report exactly
matched subsequent reads after CPU stop and after the separate232 preservation
request. Reader no longer locks PG or FIFO or reads the mutable journal. Worker
copies under PG after releasing FIFO, publishes after releasing PG, then takes
FIFO again. Ordered one-shot terminal and timeout logic is separate from the
preservation request. No guest halt/register/wait/IRQ mutation in the new snapshot
hook. Actual233 record sites and actual232 parser/preservation stay unchanged.

Actual bounded ring total16765, count256, overwritten
16509. 51 producer pairs,
51 guest-INTR pairs (51
clear NOP), 50 complete captured lifecycles.
Missing adjacent pair boundaries0; leading/
trailing unmatched rows and overwritten prefix remain visible/unknown. Captured
reset pairs0 is not a claim that no reset occurred.
Parameters ['0x7a080101'];
ERROR mask00100000, trapped100, NSOURCE1. No guest PC/ISR source pin.
Current PG-only row waits2/pending00100000,
FIFO-invalid/all ten FIFO words zero. This is the earlier LIVE sample, not the
stopped queue/current state. Copies of genuine guest dual-lock rows retain valid
FIFO words; producer rows remain FIFO-invalid. No ownership follows from an ack.

Separate stopped preservation state4/reason20/stop
4; waits2->2, steps0,
words0. GET03f7c5e8/PUT03f8c858 unchanged at
gate; numerical backlog66160 bytes. No wait cleared or
producer resumed INSIDE that request. references_retired/native_grant remain0;
surfaces/dirty/downloaded/bytes all0. 212992 actual reserved before/after bytes
unchanged; physical GDB mode restored, zero breakpoints/memory/register writes.
Guest resumed only after safe refusal and mode restoration.

Windows launch recordTrue, dashboard return
True, normal6006 count1.
CPU scopeTrue, observation scopeTrue.
Full cold allocation 320 directories/6724 files/
321 directory clusters, errors0/orphans
0; integrityTrue. Five structural
hives, selected protected hashes/startup/history and unchanged211 device policy
are checked. No synthetic null devices. Warning/error deltas: [{'source': 'Ftdisk', 'event_id': 49, 'type': 1}]; new
application events0. Strict qualification
False; preservation/ownership remain UNQUALIFIED.
This is one debugger-observed boot, not ordinary GPU acceleration, repeated-boot
storage qualification or an all-file-content audit. USB's ccd210f stale marker/
two invalid hives remain a separate unresolved repeated-boot failure.

Matched actual compiled helpers/QEMU atomic headers with explicit host clock,
register/FIFO/mutex/object/string adapters passed O0/O2 ASan/UBSan:
checks=26873006 race_pairs=20000 publication_pairs=2000 wrapped_records=100000 completion_winners=6585 timeout_winners=13415 immutable=covered late_completion=hidden fifo_validity=covered
checks=28865336 race_pairs=20000 publication_pairs=2000 wrapped_records=100000 completion_winners=7290 timeout_winners=12710 immutable=covered late_completion=hidden fifo_validity=covered
72 actual guard checks/PowerShell syntax/source lock review passed. Three source
files changed versus selected233; seven borrowed sources restored. Selected exe
SHA 7d953556b2bd4155f43779250fb2240e5d8f7f656525e9c33fdbad6ccf1a976e.

Preparation001 host path failure preserved, NO guest launch/source fixture.
Broad harness substitution incorrectly changed selected224 probe build002 to
missing build001. Fresh prepare002 fixes only that unrelated selected path and
uses unique trace002 outputs; immutable parent and payload hashes verified.
Legacy console labels saying227/trace001 remain verbatim; actual argument,
fixture JSON, owned paths and process records identify234 trace002.

Fixture E:/Codex-archive/xbox-windows-native/snapshot234/trace002-source.qcow2;
run E:/Codex-private-artifacts/xbox-windows-feasibility/snapshot234-runs/
nt5-snapshot234-trace002. All388 frozen inputs unchanged. Preserve20GiB C build
guard, physical0101/video0093, original0088 rollback, immutable0.1.0 and failures.
Next: pin the actual guest IRQ acknowledgement/loader producer-close transition
in a fresh bounded diagnostic. Do not turn host one-shot publication or stopped
safe refusal into a native grant, or retry for an empty queue. Retired references,
dirty readback, instance/context allocation and alias-coherence gates remain open.

Postclosure host review001 assumed the prior233 leading row kind5 and FAILED.
Actual234 starts with kind3 (post-IRQ-update worker return), then guest4/5;
its producer set lies outside the retained ring. The trailing1/2/3 producer has
no captured acknowledgement. Fresh review002 checks these actual boundaries;
original reviewer/failure record remain intact. No guest replay or gate change.

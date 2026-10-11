"""Record actual CLOSED234 results and prepend continuation without rewriting history."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (k/'REPORT.md').exists()
h=read(k/'trace002/host-state.json');a=read(k/'trace002/audit.json');t=read(k/'trace002/trace.json');q=read(k/'snapshot-review001.json');d=read(k/'consume-review001.json');al=read(k/'trace002/allocation.json');b=read(k/'build001.json')
assert h['closed'] and h['cleanup_record_exists'] and t['closed'] and q['complete_snapshot_protocol']
v=q['views']['wait_live_snapshot'];rows=v['rows'];current=v['current'];header=v['header'];p=t['preserve_result']
events=[dict(source=x['source'],event_id=x['event_id'],type=x['type']) for x in a['warnings_errors']]
tests=read(k/'test001.json')
report=f'''#234 CLOSED: worker journal publication succeeded, ownership still refused

Head before turn1624710. Fresh emulator trace002 CLOSED {h['closed_utc']}.
Controller{h['controller_pid']}/runner{h['runner_pid']}/tracer{h['tracer_pid']}/
observer{h['observer_pid']} CLOSED; cooperative leases released. Never relaunch,
recollect or audit closed trace002. No physical access, device merge or tag change.

ONE live worker request reached state3/tuple_published1; immutable report exactly
matched subsequent reads after CPU stop and after the separate232 preservation
request. Reader no longer locks PG or FIFO or reads the mutable journal. Worker
copies under PG after releasing FIFO, publishes after releasing PG, then takes
FIFO again. Ordered one-shot terminal and timeout logic is separate from the
preservation request. No guest halt/register/wait/IRQ mutation in the new snapshot
hook. Actual233 record sites and actual232 parser/preservation stay unchanged.

Actual bounded ring total{header['total']}, count{header['count']}, overwritten
{header['overwritten']}. {len(q['producer_pairs'])} producer pairs,
{len(q['ack_pairs'])} guest-INTR pairs ({sum(x['cleared_nop'] for x in q['ack_pairs'])}
clear NOP), {len(q['complete_captured_lifecycles'])} complete captured lifecycles.
Missing adjacent pair boundaries{len(q['missing_pair_boundaries'])}; leading/
trailing unmatched rows and overwritten prefix remain visible/unknown. Captured
reset pairs{len(q['reset_pairs'])} is not a claim that no reset occurred.
Parameters {sorted(set(hex(x['parameter']) for x in q['producer_pairs']))};
ERROR mask{q['error_mask']:08x}, trapped100, NSOURCE1. No guest PC/ISR source pin.
Current PG-only row waits{current['waits']}/pending{current['pending']:08x},
FIFO-invalid/all ten FIFO words zero. This is the earlier LIVE sample, not the
stopped queue/current state. Copies of genuine guest dual-lock rows retain valid
FIFO words; producer rows remain FIFO-invalid. No ownership follows from an ack.

Separate stopped preservation state{p['state']}/reason{p['reason']}/stop
{p['consume_stop']}; waits{p['wait_before']}->{p['wait_after']}, steps{p['consume_steps']},
words{p['consume_words']}. GET{p['request0']:08x}/PUT{p['request1']:08x} unchanged at
gate; numerical backlog{p['request1']-p['request0']} bytes. No wait cleared or
producer resumed INSIDE that request. references_retired/native_grant remain0;
surfaces/dirty/downloaded/bytes all0. 212992 actual reserved before/after bytes
unchanged; physical GDB mode restored, zero breakpoints/memory/register writes.
Guest resumed only after safe refusal and mode restoration.

Windows launch record{a['windows_launch_record_exists']}, dashboard return
{a['dashboard_return']}, normal6006 count{a['normal_shutdown_count']}.
CPU scope{a['cpu_scope_passed']}, observation scope{a['observation_scope_passed']}.
Full cold allocation {al['directories']} directories/{al['files']} files/
{al['directory_clusters']} directory clusters, errors{len(al['errors'])}/orphans
{al['orphan_cluster_count']}; integrity{a['integrity_passed']}. Five structural
hives, selected protected hashes/startup/history and unchanged211 device policy
are checked. No synthetic null devices. Warning/error deltas: {events}; new
application events{len(a['new_events']['application'])}. Strict qualification
{a['strict_qualification_passed']}; preservation/ownership remain UNQUALIFIED.
This is one debugger-observed boot, not ordinary GPU acceleration, repeated-boot
storage qualification or an all-file-content audit. USB's ccd210f stale marker/
two invalid hives remain a separate unresolved repeated-boot failure.

Matched actual compiled helpers/QEMU atomic headers with explicit host clock,
register/FIFO/mutex/object/string adapters passed O0/O2 ASan/UBSan:
{tests['runs'][0]['stdout'].strip()}
{tests['runs'][1]['stdout'].strip()}
72 actual guard checks/PowerShell syntax/source lock review passed. Three source
files changed versus selected233; seven borrowed sources restored. Selected exe
SHA {b['executable_sha256']}.

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
'''
(k/'REPORT.md').write_text(report)
continuation=ws/'outputs/engineering-notes/CONTINUATION.md';old=continuation.read_bytes()
prefix=f'''# Current: snapshot234 CLOSED; live journal protocol works, ownership still refused

Read outputs/xemu-wait-snapshot234/REPORT.md, DESIGN.md, NEXT.md and actual records.
Head before turn1624710. CLOSED {h['closed_utc']}; root sessions44346(build),
66302(host),69170(failed prep),95848(corrected prep),81528(runtime) CLOSED.
PIDs{h['controller_pid']}/{h['runner_pid']}/{h['tracer_pid']}/{h['observer_pid']} CLOSED;
leases released. Never relaunch/recollect trace002 or failed preparation001.
No physical IO/device integration/tag changes. Physical0101/video0093,0088rollback,
immutable0.1.0/all failures preserved;20GiB build guard unchanged.

ONE worker request state3, immutable live snapshot stayed identical after CPU
stop and separate232 request. total{header['total']}/256/overwritten{header['overwritten']},
{len(q['producer_pairs'])} producer pairs/{len(q['ack_pairs'])} clear ack pairs/
{len(q['complete_captured_lifecycles'])} complete lifecycles; last open producer/lost
prefix remain unknown. Current PG-only/FIFO-invalid waits{current['waits']}; no
guest ISR/producer-close pin. Stopped preservation state{p['state']}/reason{p['reason']}/
stop{p['consume_stop']}, NOP{p['wait_before']}->{p['wait_after']}, zero words/steps,
backlog{p['request1']-p['request0']} unchanged. Reserved212992bytes unchanged, GDB
mode restored/no writes/breakpoints; resumed after refusal, not inside request.
No readback/reference retirement/native grant. CPU{a['cpu_scope_passed']}/observation
{a['observation_scope_passed']}, normal6006={a['normal_shutdown_count']}/dashboard
{a['dashboard_return']}; cold{al['directories']}dirs/{al['files']}files/
{al['directory_clusters']}clusters,0errors/orphans,5hives/protected/policy intact.
Strict{a['strict_qualification_passed']}; events{events}; all warning/errors retained.

O0/O2 actual helpers/QEMU atomic headers ASan/UBSan each20000 races/2000 publication
pairs/100000 wrapped records, terminal timeout/late-hide/immutability/FIFO-validity;
72guards/PS syntax/lock-source review PASS. Exe{b['executable_sha256']}.
Preparation001 path failure preserved; NEW prepare002 selected224 build002,
unique fixture/case trace002, no failed guest launch. Frozen388 unchanged.
Private fixture snapshot234/trace002-source.qcow2; private run snapshot234-runs/
nt5-snapshot234-trace002. All root processes closed, no new experiment running.

Next actual guest IRQ/producer-close source pin, bounded fresh handoff; never
force-clear/borrow firmware state/waive retirement/alias/allocator gates.
Peer audio now reports user-observed analog login sound, dedicated tone/channel
unknown/Ftdisk49 failure. PCI a7203a1 STOP/START+CANCEL_STOP and integrity passed,
normal restart still audio-install blocked; new input/DHCP events retained.
USB ccd210f correct payload but stale exit marker/two hives parsing failed; trace
disk-transfer/completion next, no speculative driver change. Root one-boot cold
PASS does not settle peer repeated-boot failure. No peer integrated.

--- Previous continuation retained byte-exact below ---

'''.encode('utf-8')
continuation.write_bytes(prefix+old)
(k/'continuation-record001.json').write_text(json.dumps(dict(old_tail_sha256=hashlib.sha256(old).hexdigest(),prefix_sha256=hashlib.sha256(prefix).hexdigest(),new_sha256=sha(continuation),previous_tail_byte_exact=True,root_processes_closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
print('234 actual CLOSED report/continuation recorded')

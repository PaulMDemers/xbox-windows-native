"""Record closed forced-TRUE diagnostic evidence without changing frozen gates."""
import datetime, hashlib, json
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pair = read(k / 'pair-verification003.json')
assert pair['passed'] and pair['raw_tail_bytes_checked'] == 860160
rows = []
for case in ['control003', 'candidate003']:
    host = read(k / case / 'host-state.json')
    audit = read(k / case / 'audit.json')
    alloc = read(k / case / 'allocation.json')
    launch = read(k / case / 'launch.json')['cycles'][0]
    assert host['closed'] and audit['cpu_scope_passed'] and audit['integrity_passed']
    assert not host.get('still_running_pids')
    rows.append(f"{case}: accepted {launch['launch_requested_utc']}; dashboard returned "
                f"{launch['dashboard_return_utc']}; closed {host['closed_utc']}. "
                f"Allocation {alloc['directories']} directories/{alloc['files']} files/"
                f"{alloc['directory_clusters']} directory clusters, no errors/orphans.")

report = '''# Boot reset223: forced TRUE guard comparison passes

The unchanged219 candidate boot provider preserves all86016 reserved tail bytes
through its existing TRUE reset branch; the old control clears all86016 bytes.
Each compiled branch was observed through actual private and public return
frames. Independent verification compares860160 raw tail bytes across five
captures per case,8960 saved-row bytes at every capture, actual relocated
provider/caller bytes,21 UC-tagged present PTEs and exact argument mutations.
This is an emulator debugger diagnostic, not an ordinary or naturally requested
TRUE boot, physical coherence evidence or GPU context grant.

The first actual boot call was FALSE. After pinning its PE, code, caller, frame
layout, published mapping and PTEs, the003 observer changed only two BOOLEAN
argument bytes from0 to1, preserving their other three stack bytes, then seeded
the84KiB tail. It did not patch return values, statuses, event logs or guest
source. All five captures and both return pairs are retained. The observed HAL
callback target825a4f60 has resident bytes31c0c3 (xor eax,eax; ret) followed by
padding; its captured64-byte body matches between cases. The tail remains exact
across that callback and changes only before the control's ResetDisplay return.
The callback's module identity was not separately pinned. Existing reset/palette
code may access hardware; there was no new GPU context or DMA submission.

Both003 runs completed65 CPU allocations/releases/exposure refusals and3194880
verified bytes with four joined workers, one normal shutdown and dashboard
return. Each cold audit has five structural hives and28 matching protected file
hashes, preserved startup/history and unchanged selected device policy. There
are no application events/popups. Strict whole-boot qualification remains FALSE
for the sole inherited Ftdisk49 HarddiskVolume6 error3; that gate is not waived.
Ordinary, physical, GPU ownership and native deferred-fault cleanup remain
unqualified. These selected content checks are not an exhaustive file audit.

No native source was changed or rebuilt. The exact219 control/candidate DLLs and
222 resident005/probe005 were reused in fresh standalone children of immutable
211. Geometry remains1024x576,32bpp. The inherited physical-core policy has
inherited_null_policy FALSE; only the existing targeted known-wizard Cancel
helper runs. There was no physical FTP, deployment, device-branch merge or
change to physical0101/video0093,0088 rollback or immutable0.1.0.

Retained failures: control001 lost the host monitor/NIC startup race before any
Windows request or guard mutation. Its original partial audit failed because
launch.json was absent; the separate failure closure retains five exact hives,
unchanged event/setup bytes and clean allocation. Whole virtual-disk comparison
found an unidentified delta at offset1536; whole-disk equality is not claimed.
Transport was lost with one breakpoint listed, so no teardown/resume claim is
made for001, although its owned emulator process closed. The002 NIC-ready
barrier resolved that race. Its conditional FALSE skip stopped eight times at
the same armed breakpoint (not eight independent resets), then reached the hit
limit, removed all breakpoints and resumed. CPU/shutdown/cold scope passed;
guard coverage failed. Candidate001 and candidate002 were prepared NEVER
launched. The003 metadata self-pin failure is preserved beside its successful
nonrecursive source-pin review. Frozen52/65/78 input sets remain unchanged.

Corrected003 runs are closed with runner/tracer/supervisor/audit exit0, complete
breakpoint teardown and guest resume. No closed ID is to be relaunched or
recollected. Independent pair-verification003.json is authoritative for this
bounded scope. Seeds remain at E:/Codex-archive/xbox-windows-native/bootguard223;
closed run disks remain at E:/Codex-private-artifacts/xbox-windows-feasibility/
bootguard223-runs. C:20GiB build guard is unchanged; backing chains were not moved.

Next is the genuine loader-to-NT5 instance/channel ownership handoff and bounded
software context service, completion, drain and quarantine before a16x8 offscreen
copy. Review212/215/216/218 contracts and actual source/runtime state. The guard
test does not authorize firmware-channel borrowing, global reset, fabricated
ownership bits or GPU descriptor writes. Separate xemu RAMIN is not evidence of
physical UMA alias/coherence. No speed gain or additional video mode is claimed.
'''
report += '\n' + '\n\n'.join(rows) + '\n'
(k / 'REPORT.md').write_text(report, encoding='utf-8')
note = '''# Current:223 forced TRUE control003/candidate003 CLOSED; guard scope passes

Read REPORT.md, pair-verification003.json and actual records. Both003 observers
have five actual paired events, complete breakpoint teardown and guest resume.
Candidate preserves all86016 tail bytes; control clears them. Independent raw
review checks860160 bytes and frozen52/65/78 input sets. Original natural call
was FALSE; only two BOOLEAN bytes0->1 plus the tail seed were debugger-mutated.
No return/status/event/source patch. Natural TRUE/ordinary/physical/GPU grant
remain unqualified. Existing reset/palette may access hardware; no new context
or DMA submission. CPU65/3194880/four joined workers, normal shutdown/dashboard,
clean full allocation, five hives and28 protected hashes pass on each003 side.
Strict whole-boot FALSE sole inherited Ftdisk49/error3; never waive its gate.

ALL root-owned223 sessions CLOSED. Control003 controller86785 and candidate003
controller66080 closed; preparations33873/15875 closed. Earlier control001/002
failures closed and preserved; candidate001/002 prepared NEVER launched. No old
launch, collection, audit or source freeze is to be repeated. Control001 has an
unidentified whole-disk delta1536 and no full teardown claim after transport
loss. Control002 eight stops were the same armed breakpoint, not eight resets.
003 nonrecursive metadata pin review is separate from its retained self-pin
failure. No physical access/device merge;0101/video0093/0088/0.1.0 preserved.

Seeds E:/Codex-archive/xbox-windows-native/bootguard223;
runs E:/Codex-private-artifacts/xbox-windows-feasibility/bootguard223-runs.
No backing chain moves;20GiB C: build guard retained. Next NEW kit must establish
genuine loader-to-NT5 instance/channel ownership, actual bounded software context
service/completion/drain/quarantine before16x8 copy. Read212/215/216/218 and221/222
limits; no firmware channel borrow/global reset/mock witness grant. GPU runtime
PTE/alias/coherence and actual deferred cleanup fault paths remain unresolved.
'''
note += '\n' + '\n\n'.join(rows) + '\n'
(k / 'NEXT.md').write_text(note, encoding='utf-8')
p = ws / 'outputs/engineering-notes/CONTINUATION.md'
old = p.read_text(encoding='utf-8')
boundary = old.index('# Current:222 native CPU ownership runtime001 CLOSED/PASS CPU scope')
p.write_text(note + '\n' + old[boundary:], encoding='utf-8')
print(json.dumps(dict(reports_written=True, updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      pair_sha256=sha(k/'pair-verification003.json'))))

"""Summarize actual closed pair; preserve old continuation and all strict event failures."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];read=lambda p:json.loads(p.read_text());r=read(k/'pair-review.json');assert r['passed']
report=k/'REPORT.md';nextp=k/'NEXT.md';assert not report.exists() and not nextp.exists()
lines=['# Native bounded FIFO observation224','',
       'Both fresh ordinary OFF/ON cases passed the bounded observation/CPU lifetime',
       'and cold integrity scope. This checkpoint grants no GPU ownership or submission.',
       'The active physical system and0101/video0093/0088 rollback/immutable0.1.0 remain',
       'unchanged. No physical FTP, device branch integration or debugger was used.','']
for case,v in r['cases'].items():
    a=read(k/case/'audit.json');allocation=read(k/case/'allocation.json')
    lines += [f'## {case}', '',f'Accepted {v["accepted_utc"]}; dashboard returned {v["dashboard_utc"]};',f'closed {v["closed_utc"]}.', '',
        f'Raw observation: {v["reads"]} reads; reasons '+', '.join(v['reason_names'])+'.',
        f'CPU:65 allocations/releases/exposure refusals,3194880 checked bytes,four joined workers.',
        f'Cold allocation:{allocation["directories"]} directories/{allocation["files"]} files/',
        f'{allocation["directory_clusters"]} directory clusters;zero errors/orphans. Five hives and',
        f'{v["protected_files"]} protected file hashes passed. One normal shutdown; no new application events.',
        f'Strict whole-boot qualification:{a["strict_qualification_passed"]}. Actual warnings/errors:',
        '```json',json.dumps(a['warnings_errors'],indent=2),'```','']
    if v['raw_words']:
        assert all(x==v['raw_words'][0] for x in v['raw_words']) or 'CHANGED' in v['reason_names']
        lines+=['First sequential round (all eight rounds retained in audit/raw log):','',
                '| Register | Offset | Value |','|---|---:|---:|']
        for row,value in zip(read(k/'model-review002.json')['offsets'],v['raw_words'][0]):
            lines.append(f'| {row["symbol"]} | `0x{row["offset"]:06x}` | `0x{value:08x}` |')
        lines+=['']
lines += ['## Evidence and limits','',
    f'Independent pair-review.json verified{r["frozen_inputs"]} frozen inputs, exact actual logs,',
    'source derivation and retained001 inputs. Shared context/sampler objects link both',
    'drivers. Actual compiled16-word tables and intended NT5 provider exports passed.',
    'ASan/UBSan host substitutes executed actual driver dispatch/cleanup, both modes,',
    'mapping failure cleanup, wrong-owner/stale/reserved/short/elevated/lock rejection.',
    'Sampler tests covered65536 DMA-state patterns and128 interrupted read positions;',
    'nineteen parser checks reject malformed/reordered/incomplete/misdecoded evidence.','',
    'Build001 strict-aliasing failure is preserved with every exact input. Corrected',
    'host test uses memcpy without disabling warnings; no native source changed.',
    'Initial import review misclassified READ_REGISTER_ULONG as a HAL export. Actual',
    'kernel export/provider pins corrected that assertion; failed script is retained.',
    'The original inventory predates moving the table from header to C; its exact',
    'failed-build source is retained. model-review002 checks final source/native bytes.','',
    'Eight immediate non-atomic sequential snapshots cannot prove producer/backend',
    'retirement. The pinned model does not maintain DMA busy, returns constant empty',
    'RUNOUT_STATUS and does not implement real PGRAPH_STATUS. NO_OWNERSHIP and',
    'UNMODELED_BUSY remain mandatory even if register pointers/counts appear quiet.',
    'OBSERVED means bounded reads completed. CPU EXPOSE still HOLD. No GPU writes,',
    'RAMIN/USER mappings, descriptors, firmware channel borrow or reset were added.',
    'Successful read mappings remain resident until reboot. Native fallback fault',
    'cleanup, runtime PTE/cache aliases, backend drain and physical acceleration are',
    'unqualified. Cold checks cover full allocation and selected protected contents,',
    'not every payload byte. No event gate was weakened.','',
    'Private seeds:E:/Codex-archive/xbox-windows-native/retirement224.',
    'Closed runs:E:/Codex-private-artifacts/xbox-windows-feasibility/retirement224-runs.',
    'ALL root-owned224 processes closed; no old launch/collection/audit is repeated.',
    '20GiB build guard remains unchanged; backing chains were not moved.','']
report.write_text('\n'.join(lines),encoding='utf-8')
nexttext='''# Next after224

Both ordinary cases CLOSED; never relaunch/recollect/audit/rebuild old IDs.
Read REPORT.md, pair-review.json and raw retirement.log. The bounded read-only
preflight is qualified only in its stated scope; every reply refuses ownership.
Preserve all strict warning/error failures. Physical baseline/device policy and
0.1.0 unchanged; no root hardware deployment or device branch integration.

Next establish an actual loader producer-release/instance/channel handoff record
with pinned executing source/binary and bounded timing. CPU interrupt revocation
alone is not GPU/backend retirement. Determine every existing instance/channel
consumer and reserved84KiB boot-video tail before claiming a new allocation.
Current model busy/runout/status limitations prohibit a register-only idle gate.
Use a new owned unique bounded diagnostic; retain failures and complete teardown.

Only genuine ownership plus bounded software-context service/completion/backend
drain/quarantine permits a new minimal16x8 copy experiment. Do not borrow firmware
channels, reset globally, invent model idle state or convert host-mock witnesses
into a native grant. Runtime PTE/cache alias coherence and native deferred cleanup
fault paths still require separate evidence. Then strict ordinary cold regression
and one reviewed physical trial with rollback can be planned. No acceleration or
HD-mode improvement is claimed by224.
'''
nextp.write_text(nexttext,encoding='utf-8')
note=ws/'outputs/engineering-notes/CONTINUATION.md';old=note.read_text(encoding='utf-8');start=old.index('# Current:223')
head=['# Current:224 ordinary read-only FIFO pair CLOSED; observation/CPU scope PASS','',
      'Read224 REPORT.md/NEXT.md/pair-review.json and actual records. Matched OFF/ON',
      f'native build002/provider/model table/host tests passed;{r["frozen_inputs"]} frozen inputs',
      'verified. Both cases CPU65/3194880/four joined workers, normal shutdown/dashboard,',
      'clean full allocation/five hives/protected hashes/history/device policy passed.']
for case,v in r['cases'].items():
    head += [f'{case}: reads{v["reads"]}; reasons '+','.join(v['reason_names'])+';',
             f'strict whole-boot{v["strict_qualification_passed"]}. Accepted{v["accepted_utc"]},',
             f'returned{v["dashboard_utc"]}, closed{v["closed_utc"]}.']
head+=['','ALL root-owned224 sessions CLOSED (preparations74368/93283 and actual host-state',
       'controller/observer/runner PIDs). Never repeat any old launch/collect/audit.',
       'Preserve failed001 strict-aliasing inputs/import-review misclassification and',
       'all strict event failures. No GPU writes/grants, debugger, physical access or',
       'device merges.0101/video0093/0088/0.1.0 preserved; inherited_null_policy FALSE.',
       'New module maps only approved read windows, resident until normal reboot.',
       'Every reply retains NO_OWNERSHIP/UNMODELED_BUSY; no backend drain claimed.',
       '20GiB C: guard retained, all seeds/runs stay at private retirement224 E paths.',
       'Next actual loader producer/instance/channel handoff plus bounded context/',
       'completion/backend drain/quarantine before16x8 copy. No register-only idle gate.',
       'Runtime PTE/cache aliases/native cleanup fallback faults remain unqualified.','']
note.write_text('\n'.join(head)+'\n'+old[start:],encoding='utf-8');print('224 actual report and continuation recorded')

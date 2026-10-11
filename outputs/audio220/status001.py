"""Update the human-readable queue status; no console access or trial mutation."""
import argparse
from common001 import *
p=argparse.ArgumentParser();p.add_argument('stage');p.add_argument('detail');p.add_argument('--sessions',nargs='*',type=int,default=[]);args=p.parse_args()
def optional(path):return read(path) if path.exists() else None
cases={n:{key:optional(k/n/(key+'.json')) for key in ['trial','return','collection','audit','scan','allocation']} for n in ['install001','playback001']}
for n,c in cases.items():
    if (k/n/'audit002.json').exists():c['audit']=read(k/n/'audit002.json')
restored=optional(k/'restored001/restoration.json');allocation=optional(k/'restored001/allocation.json')
baseline_restored=bool(restored and restored.get('baseline_restored') and allocation and allocation.get('allocation_consistent') and not allocation.get('errors') and not allocation.get('orphan_cluster_count'))
rows=[]
for n,c in cases.items():
    t=c['trial'];a=c['audit'];col=c['collection']
    if t:
        rows.append(f"- {n}: launch requested={t['launch_requested']}, UTC={t.get('launch_utc')}, reply={t.get('launch_reply',t.get('launch_reply_uncertain'))}; dashboard return={bool(c['return'] and c['return'].get('dashboard_return'))}; startup restored={bool(col and col.get('startup_restored'))}; collection complete={bool(col and col.get('completed'))}.")
    if a:rows.append(f"  Audit: installation={a.get('scoped_installation_passed')}, runtime={a.get('scoped_runtime_passed')}, integrity={a.get('integrity_passed')}, strict whole-boot={a.get('strict_qualification_passed')}; audibility is not inferred.")
report=k/'REPORT.md'
ticket_closed=(queue/'audio-closed.json').exists()
text=f'''# Audio hardware220 live status

Updated {utc()}. Phase: {args.stage}.

{args.detail}

Queue state: {'closed after verified restoration' if ticket_closed else 'audio holds the persistent ticket'}. Owned active sessions: {args.sessions or 'none'}. Baseline restoration
with final allocation verification complete: {baseline_restored}.

Fresh capture002 preserved1223 files, including1175 INF entries, with second-read
verification. Five cold hives and actual ACI binding passed review. All11 actual
NT5 providers and three native export tables, including physical Xbox HAL, passed.
The incoming ACI service is ac97xnt5, original9cccf729...; installation reproduces
the emulator's tested starting condition by temporarily replacing that legacy
file with reviewed build004, with no offline binding edit. SetupAPI performs the
actual xwnaci207 installation. Exact original bytes remain in artifacts/before002/.

{chr(10).join(rows)}

Read-only private-file audits are permitted independently of shared build/run
leases by hardware220 coordination guidance; no shared NBD/monitor/build-tree use.
The five-hive/provider preflight itself ran under the global build lease.
Capture001's host journal PermissionError and the generator draft failure remain
preserved. No speculative register writes, disabling, event suppression or
exploratory video deployment. FATX0101/video0093,0088 and immutable0.1.0 preserved.
Physical audibility remains separately unverified unless a user observation is
recorded. Unsupported APU01B0 and strict Ftdisk49 must not be hidden by scoped success.

Report: {report}
Rollback: {k/'artifacts/before002'} (manifest capture002.json).
Trial records: {k/'install001'} and {k/'playback001'}.
Restoration: {k/'restored001'} when executed. Frozen inputs: frozen001.json.
Reviewed package source commit:7cdb191bd2ef72e24001370726f97a7383a7250b.
Branch: codex/xbox-native-audio. No physical claim is released by this status file.
'''
report.write_text(text)
save(queue/'audio-status.json',dict(owner='audio',status=args.stage,report=str(report),owned_sessions=args.sessions,physical_writes=any(c['trial'] for c in cases.values()),launch_requested=any(c['trial'] and c['trial']['launch_requested'] for c in cases.values()),baseline_restored=baseline_restored,updated_utc=utc()))
deliver=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-09/xbox-windows2000-audio/outputs/audio220-report.md');deliver.write_bytes(report.read_bytes())
print('Saved audio status: '+args.stage)

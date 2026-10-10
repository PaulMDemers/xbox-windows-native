"""Publish local progress and private queue status without console access."""
import datetime,json,pathlib,sys
k=pathlib.Path(__file__).resolve().parent
state=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/device-hardware220/state')
read=lambda p:json.loads(p.read_text())
stage=sys.argv[1]
record={'owner':'audio-listen001','status':stage,'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'report':str(k/'REPORT.md'),'baseline_restored':False,'ticket_retained':True,'connection_user_report':'Composite connectors, speakers connected and ready to test','audibility_observed':False}
lines=['# Analog listening trial','',f'Current stage: {stage}.','',
'The user confirmed a composite cable connection to speakers. Audible output is not yet recorded.',
'The new audio-listen001 ticket preserves all closed hardware220 cases. Only the unchanged build004 candidate and reviewed helpers are in scope.','']
for case in ['baseline001','install001','playback001','restored001']:
 for name in ['trial.json','return.json','collection.json','allocation.json','audit.json','restoration.json','confirmation.json']:
  p=k/case/name
  if not p.exists():continue
  r=read(p)
  fields={n:r[n] for n in ['launch_requested','startup_enabled','dashboard_return','completed','allocation_consistent','orphan_cluster_count','scoped_installation_passed','scoped_runtime_passed','strict_qualification_passed','baseline_restored','passed'] if n in r}
  lines.append(f'- {case}/{name}: `{json.dumps(fields)}`')
  if case=='restored001' and name=='confirmation.json' and r.get('passed'):record['baseline_restored']=True
closed=state/'audio-listen001-closed.json'
if closed.exists():record['ticket_retained']=False
lines+=['','Ftdisk49 remains a strict failure when present. Playback completion alone does not establish audible sound. All capture, installation, output observation and rollback evidence are kept separately.','']
(k/'REPORT.md').write_text('\n'.join(lines))
for p in [state/'audio-listen001-status.json',k/'status.json']:
 p.write_text(json.dumps(record,indent=2)+'\n')
out=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-09/xbox-windows2000-audio/outputs')
(out/'audio-listening-report.md').write_text('\n'.join(lines))
print(stage)

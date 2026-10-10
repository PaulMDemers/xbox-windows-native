"""Create a new persistent physical ticket without reopening closed tickets."""
import datetime,json,pathlib
k=pathlib.Path(__file__).resolve().parent
state=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/device-hardware220/state')
for p in state.glob('*-claimed.json'):
 closed=p.with_name(p.name.replace('-claimed.json','-closed.json'))
 assert closed.exists() and json.loads(closed.read_text()).get('baseline_restored') is True,'Physical owner remains active: '+p.name
record={'owner':'audio-listen001','claimed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'User-authorized analog speaker listening test, new baseline capture, unchanged build004, bounded installation/playback and exact rollback.','report':str(k/'REPORT.md')}
with (state/'audio-listen001-claimed.json').open('x') as f:json.dump(record,f,indent=2)
(k/'claim.json').write_text(json.dumps(record,indent=2)+'\n')
(k/'REPORT.md').write_text('# Analog listening trial in progress\n\nSuccessor ticket claimed. No console access or launch yet.\n')
print('New audio-listen001 ticket claimed; previous tickets preserved')

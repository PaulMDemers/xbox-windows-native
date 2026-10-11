"""Pure host analysis of cold extracted logs; no WSL, compiler, or disk attachment."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;repo=k.parents[1];case=sys.argv[1]
assert re.fullmatch('emu[0-9]{3}',case)
run=repo/('work/runs/nt5xidrestart-'+case);assert (run/'cleanup.json').exists()
assert (k/(case+'-review.json')).exists()
dest=k/case/'events.json';assert not dest.exists()
decoder=repo/'outputs/native-windows-physical-f/decode-legacy-events.py'
r=dict(physical_access=False,event_decoder_sha256=hashlib.sha256(decoder.read_bytes()).hexdigest(),event_history_preserved=True,new_events={})
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
    decoded=[]
    for phase in ['before','after']:
        output=run/('eventscan-'+phase+'-'+label+'.json')
        subprocess.run([sys.executable,'-B',str(decoder),str(run/(phase+'-'+name)),'--output',str(output)],check=True,stdout=subprocess.DEVNULL)
        decoded.append(json.loads(output.read_text())['records'])
    before,after=decoded;by={e['record']:e for e in after}
    r['event_history_preserved'] &= all(by.get(e['record'])==e for e in before)
    boundary=max((e['record'] for e in before),default=0)
    r['new_events'][label]=[e for e in after if e['record']>boundary]
before=(run/'before-setupapi.log').read_bytes();after=(run/'after-setupapi.log').read_bytes()
r['setupapi_history_preserved']=after.startswith(before)
if r['setupapi_history_preserved']:(run/'setupapi-delta.txt').write_text(after[len(before):].decode('cp1252',errors='replace'))
r['warnings_errors']=[e for group in r['new_events'].values() for e in group if e['type'] in [1,2]]
r['normal_shutdown_count']=sum(e['source']=='EventLog' and e['event_id']==6006 for e in r['new_events']['system'])
r['strict_events_passed']=not r['warnings_errors'] and not r['new_events']['application']
r['scope']='Record-number deltas from validated legacy EVT records, including possible stale ring records. No ordinary/physical qualification.'
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))

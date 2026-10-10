"""Physical descriptor/event evidence review after capture; never a controller-support PASS."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parent/'usb-identification207'))
from analyze import parse
CANON=Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
read=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
p=read(K/'physical001.json');assert p.get('collected_utc')
dest=K/'audit001.json';assert not dest.exists()

def data(row):
    b=(K/row['file']).read_bytes();assert sha(b)==row['sha256'];return b

r=dict(physical_result=True,controller_support=False,input_reports_captured=False,
       visual_input_qualified=False,full_physical_allocation_audit=False,
       fixed_exact=p['fixed_exact'],collector_exact=p['collector_exact'],startup_restored=not p['startup_enabled'],
       new_events={},event_history_preserved=True)
if p['after']['usb.log']:
    try:
        parsed=parse(data(p['after']['usb.log']))
        (K/'observation001.json').write_text(json.dumps(parsed,indent=2)+'\n')
        r.update(probe_complete=parsed['complete'],elapsed_ms=parsed['elapsed_ms'],reported_failures=parsed['reported_failures'],
                 failed_requests={n:v for n,v in parsed['requests'].items() if not v['success']},issues=parsed['issues'],
                 connected_ports=[v for v in parsed['ports'] if v['status']==1],configurations=parsed['configurations'])
    except (ValueError,AssertionError,KeyError) as e:r.update(probe_complete=False,parse_error=str(e))
else:r.update(probe_complete=False,parse_error='Missing usb.log')
r['collector_exit']=None if not p['after']['exit.txt'] else data(p['after']['exit.txt']).decode('ascii').strip()
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
    decoded=[]
    for phase in ['before','after']:
        d=K/'artifacts/physical001'/(phase+'-'+label+'-events.json')
        subprocess.run([sys.executable,'-B',str(CANON/'outputs/native-windows-physical-f/decode-legacy-events.py'),
            str(K/p[phase][name]['file']),'--output',str(d)],check=True,stdout=subprocess.DEVNULL)
        decoded.append(read(d)['records'])
    a,b=decoded;by={v['record']:v for v in b}
    # Disk offsets are placement, not record identity; retain original decoder outputs.
    semantic=lambda v:{n:x for n,x in v.items() if n!='offset'}
    r['event_history_preserved'] &= all(v['record'] in by and semantic(by[v['record']])==semantic(v) for v in a)
    boundary=max((v['record'] for v in a),default=0)
    r['new_events'][label]=[v for v in b if v['record']>boundary]
r['normal_shutdown_records']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['warnings_errors']=[v for vs in r['new_events'].values() for v in vs if v['type'] in [1,2]]
r['strict_events_passed']=r['event_history_preserved'] and not r['warnings_errors']
before,after=data(p['before']['setupapi.log']),data(p['after']['setupapi.log'])
r['setup_history_prefix']=after.startswith(before)
if r['setup_history_prefix']:(K/'artifacts/physical001/setupapi-delta.txt').write_bytes(after[len(before):])
r['hives_valid']=all(read(K/(phase+'-hive-audit.json'))['passed'] for phase in ['before','after'])
r['allocation_scans']={phase:read(K/(phase+'-allocation.json')) for phase in ['before','after','restored'] if (K/(phase+'-allocation.json')).exists()}
r['full_physical_allocation_audit']=all(phase in r['allocation_scans'] and r['allocation_scans'][phase]['allocation_consistent'] for phase in ['before','after'])
r['limits']='Selected payload files and full hives read back from dashboard; allocation coverage stated separately from file-content coverage. XID input unsupported. EventLog6006 alone does not prove dashboard return or restart method.'
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['probe_complete','collector_exit','fixed_exact','normal_shutdown_records','strict_events_passed','hives_valid','setup_history_prefix']}))

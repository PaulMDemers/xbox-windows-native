"""Collected physical201 known Cancel/real-idle/normal-restart scope, with strict events separate."""
import hashlib, importlib.util, json, struct, subprocess, sys
from pathlib import Path
from analyze import analyze

k = Path(__file__).resolve().parent
ws = k.parents[2]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda b: hashlib.sha256(b).hexdigest()
dest = k / 'audit.json'
assert not dest.exists()
record = read(k / 'physical.json')
assert record.get('collected_utc') and not record['startup_enabled']
ready = read(k / 'ready.json')
for name, digest in ready['pins'].items():
    assert sha((ws/name).read_bytes()) == digest, name

def data(phase, name):
    row = record[phase][name]
    if row is None:
        return None
    value = (ws / row['path']).read_bytes()
    assert sha(value) == row['sha256']
    return value

r = dict(scope=__doc__, physical_result=True, physical_qualified=False,
         strict_qualification_passed=False, release_qualified=False)
r['preserved_bytes_exact'] = all(row is None or sha((ws/row['path']).read_bytes()) == row['sha256']
                                for phase in ['before','after'] for row in record[phase].values())
wizard, guardian = [data('after', name) for name in ['wizard201.log', 'guardian201.log']]
try:
    parsed = analyze(wizard, guardian)
    rows = [line.split() for line in wizard.decode('ascii').splitlines()]
    active = [list(map(int, row[1:])) for row in rows if row[0]=='CANCEL_ACTIVE_VERIFIED']
    parsed['active_before_each_action'] = len(active)==parsed['actions'] and all(
        v[:2]==intent[:2] for v,intent in zip(active,parsed['intents']))
    parsed['physical_mode_and_targets'] = rows[0]==['START201','1','0','120000'] and all(
        1<=target<=4 for target in parsed['targets'])
    parsed['cancellation_lifecycle_passed'] &= parsed['active_before_each_action'] and parsed['physical_mode_and_targets']
    r['cancellation'] = parsed
    r['cancellation_passed'] = parsed['cancellation_lifecycle_passed']
except Exception as exc:
    r.update(cancellation_passed=False, parser_error=type(exc).__name__ + ': ' + str(exc))

sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
r['hives'] = []
for phase in ['before','after']:
    for name in ['system','software','default','sam','security']:
        value = data(phase,name)
        p = ws / record[phase][name]['path']
        try:
            h = hivex.Hivex(str(p)); seen=set(); todo=[h.root()]; count=0
            while todo:
                n=todo.pop(); assert n not in seen; seen.add(n); h.node_name(n)
                for v in h.node_values(n): h.value_key(v); h.value_value(v); count+=1
                todo.extend(h.node_children(n))
            a,b = struct.unpack_from('<II',value,4); checksum=0
            for at in range(0,508,4): checksum ^= struct.unpack_from('<I',value,at)[0]
            checksum = 0xfffffffe if checksum==0xffffffff else 1 if checksum==0 else checksum
            valid=a==b and checksum==struct.unpack_from('<I',value,508)[0]
            row=dict(phase=phase,name=name,parsed=True,keys=len(seen),values=count,header_valid=valid)
        except Exception as exc:
            row=dict(phase=phase,name=name,parsed=False,header_valid=False,error=type(exc).__name__)
        r['hives'].append(row)
subprocess.run([sys.executable,str(k/'audit-state.py')],check=True)
r['typed_state'] = read(k/'device-state.json')
r['protected_files_exact'] = all(record['before'][name]['sha256']==record['after'][name]['sha256']
                                for name in record['before'] if name.startswith('/'))
r['startup_restored_exact'] = record['startup_restored_verified'] and data('after','startup.cmd')==data('before','startup.cmd')
r['helpers_and_backup_exact'] = record['helpers_exact'] and record['startup_backup_exact'] and record['rollback_exact']
r['setupapi_history_preserved'] = data('after','setupapi.log').startswith(data('before','setupapi.log'))
r['event_history_preserved'] = True
r['new_events'] = {}
for label,name in [('system','sysevent.evt'),('application','appevent.evt')]:
    pair=[]
    for phase in ['before','after']:
        output=k/(phase+'-'+label+'-events.json');assert not output.exists()
        subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),
                        str(ws/record[phase][name]['path']),'--output',str(output)],check=True,stdout=subprocess.DEVNULL)
        pair.append(read(output)['records'])
    before,after=pair;by={v['record']:v for v in after}
    r['event_history_preserved'] &= all(by.get(v['record'])==v for v in before)
    boundary=max((v['record'] for v in before),default=0)
    r['new_events'][label]=[v for v in after if v['record']>boundary]
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['strict_events_passed']=r['event_history_preserved'] and not r['warnings_errors'] and not r['new_events']['application']
r['integrity_passed']=all(r[name] for name in ['preserved_bytes_exact','protected_files_exact','startup_restored_exact',
    'helpers_and_backup_exact','setupapi_history_preserved','event_history_preserved']) and all(
    v['parsed'] and v['header_valid'] for v in r['hives']) and all(r['typed_state'][name] for name in
    ['hive_headers_valid','selected_policy_unchanged','no_new_device_disabling'])
r['dashboard_return']=read(k/'return.json')['dashboard_return']
r['scoped_cancellation_passed']=r['cancellation_passed'] and r['integrity_passed'] and r['normal_shutdown_count']==1 and r['dashboard_return'] and not r['new_events']['application'] and not any(v['source']=='Application Popup' for v in r['new_events']['system'])
r['limits']='Physical known-wizard cancellation/normal-restart scope only. No performance or full allocation/all-file audit, driver/device support or release qualification. All warnings/errors retained as strict failures; no waiver.'
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
closure=dict(closed=True,never_relaunch_or_recollect=True,scoped_cancellation_passed=r['scoped_cancellation_passed'],
             strict_events_passed=r['strict_events_passed'],physical_qualified=False,release_qualified=False,
             startup_restored=True,pins={name:sha((k/name).read_bytes()) for name in ['physical.json','return.json','audit.json','device-state.json','ready.json']})
(k/'closure.json').write_text(json.dumps(closure,indent=2)+'\n',encoding='utf-8')
print(json.dumps({name:r[name] for name in ['scoped_cancellation_passed','integrity_passed','normal_shutdown_count','warnings_errors']},indent=2))

"""Independent preserved SYSTEM semantic comparison and physical188 evidence closure. No network."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'physical-evidence-review.json';assert not dest.exists()
p=read(k/'physical.json');a=read(k/'physical-audit.json');o=read(k/'physical-observation.json');d=read(k/'physical-device-state.json')
assert p.get('collected_utc') and not p['startup_enabled'] and read(k/'physical-closure.json')['closed']
assert a['diagnostic_usable'] and d['hive_headers_valid']
for group in [p['before'],p['after']]:
    for row in group.values():
        if row:assert sha(ws/row['path'])==row['sha256']
for name,digest in read(k/'physical-ready.json')['pins'].items():assert sha(ws/name)==digest
def tree(row):
    h=hivex.Hivex(str(ws/row['path']));keys=set();values={};todo=[('',h.root())]
    while todo:
        path,node=todo.pop();assert path not in keys;keys.add(path)
        for v in h.node_values(node):values[(path,h.value_key(v))]=h.value_value(v)
        todo.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(node))
    return keys,values
b,t=[tree(p[phase]['system']) for phase in ['before','after']]
delta=[dict(path=key[0],name=key[1]) for key in sorted(set(b[1])|set(t[1])) if b[1].get(key)!=t[1].get(key)]
samples=[]
for s in o['samples']:
    samples.append(dict(index=s['index'],elapsed_ms=s['elapsed_ms'],install_begin=s['install_state_begin'],install_end=s['install_state_end'],
        installer_commands=[v['command_utf16'] for v in s['processes'] if v['process_image'].lower()=='rundll32.exe'],
        problem_devices=[dict(instance=v['instance'],devinst=v['devinst'],problem=v['problem'],query_result=v['status_query_result']) for v in s['devices'] if v['problem']],
        free_space=s['volumes']))
delta_path=k/'artifacts/physical/setupapi-delta.txt';text=delta_path.read_text(encoding='utf-8')
ids=[line.split('DevInstall ',1)[1] for line in text.splitlines() if line.startswith('Munged cmdline:') and 'DevInstall ' in line]
r=dict(scope=__doc__,closed=True,physical_observation=True,physical_qualified=False,ordinary_qualified=False,
    evidence_sha256={v:sha(k/v) for v in ['physical.json','physical-audit.json','physical-closure.json','physical-observation.json','physical-device-state.json','user-observations.json','manual-return.json','physical-return.json','audit-device-state.py','review-physical.py','watch-return.py','watch-manual-return.py']},
    original_ready_pins_unchanged=True,all_captured_bytes_verified=True,system_keys_added=sorted(t[0]-b[0]),system_keys_removed=sorted(b[0]-t[0]),system_value_delta=delta,
    system_semantically_unchanged=b==t,samples=samples,setupapi_new_installer_ids=ids,setupapi_delta_sha256=sha(delta_path),
    setupapi_no_compatible_driver_count=text.count('Error 0xe0000228'),normal_shutdown_count=a['normal_shutdown_count'],
    new_application_events=len(a['new_events']['application']),warnings_errors=[dict(source=v['source'],event_id=v['event_id'],strings=v['strings']) for v in a['warnings_errors']],
    startup_restored=a['startup_restored'],protected_files=len(p['after_checks']),protected_exact=a['protected_exact'],
    actual_restart_method_user_confirmed=read(k/'user-observations.json')['normal_restart_method_confirmed'],
    limits='Five samples preceded user wizard completion. No post-completion idle query, durable settled-setup proof, graphics comparison, full raw allocation or new release qualification. Ftdisk49/Srv2013 remain strict failures. USB FFFF:FFFF identity is unresolved.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(closed=True,system_semantically_unchanged=r['system_semantically_unchanged'],system_value_delta=len(delta),installer_ids=ids)))

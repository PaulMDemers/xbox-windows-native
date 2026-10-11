"""Explain exactly six inactive ACI registration copies; preserve the original failing equality audit."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
k=Path(__file__).resolve().parent;out=k/'combined001';dest=out/'binding-transition-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit=read(out/'audit.json');state=read(out/'device-state.json');collection=read(out/'collection.json')
def snapshot(p):
    h=hivex.Hivex(str(p));values={};todo=[('',h.root())]
    while todo:
        path,n=todo.pop()
        for v in h.node_values(n):values[path,h.value_key(v)]=h.value_value(v)
        todo.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
    return values
before=snapshot(k/'artifacts/proposed-system');after=snapshot(k/'artifacts/combined001/F/winnt/system32/config/system')
current=int.from_bytes(before['\\Select','Current'][1],'little');assert current==1
assert after['\\Select','Current']==before['\\Select','Current']
instance='\\Enum\\PCI\\VEN_10DE&DEV_01B1&SUBSYS_00000000&REV_B1\\2&ebb567f&0&30'
cls='\\Control\\Class\\{4D36E96C-E325-11CE-BFC1-08002BE10318}\\0011'
allowed={(r'\ControlSet002'+cls,n) for n in ['Driver','DriverDesc','DriverVersion','InfPath','MatchingDeviceId']}
allowed.add((r'\ControlSet002'+instance,'Service'))
actual={(v['path'],v['name']) for v in state['binding_metadata_delta']};assert actual==allowed
rows=[]
for key in sorted(allowed):
    active=(key[0].replace('\\ControlSet002\\','\\ControlSet001\\',1),key[1])
    assert key in before and key in after and active in before and active in after
    assert before[active]==after[active]==after[key] and before[key]!=after[key]
    rows.append(dict(path=key[0],name=key[1],copied_from_preexisting_active_path=active[0],type=after[key][0],exact_value_hex=after[key][1].hex()))
# Recompute the complete equality predicate over raw values, not just the reported list.
def selected(key):
    path,name=key[0].lower(),key[1].lower()
    if '\\enum\\' in path:return name in ['service','driver','class','classguid','configflags']
    if '\\control\\class\\' in path:return name in ['infpath','infsection','infsectionext','driverversion','driverdate','driverdatedata','providername','matchingdeviceid','driverdesc','driver','associatedfilters','upperfilters','lowerfilters']
    return False
raw_changes={key for key in set(before)|set(after) if selected(key) and before.get(key)!=after.get(key)}
assert raw_changes==allowed
assert state['hive_headers_valid'] and state['selected_policy_unchanged'] and state['no_new_device_disabling']
assert not state['binding_metadata_unchanged'] and not audit['integrity_passed'] and not audit['scoped_combined_passed']
integrity=all(audit[n] for n in ['allocation_passed','event_history_preserved','setupapi_history_preserved']) and collection['protected_files_unchanged'] and collection['startup_restored'] and all(v['sequences_equal'] and v['checksum_valid'] for v in audit['hives'])
fields=['audio_probe_passed','audio_state_passed','audio_children_joined','setup_gate_passed','display_workload_passed','checkpoint_history_preserved','combined_interval_passed','dashboard_return','shared_acquire_success','installed_binary_matches','installed_inf_matches']
passed=integrity and all(audit[n] for n in fields) and audit['installed_binding']['passed'] and audit['normal_shutdown_count']==1 and not audit['new_events']['application'] and not any(v['source']=='Application Popup' for v in audit['new_events']['system'])
r=dict(original_equality_gate_passed=False,original_audit_sha256=sha(out/'audit.json'),device_state_sha256=sha(out/'device-state.json'),before_sha256=sha(k/'artifacts/proposed-system'),after_sha256=sha(k/'artifacts/combined001/F/winnt/system32/config/system'),exact_inactive_aci_copies=rows,active_and_unrelated_bindings_unchanged=True,supplemental_integrity_passed=integrity,supplemental_scoped_combined_passed=passed,strict_qualification_passed=passed and audit['strict_events_passed'],release_qualified=False,limits='Original strict binding equality failure retained. Exactly six inactive ControlSet002 ACI values now equal their already installed active ControlSet001 values; no unrelated binding allowance. This is a reviewed installation transition, not a general control-set-change exception. Windows internal copy mechanism not traced. Next255 unchanged-driver reboot keeps original binding equality gate.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

"""Read-only explanation of the failed event gate; never changes qualification."""
import hashlib,json,statistics,struct,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
K=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=K/'failure-review.json'
assert not dest.exists()
a=read(K/'physical001/audit.json');f=read(K/'final-review.json')
assert not f['scoped_passed'] and not f['strict_passed']
assert a['display_workload_passed'] and a['integrity_passed'] and a['normal_shutdown_count']==1
assert len(a['interval_warning_errors'])==1
event=a['interval_warning_errors'][0]
assert (event['source'],event['event_id'],event['strings'])==('Srv',2013,['\\Device\\LanmanServer','F:'])
old=K.parent/'shutdown-diagnostics'
historical=read(old/'physical-inventory.json')['mounted_devices']['\\DosDevices\\F:']
maps=[]
for phase in ['before001','physical001']:
    path=K/'artifacts'/phase/'F/winnt/system32/config/system'
    h=hivex.Hivex(str(path));n=h.node_get_child(h.root(),'MountedDevices')
    v=h.node_get_value(n,'\\DosDevices\\F:');typ,data=h.value_value(v)
    assert typ==3 and len(data)==12
    assert data.hex()==historical['value']
    maps.append(dict(phase=phase,system_sha256=sha(path),type=typ,value=data.hex(),
                     partition_byte_offset=struct.unpack_from('<Q',data,4)[0]))
rows=[]
for ident in range(15):
    group=[x['cases'][ident] for x in a['large_samples']]
    assert len(group)==5 and all(x['passed'] for x in a['large_samples'])
    ms=[x['elapsed_ms']/x['operations'] for x in group]
    rows.append(dict(size=group[0]['size'],kind=group[0]['kind'],
        median_ms_per_operation=statistics.median(ms),minimum_ms_per_operation=min(ms),
        maximum_ms_per_operation=max(ms),qualification_passed=False))
r=dict(scope=__doc__,physical_access=False,scoped_passed=False,strict_passed=False,
       event=event,current_and_before_drive_mapping=maps,
       historical_message_resource=read(old/'srv-message.json'),
       mapping_interpretation='Windows F: still matches the historical system-partition offset 2359820288 (dashboard C:); not host C:/E: and not the large Windows C: volume.',
       limits='No current free-space query or independent system-partition allocation scan. Historical low-space observation does not prove current free space or event cause. All original gates and failed verdicts remain unchanged. Timings below are descriptive observations from a failed combined trial, not a qualified optimization baseline or speedup. Five samples share one boot.',
       pass_gated_summary_executed=False,diagnostic_timing_rows=rows,
       pins={str(p.relative_to(K.parent.parent)):sha(p) for p in [K/'physical001/audit.json',K/'final-review.json',old/'physical-inventory.json',old/'srv-message.json',Path(__file__)]})
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(scoped_passed=False,strict_passed=False,mappings=maps,diagnostic_timing_rows=rows),indent=2))

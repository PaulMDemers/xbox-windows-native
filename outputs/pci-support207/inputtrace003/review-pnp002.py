"""Verify installed package bytes and actual resource-only PnP observation."""
import json,sys,hashlib,os
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent
variant=sys.argv[1];assert variant in ('skip','allow','veto')
k=k;repo=k.parents[2]
assert os.environ.get('XWN_BUILD_LEASE')=='held'
sys.path.insert(0,str(repo/'outputs/setup-wizard-automation201'))
from common import ColdIO,readers,read,save,sha
out=k/(variant+'001');audit=read(out/'audit.json');dest=out/'pnp-review.json';assert not dest.exists()
r=dict(scope=__doc__,physical_access=False,pnp_started=False,installed_files=[],hardware_ready=False)
target=next(v for v in audit['pci_targets'] if 'DEV_01B4' in v['instance'])
r['target']=target
driver=target.get('driver_key') or {};service=target.get('service_key') or {}
r['binding_service']=target['values'].get('Service',{}).get('decoded')
inf=driver.get('InfPath',{}).get('decoded')
with ColdIO(out/'artifacts/runtime/hdd.qcow2') as io:
    rr=readers(io,out/'artifacts/runtime/hdd.qcow2')
    for guest,p in [('winnt/system32/drivers/xwnrsc.sys',k/'artifacts/build001/xwnrsc.sys')]+([('winnt/inf/'+inf,k/'xwnrsc.inf')] if inf else []):
        try:data=rr['F'].read(guest);digest=hashlib.sha256(data).hexdigest()
        except KeyError:digest=None
        r['installed_files'].append(dict(path=guest,expected_sha256=sha(p),actual_sha256=digest,matched=digest==sha(p)))
    try:
        data=rr['F'].read('xwnpcistp1/resource-trace.bin')
        (out/'artifacts/audit/resource-trace.bin').write_bytes(data)
        import struct
        records=[];offset=0
        while offset<len(data):
            assert len(data)-offset>=28
            magic,stage,profile,status,a,b,sequence=struct.unpack_from('<7I',data,offset)
            assert magic==0x52574e58 and a<=1024 and b<=1024 and offset+28+a+b<=len(data)
            offset+=28
            records.append(dict(stage=stage,profile=profile,status=hex(status),sequence=sequence,first_hex=data[offset:offset+a].hex(),second_hex=data[offset+a:offset+a+b].hex()))
            offset+=a+b
        save(out/'resource-trace.json',dict(sha256=__import__('hashlib').sha256(data).hexdigest(),records=records))
        r['resource_trace_records']=len(records)
    except KeyError:r['resource_trace_records']=0
log=audit['logs'].get('lifecycle.log','');r['log']=log
r['pnp_started']=all(s in log.splitlines() for s in ('cm_result=0','devnode_problem=0','query_ok=1','query_bytes=40','profile=2','port=49152','started=1','powered=1','telemetry_enabled=0','telemetry_error=50'))
r['hal_probe_expected_export']=1
r['hal_probe_passed']=all(x in log.splitlines() for x in ('hal_probe_ok=1','hal_probe_bytes=24','hal_export='+str(1),'hal_invalid_ntstatus=0','hal_invalid_result='+str(1),'hal_invalid_status=0','hal_invalid_polls=0','hal_invalid_data=0'))
r['cancel_remove_qualified']=all(x in log.splitlines() for x in ('cancel_remove_result=23','cancel_remove_veto=5','CANCEL_REMOVE_RECOVERED')) and any(x['stage']==5 and x['profile']==3 for x in records)
r['stop_cancel_qualified']=all(x in log.splitlines() for x in ('REBALANCE_STOP_RECOVERED','REBALANCE_CANCEL_RECOVERED')) and all(any(x['stage']==5 and x['profile']==minor for x in records) for minor in (4,5,6))
r['pnp_restart_api_succeeded']='pnp_restart_ok=1' in log.splitlines()
r['lifecycle_completed']=audit['lifecycle_completed']
r['restart_held_pending_setup']='restart_blocked_pending_install=258' in log.splitlines()
r['qualified_resource_only_installation']=bool(audit['integrity_passed'] and audit['install_exit_zero'] and r['binding_service']=='xwnrsc' and inf and all(v['matched'] for v in r['installed_files']) and r['pnp_started'])
r['configuration_scope_qualified']=False
r['configuration_note']='Full typed binding delta is retained in audit.json for review; target installation success does not imply global configuration equality.'
r['normal_restart_qualified']=bool(audit['normal_shutdown_event_count'] and read(out/'run.json').get('dashboard_return_utc') and 'normal_restart_accepted=1' in log)
r['limits']='Resource-only test. Stage5 trace records PnP dispatch minor codes; completed removal requires interface absence and successful re-enumeration/query. Invalid-request HAL ABI probe only; no controller transactions, terminal takeover, ordinary cold-boot or physical qualification.'
save(dest,r);print(json.dumps({key:r[key] for key in ('qualified_resource_only_installation','pnp_started','pnp_restart_api_succeeded','lifecycle_completed','restart_held_pending_setup','normal_restart_qualified','installed_files')},indent=2))

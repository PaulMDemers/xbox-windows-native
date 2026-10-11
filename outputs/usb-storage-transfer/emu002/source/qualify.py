"""Strict per-boot control result; malformed logs never become a passing marker."""
import importlib.util,json,re,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];run=k.parents[1]/('work/runs/nt5storxfer-'+case);out=k/case
read=lambda p:json.loads(p.read_text());r=read(k/(case+'-review.json'));d=read(out/'details.json');t=read(out/'device-state.json');x=read(out/'no-xid-state.json');phase=r['phase']
rows=[];errors=[];helper={}
try:
    data=(run/('status'+str(phase)+'.log')).read_bytes()
    assert data.endswith(b'\r\n')
    for line in data.decode('ascii').splitlines():
        m=re.fullmatch('([A-Z_0-9]+) ([0-9a-f]{8}) tick=([0-9]+)',line);assert m,line
        rows.append((m[1],int(m[2],16),int(m[3])))
except (OSError,UnicodeDecodeError,AssertionError) as error:errors.append(str(error) or 'Missing CRLF terminal')
def values(n):return [v for name,v,tick in rows if name==n]
if phase==1 and not errors:
    try:
        p=k/'analyze-helper.py';spec=importlib.util.spec_from_file_location('helper',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        guardian='\n'.join(('HELPER_JOIN_RESULT' if n=='HELPER_JOIN' else n)+' '+str(v) for n,v,tick in rows)+'\n'
        helper=module.analyze((run/'wizard201.log').read_bytes(),guardian.encode('ascii'))
    except (OSError,UnicodeDecodeError,AssertionError) as error:errors.append('helper: '+str(error))
helper_ok=helper.get('cancellation_lifecycle_passed',False) if phase==1 else not any(n.startswith('HELPER_') or n=='KNOWN_WIZARD_HELPER_BEGIN' for n,v,tick in rows)
required_errors=[e for e in r['collection_errors'] if e['file']!='exit'+str(phase)+'.txt']
integrity=(r['protected_exact'] and r['payload_exact'] and r['allocation_consistent'] and not r['allocation_errors'] and not r['orphan_cluster_count']
    and not required_errors and all(all(h[n] for n in ['header_valid','checksum_valid','sequences_equal']) for h in r['hives'].values())
    and all(h['parsed'] for h in d['hives'].values()) and d['event_history_preserved'] and d['setupapi_history_preserved']
    and t['selected_policy_unchanged'] and t['no_new_device_disabling'] and x['xid_registry_absent'])
restart_ok=(not errors and values('STORAGE_CONTROL_PHASE')==[phase] and values('PAYLOAD_GUEST_READBACK_PASS')==[2226]
    and values('NORMAL_RESTART_REQUEST')==[0] and values('INSTALL_FINAL_RESULT')==[0] and values('INSTALL_WAIT_RESULT')==[0]
    and len(values('SETUP_IDLE_OBSERVED_MS'))==1 and values('SETUP_IDLE_OBSERVED_MS')[0]>=5000
    and not any(n.startswith(('FAIL_','RESTART_BLOCKED','RESTART_HELD')) for n,v,tick in rows)
    and r['dashboard_returned'] and d['normal_shutdown_count']==1 and helper_ok)
result=dict(case=case,phase=phase,physical_access=False,scoped_restart_passed=bool(integrity and restart_ok),cold_integrity_passed=bool(integrity),
    normal_restart_passed=bool(restart_ok),strict_events_passed=d['strict_events_passed'],xid_registry_absent=x['xid_registry_absent'],
    xid_driver_file_absent=r['checks']['xid_driver_absent'],payload_exact=r['payload_exact'],status_parse_errors=errors,helper=helper,
    collection_errors_retained=r['collection_errors'],shell_exit_optional='Shell echo follows process exit, after restart request; retained but not a required pre-restart record.',
    host_block_trace=True,debugger=False,ordinary_boot_qualified=False,limits='Instrumented host DMA/backend byte capture changes timing. Storage-only baseline control without XID. Same pinned Windows/emulator/controller and two-boot sequence; deterministic 2226-byte flushed workload substitutes for HID logging. Not identical HID workload or physical evidence.')
(out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({n:v for n,v in result.items() if n!='helper'},indent=2))

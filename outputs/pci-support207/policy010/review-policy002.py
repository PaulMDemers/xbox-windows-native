"""Review bounded live power-policy evidence without upgrading missing observations."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(k/'veto001/trace.json');p=read(k/'preflight001.json');s=read(k/'policy-static001.json')
assert read(k/'evidence-review002.json')['review_passed']
assert s['script_sha256']==sha(k/'review-static001.py') and s['static_review_passed']
assert s['emulator_source_manifest_sha256']==sha(k/'emulator-source001.json')
for f in read(k/'emulator-source001.json')['files']:assert sha(k/f['snapshot'])==f['sha256']
pins={x['rva'] for x in t['runtime_pins'] if x['module']=='ntoskrnl.exe'}
assert pins>={x['rva'] for x in s['sites'].values()}
calls=t['policy_calls'];events=t['policy_events'];hid='4d1e55b2-f16f-11cf-88cb-001111000030'
arrival='cb3a4004-46f0-11d0-b08f-00609713053f';removal='cb3a4005-46f0-11d0-b08f-00609713053f'
reg=next(c for c in calls if c['kind']=='register' and c['guid']==hid)
assert (reg['category'],reg['flags'],reg['context'],reg['status'])==(2,0,0,0)
assert reg['callback']['module']=='ntoskrnl.exe' and reg['callback']['rva']==0xdd976
assert reg['caller']['rva']==0x15ad21 and reg['registered_entry']
connects=[c for c in calls if c['kind']=='connect'];assert len(connects)==4
paths=sorted({c['name'] for c in connects});assert len(paths)==2
rows=[]
for path in paths:
    cc=[c for c in connects if c['name']==path]
    assert [c['open_status'] for c in cc]==[0,0xc0000043]
    assert all(c['policy_type']==0 and 'end_utc' in c for c in cc)
    st=[c for c in calls if c['kind']=='state' and c['name']==path]
    assert [(c['enable'],c['status']) for c in st]==[(1,0),(0,0),(1,0)]
    assert st[1]['caller']['module']=='hidclass.sys' and st[1]['caller']['rva']==0x423b
    callbacks=[e for e in events if e['site']=='policy_callback_enter' and e['name']==path]
    notifications=[e for e in events if e['site']=='policy_notify_enter' and e['name']==path]
    expected=[arrival,removal,removal,arrival] if '21b1817b' in path else [arrival,removal,arrival]
    assert [e['event_guid'] for e in callbacks]==expected
    assert [e['event_guid'] for e in notifications]==[arrival,removal,arrival]
    assert all(e['context']==0 and e['interface_guid']==hid for e in callbacks)
    assert st[-1]['end_utc']<callbacks[-1]['utc']<cc[-1]['entry_utc']
    first=[e for e in events if e['site']=='policy_complete_enter' and cc[0]['entry_utc']<e['utc']<cc[0]['end_utc']]
    assert len(first)==1;irp=first[0]['irp']['address']
    ev=[e for e in events if e.get('irp',{}).get('address')==irp]
    assert [e['site'] for e in ev]==['policy_complete_enter','policy_button_enter','policy_button_submit','policy_complete_enter','policy_button_enter','policy_button_cleanup']
    assert ev[0]['irp']['status']==ev[1]['irp']['status']==0xc000009d
    submit=ev[2];assert (submit['ioctl'],submit['input_length'],submit['output_length'])==(0x294140,4,4)
    assert bytes.fromhex(submit['next_stack_raw'])[0]==0x0e
    for e in ev[3:]:assert (e['irp']['status'],e['irp']['information'])==(0,4)
    for e in ev[4:]:
        raw=bytes.fromhex(e['context_raw']);assert struct.unpack_from('<II',raw,12)==(0,0)
    assert bytes.fromhex(ev[5]['context_raw'])[8:11]==bytes([1,0,1])
    assert ev[-1]['utc']<st[1]['entry_utc']
    classguid='884b96c3-56ef-11d1-bc8c-00a0c91405dd' if '21b1817b' in path else '378de44c-56ef-11d1-bc8c-00a0c91405dd'
    classstates=[c for c in calls if c['kind']=='state' and c['name']==path.replace(hid,classguid)]
    assert [(c['enable'],c['status']) for c in classstates]==[(1,0),(1,0x40000000)]
    rows.append(dict(name=path,connect_call_ids=[c['id'] for c in cc],open_statuses=[hex(c['open_status']) for c in cc],state_call_ids=[c['id'] for c in st],class_state_call_ids=[c['id'] for c in classstates],notification_events=[arrival,removal,arrival],callback_events=expected,irp=hex(irp),driver=submit['target']['driver_name'],capabilities=0,supported_mask=0,query_completed=True,cleaned_up_before_rebalance=True,query_event_times=[e['utc'] for e in ev]))
assert len([e for e in events if e['site']=='policy_button_submit'])==2
assert not any(e.get('ioctl')==0x294144 for e in events if e['site']=='policy_button_submit')
pending=[c for c in calls if 'end_utc' not in c]
assert len(pending)==1 and pending[0]['driver']==r'\Driver\wdmaud'
# Static calibration only: failed optional reads did not retain resident bytes.
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
provider=p['providers']['hidclass.sys'];assert sha(Path(provider['path']))==provider['sha256']
pe=pefile.PE(provider['path']);overlaps=[e.rva for b in pe.DIRECTORY_ENTRY_BASERELOC for e in b.entries if e.type==3 and e.rva<0x4209 and e.rva+4>0x4209]
assert overlaps
caller_errors=[dict(call_id=c['id'],caller=c['caller'],return_address=hex(c['args'][0])) for c in calls if c['kind']=='state' and isinstance(c.get('caller'),dict) and 'read_error' in c['caller']]
assert len(caller_errors)==4 and all('0x4209' in c['caller']['read_error'] for c in caller_errors)
assert all(c['return_address']==hex(0xf8f10000+0x4219) for c in caller_errors)
assert not (k/'veto001/loaded-site-review001.json').exists()
result=dict(review_passed=True,registration=reg,paths=rows,system_button_event_requests=0,pending_unrelated_registration=pending[0],trace_status=t['status'],relevant_connects_completed=True,kernel_runtime_sites_pinned=True,optional_caller_errors=caller_errors,static_leading_relocation_overlap_rvas=overlaps,caller_calibration='Leading relocation overlap explains an observer limitation but no corrected resident read was obtained. Return address maps to HIDCLASS RVA4219; live caller-byte pin remains unqualified. Prepared post-trace probe was not executed before host closure.',system_button_function_qualified=False,physical_access=False,driver_change_warranted_by_this_evidence=False,limits='Zero capabilities precede rebalance; these devices do not test delivery of power/sleep/lid events. Duplicate keyboard removal retained without broader attribution. Pending wdmaud registration has no observed return, not a diagnosed hang. Debugger timing, normal restart and physical SMC behavior unqualified.',source_sha256=sha(Path(__file__)),evidence_sha256={str(f.relative_to(k)):sha(f) for f in [k/'veto001/trace.json',k/'policy-static001.json',k/'emulator-source001.json',k/'evidence-review002.json']})
dest=k/'policy-review002.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(review_passed=True,paths=rows,optional_caller_errors=len(caller_errors)),indent=2))

"""Review bounded input trace, retained handles, unchanged payload and cold audit."""
import ast,collections,hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;case=k/'veto001';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(k/'preflight001.json')
for name,digest in plan['sources'].items():assert sha(k/name)==digest,name
for name,digest in plan['dependencies'].items():assert sha(Path(name))==digest,name
for item in plan['providers'].values():assert sha(Path(item['path']))==item['sha256']
a,p,r,f,t,rt=[read(case/n) for n in ('audit.json','pnp-review.json','run.json','fixture.json','trace.json','resource-trace.json')]
owner=read(k/'owner-review001.json');snapshot=read(case/'retained-snapshot001.json');capture=read(case/'memory-capture001.json')
assert r['closed'] and r['source_unchanged'] and r['observer_exit_code']==0 and not any(r.get(n) for n in ('unexpected_exit','failure','observer_host_terminated'))
assert t['status']=='both_class_failures_captured' and t['guest_resumed'] and t['breakpoints_remaining']==0 and t['pending_call_count']==0
assert not any(t.get(n) for n in ('error','cleanup_error','memory_writes','register_writes'))
assert snapshot['guest_resumed'] and not snapshot.get('error') and all(x['matching_type_device_and_context'] for x in snapshot['files'])
assert capture['guest_resumed'] and not capture.get('error') and owner['review_passed'] and owner['post_failure_owner_proven']
for path,digest in owner['dependencies'].items():assert sha(Path(path))==digest,path
assert a['integrity_passed'] and a['install_exit_zero'] and all(p[n] for n in ('qualified_resource_only_installation','pnp_started','hal_probe_passed','lifecycle_completed','cancel_remove_qualified'))
assert f['source_sha256']==read(k.parent/'rebalance002/veto001/fixture.json')['source_sha256']
assert f['hal_sha256']=='234b1714debe84ede144b9b1717cf46d2639f3c31b63669c120d7c777a2a6255'
assert sha(k/'artifacts/build001/xwnrsc.sys')=='3c906ae0cb7cb7af794de7caeabb99e52d15e00b8bc10135f8e28a8632ce1a92'
assert sha(k/'xwnrsc.inf')=='d8b50e1f6e49c7a3d1a0aea3a4fee0219351c9be8b7f8121ab02ab47d8c53e83'
assert len(t['calls'])==8 and all(x['kind']=='class_enable' for x in t['calls'])
assert not any(t['hit_counts'].get(n,0) for n in ('share_enter','share_failure','share_end'))
failed=[c for c in t['calls'] if c['status']==0xc0000043];assert len(failed)==2
assert {c['caller']['module'] for c in failed}=={'kbdclass.sys','mouclass.sys'}
rows=[]
for c in failed:
    assert c['enable']==1 and c['identity']['image']=='System' and c['irp_status_at_end']==c['status']
    steps=[s for s in c['steps'] if s['site']=='call_driver'];assert len(steps)==2
    assert all(s['irp']==c['irp'] and s['major']==0 for s in steps)
    expected='kbdhid.sys' if c['caller']['module']=='kbdclass.sys' else 'mouhid.sys'
    assert steps[0]['target']['create_dispatch']['module']==expected
    assert steps[1]['target']['create_dispatch']['module']=='hidclass.sys' and steps[1]['target']['create_dispatch']['rva']==0x88c
    old=next(x for x in t['calls'] if x.get('status')==0 and x.get('enable')==1 and x['identity']['image']=='csrss.exe' and x['caller']['module']==c['caller']['module'])
    held=next(x for x in owner['matches'] if x['call_id']==old['id'])
    assert held['file_fields']['DeviceObject']==steps[-1]['target']['address']
    assert held['file_object']!=c['file_before']['address'] and c['file_before']['FsContext']==0
    rows.append(dict(class_driver=c['caller']['module'],failed_call_id=c['id'],failed_irp=c['irp'],failed_context=c['identity'],status=hex(c['status']),dispatch_chain=[s['target'] for s in steps],failed_file=c['file_before'],earlier_successful_call_id=old['id'],post_failure_retained_handle=held))
minors=collections.Counter(x['profile'] for x in rt['records'] if x['stage']==5)
assert (minors[5],minors[4],minors[6])==(1,0,1)
segments=[]
for record in rt['records']:
    if record['sequence']==1:segments.append([])
    assert record['sequence']==len(segments[-1])+1;segments[-1].append(record)
assert all(len(s)<64 for s in segments)
events=[]
for e in a['warnings_errors']:
    row=dict(source=e['source'],event_id=e['event_id'],record=e['record'])
    if e['source'] in ('Kbdclass','Mouclass'):
        raw=bytes.fromhex(e['data_hex']);row.update(major=raw[0],status=hex(struct.unpack_from('<I',raw,20)[0]));assert row['major']==0 and row['status']=='0xc0000043'
    events.append(row)
assert collections.Counter((x['source'],x['event_id']) for x in events)==collections.Counter({('Ftdisk',49):1,('Kbdclass',9):1,('Mouclass',9):1})
for pth in k.glob('*.py'):ast.parse(pth.read_text(),filename=str(pth))
result=dict(review_passed=True,physical_access=False,ordinary_boot_qualified=False,root_cause_proven=False,trace_path_identified=True,post_failure_csrss_handles_proven=True,io_get_device_object_pointer_class_calls=0,io_check_share_access_hits=0,failed_paths=rows,pnp_minors=dict(minors),trace_load_lengths=list(map(len,segments)),cold_integrity_passed=True,payload_and_source_unchanged=True,events=events,normal_restart_qualified=False,pending_install=p['restart_held_pending_setup'],closed_utc=r['closed_utc'],evidence_sha256={str(path.relative_to(k)):sha(path) for path in list(case.glob('*.json'))+[k/'preflight001.json',k/'owner-layouts001.json',k/'owner-review001.json']},review_source_sha256=sha(Path(__file__)),limits='Debugger pauses and a post-failure memory snapshot. Handle ownership is proved at snapshot time, not continuously through the exact failure instant. HID internal rejection and causal ownership remain unproved. No functional input/network, SMBus transactions, normal restart, repeated-boot or physical qualification. Prior failures, control and DHCP1005 evidence remain unchanged.')
dest=k/'evidence-review001.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({n:result[n] for n in ('review_passed','post_failure_csrss_handles_proven','pnp_minors','trace_load_lengths','events','closed_utc')},indent=2))

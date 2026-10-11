"""Verify actual HID rejection branch, contemporaneous owner, payload and cold results."""
import ast,collections,hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;case=k/'veto001';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(k/'preflight001.json');static=read(k.parent/'hidreject007/static-review002.json');providers=read(k.parent/'hidreject007/providers001.json')
for name,digest in plan['sources'].items():assert sha(k/name)==digest,name
for path,digest in plan['dependencies'].items():assert sha(Path(path))==digest,path
for item in plan['providers'].values():assert sha(Path(item['path']))==item['sha256']
assert providers['script_sha256']==sha(k.parent/'hidreject007/extract-providers001.py') and all(x['source_equals_closed_runtime'] for x in providers['providers'])
assert static['static_review_passed'] and static['source_sha256']==sha(k.parent/'hidreject007/review-static002.py') and static['manifest_sha256']==sha(k.parent/'hidreject007/providers001.json')
t,r,a,p,f,rt=[read(case/n) for n in ('trace.json','run.json','audit.json','pnp-review.json','fixture.json','resource-trace.json')]
assert r['closed'] and r['source_unchanged'] and r['observer_exit_code']==0
assert not any(r.get(n) for n in ('failure','unexpected_exit','observer_host_terminated'))
assert t['status']=='capture_deadline' and t['guest_resumed'] and t['breakpoints_remaining']==0 and t['pending_call_count']==0
assert not any(t.get(n) for n in ('error','cleanup_error','memory_writes','register_writes'))
relevant=[c for c in t['policy_calls'] if c['kind']=='connect']
assert len(relevant)==4 and all('end_utc' in c for c in relevant)
pending=[c for c in t['policy_calls'] if 'end_utc' not in c]
assert len(pending)==1 and pending[0]['kind']=='register' and pending[0]['driver']==r'\Driver\wdmaud'
hidpins={x['rva'] for x in t['runtime_pins'] if x['module']=='hidclass.sys'}
assert hidpins>={0xabb,0xad8,0xaf9,0xb03,0xc78}
assert len(t['calls'])==8 and all(x['kind']=='class_enable' for x in t['calls'])
failed=[c for c in t['calls'] if c['status']==0xc0000043];assert len(failed)==2
assert {c['caller']['module'] for c in failed}=={'kbdclass.sys','mouclass.sys'}
rows=[]
for c in failed:
    assert c['identity']['image']=='System' and c['irp_status_at_end']==0xc0000043
    steps=[s for s in c['steps'] if 'hid_observation' in s]
    assert [s['site'] for s in steps]==['hid_share_gate','hid_read_denied_branch','hid_reject_taken','hid_sharing_status','hid_complete']
    by={s['site']:s for s in steps};gate=by['hid_share_gate']['hid_observation'];branch=by['hid_read_denied_branch']['hid_observation'];status=by['hid_sharing_status']['hid_observation'];done=by['hid_complete']['hid_observation']
    assert gate['desired_access']==0x100003 and gate['share_access']==3
    assert gate['counters']==dict(opens=1,readers=1,writers=0,deny_read=1,deny_write=0,deny_all=0)
    assert branch['jne_taken_by_flags'] and branch['eflags']&0x40==0
    assert done['local_status']==0xc0000043
    for step in steps:
        obs=step['hid_observation'];assert obs['irp']==c['irp'] and obs['extension']==gate['extension']
        assert obs['counters']==gate['counters'] and obs['desired_access']==gate['desired_access'] and obs['share_access']==gate['share_access']
    assert len(status['contexts'])==1;context=status['contexts'][0]
    assert context['desired_access']==0x100001 and context['share_access']==2
    assert context['file_info']['FsContext']==context['address'] and context['file_info']['DeviceObject']==gate['file']['DeviceObject']
    earlier=next(x for x in t['calls'] if x.get('enable')==1 and x.get('status')==0 and x['identity']['image']=='csrss.exe' and x['caller']['module']==c['caller']['module'])
    assert earlier['file_after']['address']==context['file'] and earlier['file_after']['FsContext']==context['address']
    assert len(status['csrss_owners'])==1;owner=status['csrss_owners'][0]
    assert owner['count_matches'] and len(owner['matches'])==1
    held=owner['matches'][0];assert held['file']==context['file'] and held['granted_access']==0x100001
    assert held['handle_count']==1 and held['pointer_count']==2
    assert held['handle']==(0xb8 if c['caller']['module']=='kbdclass.sys' else 0xbc)
    assert not any(c['entry_utc']<=o['utc']<=c['end_utc'] for o in t['open_callers'])
    rows.append(dict(class_driver=c['caller']['module'],call_id=c['id'],failed_irp=c['irp'],new_request_context=c['identity'],new_access=hex(gate['desired_access']),new_share=gate['share_access'],counters=gate['counters'],branch_rva='0xad8',branch_target_rva='0xaf9',branch_eflags=hex(branch['eflags']),status_assignment_rva='0xb03',completion_status=hex(done['local_status']),held_context=context,contemporaneous_owner=owner,earlier_successful_call_id=earlier['id'],observed_site_order=[s['site'] for s in steps]))
assert not any(t['hit_counts'].get(n,0) for n in ('share_enter','share_failure','share_end'))
assert a['integrity_passed'] and a['install_exit_zero'] and all(p[n] for n in ('qualified_resource_only_installation','hal_probe_passed','lifecycle_completed','cancel_remove_qualified'))
assert f['source_sha256']==read(k.parent/'rebalance002/veto001/fixture.json')['source_sha256']
for item in read(k.parent/'rebalance002/build001.json')['files']:assert sha(k/'artifacts/build001'/item['name'])==item['sha256']
assert f['hal_sha256']=='234b1714debe84ede144b9b1717cf46d2639f3c31b63669c120d7c777a2a6255'
assert sha(k/'xwnrsc.inf')=='d8b50e1f6e49c7a3d1a0aea3a4fee0219351c9be8b7f8121ab02ab47d8c53e83'
minors=collections.Counter(x['profile'] for x in rt['records'] if x['stage']==5);assert (minors[5],minors[4],minors[6],minors[0])==(1,0,1,3)
segments=[]
for x in rt['records']:
    if x['sequence']==1:segments.append([])
    assert x['sequence']==len(segments[-1])+1;segments[-1].append(x)
assert all(len(s)<64 for s in segments)
events=[]
for e in a['warnings_errors']:
    row=dict(source=e['source'],event_id=e['event_id'],record=e['record'])
    if e['source'] in ('Kbdclass','Mouclass'):
        b=bytes.fromhex(e['data_hex']);row.update(major=b[0],status=hex(struct.unpack_from('<I',b,20)[0]));assert row['major']==0 and row['status']=='0xc0000043'
    events.append(row)
assert collections.Counter((e['source'],e['event_id']) for e in events)==collections.Counter({('Ftdisk',49):1,('Kbdclass',9):1,('Mouclass',9):1})
for path in k.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
result=dict(scope=__doc__,review_passed=True,physical_access=False,immediate_HID_rejection_and_owner_proven=True,higher_level_reopen_reason_proven=False,functional_input_qualified=False,ordinary_boot_qualified=False,normal_restart_qualified=False,pending_install=p['restart_held_pending_setup'],failed_paths=rows,trace_counts=t['hit_counts'],pnp_minors=dict(minors),trace_load_lengths=list(map(len,segments)),cold_integrity_passed=True,unchanged_guest_payload=True,events=events,closed_utc=r['closed_utc'],source_sha256=sha(Path(__file__)),control_comparison_sha256=sha(k.parent/'rebalance002/comparison002.json'),evidence_sha256={str(path.relative_to(k)):sha(path) for path in list(case.glob('*.json'))+[k/'preflight001.json']},limits='Debugger timing is unqualified. Exact HID sharing denial and contemporaneous CSRSS ownership are established for this fixture, not the purpose/correctness of the System reopen or functional input impact. No code/policy/handle change, normal shutdown, repeated-boot, SMBus transaction or physical qualification.')
dest=k/'evidence-review002.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({n:result[n] for n in ('review_passed','immediate_HID_rejection_and_owner_proven','cold_integrity_passed','trace_load_lengths','events','closed_utc')},indent=2))

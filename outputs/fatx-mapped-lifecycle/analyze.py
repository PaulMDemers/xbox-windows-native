"""Correlate actual mapped append inputs and API results with closed-file evidence."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002']
out=k/case;read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
dest=out/'lifecycle-analysis.json';assert not dest.exists()
t=read(out/'trace.json');source=out/'trace-source.py' if (out/'trace-source.py').exists() else k/'trace.py'
assert sha(source.read_bytes())==t['source_sha256']
sites=out/'sites-source.json' if (out/'sites-source.json').exists() else k/'sites.json'
assert sha(sites.read_bytes())==t['sites_sha256'] and sha((k/'atomic_json.py').read_bytes())==t['atomic_json_source_sha256']
assert t.get('guest_resumed') and not t['armed_breakpoints_remaining']
assert (ws/('work/runs/nt5-fatx-mapped-lifecycle-'+case+'/cleanup.json')).exists()
al=read(out/'alignment.json');cold=(out/'artifacts/after-setupapi.log').read_bytes();assert sha(cold)==al['after_sha256']
target=al['desired_offset'];expected=cold[target:target+al['expected_warning_bytes']]
assert al['target_warning_intact'] and len(expected)==220
rows=[];buffers=0
def verify(ref):
    global buffers
    data=(out/'artifacts'/ref['file']).read_bytes();assert sha(data)==ref['sha256'] and len(data)==ref['bytes'];buffers+=1;return data
for row in t['records']:
    source_strings={label:verify(row[label]) for label in ['first_string','second_string'] if label in row}
    events=row['events'];by={e['site']:e for e in events}
    seek=by.get('seek_call',{});mapped=verify(seek['mapped_append']) if 'mapped_append' in seek else None
    warning=verify(seek['target_warning']) if 'target_warning' in seek else None
    required=['mapping_call','mapping_return','view_call','view_return','helper_return','seek_call','seek_return','cleanup_call','unmap_call','unmap_return','close_mapping_call','close_mapping_return','eof_call','eof_return','close_file_call','close_file_return','outer_return']
    complete=all(name in by for name in required)
    api_success=bool(complete and row.get('helper_status')==0 and row.get('return_status')==0
        and by['mapping_return']['return_value']!=0 and by['view_return']['return_value']!=0
        and by['seek_return']['return_value']==seek['new_size']
        and all(by[n]['return_value']!=0 for n in ['unmap_return','close_mapping_return','eof_return','close_file_return']))
    old=seek.get('old_size');end=seek.get('new_size')
    rows.append(dict(index=row['index'],path=row['path'],pid=row['pid'],image=row['image'],flag=row['flag'],old_size=old,new_size=end,
        first_string_contains_warning=bool(source_strings.get('first_string') and expected.rstrip(b'\r\n') in source_strings['first_string']),
        second_string_contains_warning=bool(source_strings.get('second_string') and expected.rstrip(b'\r\n') in source_strings['second_string']),
        mapped_append_captured=mapped is not None,mapped_append_matches_cold=bool(mapped is not None and cold[old:end]==mapped),
        target_warning_captured=warning is not None,target_warning_exact=warning==expected,
        complete_lifecycle=complete,api_success=api_success,observed_sites=[e['site'] for e in events],
        cleanup_arguments=by.get('cleanup_call',{}).get('arguments'),mapping_arguments=by.get('mapping_call',{}).get('arguments'),
        read_errors={n:v for n,v in row.items() if n.endswith('_error')}))
a=read(out/'audit.json');p=read(out/'package-audit.json');v=read(out/'allocation.json')
coverage=[v for v in rows if v['target_warning_captured']]
r=dict(scope=__doc__,case=case,physical_access=False,ordinary_qualified=False,debugger_observation=True,
    trace_status=t['status'],trace_error=t.get('error'),records=rows,records_count=len(rows),buffers_verified=buffers,
    active_records_remaining=t['active_records_remaining'],target_capture_count=len(coverage),
    target_mapped_lifecycle_verified=bool(coverage and all(v['target_warning_exact'] and v['api_success'] and v['mapped_append_matches_cold'] for v in coverage)),
    all_captured_appends_match_cold=bool(rows) and all(v['mapped_append_matches_cold'] for v in rows if v['mapped_append_captured']),
    cold_checks_passed=all([a['diagnostic_checks_passed'],p['installation_checks_passed'],v['allocation_consistent'],not v['errors'],not v['orphan_cluster_count'],al['actual_alignment_verified'],al['prefix_preserved'],al['target_warning_intact']]),
    trace_sha256=sha((out/'trace.json').read_bytes()),evidence_sha256={name:sha((out/name).read_bytes()) for name in ['audit.json','package-audit.json','allocation.json','alignment.json','launch.json','collection.json']},
    limits='Observed reviewed code sites and API results, not a complete system-call or cache-flush census. Missing candidate hits do not establish another path. Software breakpoints alter timing; no physical cause, ordinary qualification or driver fix is implied.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['trace_status','trace_error','records_count','buffers_verified','target_capture_count','target_mapped_lifecycle_verified','all_captured_appends_match_cold','cold_checks_passed']},indent=2))

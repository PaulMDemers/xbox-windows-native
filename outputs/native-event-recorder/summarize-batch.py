"""Retain every fixed-batch outcome and extract the recorded installer timeline."""
import collections,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(k/'batch-plan.json');build=read(k/'build.json')
assert plan['maximum_launches']==len(plan['cases'])==3
assert plan['emulator_sha256']==build['binary_sha256']==sha(k/'artifacts/xemu-events.exe')
rows=[]
for case in plan['cases']:
    out=k/case
    required=['audit.json','package-audit.json','allocation.json','events.json','launch.json','host-config.json']
    if not all((out/name).exists() for name in required):
        rows.append(dict(case=case,status='not_collected',existing=[n for n in required if (out/n).exists()]))
        continue
    a,p,alloc,events,launch,host=[read(out/n) for n in required]
    f=read(k/('fixture-'+case+'.json'))
    assert f['seed_sha256']==plan['seed_sha256'] and f['fixture_sha256']==plan['fixture_sha256']
    assert host['emulator_sha256']==plan['emulator_sha256'] and host['recorder_enabled']
    assert host['resource_model']==plan['resource_model']
    assert not host['gdb_attachment'] and not host['paused_capture']
    assert len(launch['cycles'])==1
    assert (ws/('work/runs/nt5-native-event-recorder-'+case+'/cleanup.json')).exists()
    assert events['invalid_site_records']==0 and events['kernel_shutdown_observed']
    assert events['record_count']<events['capacity']
    es=events['events'];interesting=set()
    for e in es:
        if any('1B36&DEV_0005' in e.get(field,'') for field in ['command','target_command']):
            if '1B36&DEV_0005' in e.get('command',''):interesting.add(e['owner'])
            if '1B36&DEV_0005' in e.get('target_command',''):interesting.add(e['target'])
    selected=[e for e in es if e['site'].startswith('PnP_') or
              'HardError' in e['site'] or 'Shutdown' in e['site'] or
              e.get('owner') in interesting or e.get('target') in interesting or
              ('10DE&DEV_02A0' in e.get('target_command','') and e['site']=='NtTerminateProcess_AfterReference')]
    harderrors=[e for e in es if 'HardError' in e['site']]
    row=dict(case=case,status='collected',ordinary_run_valid=a['ordinary_run_valid'],
        diagnostic_checks_passed=a['diagnostic_checks_passed'],
        idle_ms=a['idle_elapsed_ms'],storage_workload_not_run=a['storage_workload_not_run'],
        installation_checks_passed=p['installation_checks_passed'],
        normal_shutdown_count=a['normal_shutdown_count'],dashboard_return=a['dashboard_return'],
        popup_records=a['popup_records'],unexpected_errors=a['unexpected_errors'],
        payload_hashes_match=all(v['matched'] for v in a['payloads']),
        runtime_hashes_match=all(v['matched'] for v in a['runtime_binary_checks']),
        hives=len(a['hives']),allocation_consistent=alloc['allocation_consistent'],
        allocation_errors=alloc['errors'],orphan_clusters=alloc['orphan_cluster_count'],
        record_count=events['record_count'],invalid_site_records=events['invalid_site_records'],
        function_counts=dict(collections.Counter(e['site'] for e in es)),
        unknown_owner_commands=sum('command' not in e for e in es),
        placeholder_processes=sorted(interesting),harderror_events=harderrors,
        selected_events=selected,raw_events_sha256=sha(out/'events.bin'),launch=launch['cycles'][0])
    assert not row['ordinary_run_valid']
    rows.append(row)
report=dict(scope=__doc__,physical_access=False,popup_fixed=False,cases=rows,
    complete=all(r['status']=='collected' for r in rows),
    popup_case_count=sum(bool(r.get('popup_records')) for r in rows),
    harderror_case_count=sum(bool(r.get('harderror_events')) for r in rows),
    limits=['Independent clones of one fixture, not consecutive boots or a physical trial.',
            'Keep clean outcomes and failed outcomes; no inference of zero recorder overhead.',
            'Function counts are observations; two hard-error functions may describe one popup.',
            'Correlate EPROCESS and thread as well as PID; absent command lines remain unknown.',
            'Service control timing is not the exact GUI shutdown state transition.'])
(k/'batch-summary.json').write_text(json.dumps(report,indent=2)+'\n')
print({n:report[n] for n in ['complete','popup_case_count','harderror_case_count']})

"""Cross-check failing lifecycle identity against the independent cold event log."""
import hashlib
import json
from pathlib import Path

k = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text())
plan = read(k / 'batch-plan.json')
rows = []
for case in plan['cases']:
    out = k / case
    if not (out / 'events.json').exists():
        continue
    trace = read(out / 'events.json')
    audit = read(out / 'audit.json')
    events = trace['events']
    assert trace['invalid_site_records'] == 0 and trace['kernel_shutdown_observed']
    calls = [e for e in events if e['site'] == 'PnP_Create_call'
             and '1B36&DEV_0005' in e.get('installer_command', '')]
    if not calls:
        assert not audit['popup_records']
        assert not any('HardError' in e['site'] for e in events)
        pnp = [e for e in events if e['site'].startswith('PnP_')]
        assert any(e['site'] == 'PnP_Create_call' and '10DE&DEV_02A0' in e.get('installer_command','') for e in pnp)
        assert any(e['site'] == 'PnP_Control_entry' and e['stack'][1] == '0x5' for e in pnp)
        rows.append(dict(case=case,placeholder_create_observed=False,popup_count=0,
                         harderror_calls=0,pnp_events=pnp,
                         evidence_sha256={name:hashlib.sha256((out/name).read_bytes()).hexdigest()
                                          for name in ['events.bin','events.json','audit.json']}))
        continue
    assert len(calls) == 1
    call = calls[0]
    returns = [e for e in events if e['site'] == 'PnP_Create_return'
               and e['index'] > call['index'] and e['thread'] == call['thread']
               and e.get('installer_command') == call['installer_command']]
    assert len(returns) == 1
    ret = returns[0]
    hard = [e for e in events if e['site'] == '_ExRaiseHardError@24']
    row = dict(case=case,create_call_index=call['index'],create_call_tick=call['tick'],
               create_return_index=ret['index'],create_return_tick=ret['tick'],
               create_result=ret['registers']['eax'],last_error=ret.get('last_error'),
               token_at_call=call.get('saved_token'),token_at_return=ret.get('saved_token'),
               popup_count=len(audit['popup_records']),harderror_calls=len(hard),
               evidence_sha256={name:hashlib.sha256((out/name).read_bytes()).hexdigest()
                                for name in ['events.bin','events.json','audit.json']})
    controls = [e for e in events if e['site'] == 'PnP_Control_entry'
                and e['stack'][1] == '0x5']
    row['shutdown_control_entries'] = [dict(index=e['index'],tick=e['tick']) for e in controls]
    if hard:
        assert len(hard) == len(audit['popup_records']) == 1
        error = hard[0]
        assert error['stack'][1] == '0xc000026b'
        assert error['command'] == call['installer_command']
        assert audit['popup_records'][0]['strings'] == [
            'rundll32.exe - DLL Initialization Failed',
            'The application failed to initialize because the window station is shutting down. ']
        owner = error['owner']
        internal = [e for e in events if e['site'] == '_ExpRaiseHardError@24']
        assert len(internal) == 1 and internal[0]['owner'] == owner
        assert internal[0]['thread'] == error['thread']
        assert internal[0]['stack'][1] == error['stack'][1]
        assert internal[0]['index'] > error['index']
        assert int(ret['process_information'][2],16) == error['pid']
        resumes = [e for e in events if e['site'] == 'NtResumeThread_BeforeResume'
                   and e.get('target') == owner and call['index'] < e['index'] < error['index']]
        win32k = [e for e in events if e['site'] == 'Win32k_Terminate_call'
                  and e.get('owner') == owner and e['index'] > error['index']]
        terms = [e for e in events if e['site'] == 'NtTerminateProcess_AfterReference'
                 and e.get('target') == owner and e['index'] > error['index']]
        exits = [e for e in events if e['site'] == '_PspExitProcess@8'
                 and e.get('target') == owner and e['index'] > error['index']]
        assert ret['registers']['eax'] == '0x1' and resumes and win32k and terms and exits
        assert all(e['target_pid'] == error['pid'] for e in resumes + terms + exits)
        assert win32k[0]['stack'][:2] == ['0xffffffff','0xc0000142']
        assert terms[0]['termination_arguments'] == ['0xffffffff','0xc0000142']
        assert ret['index'] < error['index'] < win32k[0]['index'] < terms[0]['index'] < exits[0]['index']
        shutdown = [e for e in events if e['site'] == '_NtShutdownSystem@4']
        assert len(shutdown) == 1 and shutdown[0]['index'] > exits[0]['index']
        row.update(owner=owner,pid=error['pid'],error_thread=error['thread'],
                   harderror_index=error['index'],harderror_tick=error['tick'],
                   status=error['stack'][1],resume_indices=[e['index'] for e in resumes],
                   win32k_termination_index=win32k[0]['index'],termination_index=terms[0]['index'],
                   termination_status=terms[0]['termination_arguments'][1],exit_index=exits[0]['index'],
                   harderror_before_first_shutdown_control=bool(controls and error['index'] < controls[0]['index']))
    else:
        assert not audit['popup_records']
    rows.append(row)
report = dict(scope=__doc__,cases=rows,complete=len(rows)==len(plan['cases']),
              physical_access=False,popup_fixed=False,
              limits='Resume records are pre-call boundaries, not successful-return probes. GUI shutdown state and token CloseHandle are not captured. Host logging may alter scheduling. Kernel shutdown is later than the GUI shutdown decision.')
(k/'batch-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

"""Review saved diagnostic evidence only; never launch a guest or contact hardware."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[1]


def read(path):
    return json.loads(path.read_text())


summary = {
    'scope': __doc__,
    'physical_access': False,
    'ordinary_boot_qualified': False,
    'popup_reproduced': False,
    'runs': [],
}
captures = {
    '001': [('trace.json', 'trace-initial-source.py'),
            ('trace-retry.json', 'trace-retry-source.py'),
            ('trace-paging.json', 'trace-paging-source.py')],
    '002': [('trace.json', 'trace-initial-source.py'),
            ('trace-retry.json', 'trace-retry-source.py')],
}
for case, attachments in captures.items():
    directory = ROOT / case
    audit = read(directory / 'audit.json')
    launch = read(directory / 'launch.json')
    assert len(launch['cycles']) == 1
    assert audit['diagnostic_checks_passed'] and not audit['ordinary_boot_qualified']
    assert len(audit['hives']) == 5 and all(h['parsed'] for h in audit['hives'])
    assert not audit['popups']
    assert all(b['matched'] for b in audit['runtime_binary_checks'])
    assert any(b['path'].endswith('/umpnpmgr.dll') for b in audit['runtime_binary_checks'])
    row = {
        'case': case,
        'launch': launch['cycles'][0],
        'attachments': [],
        'diagnostic_checks_passed': True,
        'normal_shutdown_count': audit['normal_shutdown_count'],
        'new_popup_count': len(audit['popups']),
        'structural_hives': len(audit['hives']),
        'cleanup': read(WORKSPACE / 'work/runs' / launch['run'] / 'cleanup.json'),
    }
    for filename, source in attachments:
        trace = read(directory / filename)
        digest = hashlib.sha256((directory / source).read_bytes()).hexdigest()
        assert digest == trace['trace_source_sha256'], (case, source)
        assert trace['guest_resumed']
        row['attachments'].append({
            'report': filename, 'source': source, 'sha256': digest,
            'source_hash_matches': True, 'status': trace['status'],
            'error': trace.get('error'), 'events': len(trace['events']),
            'guest_resumed': True,
            'unreadable_site_hits': trace.get('unreadable_site_hits', []),
            'pending_return_count': len(trace.get('pending_returns', [])),
        })
    summary['runs'].append(row)

events = read(ROOT / '001/trace-paging.json')['events']
assert [e['function'] for e in events] == [
    'CreateProcessAsUserW', 'CreateProcessInternalW',
    'NtSetInformationProcess_return', 'CreateProcess_CsrReply',
    'CreateProcessInternalW_return', 'NtTerminateProcess',
    'CreateProcessAsUserW_return', '_NtShutdownSystem@4']
outer, inner, setinfo, csr, created, terminate, failed, shutdown = events
assert 'DEV_01B4' in outer['command_line'] == inner['command_line']
assert len({e['thread'] for e in events[:7]}) == 1
assert outer['caller'] == '0x767a66de'
assert setinfo['eax'] == csr['eax'] == csr['csr_message_status'] == '0x0'
assert created['return_eax'] == '0x1'
assert outer['arguments'][0] == created['process_information'][1] == '0x8f4'
assert created['process_information'][0] == terminate['arguments'][0] == '0x904'
assert terminate['caller'] == '0x7c2f7027' and terminate['arguments'][1] == '0x5'
assert terminate['last_error'] == failed['last_error'] == 6
assert failed['return_eax'] == '0x0'
assert shutdown['arguments'] == ['0x1']
summary['late_attempt'] = {
    'report': '001/trace-paging.json', 'event_indices': list(range(8)),
    'command': outer['command_line'], 'caller': outer['caller'],
    'input_token': outer['arguments'][0],
    'created_process_information': created['process_information'],
    'inner_success': True, 'outer_success': False, 'last_error': 6,
    'cleanup_status': 5,
    'cleanup_status_is_original_error': False,
    'token_numeric_value_equals_new_thread_handle': True,
}
summary['limits'] = [
    'Two diagnostic boots and five attachments, not five Windows launches.',
    'All partial traces and the 512-event bound remain recorded; gaps are not reconstructed.',
    'Debugger pauses alter scheduling; clean controls do not qualify normal boots.',
    'Run002 retry captured only kernel shutdown, so native token-query evidence remains incomplete.',
    'Run001 CSR caller field is an interior stack value, not a return address; attribution uses API entries.',
    'Static saved-token close/clear order and handle-value reuse do not prove a race or the responsible close.',
    'No intermittent popup reproduced; physical soak3 strict failure and all event gates remain unchanged.',
]
(ROOT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print('Reviewed two boots, five source-matched attachments, late creation/unwind and cold audits.')

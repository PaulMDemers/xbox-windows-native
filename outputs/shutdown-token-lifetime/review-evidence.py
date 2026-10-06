"""Check saved token trace provenance and ordering without launching anything."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
workspace = root.parents[1]


def read(path):
    return json.loads(path.read_text())


summary = dict(scope=__doc__, physical_access=False, ordinary_boot_qualified=False,
               runs=[], findings=[], limits=[])
for case in ['001', '002']:
    directory = root / case
    trace = read(directory / 'trace.json')
    audit = read(directory / 'audit.json')
    launch = read(directory / 'launch.json')
    source_hash = hashlib.sha256((directory / 'trace-source.py').read_bytes()).hexdigest()
    assert source_hash == trace['trace_source_sha256']
    assert len(launch['cycles']) == 1 and trace['guest_resumed']
    assert trace['status'] == 'reached_kernel_shutdown'
    assert audit['diagnostic_checks_passed'] and not audit['ordinary_boot_qualified']
    assert len(audit['hives']) == 5 and all(h['parsed'] for h in audit['hives'])
    assert all(b['matched'] for b in audit['runtime_binary_checks'])
    events = trace['events']
    summary['runs'].append(dict(
        case=case, launch=launch['cycles'][0], events=len(events),
        generic_close_observer_enabled=trace.get('generic_close_observer_enabled', case=='001'),
        ignored_hits=trace['ignored_hits'],
        unreadable_site_hits=trace.get('unreadable_site_hits', []),
        trace_source_sha256=source_hash, source_hash_matches=True,
        status=trace['status'], guest_resumed=True,
        diagnostic_checks_passed=audit['diagnostic_checks_passed'],
        new_popup_count=len(audit['popups']),
        normal_shutdown_count=audit['normal_shutdown_count'],
        creation_returns=[{key:e[key] for key in ['index','command_line','return_eax','last_error','saved_token'] if key in e}
                          for e in events if e['function']=='CreateProcessAsUserW_return'],
        cleanup=read(workspace / 'work/runs' / launch['run'] / 'cleanup.json')))

events = read(root / '001/trace.json')['events']
check, control, wait, close_call, close_entry, close_return, before, after, push, create = events[49:59]
assert check['function'] == 'PnP_Install_token_check'
assert check['registers']['ESI'] == '0x0' and check['saved_token'] == '0x770'
assert control['function'] == 'PnP_Control_entry' and control['stack_words'][1] == '0x5'
assert wait['function'] == 'PnP_Control_wait_return' and wait['eax'] == '0x1'
assert close_call['function'] == 'PnP_Token_close_call'
assert close_entry['function'] == 'CloseHandle_saved_token' and close_entry['arguments'] == ['0x770']
assert close_entry['caller'] == '0x767a599b'
assert close_return['function'] == 'CloseHandle_saved_token_return' and close_return['return_eax'] == '0x1'
assert before['saved_token'] == '0x770' and after['saved_token'] == '0x0'
assert after['function'] == 'PnP_Token_clear_after'
assert push['function'] == 'PnP_Install_token_push' and push['saved_token'] == '0x0'
assert check['thread'] == push['thread'] == create['thread'] != control['thread']
assert all(e['thread'] == control['thread'] for e in events[50:57])
assert len({e['owner']['eprocess'] for e in events[49:59]}) == 1
assert create['function'] == 'CreateProcessAsUserW' and create['arguments'][0] == '0x0'
assert 'DEV_01B4' in create['command_line']
for index in [59,64]:
    assert events[index]['function'] == 'NtQueryInformationToken_return'
    assert events[index]['arguments'][0] == '0x0' and events[index]['eax'] == '0xc0000008'
assert events[63]['function'] == 'CreateProcessInternalW_return' and events[63]['return_eax'] == '0x1'
assert events[66]['function'] == 'CreateProcessAsUserW_return'
assert events[66]['return_eax'] == '0x0' and events[66]['last_error'] == 6
assert events[48]['function'] == 'CreateProcessAsUserW_return' and events[48]['return_eax'] == '0x1'
assert 'DEV_01B0' in events[48]['command_line']
summary['findings'].append(dict(
    case='001', indices=list(range(49,67)),
    observation='Installer checks a nonzero saved token; another services.exe thread successfully closes it and clears the global; installer then supplies zero. Native token queries fail, inner creation succeeds, outer creation fails with last-error6.',
    control='Earlier01B0 installer creation succeeds using the same saved handle value.',
    scope='Direct ordering in this debugger run, not an uninstrumented reproduction or proof of popup cause.'))
events = read(root / '002/trace.json')['events']
assert events[49]['function'] == 'PnP_Install_token_check' and events[49]['saved_token'] == '0x908'
assert events[50]['function'] == 'PnP_Install_token_push' and events[50]['saved_token'] == '0x908'
assert events[51]['function'] == 'CreateProcessAsUserW' and events[51]['arguments'][0] == '0x908'
assert 'DEV_01B4' in events[51]['command_line']
assert events[52]['function'] == 'NtQueryInformationToken_return'
assert events[52]['arguments'][0] == '0x908' and events[52]['eax'] == '0x0'
assert events[53]['function'] == 'CreateProcessInternalW'
assert events[54]['function'] == 'PnP_Control_entry' and events[54]['stack_words'][1] == '0x5'
assert events[56]['function'] == 'PnP_Token_close_call' and events[56]['stack_words'][0] == '0x908'
assert events[57]['function'] == 'PnP_Token_close_return' and events[57]['eax'] == '0x1'
assert events[59]['function'] == 'PnP_Token_clear_after' and events[59]['saved_token'] == '0x0'
assert events[62]['function'] == 'CreateProcessInternalW_return' and events[62]['return_eax'] == '0x1'
assert events[63]['function'] == 'NtQueryInformationToken_return'
assert events[63]['arguments'][0] == '0x908' and events[63]['eax'] == '0xc0000008'
assert events[65]['function'] == 'CreateProcessAsUserW_return'
assert events[65]['return_eax'] == '0x0' and events[65]['last_error'] == 6
assert events[49]['thread'] == events[51]['thread'] == events[63]['thread'] != events[54]['thread']
assert all(e['thread'] == events[54]['thread'] for e in events[54:60])
assert len({e['owner']['eprocess'] for e in events[49:66]}) == 1
assert events[48]['function'] == 'CreateProcessAsUserW_return' and events[48]['return_eax'] == '0x1'
assert 'DEV_01B0' in events[48]['command_line']
summary['findings'].append(dict(
    case='002', indices=list(range(49,66)),
    observation='Nonzero input token first passes a native query. Another services.exe thread closes it during inner creation and clears the saved global. Inner creation succeeds; a later query of the original handle returns0xc0000008 and the outer call fails with last-error6.',
    scope='Reduced observer reproduces the lifetime failure at a different point; both runs remain debugger-interrupted, without popup reproduction.'))
summary['limits'] = [
    'No guest driver, registry/device policy, API result or register mutation; breakpoint pauses and single stepping change scheduling.',
    'Case001 observes generic CloseHandle and has substantial startup overhead; case002 omits that observer.',
    'PnP_Token_close_return is also a branch target when the saved token is zero. Its name alone does not prove that CloseHandle executed.',
    'Unreadable sites/globals remain unknown; no claim covers omitted intervals.',
    'No complete allocation audit or physical qualification follows from these bounded cold checks.',
    'The prior nonzero reused-handle trace and this zero-token trace are distinct observations; do not retroactively assign one ordering to the other.',
    'Strict physical soak3 event failures and the pending popup investigation remain unchanged.',
]
(root / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print('Reviewed both launches, exact tracer sources, cold audits and both token interleavings.')

"""Verify completed instruction observations without rewriting the capture failure."""
import copy
import hashlib
import json
from pathlib import Path

K=Path(__file__).resolve().parent
r=json.loads((K/'emu001/trace.json').read_text(encoding='utf-8'))
review=json.loads((K/'source-review.json').read_text(encoding='utf-8'))
xbe=Path('E:/xwn374/build001/default.xbe').read_bytes()
blobs={}
for item in r['reads']:
    data=Path(item['private_file']).read_bytes()
    assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
    assert item['label'] not in blobs
    blobs[item['label']]=data
assert blobs['loaded-original-wrapper']==xbe[0x1100:0x3000]
assert blobs['loaded-original-payload']==blobs['relocated-cromwell']==xbe[0x3000:0x3000+288316]
for target in review['stops']:
    assert blobs[target['label']+'-code'].hex()==target['expected_code']


def observations(t):
    assert t['passed'] is False and t['error']=='AssertionError()'
    assert "unknown command: 'screendump'" in t['screen_reply']
    assert not t.get('cleanup_error') and not t['remaining_breakpoints']
    assert not t['physical_mode_remaining'] and t['physical_mode_restored']
    assert not t['guest_memory_or_register_writes'] and not t['physical_access'] and not t['ordinary_qualified']
    stops=[dict(address=0x11100,label='original_entry'),dict(address=0x2600000,label='cromwell_entry')]+review['stops']
    assert len(t['checkpoints'])==len(stops)
    for i,(row,expected) in enumerate(zip(t['checkpoints'],stops)):
        assert row['label']==expected['label'] and row['registers']['EIP']==expected['address']
        assert bool(row['registers']['CR0']&0x80000000)==(i==0)
        if i>=2:
            assert row['resident_code_exact']
    armed=set()
    for b in t['breakpoints']:
        assert b['reply']=='OK'
        command=b['command'];address=int(command.split(',')[1],16)
        if command.startswith('Z1,'):
            assert address not in armed
            armed.add(address)
        else:
            assert command.startswith('z1,') and address in armed
            armed.remove(address)
    assert not armed and len(t['breakpoints'])==18


observations(r)
negatives=0
for index in range(9):
    for field in ['EIP','CR0']:
        t=copy.deepcopy(r)
        t['checkpoints'][index]['registers'][field]^=0x80000000
        try:observations(t)
        except AssertionError:negatives+=1
        else:raise AssertionError('Changed checkpoint accepted')
for field,value in [('passed',True),('remaining_breakpoints',[1]),('physical_mode_remaining',True),
                    ('physical_mode_restored',False),('guest_memory_or_register_writes',True),('physical_access',True)]:
    t=copy.deepcopy(r);t[field]=value
    try:observations(t)
    except AssertionError:negatives+=1
    else:raise AssertionError('Changed observation accepted')
result=dict(completed_instruction_observations_verified=True,original_run_passed=False,
            screenshot_failure_preserved=True,visible_screen_proved=False,ordinary_qualified=False,
            physical_failure_reproduced=False,checkpoints=9,private_captures_rehashed=len(blobs),
            actual_report_mutations_rejected=negatives,stopped_at_usb_call_before_execution=True,
            all_breakpoints_removed=True,physical_mode_restored=True)
with (K/'emu001/instruction-review.json').open('x',encoding='utf-8') as f:
    json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))

"""Verify completed instruction observations and framebuffer data without inferring physical scanout."""
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
    assert t['passed'] is True and not t.get('error')
    assert t['stopped_before_boot_device'] and not t['windows_started']
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
    assert not armed and len(t['breakpoints'])==14


observations(r)
negatives=0
for index in range(7):
    for field in ['EIP','CR0']:
        t=copy.deepcopy(r)
        t['checkpoints'][index]['registers'][field]^=0x80000000
        try:observations(t)
        except AssertionError:negatives+=1
        else:raise AssertionError('Changed checkpoint accepted')
for field,value in [('passed',False),('remaining_breakpoints',[1]),('physical_mode_remaining',True),
                    ('physical_mode_restored',False),('guest_memory_or_register_writes',True),('physical_access',True)]:
    t=copy.deepcopy(r);t[field]=value
    try:observations(t)
    except AssertionError:negatives+=1
    else:raise AssertionError('Changed observation accepted')
from frame import geometry
frames=[]
for row in r['checkpoints']:
    if 'framebuffer' not in row:continue
    label=row['label'];f=row['framebuffer']
    shape=geometry(blobs[label+'-vmode'],int.from_bytes(blobs[label+'-fb-register'],'little'))
    assert all(f[key]==value for key,value in shape.items())
    data=b''.join(blobs[label+f'-pixels-{off}'] for off in range(0,shape['bytes'],1048576))
    assert data==Path(f['private_file']).read_bytes() and hashlib.sha256(data).hexdigest()==f['sha256']
    frames.append(dict(label=label,bytes=len(data),sha256=f['sha256'],width=shape['width'],height=shape['height']))
assert len(frames)==2
result=dict(scoped_device_initialization_trace_passed=True,checkpoints=7,
            private_captures_rehashed=len(blobs),frames=frames,actual_report_mutations_rejected=negatives,
            stopped_before_boot_device=True,all_breakpoints_removed=True,physical_mode_restored=True,
            ordinary_qualified=False,physical_failure_reproduced=False,actual_tv_scanout_proved=False,
            keyboard_scope='Generic emulator keyboard/mouse only, not physical Razer behavior')
with (K/'emu001/trace-review.json').open('x',encoding='utf-8') as f:
    json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))

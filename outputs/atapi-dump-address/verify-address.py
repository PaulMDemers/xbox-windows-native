"""Check the arithmetic and exact runtime producer of the 128GiB address loss."""
import hashlib
import json
from pathlib import Path
k = Path(__file__).resolve().parent
r = json.loads((k/'crash005/trace.json').read_text())
e = {v['kind']: v for v in r['events']}
assert r['status'] == 'dump_return_observed'
assert not r['armed_breakpoints_remaining'] and r['guest_resumed']
d = e['divide_call']
assert d['dividend'] == e['first_write_call']['volume_offset']+d['partition_offset'] == 148440145920
assert d['divisor'] == d['sector_size'] == 512
lba = e['divide_return']['quotient']
assert lba == d['dividend']//512 == 289922160
assert e['dispatch_call']['cdb_lba'] == e['decoded_lba']['lba'] == lba
assert e['dispatch_call']['cdb_count'] == 8
assert e['dispatch_call']['device_flags'] & 0x400000
assert e['dispatch_call']['command_table'] == 'c4c5ff2939'
assert e['before_head_mask']['al'] == lba >> 24 == 0x11
assert e['after_head_mask']['al'] == (lba >> 24)&15 == 1
assert e['select_write_command']['command'] == e['write_command_call']['command_argument']&255 == 0xc5
assert e['write_command_call']['port'] == 0x1f7
assert e['first_write_return']['status'] == '0x0'
assert e['dump_return']['returned_boolean'] == 1 and e['dump_return']['final_status'] == '0x0'
registry = json.loads((k/'registry-state.json').read_text())
params = next(v for v in registry['keys'] if v['path'].endswith('\\Parameters'))
assert params['values']['EnableBigLba']['value'] == 1
result = dict(localization_verified=True, physical_access=False, ordinary_qualified=False,
    dump_qualified=False, recovery_allowed=False, intended_lba=lba,
    emitted_lba=lba&0xfffffff, lost_bytes=(lba-(lba&0xfffffff))*512,
    exact_producer='Pinned atapi.sys RVA28e7: and al,0x0f; dump writer direct call at RVA1360e bypasses the normal 48-bit selection.',
    enable_big_lba=1, device_48bit_flag=True, available_extended_pio_write_command='0x39',
    trace_sha256=hashlib.sha256((k/'crash005/trace.json').read_bytes()).hexdigest())
(k/'address-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

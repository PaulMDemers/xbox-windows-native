"""Read-only closeout of the collected 462 attempt; no console operations."""
import hashlib
import json
import struct
from pathlib import Path
from decode import decode

K = Path(__file__).resolve().parent
W = K.parents[1]

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def sha(b):
    return hashlib.sha256(b).hexdigest()

out = K / 'closeout001.json'
assert not out.exists()
c = read(K / 'collection001.json')
a = read(K / 'cold-review001.json')
assert c['completed'] and a['selected_cold_audit_passed']
assert read(K / 'user-observation001.json')['desktop_observed_by_user']
assert read(K / 'user-restart001.json')['dashboard_return_confirmed']
assert a['events']['sysevent.evt']['normal_shutdown_delta'] == 1
assert not a['refusal_present']
item = c['files']['/E/Applications/XWNBoot462a/report.bin']
b = Path(item['path']).read_bytes()
assert sha(b) == item['sha256'] and decode(b) == c['decoded'] == a['primary']
rejected = 0

def refuse(data):
    global rejected
    try:
        decode(data)
    except ValueError:
        rejected += 1
        return
    raise AssertionError('Accepted malformed actual report')

for length in range(len(b)):
    refuse(b[:length])
refuse(b + b'\0')
for at in [0,4,8,12,20,48,60,64,68,72,76,80,108,116,120,124,128,132,144,148,152,156,160,164,168,172]:
    for value in [0,0xffffffff,0x12345678]:
        changed = bytearray(b)
        struct.pack_into('<I', changed, at, value)
        if changed != b:
            refuse(changed)
for at,value in [(24,0),(28,0),(32,0),(36,0),(40,0x103),(44,0),(52,0x400),(56,0),(84,0),(84,1),(88,0),(92,0),(96,0),(100,0),(104,0),(112,0x400)]:
    changed = bytearray(b)
    struct.pack_into('<I', changed, at, value)
    refuse(changed)

comparisons = {}
words = struct.unpack('<44I', b)
for kit,remote in [('boot-handoff460','XWNBoot460a'),('boot-handoff461','XWNBoot461a')]:
    prior = read(K.parent / kit / 'collection001.json')
    old_item = prior['files']['/E/Applications/' + remote + '/report.bin']
    old = Path(old_item['path']).read_bytes()
    assert sha(old) == old_item['sha256']
    old_words = struct.unpack('<44I', old)
    differences = [i for i in range(44) if words[i] != old_words[i]]
    assert set(differences) <= {0,3,42}
    comparisons[kit] = dict(prior_sha256=sha(old),different_word_indices=differences,
                           all_nonidentity_words_equal=True)

private = {}
for p in sorted((W / 'work/boot-refusal462/physical001').rglob('*')):
    if p.is_file():
        data = p.read_bytes()
        private[str(p.relative_to(W))] = dict(bytes=len(data),sha256=sha(data))
events_path = W / 'work/boot-refusal462/physical001/after/E/winnt/system32/config/sysevent.evt-review462.json'
warning = [r for r in read(events_path)['records'] if r['record'] == 593]
assert len(warning) == 1 and warning[0]['source'] == 'Srv' and warning[0]['event_id'] == 2013
assert warning[0]['strings'] == ['\\Device\\LanmanServer','F:']
result = dict(passed=True,actual_report_negative_controls=rejected,
              report_sha256=sha(b),comparisons=comparisons,private_files=private,
              private_files_verified=len(private),normal_restart_corroborated=True,
              new_srv_warning=warning[0],strict_system_pass=False,
              strict_reasons=['Ftdisk49','Srv2013'],refusal_present=False,
              missing_refusal_does_not_prove_handoff=True,
              intermittent_boot_root_cause_established=False,
              original_launcher_startup_drivers_unchanged=True,
              full_FATX_allocation_audit=False,D3D_sample_run=False,
              console_C_accessed=False,next_launch_queued=False)
with out.open('x',encoding='utf-8',newline='\n') as f:
    json.dump(result,f,indent=2)
    f.write('\n')
print(json.dumps({k:result[k] for k in ['passed','actual_report_negative_controls','private_files_verified','comparisons']}))

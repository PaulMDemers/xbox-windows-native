"""Close both owned runs; distinguish natural handoff from injected refusal."""
import hashlib,json,struct
from pathlib import Path
from refusal_decode002 import decode_refusal
from marker_decode import success
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'final-review.json';assert not out.exists()
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
summary=[];captures={};rejected=0
assert read(K/'source-review001.json')['passed']
for idx in ('001','002'):
 d=K/f'emu{idx}';t=read(d/'trace.json');a=read(d/'audit.json');p=read(d/'protected.json')
 assert t['passed'] and not t.get('cleanup_error') and not t['remaining_breakpoints'] and t['physical_mode_restored']
 assert a['host_exit']['passed'] and a['host_exit']['exit_code']==0 and not a['host_exit']['fallback_kill']
 assert a['eeprom_unchanged'] and a['source_unchanged'] and p['passed']
 for name,h in read(d/'frozen.json').items():assert sha(W/name)==h,name
 for row in t['reads']:
  file=Path(row['private_file']);assert file.stat().st_size==row['bytes'] and sha(file)==row['sha256'];captures[str(file)]=row['sha256']
 for row in t['reads']:
  if row['label'] in ('first-marker-record','second-marker-record'):
   stage=1 if row['label']=='first-marker-record' else 2;data=Path(row['private_file']).read_bytes();success(data,stage)
   for n in range(96):
    try:success(data[:n],stage)
    except ValueError:rejected+=1
    else:raise AssertionError('Truncated actual marker accepted')
 summary.append(dict(case=idx,checkpoints=len(t['checkpoints']),captures=len(t['reads']),
  injected=idx=='002',host_exit=a['host_exit'],allocation=a['allocation'],changed_bytes=a['changed_bytes'],
  strict_disk_equal=a['strict_whole_disk_equal'],complete_mapping=a['complete_virtual_mapping_bytes'],
  compared=a['local_extent_bytes_compared'],protected_hives=p['hives'],baseline_binaries=p['baseline_binaries']))
assert not read(K/'emu001/trace.json')['guest_memory_or_register_writes']
assert read(K/'emu002/trace.json')['injected_refusal'] and read(K/'emu002/audit.json')['refusal_memory_disk_exact']
data=Path('C:/xwn468/cold003/refusal.bin').read_bytes();decode_refusal(data)
for n in range(192):
 try:decode_refusal(data[:n])
 except ValueError:rejected+=1
 else:raise AssertionError('Truncated actual file accepted')
for offset in [0,4,8,12,16,20,24,32,36,44,48,52,64,76,80,84,88,92,96,100,104,108,112,116,152,156,160,164,168,172,176,180,184,188]:
 m=bytearray(data);struct.pack_into('<I',m,offset,0 if offset==32 else 0xffffffff)
 try:decode_refusal(m)
 except ValueError:rejected+=1
 else:raise AssertionError(('actual mutation accepted',offset))
r=dict(passed=True,physical_access=False,candidate_sha256=read(K/'build001.json')['sha256'],
 source_parent_reconstructed=True,payload_byte_identical=True,host_cases=85,host_decoder_negatives=243,
 emulator_actual_record_negatives=rejected,runs=summary,private_captures=captures,
 physical_status_captured=False,historical_intermittent_failure_explained=False,
 no_console_launch_queued=True,all_owned_emulators_closed=True,
 preserved_failures=['decoder001-failure.json','cold002-failure.json','final-review001-failure.json'])
out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k not in ('runs','private_captures')}))

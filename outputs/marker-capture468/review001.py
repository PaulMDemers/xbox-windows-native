"""Independent record negatives and exact child reconstruction; no execution."""
import hashlib,json,struct
from pathlib import Path
from decode import decode
from refusal_decode002 import decode_refusal
K=Path(__file__).resolve().parent;O=Path('C:/xwn468');out=K/'source-review001.json'
assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False)
try:
 b=json.loads((K/'build001.json').read_text());h=json.loads((K/'host001.json').read_text())
 assert b['status']=='compiled' and h['status']=='passed' and h['cases']==85
 for record in [b,h]:
  for path,v in record['files'].items():
   p=Path(path.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256'],p
 s=(O/'build001/xbeboot.S').read_text()
 for old,new in reversed(b['source_edits']):
  assert s.count(new)==1;s=s.replace(new,old)
 assert s.replace('468','466')==Path('C:/xwn466/build001/xbeboot.S').read_text()
 assert (O/'build001/default.xbe').read_bytes()[0x3000:]==Path('C:/xwn466/build001/default.xbe').read_bytes()[0x3000:]
 good=bad=0
 def reject(data):
  global bad
  try:decode_refusal(data)
  except ValueError:bad+=1
  else:raise AssertionError('Malformed refusal accepted')
 for p in sorted((O/'host001').glob('refusal*.bin')):
  data=p.read_bytes()
  if len(data)==192:decode_refusal(data);good+=1
  else:reject(data)
 for p in sorted((O/'host001').glob('case*.bin')):
  if p.stat().st_size==176:decode(p.read_bytes())
 sample=(O/'host001/refusal61.bin').read_bytes();words=list(struct.unpack('<48I',sample))
 assert words[4]==12 and words[25]==5 and words[26]==1
 for n in range(192):reject(sample[:n])
 reject(sample+b'\0')
 mutations=[(0,0),(1,1),(2,96),(3,0),(4,13),(5,1),(6,0x103),(8,0),(9,1),
 (11,0),(12,0),(13,0),(16,0x400),(19,1),(44,0),(45,1),(46,0),(47,96),
 (20,0),(21,2),(22,95),(23,2),(24,0xa5),(25,1),(26,2),(27,2),(28,0x10),
 (29,4097),(34,0x800),(35,0x20),(36,0),(37,0x10),(38,2),(39,0),(40,4),(41,0),(42,0),(43,1)]
 for i,value in mutations:
  m=words[:];assert m[i]!=value;m[i]=value;reject(struct.pack('<48I',*m))
 # Explicit unknown outcome: complete bytes do not certify flush/close success.
 for n in [48,49,52,77,78,81]:
  d=decode_refusal((O/f'host001/refusal{n:02}.bin').read_bytes())
  assert d['fallback_flush_close_proved'] is False
 r.update(passed=True,parent_source_reconstructed_exact=True,payload_byte_exact=True,
  host_actual_wrapper_cases=85,complete_refusals_decoded=good,malformed_refusals_rejected=bad,
  no_additional_hardware_io_after_snapshot=True,immutable_snapshot_under_later_live_record_mutation=True,
  file_flush_close_not_inferred=True,hardware_kernel_TSC_effects='MODELED',
  private_files={str(p):sha(p) for p in O.rglob('*') if p.is_file()},
  decoder_sources={str(p):sha(p) for p in [K/'review001.py',K/'failure_marker002.py',K/'refusal_decode002.py',K/'decode.py']})
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k not in ('private_files','decoder_sources')}))

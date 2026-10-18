"""Join actual cold captures to independent symbols and the original saved frame."""
import hashlib,json,struct
from pathlib import Path
from primary_decode import decode as primary_decode
from witness_decode import decode_witness
from receipts import decode_refusal
from decode import decode as context_decode
K=Path(__file__).resolve().parent;out=K/'actual-context001.json';assert not out.exists()
c=json.loads((K/'physical001-collection.json').read_text());assert c['completed'] and c['hook_removed']
root='/E/Applications/XWNBoot526a/';sha=lambda b:hashlib.sha256(b).hexdigest()
def load(n):
 row=c['files'][root+n]
 if row is None:return None
 b=Path(row['path']).read_bytes();assert sha(b)==row['sha256'] and len(b)==row['bytes'];return b
p,w,x,f=[load(n) for n in ['report.bin','handoff.bin','context.bin','refusal.bin']]
r=dict(passed=False,physical_origin='one recorded526 launch; retained490 diagnostic schema and double cold reads',hashes={n:None if b is None else sha(b) for n,b in [('primary',p),('witness',w),('context',x),('refusal',f)]},windows_started=None,boot_qualified=False)
try:
 r['primary']=primary_decode(p)
 if f is not None:r['refusal']=decode_refusal(f)
 r['witness']=decode_witness(w,p)
 s=json.loads((K/'build002.json').read_text())['wrapper_symbols'];frame=struct.unpack_from('<9I',w,160)
 args=dict(witness_address=s['witness_record'],frame_address=frame[3]-32,return_eips=[s['context490_pre_return'],s['context490_post_return']])
 r['context']=context_decode(x,**args);neg=0
 def reject(b):
  global neg
  try:context_decode(b,**args)
  except (ValueError,struct.error):neg+=1;return
  raise AssertionError('mutated actual context accepted')
 for n in range(400):reject(x[:n])
 reject(x+b'X')
 offsets=set(range(64))|set(range(384,400))
 for start in [64,224]:
  for a,z in [(0,20),(24,40),(56,64),(64,80),(118,120),(126,160)]:offsets.update(range(start+a,start+z))
 for off in sorted(offsets):
  for bit in range(8):
   b=bytearray(x);b[off]^=1<<bit;reject(bytes(b))
 r.update(passed=True,negative_controls=neg,originals_unchanged=[load(n)==b for n,b in [('report.bin',p),('handoff.bin',w),('context.bin',x),('refusal.bin',f)]])
except (ValueError,TypeError,struct.error) as e:r['incomplete_or_invalid']=repr(e)
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))

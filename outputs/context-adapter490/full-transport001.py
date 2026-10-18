"""Decode actual full-wrapper host outputs; CPU/kernel facts remain modeled."""
import hashlib,json,struct
from pathlib import Path
from decode import decode as context_decode
from receipts import decode_refusal
from primary_decode import decode as primary_decode
from witness_decode import decode_witness
K=Path(__file__).resolve().parent;B=Path('C:/xwn490/full001');out=K/'full-transport001.json';assert not out.exists()
full=json.loads((K/'full-host001.json').read_text());assert full['status']=='passed'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,v in full['files'].items():
 p=Path(n.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256'] and p.stat().st_size==v['bytes']
s=json.loads((K/'build001.json').read_text())['wrapper_symbols'];contexts=refusals=neg=0
def reject(call):
 global neg
 try:call()
 except (ValueError,struct.error):neg+=1
 else:raise AssertionError('negative accepted')
for p in sorted(B.glob('*refusal*.bin')):
 raw=p.read_bytes()
 if len(raw)!=192:reject(lambda b=raw:decode_refusal(b));continue
 d=decode_refusal(raw);refusals+=1
 if d['reason']>=22:
  for off in list(range(16))+list(range(176,192))+list(range(76,80)):
   for bit in range(8):
    b=bytearray(raw);b[off]^=1<<bit;reject(lambda b=bytes(b):decode_refusal(b))
  # Forging the reported API outcome to success must remove the refusal basis.
  b=bytearray(raw);struct.pack_into('<II',b,20,0,0)
  if d['reason']==22:struct.pack_into('<II',b,28,2,0x4903)
  if d['reason']==23:struct.pack_into('<I',b,28,400)
  reject(lambda b=bytes(b):decode_refusal(b))
for p in sorted(B.glob('context*.bin')):
 if p.name.startswith('contextrefusal'):continue
 raw=p.read_bytes();case=p.stem.removeprefix('context');w=(B/('witness'+case+'.bin')).read_bytes()
 if not raw:continue
 frame=struct.unpack_from('<9I',w,160)
 args=dict(witness_address=s['witness_record'],frame_address=frame[3]-32,return_eips=[s['context490_pre_return'],s['context490_post_return']])
 if len(raw)!=400:reject(lambda b=raw,a=args:context_decode(b,**a));continue
 d=context_decode(raw,**args);assert not d['own_close_attested'] and not d['later_paging_transition_attested'];contexts+=1
 # A full packet remains readable even if its own later lifecycle refused.
for p in B.glob('case*.bin'):
 raw=p.read_bytes()
 if len(raw)==176:primary_decode(raw)
 else:reject(lambda b=raw:primary_decode(b))
primary=(B/'case00.bin').read_bytes();w=(B/'witness000.bin').read_bytes();decode_witness(w,primary)
out.write_text(json.dumps(dict(passed=True,host_context_packets=contexts,host_refusals=refusals,negative_checks=neg,full_wrapper_cases=150,raw_executable_unchanged=True,privileged_CPU_facts='MODELED in this full-wrapper test; separate actual-instruction46-case fixture',physical_result=False),indent=2)+'\n')
print(json.dumps(dict(passed=True,contexts=contexts,refusals=refusals,negatives=neg)))

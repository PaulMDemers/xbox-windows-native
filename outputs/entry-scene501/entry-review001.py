"""Review actual fresh-launch provenance separately from early-entry decoding."""
import hashlib,json
from pathlib import Path
from entry_decode import decode
K=Path(__file__).resolve().parent;out=K/'entry-review001.json';assert not out.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda b:hashlib.sha256(b).hexdigest()
c=read(K/'physical001-collection.json');s=read(K/'physical001-stage.json');launch=read(K/'physical001-launch.json');pkg=read(K/'package001.json')
assert s['completed'] and c['completed'] and c['hook_removed'] and launch['requested']
assert launch['command']==r'SITE EXEC E:\Applications\XWNBoot499a\default.xbe'
root='/E/Applications/XWNBoot499a/';expected='22d3a9224965159a53cb188be9530f1b211aff8480d3d5773405d7e2974cf6d9'
assert s['staged'][root+'default.xbe']['sha256']==expected
assert c['files'][root+'default.xbe']['sha256']==expected and c['files'][root+'default.xbe']['unchanged']
for n,h in pkg['dependencies'].items():assert sha(Path(n).read_bytes())==h
row=c['files'][root+'entry.bin'];r=dict(actual_attempt=501,one_recorded_request=True,staged_and_cold_binary_exact=True,
 entry_execution_proved=False,missing_file_proves_no_entry=False,final_flush_close_proved=False,
 preparation_proved=False,windows_boot_proved=False,graphics_proved=False,originals_unchanged=True)
if row is None:r['state']='absent'
else:
 b=Path(row['path']).read_bytes();assert sha(b)==row['sha256'] and len(b)==row['bytes'];r['sha256']=sha(b);r['bytes']=len(b)
 try:r['decoded']=decode(b)
 except ValueError as e:r.update(state='malformed',error=str(e))
 else:
  r.update(state='complete',entry_execution_proved=True);count=0
  for length in range(len(b)):
   try:decode(b[:length])
   except ValueError:count+=1
   else:raise AssertionError('truncated actual entry accepted')
  for at in range(len(b)):
   bad=bytearray(b);bad[at]^=1
   try:decode(bytes(bad))
   except ValueError:count+=1
   else:raise AssertionError('mutated actual entry accepted')
  r['negative_controls']=count
  assert Path(row['path']).read_bytes()==b
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(r))

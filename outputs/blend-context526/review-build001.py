"""Independent final binary/source and retained physical transport checks."""
import ast,hashlib,json,struct,sys,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(K))
from primary_decode import decode as primary
from witness_decode import decode_witness
from decode import decode as context
out=K/'review-build001.json';assert not out.exists();js=lambda p:json.loads(p.read_bytes());sha=lambda b:hashlib.sha256(b).hexdigest()
p=Path('C:/xwn526/build002/default.xbe');b=p.read_bytes();prior=Path('C:/xwn494/build002/default.xbe').read_bytes()
old=b'\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot494a\\';new=old.replace(b'494',b'526');assert prior.count(old)==4
expected=bytearray(prior.replace(old,new));expected[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(expected)-4096)+expected[4096:]).digest()
assert b==expected and len(b)==542839 and sha(b)==js(K/'preflight001.json')['expected_sha256']
syms=js(K/'build002.json')['wrapper_symbols'];assert syms==js(K.parent/'d3d-transform494/build002.json')['wrapper_symbols']
for n in ['decode.py','primary_decode.py','witness_decode.py','legacy_refusal_decode.py','failure_marker.py','receipts.py']:assert (K/n).read_bytes()==(K.parent/'d3d-transform494'/n).read_bytes()
assert (K/'runner.c').read_bytes().replace(b'526',b'487')==(K.parent/'blend-precision487/runner.c').read_bytes()
assert Path('C:/xwn526/runner-build001/d3d.exe').read_bytes()==Path('C:/xwn487/runner-build001/d3d.exe').read_bytes()
# Use the CLOSED494 cold bytes as a decoder fixture; no recollection or execution.
c=js(K.parent/'d3d-transform494/physical001-collection.json');root='/E/Applications/XWNBoot494a/'
fixtures={}
for n in ['report.bin','handoff.bin','context.bin']:
 row=c['files'][root+n];data=Path(row['path']).read_bytes();assert sha(data)==row['sha256'];fixtures[n]=data
p,w,x=[fixtures[n] for n in ['report.bin','handoff.bin','context.bin']];pr=primary(p);wr=decode_witness(w,p);frame=struct.unpack_from('<9I',w,160)
args=dict(witness_address=syms['witness_record'],frame_address=frame[3]-32,return_eips=[syms['context490_pre_return'],syms['context490_post_return']])
cx=context(x,**args);assert not cx['own_close_attested']
rejects=0
for n in range(len(x)):
 try:context(x[:n],**args)
 except (ValueError,struct.error):rejects+=1
 else:raise AssertionError('truncated context accepted')
for n in [0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,384,388,392,396]:
 bad=bytearray(x);bad[n]^=1
 try:context(bytes(bad),**args)
 except (ValueError,struct.error):rejects+=1
 else:raise AssertionError('context identity mutation accepted')
for row in js(K/'source-copy001.json').values():assert sha(Path(row['parent']).read_bytes())==row['parent_sha256']
for f in K.glob('*.py'):ast.parse(f.read_text())
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bytes=542839,sha256=sha(b),exact494_except_four_namespaces_and_digest=True,all_symbols_exact=True,decoders_byte_exact=True,runner_exact487_except_namespace=True,sample_byte_exact486=True,retained494_fixture_only=True,context_transport_negatives=rejects,own_close_not_attested=True,physical_access=False,source_sha256=sha(Path(__file__).read_bytes()))
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(r)

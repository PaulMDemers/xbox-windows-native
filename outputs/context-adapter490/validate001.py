"""Independent binary/source closure and actual fixture transport negatives."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;H=Path('C:/xwn490/host001');B=Path('C:/xwn490/build001');P=Path('C:/xwn487/build001')
sys.path.insert(0,str(K));from review001 import review
from decode import decode
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'validation001.json';assert not out.exists()
b=json.loads((K/'build001.json').read_text());hb=json.loads((K/'host-build001.json').read_text());run=json.loads((K/'host-run001.json').read_text())
assert b['status']=='compiled' and hb['passed'] and run['passed'] and run['closed']
sym=b['wrapper_symbols'];old=(P/'default.xbe').read_bytes();new=(B/'default.xbe').read_bytes();u=lambda p,o:struct.unpack_from('<I',p,o)[0]
assert sha(B/'default.xbe')==b['sha256'] and new[:4]==b'XBEH'
assert u(new,0x104)==0x10000 and u(new,0x10c)==len(new) and u(new,0x11c)==1
sections=u(new,0x120)-0x10000;flags,va,vsize,raw,size=struct.unpack_from('<5I',new,sections)
assert (flags,va,raw)==(7,0x11000,4096) and vsize==size==len(new)-4096
assert new[sections+36:sections+56]==hashlib.sha1(struct.pack('<I',size)+new[raw:]).digest()
assert (u(new,0x128)^0xa8fc57ab)==sym['_start'] and (u(new,0x158)^0x5b6d40b6)==sym['section_1_start']
assert new[0x1000:0x1024]==old[0x1000:0x1024] and new[0x3000:0x84000]==old[0x3000:0x84000]
off=sym['blentry']-0x10000;assert new[off:off+1024]==old[off:off+1024]
assert sym['context490_path_end']<0x10000+len(new)
lo=sym['capture490_begin']-0x10000;hi=sym['capture490_end']-0x10000
assert hi-lo==313 and hashlib.sha256(new[lo:hi]).hexdigest()=='d5bed1052a1eeab8810e15f05734b2c9795d56641bf1ddb50e1a2618a808b196'
w=(B/'witness.S').read_text();w=w.replace('witness_entry:\n    call context490_pre\n','witness_entry:\n').replace('    call context490_post\n','').replace('490','487')
assert w==(P/'witness.S').read_text()
assert (B/'context.S').read_bytes()==(H/'context.S').read_bytes()==(K/'context.S').read_bytes()
assert (B/'capture.S').read_bytes()==(K.parent/'cpu-context489/capture.S').read_bytes()
raw=(H/'run001/capture.bin').read_bytes();review(raw,hb['symbols']);neg=0
def rejects(call):
 global neg
 try:call()
 except (ValueError,AssertionError,struct.error,IndexError):neg+=1
 else:raise AssertionError('mutation accepted')
# Every truncation of the actual complete fixture transport.
for n in range(len(raw)):rejects(lambda n=n:review(raw[:n],hb['symbols']))
rejects(lambda:review(raw+b'X',hb['symbols']))
packet=raw[9:409];frame=struct.unpack_from('<9I',raw,409);s=hb['symbols'];args=dict(witness_address=s['witness_record'],frame_address=frame[3]-32,return_eips=[s['context490_pre_return'],s['context490_post_return']])
decode(packet,**args)
# Complete header/trailer, slot identity/reserved/completion, actual return/stack
# and one-sided CR/table mutations. Legitimate varying CPU facts aren't rejected
# merely because they differ from this fixture.
fixed=set(range(64))|set(range(384,400))
for start in [64,224]:
 for a,z in [(0,20),(62,64),(70,80),(118,120),(126,160),(24,40),(56,62),(64,70)]:fixed.update(range(start+a,start+z))
for off in sorted(fixed):
 for bit in range(8):
  changed=bytearray(packet);changed[off]^=1<<bit
  rejects(lambda c=bytes(changed):decode(c,**args))
for field,value in [('witness_address',args['witness_address']+4),('frame_address',args['frame_address']+4),('return_eips',list(reversed(args['return_eips'])))]:
 changed=dict(args);changed[field]=value;rejects(lambda c=changed:decode(packet,**c))
pins={}
for rec in [b,hb,run]:
 for name,v in rec['files'].items():
  p=Path(name.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256'] and p.stat().st_size==v['bytes'];pins[name]=v
out.write_text(json.dumps(dict(passed=True,binary_sha256=sha(B/'default.xbe'),binary_bytes=len(new),source_reconstructed=True,loader1024_exact=True,capture313_exact=True,thunks_exact=True,payload_font_exact=True,fixture_transport_negative_checks=neg,private_files_rehashed=len(pins),host_cases=46,physical_access=False,full_wrapper_cleanup_tested=False,warning_review='One fixture-only RWX LOAD warning: deliberate flat writable code/data test image; not a new Xbox permission change.'),indent=2)+'\n')
print(json.dumps(dict(passed=True,negatives=neg,files=len(pins))))

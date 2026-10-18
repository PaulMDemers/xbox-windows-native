"""Independently invert fixed receipt ranges and decode retained494 context."""
from pathlib import Path
import hashlib,json,struct,sys
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(K))
from primary_decode import decode as primary
from witness_decode import decode_witness
from decode import decode
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
out=K/'review001.json';assert not out.exists()
q=read(K/'prepared001.json');parent=Path('C:/xwn494/build002/default.xbe').read_bytes()
assert sha(parent)==read(W/'outputs/d3d-transform494/build002.json')['sha256']
syms=q['wrapper_symbols'];ranges=[]
for name in ['report.bin','refusal.bin','handoff.bin','context.bin']:
    literal=('\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot494a\\'+name+'\0').encode()
    assert parent.count(literal)==1;ranges.append((parent.index(literal),literal))
for i,row in q['images'].items():
    data=Path(row['path']).read_bytes();assert len(data)==len(parent) and sha(data)==row['sha256']
    undo=bytearray(data)
    for off,original in ranges:
        assert data[off:off+len(original)]==original.replace(b'XWNBoot494a',('XWNBoot536'+('a' if i=='1' else 'b')).encode())
        undo[off:off+len(original)]=original
    assert data[0x36c:0x380]==hashlib.sha1(struct.pack('<I',len(data)-4096)+data[4096:]).digest()
    undo[0x36c:0x380]=parent[0x36c:0x380];assert bytes(undo)==parent
    for a,b in [('blentry',None),('capture490_begin','capture490_end')]:
        start=syms[a]-0x10000;end=start+1024 if b is None else syms[b]-0x10000
        assert data[start:end]==parent[start:end]
for name in ['decode.py','primary_decode.py','witness_decode.py','legacy_refusal_decode.py','failure_marker.py','receipts.py']:
    assert (K/name).read_bytes()==(W/'outputs/d3d-transform494'/name).read_bytes()
col=read(W/'outputs/d3d-transform494/physical001-collection.json')
fixture={}
for name in ['report.bin','handoff.bin','context.bin']:
    row=col['files']['/E/Applications/XWNBoot494a/'+name];b=Path(row['path']).read_bytes()
    assert sha(b)==row['sha256'];fixture[name]=b
p=primary(fixture['report.bin']);w=decode_witness(fixture['handoff.bin'],fixture['report.bin'])
frame=struct.unpack_from('<9I',fixture['handoff.bin'],160)
context=decode(fixture['context.bin'],witness_address=syms['witness_record'],frame_address=frame[3]-32,
               return_eips=[syms['context490_pre_return'],syms['context490_post_return']])
assert not context['own_close_attested'] and not context['mapping_validated']
out.write_text(json.dumps(dict(passed=True,images=2,full_inverse_reconstruction=True,
    instructions_and_layout_exact494=True,decoders_exact494=True,retained494_fixture_decoded=True,
    fixture_reexecuted_or_recollected=False,physical_access=False,source_sha256=sha(Path(__file__).read_bytes())),indent=2)+'\n')
print('PASS independent inverse reconstruction and retained context decoding')

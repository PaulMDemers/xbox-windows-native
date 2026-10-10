"""Post-capture 64-byte ordering discriminator, not the original probe gate."""
import hashlib,json,random,struct
from pathlib import Path

k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'physical64-analysis.json'
assert not dest.exists()
r=json.loads((k/'physical001.json').read_text());a=json.loads((k/'physical-audit001.json').read_text())
assert r['collected'] and r['probe_collection_passed'] and a['passed']
raw={n:(ws/row['path']).read_bytes() for n,row in r['reports'].items()}
sha=lambda b:hashlib.sha256(b).hexdigest()
for n,row in r['reports'].items():assert sha(raw[n])==row['sha256']
SIZE=20480

def index(i):
    assert 0<=i<SIZE
    return SIZE-64-(i//64)*64+i%64

def reversed_blocks(data,size):
    assert len(data)==SIZE and SIZE%size==0
    return b''.join(data[i:i+size] for i in reversed(range(0,SIZE,size)))

def compare(c0,c1,g0,g1):
    assert all(len(v)==SIZE for v in [c0,c1,g0,g1])
    predicted=bytes(c0[index(i)] for i in range(SIZE))
    words=struct.unpack('<5120I',c0)
    result=dict(cpu_stable=c0==c1,gpu_stable=g0==g1,
        nonzero_words=sum(v!=0 for v in words),
        distinct16_blocks=len(set(c0[i:i+16] for i in range(0,SIZE,16))),
        mismatched_bytes=sum(x!=y for x,y in zip(predicted,g0)),
        mismatched_words=sum(x!=y for x,y in zip(struct.unpack('<5120I',predicted),struct.unpack('<5120I',g0))))
    result['informative64_correlation']=result['cpu_stable'] and result['gpu_stable'] and result['nonzero_words']>=256 and result['distinct16_blocks']>=64 and result['mismatched_bytes']==0
    return result

checks=0
for i in range(SIZE):
    j=index(i);assert 0<=j<SIZE and index(j)==i and j%64==i%64;checks+=1
assert len({index(i) for i in range(SIZE)})==SIZE;checks+=1
for seed in range(16):
    gen=random.Random(seed);data=gen.randbytes(SIZE);other=reversed_blocks(data,64)
    assert bytes(data[index(i)] for i in range(SIZE))==other
    assert compare(data,data,other,other)['informative64_correlation'];checks+=2
    for i in [0,63,64,4095,4096,SIZE-64,SIZE-1]:
        damaged=bytearray(other);damaged[i]^=1
        v=compare(data,data,damaged,damaged)
        assert v['mismatched_bytes']==1 and v['mismatched_words']==1 and not v['informative64_correlation'];checks+=1
    changed=bytearray(data);changed[0]^=1
    assert not compare(data,changed,other,other)['informative64_correlation'];checks+=1
    assert not compare(data,data,other,damaged)['informative64_correlation'];checks+=1
    for size in [16,32,128]:
        wrong=reversed_blocks(data,size);assert not compare(data,data,wrong,wrong)['informative64_correlation'];checks+=1
assert not compare(bytes(SIZE),bytes(SIZE),bytes(SIZE),bytes(SIZE))['informative64_correlation'];checks+=1
actual=compare(*[raw[n] for n in ['cpu0.bin','cpu1.bin','gpu0.bin','gpu1.bin']])
assert actual['informative64_correlation'] and actual['mismatched_bytes']==0
out=dict(scope=__doc__,physical_result=True,physical_qualified=False,gpu_alias_proven=False,
    nt5_ownership_granted=False,post_hoc_discovery=True,original_gate_unchanged=True,
    actual=actual,host_tests=dict(passed=True,seeds=16,checks=checks),
    tested_reversal_sizes=[dict(block_bytes=s,mismatched_words=sum(x!=y for x,y in zip(struct.unpack('<5120I',reversed_blocks(raw['cpu0.bin'],s)),struct.unpack('<5120I',raw['gpu0.bin'])))) for s in [4,8,16,32,64,128,256,512,1024,4096]],
    formula='For observed GPU byte offset o in [0,0x5000): CPU physical=0x03ff0000-64-(o//64)*64+(o%64). GPU address=0xfd710000+o.',
    first_gpu_block_cpu_physical=0x03feffc0,last_gpu_block_cpu_physical=0x03feb000,
    bytes_compared_per_pass=SIZE,cpu_snapshot_sha256=sha(raw['cpu0.bin']),gpu_snapshot_sha256=sha(raw['gpu0.bin']),
    limits='Exact passive content correlation in two stable captures from one stock-kernel4034 boot. Does not prove causal alias/cache coherence or generalize outside the observed window; no writes, allocator resize, NT5 ownership, context switch or GPU copy.',
    inputs={p.relative_to(ws).as_posix():sha(p.read_bytes()) for p in [Path(__file__),k/'physical001.json',k/'physical-audit001.json']})
dest.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(actual=actual,host_tests=out['host_tests'])))

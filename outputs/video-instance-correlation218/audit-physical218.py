"""Read-only audit of the closed physical218 captures; no console access."""
import hashlib,json,struct,sys
from collections import Counter
from pathlib import Path

k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read(k/'physical001.json');dest=k/'physical-audit001.json'
assert r['collected'] and not dest.exists()
for name,digest in read(k/'physical-inputs.json').items():
    path=Path(name)
    if sys.platform!='win32' and len(name)>2 and name[1]==':':
        path=Path('/mnt/'+name[0].lower()+name[2:].replace('\\','/'))
    assert sha(path)==digest, name
for phase in ['before','after','reports']:
    for name,row in r[phase].items():
        p=ws/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex

def hive(p):
    h=hivex.Hivex(str(p));todo=[h.root()];seen=set();values=0
    while todo:
        n=todo.pop();assert n not in seen;seen.add(n);h.node_name(n)
        for v in h.node_values(n):h.value_key(v);h.value_value(v);values+=1
        todo.extend(h.node_children(n))
    return dict(parsed=True,keys=len(seen),values=values,sha256=sha(p))

out=dict(scope=__doc__,physical_result=True,physical_qualified=False,
    gpu_alias_proven=False,nt5_ownership_granted=False,hives=[],inputs={})
for n in ['system','software','default','sam','security']:
    path='/F/winnt/system32/config/'+n
    before=hive(ws/r['before'][path]['path']);after=hive(ws/r['after'][path]['path'])
    assert before==after
    out['hives'].append(dict(name=n,before=before,after=after,unchanged=True))
raw={n:(ws/row['path']).read_bytes() for n,row in r['reports'].items()}
assert raw['cpu0.bin']==raw['cpu1.bin'] and raw['gpu0.bin']==raw['gpu1.bin']
c,g=[struct.unpack('<5120I',raw[n]) for n in ['cpu0.bin','gpu0.bin']]
out['word_statistics']={name:dict(nonzero_words=sum(v!=0 for v in a),distinct_words=len(set(a))) for name,a in [('cpu',c),('gpu',g)]}
# Count exact nonzero block matches without assuming a transform. Duplicate
# blocks are retained as ambiguous; zero-only matches are excluded.
out['block_correspondence']=[]
for size in [16,32,64,128,256]:
    cb=[raw['cpu0.bin'][i:i+size] for i in range(0,20480,size)]
    gb=[raw['gpu0.bin'][i:i+size] for i in range(0,20480,size)]
    cc,gc=Counter(cb),Counter(gb);index={b:i for i,b in enumerate(cb) if cc[b]==1 and any(b)}
    pairs=[(index[b],i) for i,b in enumerate(gb) if b in index and gc[b]==1]
    out['block_correspondence'].append(dict(block_bytes=size,cpu_distinct_nonzero=sum(any(b) for b in cc),
        gpu_distinct_nonzero=sum(any(b) for b in gc),unique_nonzero_pairs=len(pairs),
        pairs=[dict(cpu_offset=a*size,gpu_offset=b*size) for a,b in pairs],
        limits='Matches are observational leads, not a causal alias, cache-coherence proof or ownership grant.'))
out.update(probe_collection_passed=r['probe_collection_passed'],baseline_files_unchanged=len(r['after']),
    dashboard_return_observed=bool(r.get('observed_return_utc')),closed=True,
    full_allocation_audit_performed=False,full_file_content_audit_performed=False,
    limits='Ten hive snapshots and 23 baseline file pairs; no full physical allocation or all-file audit. Stock kernel4034 differs from the calibrated emulator kernel4627. No Windows boot, GPU writes, cache flush, allocator resize or context operation.')
for p in [Path(__file__),k/'physical001.json',k/'physical-inputs.json']:
    out['inputs'][p.relative_to(ws).as_posix()]=sha(p)
out['passed']=out['probe_collection_passed'] and all(v['unchanged'] for v in out['hives'])
dest.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({n:out[n] for n in ['passed','baseline_files_unchanged','word_statistics','closed']}))
print(json.dumps([{n:v[n] for n in ['block_bytes','unique_nonzero_pairs']} for v in out['block_correspondence']]))
